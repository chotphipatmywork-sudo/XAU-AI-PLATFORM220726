"""Compare completed-tick microstructure candidates on purged Train folds."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Sequence

from nested_walk_forward_select import gate_floor_ratio, selection_key
from price_path_state_diagnostic import evaluate_feature_sets, read_dataset_keys
from train_classifier import (
    FEATURE_SCHEMA_VERSION,
    LABEL_SCHEMA_VERSION,
    TRAINING_CONTRACT_VERSION,
    read_dataset,
)
from walk_forward_select import build_expanding_folds


PURGE_BARS = 16
CONTEXT_COLUMNS = (
    "id",
    "timestamp",
    "tick_direction_imbalance",
    "tick_burst_concentration",
    "mean_spread_atr",
    "maximum_spread_atr",
    "realized_tick_volatility_atr",
    "tick_path_efficiency",
    "tick_count",
    "tick_microstructure_valid",
)
CONTEXT_FEATURE_COLUMNS = CONTEXT_COLUMNS[2:8]


def contract_metadata() -> dict[str, str]:
    return {
        "training_contract_version": TRAINING_CONTRACT_VERSION,
        "source_feature_schema_version": FEATURE_SCHEMA_VERSION,
        "label_schema_version": LABEL_SCHEMA_VERSION,
    }


def read_tick_context(path: Path) -> dict[tuple[int, str], list[float]]:
    context: dict[tuple[int, str], list[float]] = {}
    with path.open("r", newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames is None or tuple(reader.fieldnames) != CONTEXT_COLUMNS:
            raise ValueError(f"Unexpected Tick Microstructure CSV schema in {path}")
        for row_number, row in enumerate(reader, start=2):
            try:
                key = (int(row["id"]), str(row["timestamp"]))
                values = [float(row[name]) for name in CONTEXT_FEATURE_COLUMNS]
                tick_count = int(row["tick_count"])
                valid = float(row["tick_microstructure_valid"])
            except (KeyError, TypeError, ValueError) as error:
                raise ValueError(f"Invalid Tick Microstructure row {row_number}") from error
            if key in context:
                raise ValueError(f"Duplicate Tick Microstructure key at row {row_number}: {key}")
            if any(value < 0.0 or value > 100.0 for value in values):
                raise ValueError(f"Out-of-range Tick Microstructure value at row {row_number}")
            if tick_count < 0:
                raise ValueError(f"Negative tick count at row {row_number}")
            if valid not in (0.0, 100.0):
                raise ValueError(f"Invalid Tick Microstructure validity at row {row_number}")
            if valid == 0.0 and any(value != 50.0 for value in values):
                raise ValueError(f"Invalid Tick Microstructure row is not neutral at {row_number}")
            context[key] = values + [float(tick_count), valid]
    if not context:
        raise ValueError(f"Tick Microstructure research dataset is empty: {path}")
    return context


def context_coverage(
    context: dict[tuple[int, str], list[float]],
) -> dict[str, float | int]:
    total = len(context)
    valid = sum(values[7] == 100.0 for values in context.values())
    tick_counts = [int(values[6]) for values in context.values()]
    return {
        "total_records": total,
        "valid_records": valid,
        "neutral_invalid_records": total - valid,
        "valid_ratio": valid / total,
        "minimum_tick_count": min(tick_counts),
        "maximum_tick_count": max(tick_counts),
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
        raise ValueError("Tick Microstructure context index is outside registered fields")
    missing = [key for key in keys if key not in context]
    if missing:
        raise ValueError(f"Missing Tick Microstructure context for {len(missing)} rows")
    return [
        [float(value) for value in row]
        + [float(context[key][index]) for index in indices]
        for row, key in zip(features, keys)
    ]


def feature_set_specs() -> list[dict[str, Any]]:
    return [
        {"name": "schema4_baseline", "context_indices": []},
        {"name": "liquidity_tick_flow", "context_indices": [0, 1, 5]},
        {"name": "volatility_tick_state", "context_indices": [2, 3, 4]},
        {"name": "all_tick_microstructure", "context_indices": list(range(6))},
    ]


def improving_fold_count(candidate: dict[str, Any], baseline: dict[str, Any]) -> int:
    return sum(
        float(candidate_fold["metrics"]["macro_f1"])
        > float(baseline_fold["metrics"]["macro_f1"])
        for candidate_fold, baseline_fold in zip(candidate["folds"], baseline["folds"])
    )


def directional_coverage_stable(candidate: dict[str, Any], baseline: dict[str, Any]) -> bool:
    fields = ("sell_precision", "sell_recall", "buy_precision", "buy_recall")
    return all(
        float(candidate["aggregate_metrics"][field])
        >= float(baseline["aggregate_metrics"][field])
        for field in fields
    )


def promotion_candidate(results: list[dict[str, Any]]) -> dict[str, Any] | None:
    baseline = next(item for item in results if item["feature_set"] == "schema4_baseline")
    eligible = [
        item
        for item in results
        if item["feature_set"] != "schema4_baseline"
        and float(item["aggregate_metrics"]["macro_f1"])
        >= float(baseline["aggregate_metrics"]["macro_f1"]) + 0.01
        and float(item["gate_floor_ratio"]) >= float(baseline["gate_floor_ratio"])
        and improving_fold_count(item, baseline) >= 2
        and directional_coverage_stable(item, baseline)
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
    parser.add_argument("--tick-context", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--folds", type=int, default=4)
    parser.add_argument("--purge-bars", type=int, default=PURGE_BARS)
    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()
    if arguments.purge_bars != PURGE_BARS:
        raise ValueError("The approved Label Contract requires a 16-bar purge")
    if arguments.folds != 4:
        raise ValueError("CR-011 controlled comparison requires exactly four folds")
    features, labels = read_dataset(arguments.train)
    keys = read_dataset_keys(arguments.train)
    context = read_tick_context(arguments.tick_context)
    coverage = context_coverage(context)
    if coverage["valid_ratio"] < 0.80:
        raise ValueError("Completed-tick coverage is below the CR-011 minimum of 80%")
    feature_sets = {
        spec["name"]: append_context(features, keys, context, spec["context_indices"])
        for spec in feature_set_specs()
    }
    folds = build_expanding_folds(len(features), fold_count=4, purge_bars=PURGE_BARS)
    results = evaluate_feature_sets(feature_sets, labels, folds)
    ranked = sorted(
        results,
        key=lambda item: selection_key(
            item["aggregate_metrics"], int(item["folds_passing_gate"]), len(folds)
        ),
        reverse=True,
    )
    promoted = promotion_candidate(results)
    report = {
        "diagnostic_stage": "train_only_tick_microstructure_comparison",
        "validation_dataset_used": False,
        "test_dataset_used": False,
        **contract_metadata(),
        "purge_bars": PURGE_BARS,
        "future_rows_used": False,
        "model_candidate": "random_forest_depth_5_balanced",
        "probability_variant": "raw",
        "decision_policy": {"type": "argmax"},
        "canonical_train_records": len(features),
        "tick_context_records": len(context),
        "tick_context_coverage": coverage,
        "candidate_context_features": list(CONTEXT_FEATURE_COLUMNS),
        "feature_sets_ranked": [item["feature_set"] for item in ranked],
        "feature_sets": results,
        "promotion_rules": {
            "minimum_macro_f1_improvement": 0.01,
            "gate_floor_must_not_decrease": True,
            "minimum_improving_folds": 2,
            "buy_sell_precision_recall_must_not_decrease": True,
            "nested_confirmation_required": True,
        },
        "promoted_feature_set": promoted["feature_set"] if promoted else None,
        "nested_confirmation_authorized": promoted is not None,
        "limitations": [
            "Only Train and the auxiliary completed-tick file are read.",
            "Tick count and validity are metadata and are not model inputs.",
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
        "tick_context_coverage": coverage,
        "feature_sets_ranked": report["feature_sets_ranked"],
        "results": [{
            "feature_set": item["feature_set"],
            "aggregate_metrics": item["aggregate_metrics"],
            "gate_floor_ratio": item["gate_floor_ratio"],
            "folds_passing_gate": item["folds_passing_gate"],
        } for item in ranked],
        "promoted_feature_set": report["promoted_feature_set"],
        "nested_confirmation_authorized": report["nested_confirmation_authorized"],
        "diagnostic_file": str(arguments.output),
    }, indent=2))


if __name__ == "__main__":
    main()
