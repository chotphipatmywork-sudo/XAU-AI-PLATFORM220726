"""Compare bounded past-only 16-bar price-path state on purged Train folds."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Sequence

from nested_walk_forward_select import gate_floor_ratio, selection_key
from select_candidate import predict_with_policy
from train_classifier import (
    FEATURE_SCHEMA_VERSION,
    LABEL_SCHEMA_VERSION,
    REQUIRED_COLUMNS,
    TRAINING_CONTRACT_VERSION,
    evaluation_metrics,
    meets_evaluation_contract,
    read_dataset,
)
from walk_forward_select import build_expanding_folds, fresh_model, metrics_for_folds


PURGE_BARS = 16
MODEL_CANDIDATE = "random_forest_depth_5_balanced"
DECISION_POLICY: dict[str, str] = {"type": "argmax"}
CONTEXT_COLUMNS = (
    "id",
    "timestamp",
    "path_directional_efficiency",
    "up_close_ratio",
    "directional_run_balance",
    "return_sign_persistence",
    "path_travel_atr",
    "range_efficiency",
    "range_expansion",
    "price_path_valid",
)
CONTEXT_FEATURE_COLUMNS = CONTEXT_COLUMNS[2:9]


def contract_metadata() -> dict[str, str]:
    return {
        "training_contract_version": TRAINING_CONTRACT_VERSION,
        "source_feature_schema_version": FEATURE_SCHEMA_VERSION,
        "label_schema_version": LABEL_SCHEMA_VERSION,
    }


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


def read_price_path_context(path: Path) -> dict[tuple[int, str], list[float]]:
    context: dict[tuple[int, str], list[float]] = {}
    with path.open("r", newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames is None or tuple(reader.fieldnames) != CONTEXT_COLUMNS:
            raise ValueError(f"Unexpected Price Path CSV schema in {path}")
        for row_number, row in enumerate(reader, start=2):
            try:
                key = (int(row["id"]), str(row["timestamp"]))
                values = [float(row[name]) for name in CONTEXT_FEATURE_COLUMNS]
                valid = float(row["price_path_valid"])
            except (KeyError, TypeError, ValueError) as error:
                raise ValueError(f"Invalid Price Path row {row_number}") from error
            if key in context:
                raise ValueError(f"Duplicate Price Path key at row {row_number}: {key}")
            if any(value < 0.0 or value > 100.0 for value in values):
                raise ValueError(f"Out-of-range Price Path value at row {row_number}")
            if valid not in (0.0, 100.0):
                raise ValueError(f"Invalid Price Path validity at row {row_number}")
            if valid == 0.0 and any(value != 50.0 for value in values):
                raise ValueError(f"Invalid Price Path row is not neutral at {row_number}")
            context[key] = values + [valid]
    if not context:
        raise ValueError(f"Price Path research dataset is empty: {path}")
    return context


def context_coverage(
    context: dict[tuple[int, str], list[float]],
) -> dict[str, float | int]:
    valid = sum(values[7] == 100.0 for values in context.values())
    total = len(context)
    return {
        "total_records": total,
        "valid_records": valid,
        "neutral_invalid_records": total - valid,
        "valid_ratio": valid / total,
    }


def append_context(
    features: Sequence[Sequence[float]],
    keys: Sequence[tuple[int, str]],
    context: dict[tuple[int, str], list[float]],
    indices: Sequence[int],
) -> list[list[float]]:
    if len(features) != len(keys):
        raise ValueError("Canonical feature and key lengths do not match")
    if any(index < 0 or index >= len(CONTEXT_FEATURE_COLUMNS) for index in indices):
        raise ValueError("Price Path context index is outside registered fields")
    missing = [key for key in keys if key not in context]
    if missing:
        raise ValueError(f"Missing Price Path context for {len(missing)} rows")
    return [
        [float(value) for value in row]
        + [float(context[key][index]) for index in indices]
        for row, key in zip(features, keys)
    ]


def feature_set_specs() -> list[dict[str, Any]]:
    return [
        {"name": "schema4_baseline", "context_indices": []},
        {"name": "trend_path_state", "context_indices": [0, 1, 2, 3]},
        {"name": "volatility_path_state", "context_indices": [4, 5, 6]},
        {"name": "all_price_path_state", "context_indices": list(range(7))},
    ]


def promotion_candidate(results: list[dict[str, Any]]) -> dict[str, Any] | None:
    baseline = next(
        item for item in results if item["feature_set"] == "schema4_baseline"
    )
    baseline_key = selection_key(
        baseline["aggregate_metrics"], int(baseline["folds_passing_gate"]), 4
    )
    eligible = [
        item
        for item in results
        if item["feature_set"] != "schema4_baseline"
        and selection_key(
            item["aggregate_metrics"], int(item["folds_passing_gate"]), 4
        ) > baseline_key
        and float(item["gate_floor_ratio"])
        >= float(baseline["gate_floor_ratio"]) + 0.01
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


def evaluate_feature_sets(
    feature_sets: dict[str, list[list[float]]],
    labels: list[int],
    folds: list[tuple[int, int, int]],
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for feature_set_name, transformed in feature_sets.items():
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
        passing = sum(meets_evaluation_contract(item) for item in fold_metrics)
        results.append({
            "feature_set": feature_set_name,
            "input_width": len(transformed[0]),
            "aggregate_metrics": aggregate_metrics,
            "gate_floor_ratio": gate_floor_ratio(aggregate_metrics),
            "aggregate_gate_met": meets_evaluation_contract(aggregate_metrics),
            "folds_passing_gate": passing,
            "stable_gate_met": (
                meets_evaluation_contract(aggregate_metrics)
                and passing == len(folds)
            ),
            "folds": fold_reports,
        })
    return results


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", required=True, type=Path)
    parser.add_argument("--price-path-context", required=True, type=Path)
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
        raise ValueError("CR-007 controlled comparison requires exactly four folds")
    features, labels = read_dataset(arguments.train)
    keys = read_dataset_keys(arguments.train)
    context = read_price_path_context(arguments.price_path_context)
    feature_sets = {
        spec["name"]: append_context(
            features, keys, context, list(spec["context_indices"])
        )
        for spec in feature_set_specs()
    }
    folds = build_expanding_folds(
        len(features), fold_count=arguments.folds, purge_bars=PURGE_BARS
    )
    results = evaluate_feature_sets(feature_sets, labels, folds)
    ranked = sorted(
        results,
        key=lambda item: selection_key(
            item["aggregate_metrics"], int(item["folds_passing_gate"]), len(folds)
        ),
        reverse=True,
    )
    promoted = promotion_candidate(results)
    coverage = context_coverage(context)
    report = {
        "diagnostic_stage": "train_only_price_path_state_comparison",
        "validation_dataset_used": False,
        "test_dataset_used": False,
        **contract_metadata(),
        "purge_bars": PURGE_BARS,
        "future_rows_used": False,
        "path_window_bars": 16,
        "model_candidate": MODEL_CANDIDATE,
        "probability_variant": "raw",
        "decision_policy": DECISION_POLICY,
        "canonical_train_records": len(features),
        "price_path_context_records": len(context),
        "price_path_context_coverage": coverage,
        "candidate_context_features": list(CONTEXT_FEATURE_COLUMNS),
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
            "Only Train and the auxiliary completed price-path file are read.",
            "The fixed model and policy isolate the feature-set comparison.",
            "The auxiliary fields are not active Schema 4.0 inputs.",
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
        "price_path_context_coverage": coverage,
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
