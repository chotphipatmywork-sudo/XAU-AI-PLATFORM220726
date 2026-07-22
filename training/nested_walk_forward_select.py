"""Select and evaluate a model with nested purged walk-forward folds inside Train only."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Sequence

import joblib

from chronological_calibrated_classifier import ChronologicalCalibratedClassifier
from select_candidate import candidate_models, predict_with_policy
from train_classifier import (
    FEATURE_SCHEMA_VERSION,
    LABEL_SCHEMA_VERSION,
    TRAINING_CONTRACT_VERSION,
    evaluation_metrics,
    meets_evaluation_contract,
    read_dataset,
)
from walk_forward_select import build_expanding_folds, fresh_model, metrics_for_folds


PURGE_BARS = 16
GATE_THRESHOLDS = {
    "accuracy": 0.45,
    "macro_f1": 0.40,
    "sell_precision": 0.50,
    "sell_recall": 0.30,
    "buy_precision": 0.50,
    "buy_recall": 0.30,
}


def nested_candidate_policies() -> list[tuple[str, dict[str, float | str]]]:
    """Return a bounded asymmetric policy grid for Train-only inner selection."""
    policies: list[tuple[str, dict[str, float | str]]] = [("argmax", {"type": "argmax"})]
    for sell_minimum in (0.35, 0.40):
        for buy_minimum in (0.40, 0.45, 0.50, 0.55, 0.60):
            for margin in (0.00, 0.02, 0.05):
                name = (
                    f"asymmetric_sell_{sell_minimum:.2f}_buy_{buy_minimum:.2f}"
                    f"_margin_{margin:.2f}"
                ).replace(".", "_")
                policies.append((name, {
                    "type": "confidence",
                    "sell_minimum": sell_minimum,
                    "buy_minimum": buy_minimum,
                    "margin": margin,
                }))
    return policies


def gate_floor_ratio(metrics: dict[str, float | int]) -> float:
    """Measure the weakest contract metric relative to its required threshold."""
    return min(float(metrics[name]) / threshold for name, threshold in GATE_THRESHOLDS.items())


def selection_key(
    metrics: dict[str, float | int],
    folds_passing: int,
    fold_count: int,
) -> tuple[int, int, int, float, float, float]:
    """Prioritize full stability, then the weakest gate metric and broad quality."""
    aggregate_gate = meets_evaluation_contract(metrics)
    stable_gate = aggregate_gate and folds_passing == fold_count
    return (
        int(stable_gate),
        folds_passing,
        int(aggregate_gate),
        gate_floor_ratio(metrics),
        float(metrics["macro_f1"]),
        float(metrics["accuracy"]),
    )


def fit_variant(
    candidate_name: str,
    probability_variant: str,
    features: Sequence[Sequence[float]],
    labels: Sequence[int],
) -> Any:
    """Fit one raw or chronologically calibrated candidate."""
    if probability_variant == "raw":
        model = fresh_model(candidate_name)
    elif probability_variant == "calibrated":
        model = ChronologicalCalibratedClassifier(
            fresh_model(candidate_name), purge_bars=PURGE_BARS
        )
    else:
        raise ValueError(f"Unknown probability variant: {probability_variant}")
    model.fit(features, labels)
    return model


def select_on_inner_folds(
    features: list[list[float]],
    labels: list[int],
    fold_count: int,
) -> dict[str, Any]:
    """Select one configuration using only purged folds inside the supplied history."""
    folds = build_expanding_folds(
        len(features), fold_count=fold_count, purge_bars=PURGE_BARS
    )
    results: list[dict[str, Any]] = []
    best_key = (-1, -1, -1, -1.0, -1.0, -1.0)
    selected: dict[str, Any] | None = None

    for candidate_name, _ in candidate_models():
        variant_probabilities: dict[str, list[list[float]]] = {"raw": [], "calibrated": []}
        variant_classes: dict[str, list[int]] = {}
        actual: list[int] = []
        fold_lengths: list[int] = []

        for train_end, evaluation_start, evaluation_end in folds:
            train_features = features[:train_end]
            train_labels = labels[:train_end]
            evaluation_features = features[evaluation_start:evaluation_end]
            evaluation_labels = labels[evaluation_start:evaluation_end]
            for variant_name in ("raw", "calibrated"):
                model = fit_variant(candidate_name, variant_name, train_features, train_labels)
                variant_probabilities[variant_name].extend(
                    model.predict_proba(evaluation_features).tolist()
                )
                variant_classes[variant_name] = [
                    int(value) for value in model.classes_.tolist()
                ]
            actual.extend(evaluation_labels)
            fold_lengths.append(len(evaluation_labels))

        for variant_name in ("raw", "calibrated"):
            for policy_name, policy in nested_candidate_policies():
                predicted = predict_with_policy(
                    variant_probabilities[variant_name], variant_classes[variant_name], policy
                )
                aggregate_metrics = evaluation_metrics(actual, predicted)
                fold_metrics = metrics_for_folds(actual, predicted, fold_lengths)
                folds_passing = sum(meets_evaluation_contract(item) for item in fold_metrics)
                result = {
                    "model_candidate": candidate_name,
                    "probability_variant": variant_name,
                    "decision_policy_name": policy_name,
                    "decision_policy": policy,
                    "aggregate_metrics": aggregate_metrics,
                    "gate_floor_ratio": gate_floor_ratio(aggregate_metrics),
                    "aggregate_gate_met": meets_evaluation_contract(aggregate_metrics),
                    "folds_passing_gate": folds_passing,
                    "stable_inner_gate_met": (
                        meets_evaluation_contract(aggregate_metrics)
                        and folds_passing == len(folds)
                    ),
                }
                results.append(result)
                key = selection_key(aggregate_metrics, folds_passing, len(folds))
                if key > best_key:
                    best_key = key
                    selected = result

    if selected is None:
        raise RuntimeError("Nested inner selection evaluated no candidates")
    ranked = sorted(
        results,
        key=lambda item: selection_key(
            item["aggregate_metrics"], int(item["folds_passing_gate"]), len(folds)
        ),
        reverse=True,
    )
    return {
        "fold_count": len(folds),
        "candidate_policy_combinations": len(results),
        "selected": selected,
        "top_candidates": ranked[:10],
    }


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--outer-folds", type=int, default=4)
    parser.add_argument("--inner-folds", type=int, default=3)
    parser.add_argument("--purge-bars", type=int, default=PURGE_BARS)
    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()
    if arguments.purge_bars != PURGE_BARS:
        raise ValueError(
            f"Feature/Label Contract {FEATURE_SCHEMA_VERSION}/{LABEL_SCHEMA_VERSION} "
            "requires a 16-bar purge"
        )
    features, labels = read_dataset(arguments.train)
    outer_folds = build_expanding_folds(
        len(features), fold_count=arguments.outer_folds, purge_bars=PURGE_BARS
    )

    outer_actual: list[int] = []
    outer_predicted: list[int] = []
    outer_fold_reports: list[dict[str, Any]] = []
    outer_fold_lengths: list[int] = []
    for fold_index, (train_end, evaluation_start, evaluation_end) in enumerate(
        outer_folds, start=1
    ):
        history_features = features[:train_end]
        history_labels = labels[:train_end]
        inner = select_on_inner_folds(
            history_features, history_labels, fold_count=arguments.inner_folds
        )
        selected = inner["selected"]
        model = fit_variant(
            str(selected["model_candidate"]),
            str(selected["probability_variant"]),
            history_features,
            history_labels,
        )
        evaluation_features = features[evaluation_start:evaluation_end]
        evaluation_labels = labels[evaluation_start:evaluation_end]
        predictions = predict_with_policy(
            model.predict_proba(evaluation_features).tolist(),
            [int(value) for value in model.classes_.tolist()],
            dict(selected["decision_policy"]),
        )
        metrics = evaluation_metrics(evaluation_labels, predictions)
        outer_actual.extend(evaluation_labels)
        outer_predicted.extend(predictions)
        outer_fold_lengths.append(len(evaluation_labels))
        outer_fold_reports.append({
            "fold": fold_index,
            "train_records": train_end,
            "purged_records": evaluation_start - train_end,
            "evaluation_start": evaluation_start,
            "evaluation_end": evaluation_end,
            "evaluation_records": len(evaluation_labels),
            "inner_selection": inner,
            "outer_metrics": metrics,
            "outer_gate_met": meets_evaluation_contract(metrics),
        })

    aggregate_metrics = evaluation_metrics(outer_actual, outer_predicted)
    outer_metrics = metrics_for_folds(outer_actual, outer_predicted, outer_fold_lengths)
    outer_folds_passing = sum(meets_evaluation_contract(item) for item in outer_metrics)
    nested_gate_met = (
        meets_evaluation_contract(aggregate_metrics)
        and outer_folds_passing == len(outer_folds)
    )

    final_inner = select_on_inner_folds(
        features, labels, fold_count=arguments.inner_folds
    )
    final_selected = final_inner["selected"]
    locked_model = fit_variant(
        str(final_selected["model_candidate"]),
        str(final_selected["probability_variant"]),
        features,
        labels,
    )

    arguments.output_dir.mkdir(parents=True, exist_ok=True)
    model_path = arguments.output_dir / "xau_ai_nested_walk_forward_locked.joblib"
    policy_path = arguments.output_dir / "xau_ai_nested_walk_forward_locked_policy.json"
    report_path = arguments.output_dir / "nested_walk_forward_diagnostics.json"
    joblib.dump(locked_model, model_path)
    policy_path.write_text(json.dumps({
        "methodology_version": "1.0.0",
        "training_contract_version": TRAINING_CONTRACT_VERSION,
        "feature_schema_version": FEATURE_SCHEMA_VERSION,
        "label_schema_version": LABEL_SCHEMA_VERSION,
        "purge_bars": PURGE_BARS,
        "model_candidate": final_selected["model_candidate"],
        "probability_variant": final_selected["probability_variant"],
        "decision_policy_name": final_selected["decision_policy_name"],
        "decision_policy": final_selected["decision_policy"],
        "deployment_authorized": False,
    }, indent=2), encoding="utf-8")

    report = {
        "selection_stage": "train_internal_nested_purged_walk_forward_only",
        "validation_dataset_used": False,
        "test_dataset_used": False,
        "methodology_version": "1.0.0",
        "training_contract_version": TRAINING_CONTRACT_VERSION,
        "feature_schema_version": FEATURE_SCHEMA_VERSION,
        "label_schema_version": LABEL_SCHEMA_VERSION,
        "purge_bars": PURGE_BARS,
        "outer_fold_count": len(outer_folds),
        "inner_fold_count": arguments.inner_folds,
        "selection_metric": "stable_gate_then_folds_then_gate_floor_then_macro_f1_then_accuracy",
        "outer_folds": outer_fold_reports,
        "aggregate_outer_metrics": aggregate_metrics,
        "outer_folds_passing_gate": outer_folds_passing,
        "nested_stable_gate_met": nested_gate_met,
        "final_full_train_inner_selection": final_inner,
        "locked_model_file": str(model_path),
        "locked_policy_file": str(policy_path),
        "limitations": [
            "Only the purged Train partition is read; Validation and Test remain untouched.",
            "Outer folds estimate a selection process; they are not used to choose each outer configuration.",
            "The locked artifacts are Python-only development outputs and are not deployment authorization.",
        ],
    }
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({
        "selection_stage": report["selection_stage"],
        "validation_dataset_used": False,
        "test_dataset_used": False,
        "purge_bars": PURGE_BARS,
        "outer_fold_count": len(outer_folds),
        "inner_fold_count": arguments.inner_folds,
        "aggregate_outer_metrics": aggregate_metrics,
        "outer_folds_passing_gate": outer_folds_passing,
        "nested_stable_gate_met": nested_gate_met,
        "final_selected": final_selected,
        "locked_model_file": str(model_path),
        "locked_policy_file": str(policy_path),
        "diagnostics_file": str(report_path),
    }, indent=2))


if __name__ == "__main__":
    main()
