"""Nested confirmation of one controlled-promoted Swing Structure feature set."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from nested_h1_context_diagnostic import run_nested_feature_set_selection
from swing_structure_diagnostic import (
    DECISION_POLICY,
    MODEL_CANDIDATE,
    PURGE_BARS,
    append_context,
    context_coverage,
    feature_set_specs,
    read_dataset_keys,
    read_swing_context,
)
from train_classifier import (
    FEATURE_SCHEMA_VERSION,
    LABEL_SCHEMA_VERSION,
    read_dataset,
)


BASELINE = "schema4_baseline"


def authorized_feature_sets(controlled_report: dict[str, Any]) -> tuple[str, str]:
    """Return the fixed nested pair only after controlled promotion."""
    if controlled_report.get("diagnostic_stage") != (
        "train_only_confirmed_swing_structure_comparison"
    ):
        raise ValueError("Unexpected controlled Swing Structure report")
    if controlled_report.get("validation_dataset_used") or controlled_report.get(
        "test_dataset_used"
    ):
        raise ValueError("Controlled Swing Structure report is not Train-only")
    if controlled_report.get("source_feature_schema_version") != FEATURE_SCHEMA_VERSION:
        raise ValueError("Controlled report Feature Schema does not match")
    if controlled_report.get("label_schema_version") != LABEL_SCHEMA_VERSION:
        raise ValueError("Controlled report Label Schema does not match")
    if not controlled_report.get("nested_confirmation_authorized"):
        raise ValueError("Controlled promotion did not authorize nested confirmation")
    promoted = controlled_report.get("promoted_feature_set")
    registered = {item["name"] for item in feature_set_specs()}
    if promoted not in registered or promoted == BASELINE:
        raise ValueError("Controlled report has no valid promoted Swing Structure set")
    return BASELINE, str(promoted)


def build_feature_sets(
    features: list[list[float]],
    keys: list[tuple[int, str]],
    context: dict[tuple[int, str], list[float]],
    names: tuple[str, str],
) -> dict[str, list[list[float]]]:
    specs = {item["name"]: list(item["context_indices"]) for item in feature_set_specs()}
    return {
        name: append_context(features, keys, context, specs[name])
        for name in names
    }


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", required=True, type=Path)
    parser.add_argument("--swing-context", required=True, type=Path)
    parser.add_argument("--controlled-report", required=True, type=Path)
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
    if arguments.outer_folds != 4 or arguments.inner_folds != 3:
        raise ValueError("CR-005 nested confirmation requires 4 Outer and 3 Inner folds")
    controlled_report = json.loads(
        arguments.controlled_report.read_text(encoding="utf-8")
    )
    feature_set_names = authorized_feature_sets(controlled_report)
    features, labels = read_dataset(arguments.train)
    keys = read_dataset_keys(arguments.train)
    context = read_swing_context(arguments.swing_context)
    feature_sets = build_feature_sets(features, keys, context, feature_set_names)
    nested = run_nested_feature_set_selection(
        feature_sets,
        labels,
        feature_set_names,
        arguments.outer_folds,
        arguments.inner_folds,
    )
    promoted_name = feature_set_names[1]
    selected_count = sum(
        item["selected_feature_set"] == promoted_name
        for item in nested["outer_folds"]
    )
    canonical_change_evidence_met = (
        selected_count == arguments.outer_folds
        and nested["nested_stable_gate_met"]
    )
    report = {
        "diagnostic_stage": "train_only_nested_swing_structure_confirmation",
        "validation_dataset_used": False,
        "test_dataset_used": False,
        "source_feature_schema_version": FEATURE_SCHEMA_VERSION,
        "label_schema_version": LABEL_SCHEMA_VERSION,
        "feature_sets": list(feature_set_names),
        "controlled_promoted_feature_set": promoted_name,
        "model_candidate": MODEL_CANDIDATE,
        "probability_variant": "raw",
        "decision_policy": DECISION_POLICY,
        "purge_bars": PURGE_BARS,
        "outer_fold_count": arguments.outer_folds,
        "inner_fold_count": arguments.inner_folds,
        "swing_context_coverage": context_coverage(context),
        **nested,
        "promoted_feature_set_outer_selection_count": selected_count,
        "canonical_change_evidence_met": canonical_change_evidence_met,
        "deployment_authorized": False,
        "limitations": [
            "Nested confirmation can run only after the controlled promotion gate.",
            "Only Train and the auxiliary confirmed-swing research file are read.",
            "Even a nested pass requires separate architecture approval and fresh evidence.",
            "Validation and Test remain unread and deployment remains unauthorized.",
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
        "promoted_feature_set_outer_selection_count": selected_count,
        "canonical_change_evidence_met": canonical_change_evidence_met,
        "deployment_authorized": False,
        "diagnostic_file": str(arguments.output),
    }, indent=2))


if __name__ == "__main__":
    main()
