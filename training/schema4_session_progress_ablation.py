"""Nested Train-only Schema 4.0 ablation of Session Progress."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

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
MODEL_CANDIDATE = "random_forest_depth_10_hold_2"
DECISION_POLICY: dict[str, str] = {"type": "argmax"}
FEATURE_SETS = {
    "without_session_progress": False,
    "with_session_progress": True,
}


def choose_feature_set(results: list[dict[str, Any]], fold_count: int) -> dict[str, Any]:
    """Select by the established stable-gate and weakest-gate ordering."""
    if not results:
        raise ValueError("At least one feature-set result is required")
    return max(
        results,
        key=lambda item: selection_key(
            item["aggregate_metrics"], int(item["folds_passing_gate"]), fold_count
        ),
    )


def transform_feature_set(
    features: list[list[float]], include_progress: bool
) -> list[list[float]]:
    """Keep the strict Schema 4.0 tensor or remove only its final Progress field."""
    expected_width = len(FEATURE_COLUMNS)
    if FEATURE_SCHEMA_VERSION != "4.0.0" or FEATURE_COLUMNS[-1] != "session_progress":
        raise ValueError("Schema 4.0 Session Progress must be the final feature")
    transformed: list[list[float]] = []
    for row in features:
        if len(row) != expected_width:
            raise ValueError(f"Expected {expected_width} Schema 4.0 features")
        values = [float(value) for value in row]
        transformed.append(values if include_progress else values[:-1])
    return transformed


def inner_select_feature_set(
    features: list[list[float]], labels: list[int], fold_count: int
) -> dict[str, Any]:
    """Select one of the two bounded feature sets inside a supplied history."""
    folds = build_expanding_folds(
        len(features), fold_count=fold_count, purge_bars=PURGE_BARS
    )
    results: list[dict[str, Any]] = []
    for feature_set_name, include_progress in FEATURE_SETS.items():
        transformed = transform_feature_set(features, include_progress)
        actual: list[int] = []
        predicted: list[int] = []
        fold_lengths: list[int] = []
        for train_end, evaluation_start, evaluation_end in folds:
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
            actual.extend(evaluation_labels)
            predicted.extend(fold_prediction)
            fold_lengths.append(len(evaluation_labels))
        aggregate_metrics = evaluation_metrics(actual, predicted)
        fold_metrics = metrics_for_folds(actual, predicted, fold_lengths)
        folds_passing = sum(meets_evaluation_contract(item) for item in fold_metrics)
        results.append({
            "feature_set": feature_set_name,
            "includes_session_progress": include_progress,
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


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--outer-folds", type=int, default=4)
    parser.add_argument("--inner-folds", type=int, default=3)
    parser.add_argument("--purge-bars", type=int, default=PURGE_BARS)
    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()
    if arguments.purge_bars != PURGE_BARS:
        raise ValueError("Feature/Label Contract 4.0/1.1 requires a 16-bar purge")
    features, labels = read_dataset(arguments.train)
    transformed_sets = {
        name: transform_feature_set(features, include_progress)
        for name, include_progress in FEATURE_SETS.items()
    }
    outer_folds = build_expanding_folds(
        len(features), fold_count=arguments.outer_folds, purge_bars=PURGE_BARS
    )

    aggregate_actual: list[int] = []
    aggregate_predicted: list[int] = []
    fold_lengths: list[int] = []
    outer_reports: list[dict[str, Any]] = []
    for fold_number, (train_end, evaluation_start, evaluation_end) in enumerate(
        outer_folds, start=1
    ):
        inner = inner_select_feature_set(
            features[:train_end], labels[:train_end], fold_count=arguments.inner_folds
        )
        selected_name = str(inner["selected"]["feature_set"])
        transformed = transformed_sets[selected_name]
        model = fresh_model(MODEL_CANDIDATE)
        model.fit(transformed[:train_end], labels[:train_end])
        evaluation_labels = labels[evaluation_start:evaluation_end]
        predictions = predict_with_policy(
            model.predict_proba(transformed[evaluation_start:evaluation_end]).tolist(),
            [int(value) for value in model.classes_.tolist()],
            DECISION_POLICY,
        )
        metrics = evaluation_metrics(evaluation_labels, predictions)
        aggregate_actual.extend(evaluation_labels)
        aggregate_predicted.extend(predictions)
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

    aggregate_metrics = evaluation_metrics(aggregate_actual, aggregate_predicted)
    outer_metrics = metrics_for_folds(aggregate_actual, aggregate_predicted, fold_lengths)
    folds_passing = sum(meets_evaluation_contract(item) for item in outer_metrics)
    final_inner = inner_select_feature_set(
        features, labels, fold_count=arguments.inner_folds
    )
    report = {
        "diagnostic_stage": "schema4_train_only_nested_session_progress_ablation",
        "validation_dataset_used": False,
        "test_dataset_used": False,
        "training_contract_version": TRAINING_CONTRACT_VERSION,
        "source_feature_schema_version": FEATURE_SCHEMA_VERSION,
        "label_schema_version": LABEL_SCHEMA_VERSION,
        "feature_sets": FEATURE_SETS,
        "purge_bars": PURGE_BARS,
        "model_candidate": MODEL_CANDIDATE,
        "probability_variant": "raw",
        "decision_policy": DECISION_POLICY,
        "outer_fold_count": len(outer_folds),
        "inner_fold_count": arguments.inner_folds,
        "outer_folds": outer_reports,
        "aggregate_outer_metrics": aggregate_metrics,
        "outer_folds_passing_gate": folds_passing,
        "nested_stable_gate_met": (
            meets_evaluation_contract(aggregate_metrics)
            and folds_passing == len(outer_folds)
        ),
        "final_full_train_inner_selection": final_inner,
        "limitations": [
            "Only the purged Train partition is read; Validation and Test remain untouched.",
            "The model and argmax policy are fixed to isolate Session Progress.",
            "This ablation does not authorize deployment or a live trading change.",
        ],
    }
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({
        "diagnostic_stage": report["diagnostic_stage"],
        "validation_dataset_used": False,
        "test_dataset_used": False,
        "outer_selected_feature_sets": [
            item["selected_feature_set"] for item in outer_reports
        ],
        "aggregate_outer_metrics": aggregate_metrics,
        "outer_folds_passing_gate": folds_passing,
        "nested_stable_gate_met": report["nested_stable_gate_met"],
        "final_full_train_selected_feature_set": final_inner["selected"]["feature_set"],
        "diagnostic_file": str(arguments.output),
    }, indent=2))


if __name__ == "__main__":
    main()
