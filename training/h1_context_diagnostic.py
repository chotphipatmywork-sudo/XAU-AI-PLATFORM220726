"""Compare strict Schema 4.0 with closed-H1 Brain context on purged Train folds."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from nested_walk_forward_select import gate_floor_ratio, selection_key
from select_candidate import predict_with_policy
from train_classifier import (
    FEATURE_SCHEMA_VERSION,
    LABEL_SCHEMA_VERSION,
    REQUIRED_COLUMNS,
    evaluation_metrics,
    meets_evaluation_contract,
    read_dataset,
)
from walk_forward_select import build_expanding_folds, fresh_model, metrics_for_folds


PURGE_BARS = 16
MODEL_CANDIDATE = "random_forest_depth_10_hold_2"
DECISION_POLICY: dict[str, str] = {"type": "argmax"}
H1_COLUMNS = (
    "id",
    "timestamp",
    "h1_trend_regime",
    "h1_trend_momentum",
    "h1_trend_slope",
    "h1_volatility_regime",
    "h1_volatility_change",
)
H1_FEATURE_COLUMNS = H1_COLUMNS[2:]


def read_dataset_keys(path: Path) -> list[tuple[int, str]]:
    keys: list[tuple[int, str]] = []
    seen: set[tuple[int, str]] = set()
    with path.open("r", newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames is None or tuple(reader.fieldnames) != REQUIRED_COLUMNS:
            raise ValueError(f"Unexpected canonical CSV schema in {path}")
        for row_number, row in enumerate(reader, start=2):
            try:
                key = (int(row["id"]), str(row["timestamp"]))
            except (KeyError, TypeError, ValueError) as error:
                raise ValueError(f"Invalid canonical key at row {row_number}") from error
            if key in seen:
                raise ValueError(f"Duplicate canonical key at row {row_number}: {key}")
            seen.add(key)
            keys.append(key)
    if not keys:
        raise ValueError(f"Canonical dataset is empty: {path}")
    return keys


def read_h1_context(path: Path) -> dict[tuple[int, str], list[float]]:
    context: dict[tuple[int, str], list[float]] = {}
    with path.open("r", newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames is None or tuple(reader.fieldnames) != H1_COLUMNS:
            raise ValueError(f"Unexpected H1 research CSV schema in {path}")
        for row_number, row in enumerate(reader, start=2):
            try:
                key = (int(row["id"]), str(row["timestamp"]))
                values = [float(row[name]) for name in H1_FEATURE_COLUMNS]
            except (KeyError, TypeError, ValueError) as error:
                raise ValueError(f"Invalid H1 context at row {row_number}") from error
            if key in context:
                raise ValueError(f"Duplicate H1 context key at row {row_number}: {key}")
            if any(value < 0.0 or value > 100.0 for value in values):
                raise ValueError(f"Out-of-range H1 context at row {row_number}")
            context[key] = values
    if not context:
        raise ValueError(f"H1 research dataset is empty: {path}")
    return context


def append_h1_context(
    features: list[list[float]],
    keys: list[tuple[int, str]],
    context: dict[tuple[int, str], list[float]],
) -> list[list[float]]:
    if len(features) != len(keys):
        raise ValueError("Canonical feature and key lengths do not match")
    missing = [key for key in keys if key not in context]
    if missing:
        raise ValueError(f"Missing H1 context for {len(missing)} canonical rows")
    return [
        [float(value) for value in row] + [float(value) for value in context[key]]
        for row, key in zip(features, keys)
    ]


def choose_result(results: list[dict[str, Any]], fold_count: int) -> dict[str, Any]:
    if not results:
        raise ValueError("At least one feature-set result is required")
    return max(
        results,
        key=lambda item: selection_key(
            item["aggregate_metrics"], int(item["folds_passing_gate"]), fold_count
        ),
    )


def evaluate_feature_sets(
    feature_sets: dict[str, list[list[float]]],
    labels: list[int],
    folds: list[tuple[int, int, int]],
) -> list[dict[str, Any]]:
    """Evaluate bounded feature sets with one fixed method over shared folds."""
    results: list[dict[str, Any]] = []
    for feature_set_name, transformed in feature_sets.items():
        if len(transformed) != len(labels):
            raise ValueError(f"Feature/label length mismatch for {feature_set_name}")
        actual: list[int] = []
        predicted: list[int] = []
        fold_lengths: list[int] = []
        fold_reports: list[dict[str, Any]] = []
        for fold_number, (train_end, evaluation_start, evaluation_end) in enumerate(
            folds, start=1
        ):
            model = fresh_model(MODEL_CANDIDATE)
            model.fit(transformed[:train_end], labels[:train_end])
            evaluation_labels = labels[evaluation_start:evaluation_end]
            fold_prediction = predict_with_policy(
                model.predict_proba(transformed[evaluation_start:evaluation_end]).tolist(),
                [int(value) for value in model.classes_.tolist()],
                DECISION_POLICY,
            )
            metrics = evaluation_metrics(evaluation_labels, fold_prediction)
            actual.extend(evaluation_labels)
            predicted.extend(fold_prediction)
            fold_lengths.append(len(evaluation_labels))
            fold_reports.append({
                "fold": fold_number,
                "train_records": train_end,
                "purged_records": evaluation_start - train_end,
                "evaluation_records": len(evaluation_labels),
                "metrics": metrics,
                "gate_floor_ratio": gate_floor_ratio(metrics),
                "gate_met": meets_evaluation_contract(metrics),
            })
        aggregate_metrics = evaluation_metrics(actual, predicted)
        fold_metrics = metrics_for_folds(actual, predicted, fold_lengths)
        folds_passing = sum(meets_evaluation_contract(item) for item in fold_metrics)
        results.append({
            "feature_set": feature_set_name,
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
    return results


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", required=True, type=Path)
    parser.add_argument("--h1-context", required=True, type=Path)
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
    features, labels = read_dataset(arguments.train)
    keys = read_dataset_keys(arguments.train)
    context = read_h1_context(arguments.h1_context)
    feature_sets = {
        "schema4_baseline": features,
        "schema4_plus_closed_h1": append_h1_context(features, keys, context),
    }
    folds = build_expanding_folds(
        len(features), fold_count=arguments.folds, purge_bars=PURGE_BARS
    )

    results = evaluate_feature_sets(feature_sets, labels, folds)

    selected = choose_result(results, len(folds))
    report = {
        "diagnostic_stage": "train_only_closed_h1_context_controlled_comparison",
        "validation_dataset_used": False,
        "test_dataset_used": False,
        "source_feature_schema_version": FEATURE_SCHEMA_VERSION,
        "label_schema_version": LABEL_SCHEMA_VERSION,
        "candidate_h1_features": list(H1_FEATURE_COLUMNS),
        "model_candidate": MODEL_CANDIDATE,
        "probability_variant": "raw",
        "decision_policy": DECISION_POLICY,
        "purge_bars": PURGE_BARS,
        "fold_count": len(folds),
        "canonical_train_records": len(features),
        "h1_context_records": len(context),
        "results": results,
        "selected": selected,
        "limitations": [
            "Only Train and the auxiliary closed-H1 research file are read.",
            "The fixed model and policy isolate the feature-set comparison.",
            "This result cannot change the canonical Feature Contract or authorize deployment.",
        ],
    }
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({
        "diagnostic_stage": report["diagnostic_stage"],
        "validation_dataset_used": False,
        "test_dataset_used": False,
        "canonical_train_records": len(features),
        "h1_context_records": len(context),
        "selected_feature_set": selected["feature_set"],
        "selected_aggregate_metrics": selected["aggregate_metrics"],
        "selected_folds_passing_gate": selected["folds_passing_gate"],
        "selected_stable_gate_met": selected["stable_gate_met"],
        "diagnostic_file": str(arguments.output),
    }, indent=2))


if __name__ == "__main__":
    main()
