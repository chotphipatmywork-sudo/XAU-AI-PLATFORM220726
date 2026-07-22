"""Measure past-neighbour label ambiguity inside purged Train folds."""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any, Sequence

import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

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
from walk_forward_select import build_expanding_folds


PURGE_BARS = 16
DEFAULT_NEIGHBOURS = 25


def contract_metadata() -> dict[str, str]:
    """Return the active training, feature, and label contract versions."""
    return {
        "training_contract_version": TRAINING_CONTRACT_VERSION,
        "feature_schema_version": FEATURE_SCHEMA_VERSION,
        "label_schema_version": LABEL_SCHEMA_VERSION,
    }


def feature_groups() -> dict[str, list[int]]:
    """Return diagnostic views without changing the active Feature Schema."""
    return {
        "full_schema": list(range(len(FEATURE_COLUMNS))),
        "non_session": list(range(8)),
        "trend_group": [0, 1, 2],
        "volatility_group": [3, 4],
        "liquidity_group": [5, 6, 7],
        "session_group": [8, 9, 10, 11],
    }


def normalized_entropy(counts: Sequence[int]) -> float:
    """Return three-class Shannon entropy normalized to 0..1."""
    total = sum(int(value) for value in counts)
    if total <= 0:
        raise ValueError("Entropy requires at least one observation")
    entropy = 0.0
    for count in counts:
        if count > 0:
            probability = count / total
            entropy -= probability * math.log(probability)
    return entropy / math.log(len(LABELS))


def majority_label(counts: Sequence[int]) -> int:
    """Resolve ties deterministically in canonical SELL/HOLD/BUY order."""
    if len(counts) != len(LABELS):
        raise ValueError("Expected one count for every canonical label")
    return LABELS[max(range(len(counts)), key=lambda index: counts[index])]


def evaluate_neighbourhood(
    train_features: Sequence[Sequence[float]],
    train_labels: Sequence[int],
    evaluation_features: Sequence[Sequence[float]],
    evaluation_labels: Sequence[int],
    feature_indices: Sequence[int],
    neighbours: int = DEFAULT_NEIGHBOURS,
) -> dict[str, Any]:
    """Evaluate labels of nearest past rows for one purged fold."""
    if not feature_indices:
        raise ValueError("At least one feature is required")
    if neighbours <= 0 or not train_features or not evaluation_features:
        raise ValueError("Neighbour evaluation requires non-empty rows and positive k")
    if len(train_features) != len(train_labels) or len(evaluation_features) != len(evaluation_labels):
        raise ValueError("Feature and label lengths do not match")

    train_matrix = np.asarray(train_features, dtype=float)[:, feature_indices]
    evaluation_matrix = np.asarray(evaluation_features, dtype=float)[:, feature_indices]
    scaler = StandardScaler()
    scaled_train = scaler.fit_transform(train_matrix)
    scaled_evaluation = scaler.transform(evaluation_matrix)
    effective_k = min(neighbours, len(train_labels))
    neighbour_model = NearestNeighbors(n_neighbors=effective_k, metric="euclidean")
    neighbour_model.fit(scaled_train)
    distances, indices = neighbour_model.kneighbors(scaled_evaluation)

    train_counts = Counter(int(label) for label in train_labels)
    history_distribution = [train_counts[label] / len(train_labels) for label in LABELS]
    predicted: list[int] = []
    true_supports: list[float] = []
    history_true_supports: list[float] = []
    purities: list[float] = []
    entropies: list[float] = []
    nearest_matches: list[float] = []
    class_supports: dict[int, list[float]] = {label: [] for label in LABELS}

    for row_number, neighbour_indices in enumerate(indices):
        actual = int(evaluation_labels[row_number])
        neighbour_labels = [int(train_labels[index]) for index in neighbour_indices]
        counts = [neighbour_labels.count(label) for label in LABELS]
        predicted.append(majority_label(counts))
        support = counts[LABELS.index(actual)] / effective_k
        true_supports.append(support)
        history_true_supports.append(history_distribution[LABELS.index(actual)])
        class_supports[actual].append(support)
        purities.append(max(counts) / effective_k)
        entropies.append(normalized_entropy(counts))
        nearest_matches.append(float(neighbour_labels[0] == actual))

    return {
        "neighbours": effective_k,
        "records": len(evaluation_labels),
        "mean_true_label_support": float(np.mean(true_supports)),
        "mean_history_true_label_support": float(np.mean(history_true_supports)),
        "mean_true_label_support_gain": float(
            np.mean(true_supports) - np.mean(history_true_supports)
        ),
        "mean_neighbourhood_purity": float(np.mean(purities)),
        "mean_normalized_label_entropy": float(np.mean(entropies)),
        "nearest_label_match_rate": float(np.mean(nearest_matches)),
        "low_true_support_rate": float(np.mean(np.asarray(true_supports) < (1.0 / 3.0))),
        "mean_true_support_by_class": {
            name: (float(np.mean(class_supports[label])) if class_supports[label] else None)
            for label, name in zip(LABELS, CLASS_NAMES)
        },
        "majority_vote_metrics": evaluation_metrics(list(evaluation_labels), predicted),
        "mean_nearest_distance": float(np.mean(distances[:, 0])),
    }


