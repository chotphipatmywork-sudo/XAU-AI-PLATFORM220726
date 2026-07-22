"""Produce a read-only feature diagnostic for a selected XAU AI candidate."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from statistics import fmean, pstdev
from typing import Any

import joblib
from sklearn.inspection import permutation_importance
from sklearn.metrics import f1_score

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


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, type=Path)
    parser.add_argument("--train", required=True, type=Path)
    parser.add_argument("--validation", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def feature_summary(features: list[list[float]], labels: list[int]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for index, feature_name in enumerate(FEATURE_COLUMNS):
        values = [row[index] for row in features]
        by_class: dict[str, dict[str, float]] = {}
        for label, class_name in zip(LABELS, CLASS_NAMES):
            class_values = [value for value, row_label in zip(values, labels) if row_label == label]
            by_class[class_name] = {
                "mean": fmean(class_values),
                "standard_deviation": pstdev(class_values),
            }
        result[feature_name] = {
            "minimum": min(values),
            "maximum": max(values),
            "distinct_count": len(set(values)),
            "standard_deviation": pstdev(values),
            "by_class": by_class,
        }
    return result


def macro_f1_scorer(model: Any, features: list[list[float]], labels: list[int]) -> float:
    prediction = model.predict(features)
    return float(f1_score(labels, prediction, labels=LABELS, average="macro", zero_division=0))


def class_counts(labels: list[int]) -> dict[str, int]:
    counts = Counter(labels)
    return {class_name: counts[label] for label, class_name in zip(LABELS, CLASS_NAMES)}


def main() -> None:
    arguments = parse_arguments()
    if not arguments.model.is_file():
        raise ValueError(f"Candidate model not found: {arguments.model}")

    model = joblib.load(arguments.model)
    train_features, train_labels = read_dataset(arguments.train)
    validation_features, validation_labels = read_dataset(arguments.validation)
    validation_prediction = model.predict(validation_features).tolist()

    permutation = permutation_importance(
        model,
        validation_features,
        validation_labels,
        scoring=macro_f1_scorer,
        n_repeats=20,
        random_state=42,
        n_jobs=-1,
    )
    permutation_summary = {
        feature_name: {
            "mean_macro_f1_drop": float(permutation.importances_mean[index]),
            "standard_deviation": float(permutation.importances_std[index]),
        }
        for index, feature_name in enumerate(FEATURE_COLUMNS)
    }
    model_importance = getattr(model, "feature_importances_", None)
    impurity_summary = (
        {feature_name: float(model_importance[index]) for index, feature_name in enumerate(FEATURE_COLUMNS)}
        if model_importance is not None
        else None
    )

    report = {
        "diagnostic_stage": "train_validation_read_only",
        "test_dataset_used": False,
        "training_contract_version": TRAINING_CONTRACT_VERSION,
        "feature_schema_version": FEATURE_SCHEMA_VERSION,
        "label_schema_version": LABEL_SCHEMA_VERSION,
        "model_type": type(model).__name__,
        "train_class_distribution": class_counts(train_labels),
        "validation_class_distribution": class_counts(validation_labels),
        "validation_metrics": evaluation_metrics(validation_labels, validation_prediction),
        "train_feature_summary": feature_summary(train_features, train_labels),
        "validation_permutation_importance": permutation_summary,
        "model_impurity_importance": impurity_summary,
        "limitations": [
            "This report does not select, train, or modify a model.",
            "The Test partition is intentionally not read.",
            "Permutation importance shows association on the Validation period, not causal trading value.",
        ],
    }
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
