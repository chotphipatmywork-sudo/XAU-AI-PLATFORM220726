"""Diagnose temporal feature and regime drift on nested Train-only Outer folds."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from statistics import fmean, pstdev
from typing import Any, Callable, Sequence

from nested_walk_forward_select import fit_variant
from select_candidate import predict_with_policy
from train_classifier import (
    CLASS_NAMES,
    FEATURE_COLUMNS,
    FEATURE_SCHEMA_VERSION,
    LABEL_SCHEMA_VERSION,
    LABELS,
    TRAINING_CONTRACT_VERSION,
    evaluation_metrics,
    read_dataset,
)


def contract_metadata() -> dict[str, str]:
    """Return the active training, feature, and label contract versions."""
    return {
        "training_contract_version": TRAINING_CONTRACT_VERSION,
        "feature_schema_version": FEATURE_SCHEMA_VERSION,
        "label_schema_version": LABEL_SCHEMA_VERSION,
    }


def normalized_distribution(values: Sequence[int]) -> dict[str, float]:
    """Return fixed SELL/HOLD/BUY ratios for labels or predictions."""
    counts = Counter(values)
    total = len(values)
    if total == 0:
        return {name: 0.0 for name in CLASS_NAMES}
    return {
        name: counts[label] / total
        for label, name in zip(LABELS, CLASS_NAMES)
    }


def standardized_mean_difference(history: Sequence[float], evaluation: Sequence[float]) -> float:
    """Express an evaluation mean shift in history standard-deviation units."""
    if not history or not evaluation:
        raise ValueError("Drift comparison requires non-empty blocks")
    scale = pstdev(history)
    difference = fmean(evaluation) - fmean(history)
    if scale <= 1.0e-12:
        return 0.0 if abs(difference) <= 1.0e-12 else (1.0 if difference > 0.0 else -1.0)
    return difference / scale


def segment_metrics(
    actual: list[int],
    predicted: list[int],
    segment_names: Sequence[str],
) -> dict[str, dict[str, float | int]]:
    """Calculate classification metrics for every non-empty named segment."""
    result: dict[str, dict[str, float | int]] = {}
    for segment_name in sorted(set(segment_names)):
        indices = [index for index, value in enumerate(segment_names) if value == segment_name]
        result[segment_name] = evaluation_metrics(
            [actual[index] for index in indices],
            [predicted[index] for index in indices],
        )
    return result


def numeric_bucket(value: float) -> str:
    if value < 33.333333:
        return "low"
    if value < 66.666667:
        return "middle"
    return "high"


def session_name(row: Sequence[float]) -> str:
    session = row[8:11]
    return ("ASIA", "LONDON", "NEW_YORK")[max(range(3), key=lambda index: session[index])]


def read_timestamps(path: Path) -> list[str]:
    with path.open("r", newline="", encoding="utf-8") as dataset_file:
        reader = csv.DictReader(dataset_file)
        if reader.fieldnames is None or "timestamp" not in reader.fieldnames:
            raise ValueError("Dataset timestamp column is missing")
        return [str(row["timestamp"]) for row in reader]


def feature_drift(
    history: list[list[float]],
    evaluation: list[list[float]],
) -> dict[str, dict[str, float]]:
    result: dict[str, dict[str, float]] = {}
    for feature_index, feature_name in enumerate(FEATURE_COLUMNS):
        history_values = [row[feature_index] for row in history]
        evaluation_values = [row[feature_index] for row in evaluation]
        shift = standardized_mean_difference(history_values, evaluation_values)
        result[feature_name] = {
            "history_mean": fmean(history_values),
            "evaluation_mean": fmean(evaluation_values),
            "standardized_mean_difference": shift,
            "absolute_standardized_mean_difference": abs(shift),
        }
    return result


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", required=True, type=Path)
    parser.add_argument("--nested-report", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()
    if not arguments.nested_report.is_file():
        raise ValueError(f"Nested report not found: {arguments.nested_report}")
    nested = json.loads(arguments.nested_report.read_text(encoding="utf-8"))
    if nested.get("selection_stage") != "train_internal_nested_purged_walk_forward_only":
        raise ValueError("Temporal diagnostic requires a nested Train-only report")
    if nested.get("validation_dataset_used") or nested.get("test_dataset_used"):
        raise ValueError("Nested report is not Train-only")
    if int(nested.get("purge_bars", 0)) != 16:
        raise ValueError("Temporal diagnostic requires the approved 16-bar purge")

    features, labels = read_dataset(arguments.train)
    timestamps = read_timestamps(arguments.train)
    if len(timestamps) != len(features):
        raise ValueError("Timestamp and feature row counts differ")

    fold_reports: list[dict[str, Any]] = []
    shift_values = {feature_name: [] for feature_name in FEATURE_COLUMNS}
    for outer in nested["outer_folds"]:
        train_end = int(outer["train_records"])
        evaluation_start = int(outer["evaluation_start"])
        evaluation_end = int(outer["evaluation_end"])
        selected = outer["inner_selection"]["selected"]
        history_features = features[:train_end]
        history_labels = labels[:train_end]
        evaluation_features = features[evaluation_start:evaluation_end]
        evaluation_labels = labels[evaluation_start:evaluation_end]

        model = fit_variant(
            str(selected["model_candidate"]),
            str(selected["probability_variant"]),
            history_features,
            history_labels,
        )
        probabilities = model.predict_proba(evaluation_features).tolist()
        model_classes = [int(value) for value in model.classes_.tolist()]
        predictions = predict_with_policy(
            probabilities,
            model_classes,
            dict(selected["decision_policy"]),
        )
        metrics = evaluation_metrics(evaluation_labels, predictions)
        recorded = outer["outer_metrics"]
        if any(abs(float(metrics[name]) - float(recorded[name])) > 1.0e-12 for name in metrics):
            raise RuntimeError(f"Fold {outer['fold']} metrics do not reproduce the nested report")

        drift = feature_drift(history_features, evaluation_features)
        for feature_name in FEATURE_COLUMNS:
            shift_values[feature_name].append(
                float(drift[feature_name]["absolute_standardized_mean_difference"])
            )
        ranked_shift = sorted(
            FEATURE_COLUMNS,
            key=lambda name: drift[name]["absolute_standardized_mean_difference"],
            reverse=True,
        )
        prediction_distribution = normalized_distribution(predictions)
        mean_probabilities = {
            CLASS_NAMES[LABELS.index(label)]: fmean(row[index] for row in probabilities)
            for index, label in enumerate(model_classes)
        }
        raw_counterfactual: dict[str, Any] | None = None
        if str(selected["probability_variant"]) == "calibrated":
            raw_model = fit_variant(
                str(selected["model_candidate"]),
                "raw",
                history_features,
                history_labels,
            )
            raw_probabilities = raw_model.predict_proba(evaluation_features).tolist()
            raw_predictions = predict_with_policy(
                raw_probabilities,
                [int(value) for value in raw_model.classes_.tolist()],
                dict(selected["decision_policy"]),
            )
            raw_counterfactual = {
                "purpose": "diagnostic_only_same_model_and_policy_without_calibration",
                "metrics": evaluation_metrics(evaluation_labels, raw_predictions),
                "prediction_distribution": normalized_distribution(raw_predictions),
            }
        fold_reports.append({
            "fold": int(outer["fold"]),
            "history_start": timestamps[0],
            "history_end": timestamps[train_end - 1],
            "evaluation_start": timestamps[evaluation_start],
            "evaluation_end": timestamps[evaluation_end - 1],
            "history_records": train_end,
            "purged_records": evaluation_start - train_end,
            "evaluation_records": evaluation_end - evaluation_start,
            "selected_model": selected["model_candidate"],
            "selected_probability_variant": selected["probability_variant"],
            "selected_decision_policy": selected["decision_policy"],
            "metrics": metrics,
            "history_label_distribution": normalized_distribution(history_labels),
            "evaluation_label_distribution": normalized_distribution(evaluation_labels),
            "prediction_distribution": prediction_distribution,
            "mean_class_probabilities": mean_probabilities,
            "dominant_prediction_ratio": max(prediction_distribution.values()),
            "raw_probability_counterfactual": raw_counterfactual,
            "feature_drift": drift,
            "features_ranked_by_absolute_shift": ranked_shift,
            "metrics_by_session": segment_metrics(
                evaluation_labels,
                predictions,
                [session_name(row) for row in evaluation_features],
            ),
            "metrics_by_trend_regime": segment_metrics(
                evaluation_labels,
                predictions,
                [numeric_bucket(row[0]) for row in evaluation_features],
            ),
            "metrics_by_volatility_regime": segment_metrics(
                evaluation_labels,
                predictions,
                [numeric_bucket(row[3]) for row in evaluation_features],
            ),
            "metrics_by_liquidity_activity": segment_metrics(
                evaluation_labels,
                predictions,
                [numeric_bucket(row[5]) for row in evaluation_features],
            ),
        })

    feature_shift_summary = {
        feature_name: {
            "mean_absolute_standardized_shift": fmean(values),
            "maximum_absolute_standardized_shift": max(values),
            "folds_at_or_above_0_25": sum(value >= 0.25 for value in values),
        }
        for feature_name, values in shift_values.items()
    }
    report = {
        "diagnostic_stage": "train_only_nested_outer_temporal_regime_drift",
        "validation_dataset_used": False,
        "test_dataset_used": False,
        **contract_metadata(),
        "purge_bars": 16,
        "fold_count": len(fold_reports),
        "feature_shift_summary": feature_shift_summary,
        "features_ranked_by_mean_absolute_shift": sorted(
            FEATURE_COLUMNS,
            key=lambda name: feature_shift_summary[name]["mean_absolute_standardized_shift"],
            reverse=True,
        ),
        "folds": fold_reports,
        "limitations": [
            "The diagnostic refits only each already-selected Outer configuration on Train history.",
            "Standardized mean differences show distribution shift, not causal trading value.",
            "Segment metrics can be noisy when a regime contains few samples.",
            "Validation and Test are not read and deployment remains unauthorized.",
        ],
    }
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({
        "diagnostic_stage": report["diagnostic_stage"],
        "validation_dataset_used": False,
        "test_dataset_used": False,
        "fold_count": len(fold_reports),
        "features_ranked_by_mean_absolute_shift": report[
            "features_ranked_by_mean_absolute_shift"
        ],
        "fold_summary": [
            {
                "fold": fold["fold"],
                "evaluation_start": fold["evaluation_start"],
                "evaluation_end": fold["evaluation_end"],
                "macro_f1": fold["metrics"]["macro_f1"],
                "buy_precision": fold["metrics"]["buy_precision"],
                "dominant_prediction_ratio": fold["dominant_prediction_ratio"],
                "top_shifted_features": fold["features_ranked_by_absolute_shift"][:3],
            }
            for fold in fold_reports
        ],
        "diagnostic_file": str(arguments.output),
    }, indent=2))


if __name__ == "__main__":
    main()
