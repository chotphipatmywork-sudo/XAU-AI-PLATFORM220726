"""XAU AI PLATFORM | Offline Research Diagnostic | Version 1.0.0.

Measure past-only canonical-feature separation of causal lifecycle responses
without selecting a threshold, changing Runtime, or reading sealed evidence.
"""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path
from statistics import fmean
from typing import Any, Callable, Sequence

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    f1_score,
    precision_recall_fscore_support,
)
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

from augment_pretrain_history import read_trainable, sha256
from build_lifecycle_path_requests import CANDIDATES
from build_setup_outcome_dataset import parse_time
from diagnose_entry_stop_expectancy import load_audited_effective_rows
from diagnose_lifecycle_differential_attribution import (
    DIAGNOSTIC_SCHEMA_VERSION as IMP085_SCHEMA_VERSION,
    attribute_transition,
)
from replay_lifecycle_management import read_paths, read_requests, simulate_path
from temporal_regime_diagnostic import numeric_bucket
from train_classifier import FEATURE_COLUMNS, FEATURE_SCHEMA_VERSION


ATTRIBUTION_SCHEMA_VERSION = "1.0.0"
RESPONSE_CLASSES = (
    "STOP_UNCHANGED",
    "STOP_LOSS_IMPROVED_BY_MANAGEMENT",
    "TARGET_CLIPPED_BY_MANAGEMENT",
    "TARGET_PRESERVED",
)
FEATURE_GROUPS = {
    "full_schema": tuple(range(12)),
    "trend_group": (0, 1, 2),
    "volatility_group": (3, 4),
    "liquidity_group": (5, 6, 7),
    "session_group": (8, 9, 10, 11),
}
NEIGHBOURS = 15
FOLDS = 4
INITIAL_TRAIN_FRACTION = 0.50
READINESS_GATE = {
    "minimum_support_gain": 0.03,
    "minimum_balanced_accuracy": 0.30,
    "minimum_macro_f1": 0.30,
    "minimum_nearest_match": 0.30,
    "positive_support_gain_folds": 4,
    "minimum_every_class_recall": 0.15,
}


def valid_hash(value: str, name: str) -> str:
    normalized = value.strip().upper()
    if len(normalized) != 64 or any(
        character not in "0123456789ABCDEF" for character in normalized
    ):
        raise ValueError(f"Canonical Setup attribution {name} SHA-256 is invalid")
    return normalized


def feature_groups() -> dict[str, tuple[int, ...]]:
    return dict(FEATURE_GROUPS)


def normalized_entropy(counts: Sequence[int]) -> float:
    total = sum(int(value) for value in counts)
    if total <= 0:
        raise ValueError("Canonical Setup entropy requires observations")
    entropy = 0.0
    for count in counts:
        if count > 0:
            probability = count / total
            entropy -= probability * math.log(probability)
    return entropy / math.log(len(RESPONSE_CLASSES))


def majority_class(counts: Sequence[int]) -> int:
    if len(counts) != len(RESPONSE_CLASSES):
        raise ValueError("Canonical Setup class count changed")
    return max(range(len(counts)), key=lambda index: counts[index])


def classification_metrics(actual: list[int], predicted: list[int]) -> dict[str, Any]:
    labels = list(range(len(RESPONSE_CLASSES)))
    precision, recall, class_f1, _ = precision_recall_fscore_support(
        actual, predicted, labels=labels, zero_division=0
    )
    return {
        "records": len(actual),
        "accuracy": float(accuracy_score(actual, predicted)),
        "balanced_accuracy": float(balanced_accuracy_score(actual, predicted)),
        "macro_f1": float(f1_score(
            actual, predicted, labels=labels, average="macro", zero_division=0
        )),
        "by_class": {
            name: {
                "precision": float(precision[index]),
                "recall": float(recall[index]),
                "f1": float(class_f1[index]),
                "support": sum(value == index for value in actual),
            }
            for index, name in enumerate(RESPONSE_CLASSES)
        },
    }


