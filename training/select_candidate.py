"""Select an XAU AI classifier candidate using Train and Validation only."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from statistics import fmean
from typing import Any, Sequence

import joblib
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression

from train_classifier import (
    CLASS_NAMES,
    FEATURE_COLUMNS,
    FEATURE_SCHEMA_VERSION,
    LABEL_SCHEMA_VERSION,
    LABELS,
    TRAINING_CONTRACT_VERSION,
    evaluation_metrics,
    meets_evaluation_contract,
    read_dataset,
)


def class_distribution(labels: list[int]) -> dict[str, int]:
    counts = Counter(labels)
    return {class_name: counts[label] for label, class_name in zip(LABELS, CLASS_NAMES)}


def feature_means_by_class(features: list[list[float]], labels: list[int]) -> dict[str, dict[str, float]]:
    summary: dict[str, dict[str, float]] = {}
    for label, class_name in zip(LABELS, CLASS_NAMES):
        rows = [row for row, row_label in zip(features, labels) if row_label == label]
        summary[class_name] = {
            feature_name: fmean(row[index] for row in rows)
            for index, feature_name in enumerate(FEATURE_COLUMNS)
        }
    return summary


def candidate_models() -> list[tuple[str, Any]]:
    return [
        ("majority_baseline", DummyClassifier(strategy="most_frequent")),
        (
            "logistic_balanced_c_0_1",
            LogisticRegression(C=0.1, class_weight="balanced", max_iter=2000, random_state=42),
        ),
        (
            "logistic_balanced_c_1_0",
            LogisticRegression(C=1.0, class_weight="balanced", max_iter=2000, random_state=42),
        ),
        (
            "random_forest_depth_5_balanced",
            RandomForestClassifier(
                n_estimators=400,
                max_depth=5,
                min_samples_leaf=5,
                class_weight="balanced_subsample",
                n_jobs=-1,
                random_state=42,
            ),
        ),
        (
            "random_forest_depth_8_balanced",
            RandomForestClassifier(
                n_estimators=400,
                max_depth=8,
                min_samples_leaf=3,
                class_weight="balanced_subsample",
                n_jobs=-1,
                random_state=42,
            ),
        ),
        (
            "random_forest_depth_5_hold_4",
            RandomForestClassifier(
                n_estimators=400,
                max_depth=5,
                min_samples_leaf=5,
                class_weight={-1: 1.0, 0: 4.0, 1: 1.0},
                n_jobs=-1,
                random_state=42,
            ),
        ),
        (
            "random_forest_depth_8_hold_4",
            RandomForestClassifier(
                n_estimators=400,
                max_depth=8,
                min_samples_leaf=3,
                class_weight={-1: 1.0, 0: 4.0, 1: 1.0},
                n_jobs=-1,
                random_state=42,
            ),
        ),
        (
            "random_forest_depth_8_hold_2",
            RandomForestClassifier(
                n_estimators=400,
                max_depth=8,
                min_samples_leaf=3,
                class_weight={-1: 1.0, 0: 2.0, 1: 1.0},
                n_jobs=-1,
                random_state=42,
            ),
        ),
        (
            "random_forest_depth_10_hold_2",
            RandomForestClassifier(
                n_estimators=400,
                max_depth=10,
                min_samples_leaf=4,
                class_weight={-1: 1.0, 0: 2.0, 1: 1.0},
                n_jobs=-1,
                random_state=42,
            ),
        ),
        (
            "random_forest_depth_10_balanced",
            RandomForestClassifier(
                n_estimators=400,
                max_depth=10,
                min_samples_leaf=4,
                class_weight="balanced_subsample",
                n_jobs=-1,
                random_state=42,
            ),
        ),
        (
            "extra_trees_depth_6_hold_4",
            ExtraTreesClassifier(
                n_estimators=400,
                max_depth=6,
                min_samples_leaf=4,
                class_weight={-1: 1.0, 0: 4.0, 1: 1.0},
                n_jobs=-1,
                random_state=42,
            ),
        ),
    ]


def candidate_policies() -> list[tuple[str, dict[str, float | str]]]:
    """Return validation-only probability-to-label policies."""
    return [
        ("argmax", {"type": "argmax"}),
        (
            "confidence_0_35",
            {"type": "confidence", "sell_minimum": 0.35, "buy_minimum": 0.35, "margin": 0.00},
        ),
        (
            "confidence_0_40",
            {"type": "confidence", "sell_minimum": 0.40, "buy_minimum": 0.40, "margin": 0.00},
        ),
        (
            "margin_only_0_02",
            {"type": "confidence", "sell_minimum": 0.00, "buy_minimum": 0.00, "margin": 0.02},
        ),
        (
            "margin_only_0_05",
            {"type": "confidence", "sell_minimum": 0.00, "buy_minimum": 0.00, "margin": 0.05},
        ),
        (
            "confidence_0_35_margin_0_02",
            {"type": "confidence", "sell_minimum": 0.35, "buy_minimum": 0.35, "margin": 0.02},
        ),
        (
            "confidence_buy_0_40_margin_0_02",
            {"type": "confidence", "sell_minimum": 0.35, "buy_minimum": 0.40, "margin": 0.02},
        ),
        (
            "confidence_0_45",
            {"type": "confidence", "sell_minimum": 0.45, "buy_minimum": 0.45, "margin": 0.00},
        ),
        (
            "confidence_0_50",
            {"type": "confidence", "sell_minimum": 0.50, "buy_minimum": 0.50, "margin": 0.00},
        ),
        (
            "confidence_buy_0_55",
            {"type": "confidence", "sell_minimum": 0.50, "buy_minimum": 0.55, "margin": 0.00},
        ),
        (
            "confidence_0_45_margin_0_05",
            {"type": "confidence", "sell_minimum": 0.45, "buy_minimum": 0.45, "margin": 0.05},
        ),
        (
            "confidence_buy_0_50_margin_0_05",
            {"type": "confidence", "sell_minimum": 0.45, "buy_minimum": 0.50, "margin": 0.05},
        ),
    ]


def predict_with_policy(
    probabilities: Sequence[Sequence[float]],
    classes: Sequence[int],
    policy: dict[str, float | str],
) -> list[int]:
    """Convert model probabilities to SELL/HOLD/BUY without reading future data."""
    if set(classes) != set(LABELS):
        raise ValueError(f"Unexpected model classes: {classes}")

    predictions: list[int] = []
    for row in probabilities:
        values = {int(label): float(row[index]) for index, label in enumerate(classes)}
        if policy["type"] == "argmax":
            predictions.append(max(values, key=values.get))
            continue

        sell = values[-1]
        hold = values[0]
        buy = values[1]
        sell_ready = (
            sell >= float(policy["sell_minimum"])
            and sell - max(hold, buy) >= float(policy["margin"])
        )
        buy_ready = (
            buy >= float(policy["buy_minimum"])
            and buy - max(sell, hold) >= float(policy["margin"])
        )
        if sell_ready and (not buy_ready or sell >= buy):
            predictions.append(-1)
        elif buy_ready:
            predictions.append(1)
        else:
            predictions.append(0)
    return predictions


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", required=True, type=Path)
    parser.add_argument("--validation", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()
    train_features, train_labels = read_dataset(arguments.train)
    validation_features, validation_labels = read_dataset(arguments.validation)

    candidates: list[dict[str, Any]] = []
    selected_model: Any | None = None
    selected_name = ""
    selected_policy_name = ""
    selected_policy: dict[str, float | str] = {}
    selected_metrics: dict[str, float | int] = {}
    selected_gate_met = False
    selected_key = (-1, -1.0, -1.0)
    for name, model in candidate_models():
        model.fit(train_features, train_labels)
        probabilities = model.predict_proba(validation_features).tolist()
        classes = [int(label) for label in model.classes_.tolist()]
        for policy_name, policy in candidate_policies():
            predicted = predict_with_policy(probabilities, classes, policy)
            metrics = evaluation_metrics(validation_labels, predicted)
            gate_met = meets_evaluation_contract(metrics)
            candidates.append({
                "name": name,
                "decision_policy_name": policy_name,
                "decision_policy": policy,
                "validation_metrics": metrics,
                "validation_gate_met": gate_met,
            })
            selection_key = (
                int(gate_met),
                float(metrics["macro_f1"]),
                float(metrics["accuracy"]),
            )
            if selection_key > selected_key:
                selected_model = model
                selected_name = name
                selected_policy_name = policy_name
                selected_policy = policy
                selected_metrics = metrics
                selected_gate_met = gate_met
                selected_key = selection_key

    if selected_model is None:
        raise RuntimeError("No candidate model was trained")

    arguments.output_dir.mkdir(parents=True, exist_ok=True)
    preliminary_model_path = arguments.output_dir / "xau_ai_candidate_preliminary.joblib"
    joblib.dump(selected_model, preliminary_model_path)
    preliminary_policy_path = arguments.output_dir / "xau_ai_candidate_preliminary_policy.json"
    preliminary_policy_path.write_text(json.dumps({
        "training_contract_version": TRAINING_CONTRACT_VERSION,
        "feature_schema_version": FEATURE_SCHEMA_VERSION,
        "label_schema_version": LABEL_SCHEMA_VERSION,
        "model_candidate": selected_name,
        "decision_policy_name": selected_policy_name,
        "decision_policy": selected_policy,
        "limitations": [
            "This policy is selected with Validation only and is not a deployment authorization.",
            "A future inference adapter must load the model and policy together.",
        ],
    }, indent=2), encoding="utf-8")
    report = {
        "selection_stage": "train_validation_only",
        "test_dataset_used": False,
        "training_contract_version": TRAINING_CONTRACT_VERSION,
        "feature_schema_version": FEATURE_SCHEMA_VERSION,
        "label_schema_version": LABEL_SCHEMA_VERSION,
        "selection_metric": "validation_gate_then_macro_f1_then_accuracy",
        "train_class_distribution": class_distribution(train_labels),
        "validation_class_distribution": class_distribution(validation_labels),
        "train_feature_means_by_class": feature_means_by_class(train_features, train_labels),
        "candidates": candidates,
        "selected_candidate": selected_name,
        "selected_decision_policy_name": selected_policy_name,
        "selected_decision_policy": selected_policy,
        "selected_validation_metrics": selected_metrics,
        "selected_validation_gate_met": selected_gate_met,
        "preliminary_model_file": str(preliminary_model_path),
        "preliminary_policy_file": str(preliminary_policy_path),
        "limitations": [
            "Do not use this preliminary artifact in MQL5 or for trading.",
            "The existing Test partition is intentionally not read by this script.",
            "A new untouched final test period is required after candidate selection.",
        ],
    }
    report_path = arguments.output_dir / "candidate_diagnostics.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
