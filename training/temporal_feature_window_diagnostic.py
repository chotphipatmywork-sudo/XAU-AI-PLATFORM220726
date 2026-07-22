"""Compare fixed past Brain feature windows on purged Train folds."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Sequence

from nested_walk_forward_select import gate_floor_ratio, selection_key
from select_candidate import predict_with_policy
from train_classifier import (
    FEATURE_COLUMNS,
    FEATURE_SCHEMA_VERSION,
    LABEL_SCHEMA_VERSION,
    TRAINING_CONTRACT_VERSION,
    evaluation_metrics,
    meets_evaluation_contract,
    read_dataset,
)
from walk_forward_select import build_expanding_folds, fresh_model, metrics_for_folds


PURGE_BARS = 16
MODEL_CANDIDATE = "random_forest_depth_5_balanced"
DECISION_POLICY: dict[str, str] = {"type": "argmax"}


def contract_metadata() -> dict[str, str]:
    return {
        "training_contract_version": TRAINING_CONTRACT_VERSION,
        "source_feature_schema_version": FEATURE_SCHEMA_VERSION,
        "label_schema_version": LABEL_SCHEMA_VERSION,
    }


def feature_set_specs() -> list[dict[str, Any]]:
    return [
        {"name": "baseline", "lags": []},
        {"name": "lag_1", "lags": [1]},
        {"name": "lags_1_4", "lags": [1, 4]},
        {"name": "lags_1_4_8", "lags": [1, 4, 8]},
    ]


def transform_features(
    features: Sequence[Sequence[float]],
    lags: Sequence[int],
) -> list[list[float]]:
    """Append exact past canonical rows at fixed positive observation lags."""
    if not features:
        raise ValueError("Temporal feature window requires non-empty rows")
    if any(lag <= 0 for lag in lags) or list(lags) != sorted(set(lags)):
        raise ValueError("Temporal lags must be unique positive values in ascending order")
    width = len(FEATURE_COLUMNS)
    if any(len(row) != width for row in features):
        raise ValueError("Temporal window source row does not match the active schema")

    transformed: list[list[float]] = []
    for index, row in enumerate(features):
        values = [float(value) for value in row]
        for lag in lags:
            source_index = max(0, index - lag)
            values.extend(float(value) for value in features[source_index])
        transformed.append(values)
    return transformed


def promotion_candidate(results: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Apply the CR-004 predeclared promotion boundary."""
    baseline = next(item for item in results if item["feature_set"] == "baseline")
    baseline_key = selection_key(
        baseline["aggregate_metrics"], int(baseline["folds_passing_gate"]), 4
    )
    eligible = [
        item
        for item in results
        if item["feature_set"] != "baseline"
        and selection_key(
            item["aggregate_metrics"], int(item["folds_passing_gate"]), 4
        ) > baseline_key
        and float(item["gate_floor_ratio"]) >= float(baseline["gate_floor_ratio"]) + 0.01
        and float(item["aggregate_metrics"]["macro_f1"])
        >= float(baseline["aggregate_metrics"]["macro_f1"])
        and int(item["folds_passing_gate"]) >= 1
    ]
    if not eligible:
        return None
    return max(
        eligible,
        key=lambda item: selection_key(
            item["aggregate_metrics"], int(item["folds_passing_gate"]), 4
        ),
    )


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
        raise ValueError(
            f"Feature/Label Contract {FEATURE_SCHEMA_VERSION}/{LABEL_SCHEMA_VERSION} "
            "requires a 16-bar purge"
        )
    if arguments.folds != 4:
        raise ValueError("CR-004 controlled comparison requires exactly four folds")

    features, labels = read_dataset(arguments.train)
    folds = build_expanding_folds(
        len(features), fold_count=arguments.folds, purge_bars=PURGE_BARS
    )
    results: list[dict[str, Any]] = []
    for feature_set in feature_set_specs():
        lags = list(feature_set["lags"])
        transformed = transform_features(features, lags)
        actual: list[int] = []
        predicted: list[int] = []
        fold_lengths: list[int] = []
        fold_reports: list[dict[str, Any]] = []
        for fold_index, (train_end, evaluation_start, evaluation_end) in enumerate(
            folds, start=1
        ):
            model = fresh_model(MODEL_CANDIDATE)
            model.fit(transformed[:train_end], labels[:train_end])
            evaluation_labels = labels[evaluation_start:evaluation_end]
            fold_prediction = predict_with_policy(
                model.predict_proba(
                    transformed[evaluation_start:evaluation_end]
                ).tolist(),
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
            "lags": lags,
            "input_width": len(FEATURE_COLUMNS) * (1 + len(lags)),
            "aggregate_metrics": aggregate_metrics,
            "gate_floor_ratio": gate_floor_ratio(aggregate_metrics),
            "aggregate_gate_met": meets_evaluation_contract(aggregate_metrics),
            "folds_passing_gate": folds_passing,
            "stable_gate_met": (
                meets_evaluation_contract(aggregate_metrics)
                and folds_passing == len(folds)
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
    promoted = promotion_candidate(results)
    report = {
        "diagnostic_stage": "train_only_purged_temporal_brain_feature_window",
        "validation_dataset_used": False,
        "test_dataset_used": False,
        **contract_metadata(),
        "purge_bars": PURGE_BARS,
        "future_rows_used": False,
        "model_candidate": MODEL_CANDIDATE,
        "probability_variant": "raw",
        "decision_policy": DECISION_POLICY,
        "feature_sets_ranked": [item["feature_set"] for item in ranked],
        "feature_sets": results,
        "promotion_rules": {
            "gate_floor_improvement_minimum": 0.01,
            "macro_f1_must_not_decrease": True,
            "minimum_complete_passing_folds": 1,
        },
        "promoted_feature_set": (
            promoted["feature_set"] if promoted is not None else None
        ),
        "nested_confirmation_authorized": promoted is not None,
        "limitations": [
            "This controlled comparison reuses inspected Train development periods.",
            "Lagged rows are research-only and are not an active inference tensor.",
            "Observation lags can span broker market closures.",
            "Validation and Test are not read and deployment remains unauthorized.",
        ],
    }
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({
        "diagnostic_stage": report["diagnostic_stage"],
        "validation_dataset_used": False,
        "test_dataset_used": False,
        "future_rows_used": False,
        "feature_sets_ranked": report["feature_sets_ranked"],
        "results": [
            {
                "feature_set": item["feature_set"],
                "input_width": item["input_width"],
                "aggregate_metrics": item["aggregate_metrics"],
                "gate_floor_ratio": item["gate_floor_ratio"],
                "folds_passing_gate": item["folds_passing_gate"],
            }
            for item in ranked
        ],
        "promoted_feature_set": report["promoted_feature_set"],
        "nested_confirmation_authorized": report["nested_confirmation_authorized"],
        "diagnostic_file": str(arguments.output),
    }, indent=2))


if __name__ == "__main__":
    main()