def weighted_mean(reports: Sequence[dict[str, Any]], field: str) -> float:
    total = sum(int(report["records"]) for report in reports)
    return sum(float(report[field]) * int(report["records"]) for report in reports) / total


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--folds", type=int, default=4)
    parser.add_argument("--neighbours", type=int, default=DEFAULT_NEIGHBOURS)
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

    group_reports: list[dict[str, Any]] = []
    for group_name, indices in feature_groups().items():
        fold_reports: list[dict[str, Any]] = []
        actual: list[int] = []
        predicted: list[int] = []
        for fold_number, (train_end, evaluation_start, evaluation_end) in enumerate(folds, start=1):
            result = evaluate_neighbourhood(
                features[:train_end],
                labels[:train_end],
                features[evaluation_start:evaluation_end],
                labels[evaluation_start:evaluation_end],
                indices,
                neighbours=arguments.neighbours,
            )
            result.update({
                "fold": fold_number,
                "train_records": train_end,
                "purged_records": evaluation_start - train_end,
            })
            fold_reports.append(result)

            # Recreate only the deterministic majority vote for exact aggregate metrics.
            train_matrix = np.asarray(features[:train_end], dtype=float)[:, indices]
            evaluation_matrix = np.asarray(features[evaluation_start:evaluation_end], dtype=float)[:, indices]
            scaler = StandardScaler()
            scaled_train = scaler.fit_transform(train_matrix)
            scaled_evaluation = scaler.transform(evaluation_matrix)
            effective_k = min(arguments.neighbours, train_end)
            model = NearestNeighbors(n_neighbors=effective_k).fit(scaled_train)
            neighbour_indices = model.kneighbors(scaled_evaluation, return_distance=False)
            for row in neighbour_indices:
                counts = [sum(int(labels[index]) == label for index in row) for label in LABELS]
                predicted.append(majority_label(counts))
            actual.extend(labels[evaluation_start:evaluation_end])

        group_reports.append({
            "feature_view": group_name,
            "feature_names": [FEATURE_COLUMNS[index] for index in indices],
            "mean_true_label_support": weighted_mean(fold_reports, "mean_true_label_support"),
            "mean_history_true_label_support": weighted_mean(
                fold_reports, "mean_history_true_label_support"
            ),
            "mean_true_label_support_gain": weighted_mean(
                fold_reports, "mean_true_label_support_gain"
            ),
            "mean_neighbourhood_purity": weighted_mean(
                fold_reports, "mean_neighbourhood_purity"
            ),
            "mean_normalized_label_entropy": weighted_mean(
                fold_reports, "mean_normalized_label_entropy"
            ),
            "nearest_label_match_rate": weighted_mean(
                fold_reports, "nearest_label_match_rate"
            ),
            "low_true_support_rate": weighted_mean(fold_reports, "low_true_support_rate"),
            "majority_vote_metrics": evaluation_metrics(actual, predicted),
            "folds": fold_reports,
        })

    report = {
        "diagnostic_stage": "train_only_purged_feature_sufficiency",
        "validation_dataset_used": False,
        "test_dataset_used": False,
        **contract_metadata(),
        "purge_bars": arguments.purge_bars,
        "neighbours": arguments.neighbours,
        "future_rows_used": False,
        "feature_views": group_reports,
        "limitations": [
            "Neighbour agreement measures local label consistency, not causal trading value.",
            "All neighbours come from past Train history before a purged evaluation boundary.",
            "This diagnostic does not authorize a Feature Contract or model change.",
        ],
    }
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    summary = {
        "diagnostic_stage": report["diagnostic_stage"],
        "validation_dataset_used": False,
        "test_dataset_used": False,
        "purge_bars": arguments.purge_bars,
        "neighbours": arguments.neighbours,
        "feature_views": [
            {
                "feature_view": item["feature_view"],
                "mean_true_label_support": item["mean_true_label_support"],
                "mean_true_label_support_gain": item["mean_true_label_support_gain"],
                "mean_normalized_label_entropy": item["mean_normalized_label_entropy"],
                "nearest_label_match_rate": item["nearest_label_match_rate"],
                "majority_vote_metrics": item["majority_vote_metrics"],
            }
            for item in group_reports
        ],
        "diagnostic_file": str(arguments.output),
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