def evaluate_neighbourhood(
    train_features: Sequence[Sequence[float]],
    train_labels: Sequence[int],
    evaluation_features: Sequence[Sequence[float]],
    evaluation_labels: Sequence[int],
    indices: Sequence[int],
    neighbours: int = NEIGHBOURS,
) -> tuple[dict[str, Any], list[int]]:
    if not indices or neighbours <= 0 or not train_features or not evaluation_features:
        raise ValueError("Canonical Setup neighbourhood input is invalid")
    if len(train_features) != len(train_labels) or len(evaluation_features) != len(
        evaluation_labels
    ):
        raise ValueError("Canonical Setup feature/response lengths differ")
    train = np.asarray(train_features, dtype=float)[:, indices]
    evaluation = np.asarray(evaluation_features, dtype=float)[:, indices]
    scaler = StandardScaler()
    scaled_train = scaler.fit_transform(train)
    scaled_evaluation = scaler.transform(evaluation)
    effective_k = min(neighbours, len(train_labels))
    model = NearestNeighbors(n_neighbors=effective_k, metric="euclidean")
    model.fit(scaled_train)
    distances, neighbour_indices = model.kneighbors(scaled_evaluation)
    history = Counter(int(value) for value in train_labels)
    predicted: list[int] = []
    supports: list[float] = []
    history_supports: list[float] = []
    entropies: list[float] = []
    purities: list[float] = []
    nearest_matches: list[float] = []
    for row_number, neighbours_for_row in enumerate(neighbour_indices):
        labels = [int(train_labels[index]) for index in neighbours_for_row]
        counts = [labels.count(index) for index in range(len(RESPONSE_CLASSES))]
        actual = int(evaluation_labels[row_number])
        predicted.append(majority_class(counts))
        supports.append(counts[actual]/effective_k)
        history_supports.append(history[actual]/len(train_labels))
        entropies.append(normalized_entropy(counts))
        purities.append(max(counts)/effective_k)
        nearest_matches.append(float(labels[0] == actual))
    support = fmean(supports)
    history_support = fmean(history_supports)
    return ({
        "neighbours": effective_k,
        "records": len(evaluation_labels),
        "mean_true_class_support": support,
        "mean_history_true_class_support": history_support,
        "mean_true_class_support_gain": support-history_support,
        "mean_neighbourhood_purity": fmean(purities),
        "mean_normalized_entropy": fmean(entropies),
        "nearest_class_match_rate": fmean(nearest_matches),
        "mean_nearest_distance": float(np.mean(distances[:, 0])),
        "classification": classification_metrics(
            list(evaluation_labels), predicted
        ),
    }, predicted)


def expanding_folds(size: int) -> list[tuple[int, int, int]]:
    if size < 100:
        raise ValueError("Canonical Setup attribution requires at least 100 records")
    initial = int(size*INITIAL_TRAIN_FRACTION)
    remaining = size-initial
    base = remaining//FOLDS
    folds: list[tuple[int, int, int]] = []
    start = initial
    for index in range(FOLDS):
        end = size if index == FOLDS-1 else start+base
        folds.append((start, start, end))
        start = end
    return folds


def readiness(metrics: dict[str, Any], positive_folds: int) -> dict[str, bool]:
    recalls = [
        float(metrics["classification"]["by_class"][name]["recall"])
        for name in RESPONSE_CLASSES
    ]
    gates = {
        "support_gain": metrics["mean_true_class_support_gain"] >= (
            READINESS_GATE["minimum_support_gain"]
        ),
        "balanced_accuracy": metrics["classification"]["balanced_accuracy"] >= (
            READINESS_GATE["minimum_balanced_accuracy"]
        ),
        "macro_f1": metrics["classification"]["macro_f1"] >= (
            READINESS_GATE["minimum_macro_f1"]
        ),
        "nearest_match": metrics["nearest_class_match_rate"] >= (
            READINESS_GATE["minimum_nearest_match"]
        ),
        "fold_stability": positive_folds == (
            READINESS_GATE["positive_support_gain_folds"]
        ),
        "every_class_recall": min(recalls) >= (
            READINESS_GATE["minimum_every_class_recall"]
        ),
    }
    gates["hypothesis_ready"] = all(gates.values())
    return gates


