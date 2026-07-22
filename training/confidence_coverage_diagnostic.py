"""Measure a fixed model's directional confidence-versus-coverage frontier on Train only."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Sequence

from select_candidate import predict_with_policy
from train_classifier import (
    CLASS_NAMES,
    FEATURE_SCHEMA_VERSION,
    LABEL_SCHEMA_VERSION,
    LABELS,
    TRAINING_CONTRACT_VERSION,
    evaluation_metrics,
    read_dataset,
)
from walk_forward_select import build_expanding_folds, fresh_model


PURGE_BARS = 16
MODEL_CANDIDATE = "random_forest_depth_5_balanced"
CONFIDENCE_THRESHOLDS = (0.34, 0.38, 0.42, 0.46, 0.50, 0.55, 0.60, 0.65, 0.70)
MINIMUM_DIRECTIONAL_PREDICTIONS_PER_FOLD = 25


def contract_metadata() -> dict[str, str]:
    """Return the active training, feature, and label contract versions."""
    return {
        "training_contract_version": TRAINING_CONTRACT_VERSION,
        "feature_schema_version": FEATURE_SCHEMA_VERSION,
        "label_schema_version": LABEL_SCHEMA_VERSION,
    }


def prediction_counts(predicted: Sequence[int]) -> dict[str, int]:
    counts = Counter(int(label) for label in predicted)
    return {name: counts[label] for label, name in zip(LABELS, CLASS_NAMES)}


def threshold_report(actual: Sequence[int], predicted: Sequence[int]) -> dict[str, Any]:
    """Summarize metrics and decision coverage for one fixed threshold."""
    if len(actual) != len(predicted) or not actual:
        raise ValueError("Threshold report requires matching non-empty rows")
    counts = prediction_counts(predicted)
    directional = counts["SELL"] + counts["BUY"]
    metrics = evaluation_metrics(list(actual), list(predicted))
    directional_precision_supported = (
        counts["SELL"] >= MINIMUM_DIRECTIONAL_PREDICTIONS_PER_FOLD
        and counts["BUY"] >= MINIMUM_DIRECTIONAL_PREDICTIONS_PER_FOLD
    )
    precision_gate_met = (
        directional_precision_supported
        and float(metrics["sell_precision"]) >= 0.50
        and float(metrics["buy_precision"]) >= 0.50
    )
    return {
        "records": len(actual),
        "prediction_counts": counts,
        "directional_coverage": directional / len(actual),
        "metrics": metrics,
        "directional_precision_supported": directional_precision_supported,
        "directional_precision_gate_met": precision_gate_met,
    }


def confidence_policy(threshold: float) -> dict[str, float | str]:
    if threshold < (1.0 / 3.0) or threshold > 1.0:
        raise ValueError("Confidence threshold must be within 1/3..1")
    return {
        "type": "confidence",
        "sell_minimum": threshold,
        "buy_minimum": threshold,
        "margin": 0.0,
    }


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
    features, labels = read_dataset(arguments.train)
    folds = build_expanding_folds(
        len(features), fold_count=arguments.folds, purge_bars=arguments.purge_bars
    )

    fold_predictions: list[dict[str, Any]] = []
    for fold_number, (train_end, evaluation_start, evaluation_end) in enumerate(folds, start=1):
        model = fresh_model(MODEL_CANDIDATE)
        model.fit(features[:train_end], labels[:train_end])
        probabilities = model.predict_proba(features[evaluation_start:evaluation_end]).tolist()
        classes = [int(value) for value in model.classes_.tolist()]
        fold_predictions.append({
            "fold": fold_number,
            "train_records": train_end,
            "purged_records": evaluation_start - train_end,
            "actual": labels[evaluation_start:evaluation_end],
            "probabilities": probabilities,
            "classes": classes,
        })

    frontier: list[dict[str, Any]] = []
    for threshold in CONFIDENCE_THRESHOLDS:
        policy = confidence_policy(threshold)
        actual_all: list[int] = []
        predicted_all: list[int] = []
        fold_reports: list[dict[str, Any]] = []
        for fold_data in fold_predictions:
            predicted = predict_with_policy(
                fold_data["probabilities"], fold_data["classes"], policy
            )
            actual = list(fold_data["actual"])
            report = threshold_report(actual, predicted)
            report.update({
                "fold": fold_data["fold"],
                "train_records": fold_data["train_records"],
                "purged_records": fold_data["purged_records"],
            })
            fold_reports.append(report)
            actual_all.extend(actual)
            predicted_all.extend(predicted)

        aggregate = threshold_report(actual_all, predicted_all)
        frontier.append({
            "confidence_threshold": threshold,
            "policy": policy,
            "aggregate": aggregate,
            "folds_meeting_directional_precision_gate": sum(
                bool(item["directional_precision_gate_met"]) for item in fold_reports
            ),
            "stable_directional_precision_gate_met": all(
                bool(item["directional_precision_gate_met"]) for item in fold_reports
            ),
            "folds": fold_reports,
        })

    report = {
        "diagnostic_stage": "train_only_purged_confidence_coverage",
        "validation_dataset_used": False,
        "test_dataset_used": False,
        **contract_metadata(),
        "model_candidate": MODEL_CANDIDATE,
        "probability_variant": "raw",
        "purge_bars": arguments.purge_bars,
        "minimum_directional_predictions_per_fold": MINIMUM_DIRECTIONAL_PREDICTIONS_PER_FOLD,
        "frontier": frontier,
        "limitations": [
            "Thresholds are a diagnostic grid and no policy is selected or locked.",
            "All estimates use already inspected Train development periods only.",
            "Validation and Test are not read, and deployment is not authorized.",
        ],
    }
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({
        "diagnostic_stage": report["diagnostic_stage"],
        "validation_dataset_used": False,
        "test_dataset_used": False,
        "model_candidate": MODEL_CANDIDATE,
        "frontier": [
            {
                "confidence_threshold": item["confidence_threshold"],
                "directional_coverage": item["aggregate"]["directional_coverage"],
                "sell_predictions": item["aggregate"]["prediction_counts"]["SELL"],
                "buy_predictions": item["aggregate"]["prediction_counts"]["BUY"],
                "sell_precision": item["aggregate"]["metrics"]["sell_precision"],
                "buy_precision": item["aggregate"]["metrics"]["buy_precision"],
                "sell_recall": item["aggregate"]["metrics"]["sell_recall"],
                "buy_recall": item["aggregate"]["metrics"]["buy_recall"],
                "folds_meeting_directional_precision_gate": item[
                    "folds_meeting_directional_precision_gate"
                ],
            }
            for item in frontier
        ],
        "diagnostic_file": str(arguments.output),
    }, indent=2))


if __name__ == "__main__":
    main()
