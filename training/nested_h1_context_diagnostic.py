"""Nested Train-only selection of Schema 4.0 versus closed-H1 context."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from h1_context_diagnostic import (
    DECISION_POLICY,
    MODEL_CANDIDATE,
    PURGE_BARS,
    append_h1_context,
    read_dataset_keys,
    read_h1_context,
)
from nested_walk_forward_select import gate_floor_ratio, selection_key
from select_candidate import predict_with_policy
from train_classifier import (
    FEATURE_SCHEMA_VERSION,
    LABEL_SCHEMA_VERSION,
    evaluation_metrics,
    meets_evaluation_contract,
    read_dataset,
)
from walk_forward_select import build_expanding_folds, fresh_model, metrics_for_folds


FEATURE_SETS = ("schema4_baseline", "schema4_plus_closed_h1")


def choose_feature_set(results: list[dict[str, Any]], fold_count: int) -> dict[str, Any]:
    if not results:
        raise ValueError("At least one feature-set result is required")
    return max(
        results,
        key=lambda item: selection_key(
            item["aggregate_metrics"], int(item["folds_passing_gate"]), fold_count
        ),
    )


def inner_select_feature_set(
    feature_sets: dict[str, list[list[float]]],
    labels: list[int],
    history_end: int,
    fold_count: int,
    feature_set_names: tuple[str, ...] = FEATURE_SETS,
) -> dict[str, Any]:
    folds = build_expanding_folds(
        history_end, fold_count=fold_count, purge_bars=PURGE_BARS
    )
    results: list[dict[str, Any]] = []
    for feature_set_name in feature_set_names:
        transformed = feature_sets[feature_set_name]
        actual: list[int] = []
        predicted: list[int] = []
        fold_lengths: list[int] = []
        for train_end, evaluation_start, evaluation_end in folds:
            model = fresh_model(MODEL_CANDIDATE)
            model.fit(transformed[:train_end], labels[:train_end])
            evaluation_labels = labels[evaluation_start:evaluation_end]
            fold_prediction = predict_with_policy(
                model.predict_proba(transformed[evaluation_start:evaluation_end]).tolist(),
                [int(value) for value in model.classes_.tolist()],
                DECISION_POLICY,
            )
            actual.extend(evaluation_labels)
            predicted.extend(fold_prediction)
            fold_lengths.append(len(evaluation_labels))
        aggregate_metrics = evaluation_metrics(actual, predicted)
        fold_metrics = metrics_for_folds(actual, predicted, fold_lengths)
        folds_passing = sum(meets_evaluation_contract(item) for item in fold_metrics)
        results.append({
            "feature_set": feature_set_name,
            "aggregate_metrics": aggregate_metrics,
            "gate_floor_ratio": gate_floor_ratio(aggregate_metrics),
            "aggregate_gate_met": meets_evaluation_contract(aggregate_metrics),
            "folds_passing_gate": folds_passing,
            "stable_inner_gate_met": (
                meets_evaluation_contract(aggregate_metrics)
                and folds_passing == len(folds)
            ),
        })
    return {
        "fold_count": len(folds),
        "candidates": results,
        "selected": choose_feature_set(results, len(folds)),
    }


def run_nested_feature_set_selection(
    feature_sets: dict[str, list[list[float]]],
    labels: list[int],
    feature_set_names: tuple[str, ...],
    outer_fold_count: int,
    inner_fold_count: int,
) -> dict[str, Any]:
    """Run shared past-only Inner selection and unseen Outer evaluation."""
    if tuple(feature_sets) != feature_set_names:
        raise ValueError("Nested feature-set names and mapping order do not match")
    outer_folds = build_expanding_folds(
        len(labels), fold_count=outer_fold_count, purge_bars=PURGE_BARS
    )
    actual: list[int] = []
    predicted: list[int] = []
    fold_lengths: list[int] = []
    outer_reports: list[dict[str, Any]] = []
    for fold_number, (train_end, evaluation_start, evaluation_end) in enumerate(
        outer_folds, start=1
    ):
        inner = inner_select_feature_set(
            feature_sets,
            labels,
            train_end,
            inner_fold_count,
            feature_set_names,
        )
        selected_name = str(inner["selected"]["feature_set"])
        transformed = feature_sets[selected_name]
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
        outer_reports.append({
            "fold": fold_number,
            "train_records": train_end,
            "purged_records": evaluation_start - train_end,
            "evaluation_records": len(evaluation_labels),
            "inner_selection": inner,
            "selected_feature_set": selected_name,
            "outer_metrics": metrics,
            "outer_gate_met": meets_evaluation_contract(metrics),
        })
    aggregate_metrics = evaluation_metrics(actual, predicted)
    outer_metrics = metrics_for_folds(actual, predicted, fold_lengths)
    folds_passing = sum(meets_evaluation_contract(item) for item in outer_metrics)
    final_inner = inner_select_feature_set(
        feature_sets,
        labels,
        len(labels),
        inner_fold_count,
        feature_set_names,
    )
    return {
        "outer_folds": outer_reports,
        "aggregate_outer_metrics": aggregate_metrics,
        "outer_folds_passing_gate": folds_passing,
        "nested_stable_gate_met": (
            meets_evaluation_contract(aggregate_metrics)
            and folds_passing == len(outer_folds)
        ),
        "final_full_train_inner_selection": final_inner,
    }


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
    feature_sets = {
        "schema4_baseline": features,
        "schema4_plus_closed_h1": append_h1_context(features, keys, context),
    }
    nested = run_nested_feature_set_selection(
        feature_sets,
        labels,
        FEATURE_SETS,
        arguments.outer_folds,
        arguments.inner_folds,
    )
    report = {
        "diagnostic_stage": "train_only_nested_closed_h1_context_selection",
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
            "Only Train and the auxiliary closed-H1 research file are read.",
            "The fixed model and policy isolate past-only feature-set selection.",
            "This nested diagnostic cannot authorize a schema change or deployment.",
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
