"""Compare past-only Trend dynamics on purged Train folds without changing Schema 3.0."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Sequence

from nested_walk_forward_select import gate_floor_ratio, selection_key
from select_candidate import predict_with_policy
from train_classifier import evaluation_metrics, meets_evaluation_contract, read_dataset
from walk_forward_select import build_expanding_folds, fresh_model, metrics_for_folds


PURGE_BARS = 16
MODEL_CANDIDATE = "random_forest_depth_5_balanced"
DECISION_POLICY: dict[str, str] = {"type": "argmax"}
MAXIMUM_TREND_AGE = 16


def bounded_delta(current: float, previous: float) -> float:
    """Map a -100..100 past-only change into 0..100 with neutral at 50."""
    return 50.0 + (float(current) - float(previous)) / 2.0


def trend_side(value: float) -> int:
    if value > 50.0:
        return 1
    if value < 50.0:
        return -1
    return 0


def trend_age(features: Sequence[Sequence[float]], index: int) -> float:
    """Return capped consecutive Regime-side age using current and past rows only."""
    side = trend_side(float(features[index][0]))
    if side == 0:
        return 0.0
    age = 0
    cursor = index
    while cursor >= 0 and age < MAXIMUM_TREND_AGE:
        if trend_side(float(features[cursor][0])) != side:
            break
        age += 1
        cursor -= 1
    return 100.0 * age / MAXIMUM_TREND_AGE


def derive_trend_dynamics(features: Sequence[Sequence[float]]) -> list[list[float]]:
    """Return eight bounded dynamic columns computed without future rows."""
    derived_rows: list[list[float]] = []
    for index, row in enumerate(features):
        def delta(feature_index: int, lookback: int) -> float:
            if index < lookback:
                return 50.0
            return bounded_delta(float(row[feature_index]), float(features[index - lookback][feature_index]))

        derived = [
            delta(0, 1),
            delta(0, 4),
            delta(0, 8),
            delta(1, 1),
            delta(1, 4),
            delta(2, 1),
            delta(2, 4),
            trend_age(features, index),
        ]
        if any(value < 0.0 or value > 100.0 for value in derived):
            raise ValueError("Derived Trend dynamic is outside 0..100")
        derived_rows.append(derived)
    return derived_rows


def feature_set_specs() -> list[dict[str, Any]]:
    return [
        {"name": "baseline", "dynamic_indices": []},
        {"name": "trend_age", "dynamic_indices": [7]},
        {"name": "regime_dynamics", "dynamic_indices": [0, 1, 2, 7]},
        {"name": "short_dynamics", "dynamic_indices": [0, 3, 5, 7]},
        {"name": "medium_dynamics", "dynamic_indices": [1, 4, 6, 7]},
        {"name": "change_only", "dynamic_indices": [0, 1, 2, 3, 4, 5, 6]},
        {"name": "all_trend_dynamics", "dynamic_indices": list(range(8))},
    ]


def transform_features(
    features: Sequence[Sequence[float]],
    dynamic_indices: Sequence[int],
) -> list[list[float]]:
    dynamics = derive_trend_dynamics(features)
    return [
        [float(value) for value in row] + [dynamics[index][item] for item in dynamic_indices]
        for index, row in enumerate(features)
    ]


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

    results: list[dict[str, Any]] = []
    for feature_set in feature_set_specs():
        indices = list(feature_set["dynamic_indices"])
        transformed = transform_features(features, indices)
        actual: list[int] = []
        predicted: list[int] = []
        fold_lengths: list[int] = []
        fold_reports: list[dict[str, Any]] = []
        for fold_index, (train_end, evaluation_start, evaluation_end) in enumerate(
            folds, start=1
        ):
            model = fresh_model(MODEL_CANDIDATE)
            model.fit(transformed[:train_end], labels[:train_end])
            evaluation_features = transformed[evaluation_start:evaluation_end]
            evaluation_labels = labels[evaluation_start:evaluation_end]
            fold_prediction = predict_with_policy(
                model.predict_proba(evaluation_features).tolist(),
                [int(value) for value in model.classes_.tolist()],
                DECISION_POLICY,
            )
            metrics = evaluation_metrics(evaluation_labels, fold_prediction)
            actual.extend(evaluation_labels)
            predicted.extend(fold_prediction)
            fold_lengths.append(len(evaluation_labels))
            fold_reports.append({
                "fold": fold_index,
                "train_records": train_end,
                "purged_records": evaluation_start - train_end,
                "evaluation_records": len(evaluation_labels),
                "metrics": metrics,
                "gate_met": meets_evaluation_contract(metrics),
            })
        aggregate_metrics = evaluation_metrics(actual, predicted)
        fold_metrics = metrics_for_folds(actual, predicted, fold_lengths)
        folds_passing = sum(meets_evaluation_contract(item) for item in fold_metrics)
        results.append({
            "feature_set": feature_set["name"],
            "dynamic_indices": indices,
            "derived_feature_count": len(indices),
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
        results,
        key=lambda item: selection_key(
            item["aggregate_metrics"], int(item["folds_passing_gate"]), len(folds)
        ),
        reverse=True,
    )
    report = {
        "diagnostic_stage": "train_only_purged_past_trend_dynamics_comparison",
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
            "trend_regime_delta_1",
            "trend_regime_delta_4",
            "trend_regime_delta_8",
            "trend_momentum_delta_1",
            "trend_momentum_delta_4",
            "trend_slope_delta_1",
            "trend_slope_delta_4",
            "trend_regime_age_16",
        ],
        "future_rows_used": False,
        "feature_sets_ranked": [item["feature_set"] for item in ranked],
        "feature_sets": results,
        "best_diagnostic_feature_set": ranked[0]["feature_set"],
        "limitations": [
            "This controlled experiment reuses already-inspected Train Outer periods.",
            "Past-only dynamics are diagnostic columns, not active Feature Schema 3.0 inputs.",
            "Sequence indices represent available records and may span market closures.",
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
        "future_rows_used": False,
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
