"""Nested Train-only selection of Schema 4.0 versus closed-H1 Trend."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from h1_context_diagnostic import (
    DECISION_POLICY,
    MODEL_CANDIDATE,
    PURGE_BARS,
    read_dataset_keys,
    read_h1_context,
)
from h1_group_diagnostic import build_group_feature_sets
from nested_h1_context_diagnostic import run_nested_feature_set_selection
from train_classifier import FEATURE_SCHEMA_VERSION, LABEL_SCHEMA_VERSION, read_dataset


FEATURE_SETS = ("schema4_baseline", "schema4_plus_h1_trend")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", required=True, type=Path)
    parser.add_argument("--h1-context", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
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
    keys = read_dataset_keys(arguments.train)
    context = read_h1_context(arguments.h1_context)
    all_sets = build_group_feature_sets(features, keys, context)
    feature_sets = {name: all_sets[name] for name in FEATURE_SETS}
    nested = run_nested_feature_set_selection(
        feature_sets,
        labels,
        FEATURE_SETS,
        arguments.outer_folds,
        arguments.inner_folds,
    )
    report = {
        "diagnostic_stage": "train_only_nested_closed_h1_trend_selection",
        "validation_dataset_used": False,
        "test_dataset_used": False,
        "source_feature_schema_version": FEATURE_SCHEMA_VERSION,
        "label_schema_version": LABEL_SCHEMA_VERSION,
        "feature_sets": list(FEATURE_SETS),
        "model_candidate": MODEL_CANDIDATE,
        "probability_variant": "raw",
        "decision_policy": DECISION_POLICY,
        "purge_bars": PURGE_BARS,
        "outer_fold_count": arguments.outer_folds,
        "inner_fold_count": arguments.inner_folds,
        **nested,
        "limitations": [
            "This subgroup was registered after exploratory H1 decomposition.",
            "Only Train and the auxiliary closed-H1 research file are read.",
            "Fresh-period evidence is required before any schema or deployment approval.",
        ],
    }
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({
        "diagnostic_stage": report["diagnostic_stage"],
        "validation_dataset_used": False,
        "test_dataset_used": False,
        "outer_selected_feature_sets": [
            item["selected_feature_set"] for item in nested["outer_folds"]
        ],
        "aggregate_outer_metrics": nested["aggregate_outer_metrics"],
        "outer_folds_passing_gate": nested["outer_folds_passing_gate"],
        "nested_stable_gate_met": nested["nested_stable_gate_met"],
        "final_full_train_selected_feature_set": nested["final_full_train_inner_selection"]["selected"]["feature_set"],
        "diagnostic_file": str(arguments.output),
    }, indent=2))


if __name__ == "__main__":
    main()
