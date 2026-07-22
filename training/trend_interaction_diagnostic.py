"""Compare deterministic Trend-group interaction candidates on purged Train folds."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable, Sequence

from nested_walk_forward_select import gate_floor_ratio, selection_key
from select_candidate import predict_with_policy
from train_classifier import evaluation_metrics, meets_evaluation_contract, read_dataset
from walk_forward_select import build_expanding_folds, fresh_model, metrics_for_folds


PURGE_BARS = 16
MODEL_CANDIDATE = "random_forest_depth_5_balanced"
DECISION_POLICY: dict[str, str] = {"type": "argmax"}


def trend_interactions(row: Sequence[float]) -> list[float]:
    """Derive bounded interaction candidates from the three approved Trend dimensions."""
    regime = (float(row[0]) - 50.0) / 50.0
    momentum = (float(row[1]) - 50.0) / 50.0
    slope = (float(row[2]) - 50.0) / 50.0
    return [
        abs(regime) * 100.0,
        50.0 + 50.0 * regime * momentum,
        50.0 + 50.0 * regime * slope,
        50.0 + 50.0 * momentum * slope,
        50.0 + 25.0 * (momentum - regime),
        50.0 + 25.0 * (slope - regime),
    ]


def feature_set_specs() -> list[dict[str, Any]]:
    """Return a bounded controlled grid of Trend interaction groups."""
    return [
        {"name": "baseline", "interaction_indices": []},
        {"name": "trend_extension", "interaction_indices": [0]},
        {"name": "trend_agreements", "interaction_indices": [1, 2, 3]},
        {"name": "trend_leads", "interaction_indices": [4, 5]},
        {"name": "trend_extension_and_agreements", "interaction_indices": [0, 1, 2, 3]},
        {"name": "all_trend_interactions", "interaction_indices": [0, 1, 2, 3, 4, 5]},
    ]


def transform_features(
    features: Sequence[Sequence[float]],
    interaction_indices: Sequence[int],
) -> list[list[float]]:
    """Append selected deterministic Trend interactions without changing base values."""
    result: list[list[float]] = []
    for row in features:
        derived = trend_interactions(row)
        transformed = [float(value) for value in row]
        transformed.extend(derived[index] for index in interaction_indices)
        if any(value < 0.0 or value > 100.0 for value in transformed):
            raise ValueError("Transformed feature is outside 0..100")
        result.append(transformed)
    return result


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--folds", type=int, default=4)
    parser.add_argument("--purge-bars", type=int, default=PURGE_BARS)
    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()
    if arguments.purge_bars != PURGE_BARS:
        raise ValueError("Feature/Label Contract 3.0/1.1 requires a 16-bar purge")
    features, labels = read_dataset(arguments.train)
    folds = build_expanding_folds(
        len(features), fold_count=arguments.folds, purge_bars=PURGE_BARS
    )

    feature_set_results: list[dict[str, Any]] = []
    for feature_set in feature_set_specs():
        interaction_indices = list(feature_set["interaction_indices"])
        transformed = transform_features(features, interaction_indices)
        aggregate_actual: list[int] = []
        aggregate_predicted: list[int] = []
        fold_lengths: list[int] = []
        fold_reports: list[dict[str, Any]] = []
        for fold_index, (train_end, evaluation_start, evaluation_end) in enumerate(
            folds, start=1
        ):
            model = fresh_model(MODEL_CANDIDATE)
            model.fit(transformed[:train_end], labels[:train_end])
            evaluation_features = transformed[evaluation_start:evaluation_end]
            evaluation_labels = labels[evaluation_start:evaluation_end]
            predictions = predict_with_policy(
                model.predict_proba(evaluation_features).tolist(),
                [int(value) for value in model.classes_.tolist()],
                DECISION_POLICY,
            )
            metrics = evaluation_metrics(evaluation_labels, predictions)
            aggregate_actual.extend(evaluation_labels)
            aggregate_predicted.extend(predictions)
            fold_lengths.append(len(evaluation_labels))
            fold_reports.append({
                "fold": fold_index,
                "train_records": train_end,
                "purged_records": evaluation_start - train_end,
                "evaluation_records": len(evaluation_labels),
                "metrics": metrics,
                "gate_met": meets_evaluation_contract(metrics),
            })

        aggregate_metrics = evaluation_metrics(aggregate_actual, aggregate_predicted)
        per_fold_metrics = metrics_for_folds(
            aggregate_actual, aggregate_predicted, fold_lengths
        )
        folds_passing = sum(meets_evaluation_contract(metrics) for metrics in per_fold_metrics)
        feature_set_results.append({
            "feature_set": feature_set["name"],
            "base_feature_count": len(features[0]),
            "derived_feature_count": len(interaction_indices),
            "total_feature_count": len(transformed[0]),
            "interaction_indices": interaction_indices,
            "aggregate_metrics": aggregate_metrics,
            "gate_floor_ratio": gate_floor_ratio(aggregate_metrics),
            "aggregate_gate_met": meets_evaluation_contract(aggregate_metrics),
            "folds_passing_gate": folds_passing,
            "stable_gate_met": (
                meets_evaluation_contract(aggregate_metrics) and folds_passing == len(folds)
            ),
            "folds": fold_reports,
        })

    ranked = sorted(
        feature_set_results,
        key=lambda item: selection_key(
            item["aggregate_metrics"], int(item["folds_passing_gate"]), len(folds)
        ),
        reverse=True,
    )
    report = {
        "diagnostic_stage": "train_only_purged_trend_interaction_comparison",
        "validation_dataset_used": False,
        "test_dataset_used": False,
        "training_contract_version": "3.0.0",
        "source_feature_schema_version": "3.0.0",
        "label_schema_version": "1.1.0",
        "purge_bars": PURGE_BARS,
        "model_candidate": MODEL_CANDIDATE,
        "probability_variant": "raw",
        "decision_policy": DECISION_POLICY,
        "derived_feature_names": [
            "trend_extension",
            "regime_momentum_agreement",
            "regime_slope_agreement",
            "momentum_slope_agreement",
            "momentum_lead_over_regime",
            "slope_lead_over_regime",
        ],
        "comparison_control": "only_deterministic_trend_interaction_columns_change",
        "feature_sets_ranked": [item["feature_set"] for item in ranked],
        "feature_sets": feature_set_results,
        "best_diagnostic_feature_set": ranked[0]["feature_set"],
        "limitations": [
            "This experiment reuses already-inspected Train Outer periods.",
            "Derived columns are diagnostic-only and are not Feature Contract 3.0 inputs.",
            "Only one fixed raw model and argmax policy are compared.",
            "Validation and Test are not read and no MQL5 or deployment change is authorized.",
        ],
    }
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({
        "diagnostic_stage": report["diagnostic_stage"],
        "validation_dataset_used": False,
        "test_dataset_used": False,
        "purge_bars": PURGE_BARS,
        "feature_sets_ranked": report["feature_sets_ranked"],
        "results": [
            {
                "feature_set": item["feature_set"],
                "derived_feature_count": item["derived_feature_count"],
                "aggregate_metrics": item["aggregate_metrics"],
                "gate_floor_ratio": item["gate_floor_ratio"],
                "folds_passing_gate": item["folds_passing_gate"],
            }
            for item in ranked
        ],
        "diagnostic_file": str(arguments.output),
    }, indent=2))


if __name__ == "__main__":
    main()
