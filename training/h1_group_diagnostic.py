"""Decompose closed-H1 Trend and Volatility groups on purged Train folds."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from h1_context_diagnostic import (
    DECISION_POLICY,
    MODEL_CANDIDATE,
    PURGE_BARS,
    append_h1_context,
    choose_result,
    evaluate_feature_sets,
    read_dataset_keys,
    read_h1_context,
)
from train_classifier import FEATURE_SCHEMA_VERSION, LABEL_SCHEMA_VERSION, read_dataset
from walk_forward_select import build_expanding_folds


def build_group_feature_sets(
    features: list[list[float]],
    keys: list[tuple[int, str]],
    context: dict[tuple[int, str], list[float]],
) -> dict[str, list[list[float]]]:
    full = append_h1_context(features, keys, context)
    baseline_width = len(features[0])
    return {
        "schema4_baseline": [[float(value) for value in row] for row in features],
        "schema4_plus_h1_trend": [row[:baseline_width] + row[baseline_width:baseline_width + 3] for row in full],
        "schema4_plus_h1_volatility": [row[:baseline_width] + row[baseline_width + 3:] for row in full],
        "schema4_plus_h1_trend_volatility": full,
    }


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
    feature_sets = build_group_feature_sets(features, keys, context)
    folds = build_expanding_folds(
        len(features), fold_count=arguments.folds, purge_bars=PURGE_BARS
    )
    results = evaluate_feature_sets(feature_sets, labels, folds)
    selected = choose_result(results, len(folds))
    report = {
        "diagnostic_stage": "train_only_closed_h1_group_decomposition",
        "validation_dataset_used": False,
        "test_dataset_used": False,
        "source_feature_schema_version": FEATURE_SCHEMA_VERSION,
        "label_schema_version": LABEL_SCHEMA_VERSION,
        "model_candidate": MODEL_CANDIDATE,
        "probability_variant": "raw",
        "decision_policy": DECISION_POLICY,
        "purge_bars": PURGE_BARS,
        "fold_count": len(folds),
        "results": results,
        "selected": selected,
        "limitations": [
            "This is an exploratory decomposition after the complete H1 group was inspected.",
            "Only Train and the auxiliary closed-H1 research file are read.",
            "Any selected subgroup requires nested confirmation and fresh evidence before a schema change.",
        ],
    }
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({
        "diagnostic_stage": report["diagnostic_stage"],
        "validation_dataset_used": False,
        "test_dataset_used": False,
        "selected_feature_set": selected["feature_set"],
        "selected_aggregate_metrics": selected["aggregate_metrics"],
        "selected_folds_passing_gate": selected["folds_passing_gate"],
        "selected_stable_gate_met": selected["stable_gate_met"],
        "diagnostic_file": str(arguments.output),
    }, indent=2))


if __name__ == "__main__":
    main()