def aggregate_view(
    records: list[dict[str, Any]], indices: Sequence[int]
) -> dict[str, Any]:
    folds = expanding_folds(len(records))
    fold_reports: list[dict[str, Any]] = []
    actual: list[int] = []
    predicted: list[int] = []
    support_weight = 0.0
    history_weight = 0.0
    purity_weight = 0.0
    entropy_weight = 0.0
    nearest_weight = 0.0
    total = 0
    positive_folds = 0
    features = [record["features"] for record in records]
    labels = [int(record["response_index"]) for record in records]
    for fold_number, (train_end, evaluation_start, evaluation_end) in enumerate(
        folds, start=1
    ):
        if records[train_end-1]["outcome_known_at"] > records[evaluation_start][
            "observation"
        ]:
            raise ValueError("Canonical Setup past-only fold overlaps maturity")
        report, fold_prediction = evaluate_neighbourhood(
            features[:train_end], labels[:train_end],
            features[evaluation_start:evaluation_end],
            labels[evaluation_start:evaluation_end], indices,
        )
        count = int(report["records"])
        total += count
        support_weight += float(report["mean_true_class_support"])*count
        history_weight += float(report["mean_history_true_class_support"])*count
        purity_weight += float(report["mean_neighbourhood_purity"])*count
        entropy_weight += float(report["mean_normalized_entropy"])*count
        nearest_weight += float(report["nearest_class_match_rate"])*count
        positive_folds += report["mean_true_class_support_gain"] > 0.0
        actual.extend(labels[evaluation_start:evaluation_end])
        predicted.extend(fold_prediction)
        fold_reports.append({
            "fold": fold_number,
            "train_records": train_end,
            "evaluation_start": evaluation_start,
            "evaluation_end": evaluation_end,
            **report,
        })
    aggregate_classification = classification_metrics(actual, predicted)
    aggregate = {
        "records": total,
        "mean_true_class_support": support_weight/total,
        "mean_history_true_class_support": history_weight/total,
        "mean_true_class_support_gain": (support_weight-history_weight)/total,
        "mean_neighbourhood_purity": purity_weight/total,
        "mean_normalized_entropy": entropy_weight/total,
        "nearest_class_match_rate": nearest_weight/total,
        "classification": aggregate_classification,
        "positive_support_gain_folds": positive_folds,
        "folds": fold_reports,
    }
    aggregate["hypothesis_readiness_gates"] = readiness(aggregate, positive_folds)
    return aggregate


def economic_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    if not records:
        raise ValueError("Canonical Setup bucket is empty")
    counts = Counter(str(record["response_class"]) for record in records)
    targets = counts["TARGET_PRESERVED"] + counts["TARGET_CLIPPED_BY_MANAGEMENT"]
    stops = counts["STOP_UNCHANGED"] + counts["STOP_LOSS_IMPROVED_BY_MANAGEMENT"]
    return {
        "records": len(records),
        "response_counts": {
            name: counts.get(name, 0) for name in RESPONSE_CLASSES
        },
        "response_rates": {
            name: counts.get(name, 0)/len(records) for name in RESPONSE_CLASSES
        },
        "baseline_target_rate": targets/len(records),
        "target_preservation_rate": (
            counts["TARGET_PRESERVED"]/targets if targets else None
        ),
        "stop_improvement_rate": (
            counts["STOP_LOSS_IMPROVED_BY_MANAGEMENT"]/stops if stops else None
        ),
        "baseline_mean_r": fmean(float(record["baseline_r"]) for record in records),
        "candidate_mean_r": fmean(float(record["candidate_r"]) for record in records),
        "mean_delta_r": fmean(float(record["delta_r"]) for record in records),
        "net_delta_r": sum(float(record["delta_r"]) for record in records),
    }


def session_bucket(features: Sequence[float]) -> str:
    values = features[8:11]
    if any(value not in (0.0, 100.0) for value in values) or sum(values) != 100.0:
        raise ValueError("Canonical Setup Session one-hot is invalid")
    return ("ASIA", "LONDON", "NEW_YORK")[max(
        range(3), key=lambda index: values[index]
    )]


def sweep_bucket(features: Sequence[float]) -> str:
    value = features[7]
    mapping = {0.0: "down", 50.0: "neutral", 100.0: "up"}
    if value not in mapping:
        raise ValueError("Canonical Setup Liquidity Sweep is invalid")
    return mapping[value]


def bucket_specs() -> list[tuple[str, Callable[[Sequence[float]], str]]]:
    numeric = (0, 1, 2, 3, 4, 5, 6, 11)
    specs = [
        (FEATURE_COLUMNS[index], lambda row, selected=index: numeric_bucket(row[selected]))
        for index in numeric
    ]
    specs.extend((
        ("liquidity_sweep_direction", sweep_bucket),
        ("session", session_bucket),
    ))
    return specs


