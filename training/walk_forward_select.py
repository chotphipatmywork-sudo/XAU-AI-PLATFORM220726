"""Select and lock a candidate using expanding folds inside Train only."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import joblib

from chronological_calibrated_classifier import ChronologicalCalibratedClassifier
from select_candidate import candidate_models, candidate_policies, predict_with_policy
from train_classifier import (
    FEATURE_SCHEMA_VERSION,
    LABEL_SCHEMA_VERSION,
    TRAINING_CONTRACT_VERSION,
    evaluation_metrics,
    meets_evaluation_contract,
    read_dataset,
)


def build_expanding_folds(
    sample_count: int,
    fold_count: int = 4,
    initial_train_fraction: float = 0.50,
    purge_bars: int = 16,
) -> list[tuple[int, int, int]]:
    """Return (train_end, evaluation_start, evaluation_end) in chronological order."""
    if fold_count < 2 or sample_count < 100 or purge_bars <= 0:
        raise ValueError("Walk-forward selection requires at least two folds and 100 samples")
    initial_train = int(sample_count * initial_train_fraction)
    remaining = sample_count - initial_train
    if initial_train < 30 or remaining < fold_count:
        raise ValueError("Insufficient samples for the requested expanding folds")

    base_size = remaining // fold_count
    folds: list[tuple[int, int, int]] = []
    start = initial_train
    for fold_index in range(fold_count):
        end = sample_count if fold_index == fold_count - 1 else start + base_size
        train_end = start - purge_bars
        if train_end < 30:
            raise ValueError("Insufficient training history after the label-horizon purge")
        folds.append((train_end, start, end))
        start = end
    return folds


def fresh_model(candidate_name: str) -> Any:
    for name, model in candidate_models():
        if name == candidate_name:
            return model
    raise ValueError(f"Unknown candidate model: {candidate_name}")


def metrics_for_folds(
    actual: list[int],
    predicted: list[int],
    fold_lengths: list[int],
) -> list[dict[str, float | int]]:
    metrics: list[dict[str, float | int]] = []
    offset = 0
    for fold_length in fold_lengths:
        end = offset + fold_length
        metrics.append(evaluation_metrics(actual[offset:end], predicted[offset:end]))
        offset = end
    return metrics


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--folds", type=int, default=4)
    parser.add_argument("--purge-bars", type=int, default=16)
    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()
    if arguments.purge_bars != 16:
        raise ValueError("Feature/Label Contract 3.0/1.1 requires a 16-bar purge")
    features, labels = read_dataset(arguments.train)
    folds = build_expanding_folds(len(features), arguments.folds, purge_bars=arguments.purge_bars)
    candidate_names = [name for name, _ in candidate_models()]

    results: list[dict[str, Any]] = []
    selected_key = (-1, -1, -1.0, -1.0)
    selected: dict[str, Any] | None = None

    for candidate_name in candidate_names:
        variant_probabilities: dict[str, list[list[float]]] = {"raw": [], "calibrated": []}
        variant_classes: dict[str, list[int]] = {}
        actual: list[int] = []
        fold_lengths: list[int] = []

        for train_end, evaluation_start, evaluation_end in folds:
            train_features = features[:train_end]
            train_labels = labels[:train_end]
            evaluation_features = features[evaluation_start:evaluation_end]
            evaluation_labels = labels[evaluation_start:evaluation_end]

            raw_model = fresh_model(candidate_name)
            raw_model.fit(train_features, train_labels)
            variant_probabilities["raw"].extend(raw_model.predict_proba(evaluation_features).tolist())
            variant_classes["raw"] = [int(value) for value in raw_model.classes_.tolist()]

            calibrated_model = ChronologicalCalibratedClassifier(
                fresh_model(candidate_name), purge_bars=arguments.purge_bars
            )
            calibrated_model.fit(train_features, train_labels)
            variant_probabilities["calibrated"].extend(
                calibrated_model.predict_proba(evaluation_features).tolist()
            )
            variant_classes["calibrated"] = [int(value) for value in calibrated_model.classes_.tolist()]

            actual.extend(evaluation_labels)
            fold_lengths.append(len(evaluation_labels))

        for variant_name in ("raw", "calibrated"):
            for policy_name, policy in candidate_policies():
                predicted = predict_with_policy(
                    variant_probabilities[variant_name], variant_classes[variant_name], policy
                )
                aggregate_metrics = evaluation_metrics(actual, predicted)
                fold_metrics = metrics_for_folds(actual, predicted, fold_lengths)
                folds_passing = sum(meets_evaluation_contract(item) for item in fold_metrics)
                aggregate_gate_met = meets_evaluation_contract(aggregate_metrics)
                stable_gate_met = aggregate_gate_met and folds_passing == len(folds)
                result = {
                    "model_candidate": candidate_name,
                    "probability_variant": variant_name,
                    "decision_policy_name": policy_name,
                    "decision_policy": policy,
                    "aggregate_metrics": aggregate_metrics,
                    "aggregate_gate_met": aggregate_gate_met,
                    "folds_passing_gate": folds_passing,
                    "stable_walk_forward_gate_met": stable_gate_met,
                }
                results.append(result)
                selection_key = (
                    int(stable_gate_met),
                    folds_passing,
                    float(aggregate_metrics["macro_f1"]),
                    float(aggregate_metrics["accuracy"]),
                )
                if selection_key > selected_key:
                    selected_key = selection_key
                    selected = result

    if selected is None:
        raise RuntimeError("No walk-forward candidate was evaluated")

    final_base_model = fresh_model(str(selected["model_candidate"]))
    if selected["probability_variant"] == "calibrated":
        locked_model: Any = ChronologicalCalibratedClassifier(
            final_base_model, purge_bars=arguments.purge_bars
        )
        locked_model.fit(features, labels)
    else:
        final_base_model.fit(features, labels)
        locked_model = final_base_model

    arguments.output_dir.mkdir(parents=True, exist_ok=True)
    model_path = arguments.output_dir / "xau_ai_walk_forward_locked.joblib"
    policy_path = arguments.output_dir / "xau_ai_walk_forward_locked_policy.json"
    report_path = arguments.output_dir / "walk_forward_diagnostics.json"
    joblib.dump(locked_model, model_path)
    policy_path.write_text(json.dumps({
        "training_contract_version": TRAINING_CONTRACT_VERSION,
        "feature_schema_version": FEATURE_SCHEMA_VERSION,
        "label_schema_version": LABEL_SCHEMA_VERSION,
        "purge_bars": arguments.purge_bars,
        "model_candidate": selected["model_candidate"],
        "probability_variant": selected["probability_variant"],
        "decision_policy_name": selected["decision_policy_name"],
        "decision_policy": selected["decision_policy"],
        "deployment_authorized": False,
    }, indent=2), encoding="utf-8")

    report = {
        "selection_stage": "train_internal_walk_forward_only",
        "validation_dataset_used": False,
        "test_dataset_used": False,
        "training_contract_version": TRAINING_CONTRACT_VERSION,
        "feature_schema_version": FEATURE_SCHEMA_VERSION,
        "label_schema_version": LABEL_SCHEMA_VERSION,
        "fold_count": len(folds),
        "purge_bars": arguments.purge_bars,
        "folds": [
            {"train_records": train_end, "evaluation_start": start, "evaluation_end": end,
             "purged_records": start - train_end,
             "evaluation_records": end - start}
            for train_end, start, end in folds
        ],
        "selection_metric": "stable_gate_then_folds_passed_then_macro_f1_then_accuracy",
        "candidates": results,
        "selected": selected,
        "locked_model_file": str(model_path),
        "locked_policy_file": str(policy_path),
        "limitations": [
            "Selection uses only expanding folds inside Train.",
            "Each fold and internal calibration boundary purges the 16-bar label horizon.",
            "The locked artifact is not eligible for MQL5 or trading deployment.",
            "A newly generated later-period evaluation set is required after the methodology is frozen.",
        ],
    }
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({
        "selection_stage": report["selection_stage"],
        "validation_dataset_used": False,
        "test_dataset_used": False,
        "fold_count": len(folds),
        "purge_bars": arguments.purge_bars,
        "selected": selected,
        "locked_model_file": str(model_path),
        "locked_policy_file": str(policy_path),
        "diagnostics_file": str(report_path),
    }, indent=2))


if __name__ == "__main__":
    main()
