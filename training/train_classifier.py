"""Train and evaluate the XAU AI three-class baseline classifier."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_recall_fscore_support


FEATURE_COLUMNS = (
    "trend_regime",
    "trend_momentum",
    "trend_slope",
    "volatility_regime",
    "volatility_change",
    "liquidity_activity",
    "liquidity_range_position",
    "liquidity_sweep_direction",
    "session_asia",
    "session_london",
    "session_new_york",
    "session_progress",
)
TRAINING_CONTRACT_VERSION = "4.0.0"
FEATURE_SCHEMA_VERSION = "4.0.0"
LABEL_SCHEMA_VERSION = "1.1.0"
LABEL_COLUMN = "label"
LABELS = (-1, 0, 1)
CLASS_NAMES = ("SELL", "HOLD", "BUY")
REQUIRED_COLUMNS = ("id", "timestamp", "symbol", *FEATURE_COLUMNS, LABEL_COLUMN)

MINIMUM_SAMPLES = 100
MINIMUM_ACCURACY = 0.45
MINIMUM_MACRO_F1 = 0.40
MINIMUM_DIRECTIONAL_PRECISION = 0.50
MINIMUM_DIRECTIONAL_RECALL = 0.30


def read_dataset(path: Path) -> tuple[list[list[float]], list[int]]:
    """Read one validated MQL5 dataset CSV without changing its time order."""
    if not path.is_file():
        raise ValueError(f"Dataset file not found: {path}")

    features: list[list[float]] = []
    labels: list[int] = []
    with path.open("r", newline="", encoding="utf-8") as dataset_file:
        reader = csv.DictReader(dataset_file)
        if reader.fieldnames is None or tuple(reader.fieldnames) != REQUIRED_COLUMNS:
            raise ValueError(f"Unexpected CSV schema in {path}. Expected: {REQUIRED_COLUMNS}")
        for row_number, row in enumerate(reader, start=2):
            try:
                values = [float(row[column]) for column in FEATURE_COLUMNS]
                label = int(float(row[LABEL_COLUMN]))
            except (KeyError, TypeError, ValueError) as error:
                raise ValueError(f"Invalid row {row_number} in {path}: {error}") from error
            if any(value < 0.0 or value > 100.0 for value in values):
                raise ValueError(f"Feature outside 0..100 at row {row_number} in {path}")
            if values[7] not in (0.0, 50.0, 100.0):
                raise ValueError(f"Invalid liquidity sweep direction at row {row_number} in {path}")
            session_values = values[8:11]
            if any(value not in (0.0, 100.0) for value in session_values) or sum(session_values) != 100.0:
                raise ValueError(f"Invalid one-hot session encoding at row {row_number} in {path}")
            if values[11] < 0.0 or values[11] > 100.0:
                raise ValueError(f"Invalid Session progress at row {row_number} in {path}")
            if label not in LABELS:
                raise ValueError(f"Invalid label at row {row_number} in {path}: {label}")
            features.append(values)
            labels.append(label)

    if not features:
        raise ValueError(f"Dataset is empty: {path}")
    return features, labels


def evaluation_metrics(actual: list[int], predicted: list[int]) -> dict[str, float | int]:
    """Create the exact metric names used by the MQL5 evaluation contract."""
    precision, recall, f1, _ = precision_recall_fscore_support(
        actual, predicted, labels=LABELS, zero_division=0
    )
    return {
        "sample_count": len(actual),
        "accuracy": float(accuracy_score(actual, predicted)),
        "macro_f1": float(sum(f1) / len(f1)),
        "sell_precision": float(precision[0]),
        "sell_recall": float(recall[0]),
        "hold_precision": float(precision[1]),
        "hold_recall": float(recall[1]),
        "buy_precision": float(precision[2]),
        "buy_recall": float(recall[2]),
    }


def meets_evaluation_contract(metrics: dict[str, float | int]) -> bool:
    """Mirror the baseline ModelEvaluationContract thresholds."""
    return (
        int(metrics["sample_count"]) >= MINIMUM_SAMPLES
        and float(metrics["accuracy"]) >= MINIMUM_ACCURACY
        and float(metrics["macro_f1"]) >= MINIMUM_MACRO_F1
        and float(metrics["buy_precision"]) >= MINIMUM_DIRECTIONAL_PRECISION
        and float(metrics["sell_precision"]) >= MINIMUM_DIRECTIONAL_PRECISION
        and float(metrics["buy_recall"]) >= MINIMUM_DIRECTIONAL_RECALL
        and float(metrics["sell_recall"]) >= MINIMUM_DIRECTIONAL_RECALL
    )


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", required=True, type=Path)
    parser.add_argument("--validation", required=True, type=Path)
    parser.add_argument("--test", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()
    train_features, train_labels = read_dataset(arguments.train)
    validation_features, validation_labels = read_dataset(arguments.validation)
    test_features, test_labels = read_dataset(arguments.test)

    candidates: list[tuple[float, float, LogisticRegression, dict[str, float | int]]] = []
    for regularization_strength in (0.1, 1.0, 10.0):
        model = LogisticRegression(
            C=regularization_strength,
            class_weight="balanced",
            max_iter=2000,
            random_state=42,
        )
        model.fit(train_features, train_labels)
        validation_prediction = model.predict(validation_features).tolist()
        validation = evaluation_metrics(validation_labels, validation_prediction)
        candidates.append((
            float(validation["macro_f1"]),
            float(validation["accuracy"]),
            model,
            validation,
        ))

    _, _, selected_model, validation_metrics = max(candidates, key=lambda item: (item[0], item[1]))
    test_prediction = selected_model.predict(test_features).tolist()
    test_metrics = evaluation_metrics(test_labels, test_prediction)

    arguments.output_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(selected_model, arguments.output_dir / "xau_ai_classifier.joblib")
    metadata: dict[str, Any] = {
        "model_name": "XAU_AI_CLASSIFIER",
        "model_version": "0.1.0-baseline",
        "training_contract_version": TRAINING_CONTRACT_VERSION,
        "feature_schema_version": FEATURE_SCHEMA_VERSION,
        "label_schema_version": LABEL_SCHEMA_VERSION,
        "input_name": "features",
        "feature_order": list(FEATURE_COLUMNS),
        "output_name": "class_probabilities",
        "output_order": list(CLASS_NAMES),
        "label_mapping": {"SELL": -1, "HOLD": 0, "BUY": 1},
        "framework": "scikit-learn",
        "algorithm": "LogisticRegression(class_weight=balanced)",
        "selection_metric": "validation_macro_f1",
        "validation_metrics": validation_metrics,
        "test_metrics": test_metrics,
        "eligible_for_shadow_deployment": (
            meets_evaluation_contract(validation_metrics)
            and meets_evaluation_contract(test_metrics)
        ),
        "limitations": [
            "Baseline artifact is joblib and cannot yet be loaded by MQL5.",
            "Eligibility does not authorize live trading or bypass Risk.",
        ],
    }
    metadata_path = arguments.output_dir / "xau_ai_classifier_metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print(json.dumps({
        "validation_metrics": validation_metrics,
        "test_metrics": test_metrics,
        "eligible_for_shadow_deployment": metadata["eligible_for_shadow_deployment"],
        "model_file": str(arguments.output_dir / "xau_ai_classifier.joblib"),
        "metadata_file": str(metadata_path),
    }, indent=2))


if __name__ == "__main__":
    main()