def fixed_bucket_attribution(records: list[dict[str, Any]]) -> dict[str, Any]:
    report: dict[str, Any] = {}
    for name, bucketer in bucket_specs():
        grouped: dict[str, list[dict[str, Any]]] = {}
        for record in records:
            grouped.setdefault(bucketer(record["features"]), []).append(record)
        report[name] = {
            bucket: economic_summary(selected)
            for bucket, selected in sorted(grouped.items())
        }
    return report


def response_feature_means(records: list[dict[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for response in RESPONSE_CLASSES:
        selected = [record for record in records if record["response_class"] == response]
        if not selected:
            raise ValueError("Canonical Setup response class is empty")
        result[response] = {
            "records": len(selected),
            "feature_means": {
                name: fmean(float(record["features"][index]) for record in selected)
                for index, name in enumerate(FEATURE_COLUMNS)
            },
        }
    return result


def load_records(
    train_path: Path,
    expected_train_sha256: str,
    audit_path: Path,
    expected_audit_sha256: str,
    request_path: Path,
    manifest_path: Path,
    export_path: Path,
    attribution_path: Path,
    expected_attribution_sha256: str,
) -> tuple[list[dict[str, Any]], dict[str, str]]:
    effective, _, train_hash, audit_hash = load_audited_effective_rows(
        train_path, expected_train_sha256, audit_path, expected_audit_sha256
    )
    attribution_hash = sha256(attribution_path)
    if attribution_hash != valid_hash(expected_attribution_sha256, "IMP-085"):
        raise ValueError("Canonical Setup IMP-085 SHA-256 mismatch")
    attribution = json.loads(attribution_path.read_text(encoding="utf-8-sig"))
    if attribution.get("lifecycle_differential_attribution_schema_version") != (
        IMP085_SCHEMA_VERSION
    ) or attribution.get("candidate_selected") is not False or (
        attribution.get("subgroup_filter_authorized") is not False
    ) or attribution.get("deployment_remains_no_go") is not True:
        raise ValueError("Canonical Setup IMP-085 protected state changed")
    for flag in (
        "validation_dataset_read", "test_dataset_read", "model_training_performed",
        "runtime_changed", "risk_changed", "runtime_change_request_authorized",
        "deployment_authorized",
    ):
        if attribution.get(flag) is not False:
            raise ValueError("Canonical Setup IMP-085 protected flag changed")

    evidence_hashes = {
        "request_file_sha256": sha256(request_path),
        "request_manifest_sha256": sha256(manifest_path),
        "m5_path_export_sha256": sha256(export_path),
    }
    if any(attribution.get(name) != value for name, value in evidence_hashes.items()):
        raise ValueError("Canonical Setup IMP-085 evidence hash parity failed")

    raw = read_trainable(train_path)
    raw_by_time = {row["observation_time"]: row for row in raw}
    requests, _ = read_requests(request_path, manifest_path)
    paths = read_paths(export_path, requests)
    if len(effective) != len(requests) or [
        row["observation_time"] for row in effective
    ] != [request["observation_time"] for request in requests]:
        raise ValueError("Canonical Setup Effective Train/request join changed")
    records: list[dict[str, Any]] = []
    for selected, request in zip(effective, requests):
        observation = request["observation_time"]
        if observation not in raw_by_time:
            raise ValueError("Canonical Setup Train key is missing")
        source = raw_by_time[observation]
        if source["feature_schema_version"] != FEATURE_SCHEMA_VERSION or (
            source["direction"] != request["direction"]
        ) or source["outcome"] != request["baseline_outcome"] or (
            source["outcome_known_at"] != request["outcome_known_at"]
        ):
            raise ValueError("Canonical Setup Train/request parity failed")
        features = [float(source[name]) for name in FEATURE_COLUMNS]
        if any(not math.isfinite(value) or not 0.0 <= value <= 100.0 for value in features):
            raise ValueError("Canonical Setup feature value is invalid")
        path = paths[request["request_id"]]
        baseline = simulate_path(request, path, CANDIDATES[0], 1.0)
        managed = simulate_path(request, path, CANDIDATES[1], 1.0)
        paired = attribute_transition(baseline, managed)
        response = str(paired["category"])
        if response not in RESPONSE_CLASSES or paired["delta_r"] is None:
            raise ValueError("Canonical Setup response is inadmissible")
        records.append({
            "request_id": request["request_id"],
            "observation_time": observation,
            "observation": request["observation"],
            "outcome_known_at": request["known_at"],
            "direction": request["direction"],
            "features": features,
            "response_class": response,
            "response_index": RESPONSE_CLASSES.index(response),
            "baseline_r": paired["baseline_r"],
            "candidate_r": paired["candidate_r"],
            "delta_r": paired["delta_r"],
        })
    expected_categories = attribution["candidate_results"][CANDIDATES[1]]["1.0"][
        "overall"
    ]["categories"]
    actual_categories = Counter(record["response_class"] for record in records)
    if any(actual_categories[name] != expected_categories[name] for name in RESPONSE_CLASSES):
        raise ValueError("Canonical Setup response/IMP-085 category parity failed")
    return records, {
        "source_train_sha256": train_hash,
        "effective_sample_audit_sha256": audit_hash,
        **evidence_hashes,
        "imp085_attribution_sha256": attribution_hash,
    }


def diagnose(
    train_path: Path,
    expected_train_sha256: str,
    audit_path: Path,
    expected_audit_sha256: str,
    request_path: Path,
    manifest_path: Path,
    export_path: Path,
    attribution_path: Path,
    expected_attribution_sha256: str,
) -> dict[str, Any]:
    records, hashes = load_records(
        train_path, expected_train_sha256, audit_path, expected_audit_sha256,
        request_path, manifest_path, export_path, attribution_path,
        expected_attribution_sha256,
    )
    views: dict[str, Any] = {}
    for name, indices in FEATURE_GROUPS.items():
        views[name] = aggregate_view(records, indices)
    eligible = [
        name for name in FEATURE_GROUPS
        if name != "full_schema"
        and views[name]["hypothesis_readiness_gates"]["hypothesis_ready"]
    ]
    eligible.sort(key=lambda name: (
        -min(
            views[name]["classification"]["by_class"][response]["recall"]
            for response in RESPONSE_CLASSES
        ),
        -views[name]["mean_true_class_support_gain"],
        -views[name]["classification"]["macro_f1"],
        -views[name]["classification"]["balanced_accuracy"],
        name,
    ))
    return {
        "canonical_setup_response_attribution_schema_version": ATTRIBUTION_SCHEMA_VERSION,
        "status": "CANONICAL_SETUP_RESPONSE_ATTRIBUTION_TRAIN_ONLY_NO_GO",
        **hashes,
        "feature_schema_version": FEATURE_SCHEMA_VERSION,
        "records": len(records),
        "response_classes": list(RESPONSE_CLASSES),
        "response_class_counts": dict(sorted(Counter(
            record["response_class"] for record in records
        ).items())),
        "method": {
            "folds": FOLDS,
            "initial_train_fraction": INITIAL_TRAIN_FRACTION,
            "neighbours": NEIGHBOURS,
            "past_only_maturity_enforced": True,
            "readiness_gate": READINESS_GATE,
            "fixed_numeric_buckets": ["low", "middle", "high"],
        },
        "canonical_views": views,
        "groups_ranked_for_separate_confirmation": eligible,
        "hypothesis_ready_group": eligible[0] if eligible else None,
        "response_feature_means": response_feature_means(records),
        "fixed_bucket_attribution": fixed_bucket_attribution(records),
        "threshold_selected": False,
        "filter_authorized": False,
        "candidate_selected": False,
        "validation_dataset_read": False,
        "test_dataset_read": False,
        "model_training_performed": False,
        "runtime_changed": False,
        "risk_changed": False,
        "runtime_change_request_authorized": False,
        "deployment_authorized": False,
        "deployment_remains_no_go": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", required=True, type=Path)
    parser.add_argument("--expected-train-sha256", required=True)
    parser.add_argument("--effective-sample-audit", required=True, type=Path)
    parser.add_argument("--expected-audit-sha256", required=True)
    parser.add_argument("--request", required=True, type=Path)
    parser.add_argument("--request-manifest", required=True, type=Path)
    parser.add_argument("--m5-path-export", required=True, type=Path)
    parser.add_argument("--imp085-attribution", required=True, type=Path)
    parser.add_argument("--expected-imp085-sha256", required=True)
    parser.add_argument("--output", required=True, type=Path)
    arguments = parser.parse_args()
    report = diagnose(
        arguments.train, arguments.expected_train_sha256,
        arguments.effective_sample_audit, arguments.expected_audit_sha256,
        arguments.request, arguments.request_manifest, arguments.m5_path_export,
        arguments.imp085_attribution, arguments.expected_imp085_sha256,
    )
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
