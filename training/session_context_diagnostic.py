"""Compare future-safe Session progress with Schema 3.0 on purged Train folds."""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Sequence

from nested_walk_forward_select import gate_floor_ratio, selection_key
from select_candidate import predict_with_policy
from train_classifier import REQUIRED_COLUMNS, evaluation_metrics, meets_evaluation_contract, read_dataset
from walk_forward_select import build_expanding_folds, fresh_model, metrics_for_folds


PURGE_BARS = 16
MODEL_CANDIDATE = "random_forest_depth_5_balanced"
DECISION_POLICY: dict[str, str] = {"type": "argmax"}
TIMESTAMP_FORMAT = "%Y.%m.%d %H:%M:%S"


def parse_timestamp(value: str) -> datetime:
    try:
        return datetime.strptime(value, TIMESTAMP_FORMAT)
    except ValueError as error:
        raise ValueError(f"Invalid dataset timestamp: {value}") from error


def session_progress(timestamp: datetime) -> float:
    """Map elapsed minutes inside the active eight-hour session to 0..100."""
    session_start_hour = (timestamp.hour // 8) * 8
    elapsed_minutes = ((timestamp.hour - session_start_hour) * 60) + timestamp.minute
    progress = 100.0 * elapsed_minutes / (8.0 * 60.0)
    return max(0.0, min(100.0, progress))


def read_timestamps(path: Path) -> list[datetime]:
    timestamps: list[datetime] = []
    with path.open("r", newline="", encoding="utf-8") as dataset_file:
        reader = csv.DictReader(dataset_file)
        if reader.fieldnames is None or tuple(reader.fieldnames) != REQUIRED_COLUMNS:
            raise ValueError(f"Unexpected CSV schema in {path}")
        for row_number, row in enumerate(reader, start=2):
            try:
                timestamps.append(parse_timestamp(row["timestamp"]))
            except (KeyError, TypeError, ValueError) as error:
                raise ValueError(f"Invalid timestamp at row {row_number} in {path}: {error}") from error
    if not timestamps:
        raise ValueError(f"Dataset is empty: {path}")
    return timestamps


def append_session_progress(
    features: Sequence[Sequence[float]], timestamps: Sequence[datetime]
) -> list[list[float]]:
    if len(features) != len(timestamps):
        raise ValueError("Feature and timestamp lengths do not match")
    return [
        [float(value) for value in row] + [session_progress(timestamp)]
        for row, timestamp in zip(features, timestamps)
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
    timestamps = read_timestamps(arguments.train)
    if len(features) != len(timestamps):
        raise ValueError("Dataset readers returned different record counts")
    feature_sets = {
        "baseline": features,
        "session_progress": append_session_progress(features, timestamps),
    }
    folds = build_expanding_folds(
        len(features), fold_count=arguments.folds, purge_bars=arguments.purge_bars
    )

    results: list[dict[str, Any]] = []
    for feature_set_name, transformed in feature_sets.items():
        actual: list[int] = []
        predicted: list[int] = []
        fold_lengths: list[int] = []
        fold_reports: list[dict[str, Any]] = []
        for fold_number, (train_end, evaluation_start, evaluation_end) in enumerate(folds, start=1):
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
        "diagnostic_stage": "train_only_purged_session_context_controlled",
        "validation_dataset_used": False,
        "test_dataset_used": False,
        "feature_schema_version": "3.0.0",
        "label_schema_version": "1.1.0",
        "candidate_feature": "session_progress",
        "candidate_group": "Session",
        "candidate_encoding": "elapsed_minutes_within_eight_hour_session_to_0_100",
        "future_rows_used": False,
        "model_candidate": MODEL_CANDIDATE,
        "probability_variant": "raw",
        "decision_policy": DECISION_POLICY,
        "purge_bars": arguments.purge_bars,
        "results": results,
        "ranked_feature_sets": [item["feature_set"] for item in ranked],
        "limitations": [
            "This controlled diagnostic uses already inspected Train periods.",
            "The derived candidate is not part of Feature Schema 3.0 or MQL5.",
            "A positive result requires a separate nested confirmation before a contract proposal.",
        ],
    }
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({
        "diagnostic_stage": report["diagnostic_stage"],
        "validation_dataset_used": False,
        "test_dataset_used": False,
        "ranked_feature_sets": report["ranked_feature_sets"],
        "results": [
            {
                "feature_set": item["feature_set"],
                "aggregate_metrics": item["aggregate_metrics"],
                "gate_floor_ratio": item["gate_floor_ratio"],
                "folds_passing_gate": item["folds_passing_gate"],
            }
            for item in results
        ],
        "diagnostic_file": str(arguments.output),
    }, indent=2))


if __name__ == "__main__":
    main()

