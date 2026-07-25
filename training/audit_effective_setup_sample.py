"""XAU AI PLATFORM | Offline Evidence Audit | Version 1.0.0.

Measure the maximum independent Setup Outcome sample without reading sealed
Validation/Test evidence, training a model, or authorizing deployment.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

from augment_pretrain_history import read_trainable, sha256
from build_setup_outcome_dataset import parse_time


AUDIT_SCHEMA_VERSION = "1.0.0"
MINIMUM_EFFECTIVE_SAMPLE = 200
METHOD = "maximum_cardinality_non_overlapping_outcome_intervals"


def validate_expected_hash(value: str) -> str:
    normalized = value.strip().upper()
    if len(normalized) != 64 or any(
        character not in "0123456789ABCDEF" for character in normalized
    ):
        raise ValueError("Effective Sample expected SHA-256 is invalid")
    return normalized


def maximum_non_overlapping(
    intervals: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Return an optimal maximum-cardinality set for half-open intervals."""

    selected: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    last_end: datetime | None = None
    last_selected: dict[str, Any] | None = None
    for interval in sorted(
        intervals,
        key=lambda item: (item["end"], item["start"], item["direction"]),
    ):
        if last_end is None or interval["start"] >= last_end:
            selected.append(interval)
            last_end = interval["end"]
            last_selected = interval
            continue
        if last_selected is None:
            raise AssertionError("Effective Sample interval selection lost state")
        excluded.append({
            "observation_time": interval["observation_time"],
            "outcome_known_at": interval["outcome_known_at"],
            "direction": interval["direction"],
            "outcome": interval["outcome"],
            "reason": "overlaps_selected_outcome_interval",
            "selected_observation_time": last_selected["observation_time"],
            "selected_outcome_known_at": last_selected["outcome_known_at"],
        })
    return selected, excluded


def overlap_diagnostics(intervals: list[dict[str, Any]]) -> dict[str, int]:
    events: list[tuple[datetime, int, int]] = []
    for interval in intervals:
        events.append((interval["start"], 1, 1))
        events.append((interval["end"], 0, -1))
    active = 0
    maximum_concurrent = 0
    for _, _, delta in sorted(events):
        active += delta
        if active < 0:
            raise AssertionError("Effective Sample interval sweep became negative")
        maximum_concurrent = max(maximum_concurrent, active)
    if active != 0:
        raise AssertionError("Effective Sample interval sweep did not close")

    overlapping_clusters = 0
    overlapping_records = 0
    maximum_cluster_size = 0
    cluster_end: datetime | None = None
    cluster_size = 0
    for interval in sorted(intervals, key=lambda item: (item["start"], item["end"])):
        if cluster_end is None or interval["start"] >= cluster_end:
            if cluster_size > 1:
                overlapping_clusters += 1
                overlapping_records += cluster_size
            maximum_cluster_size = max(maximum_cluster_size, cluster_size)
            cluster_size = 1
            cluster_end = interval["end"]
        else:
            cluster_size += 1
            cluster_end = max(cluster_end, interval["end"])
    if cluster_size > 1:
        overlapping_clusters += 1
        overlapping_records += cluster_size
    maximum_cluster_size = max(maximum_cluster_size, cluster_size)
    return {
        "maximum_concurrent_intervals": maximum_concurrent,
        "overlapping_clusters": overlapping_clusters,
        "records_in_overlapping_clusters": overlapping_records,
        "maximum_overlap_cluster_size": maximum_cluster_size,
    }


def audit_effective_sample(
    train_path: Path,
    expected_sha256: str,
    minimum_effective_sample: int = MINIMUM_EFFECTIVE_SAMPLE,
) -> dict[str, Any]:
    if minimum_effective_sample <= 0:
        raise ValueError("Effective Sample minimum must be positive")
    expected = validate_expected_hash(expected_sha256)
    actual = sha256(train_path)
    if actual != expected:
        raise ValueError("Effective Sample Train SHA-256 mismatch")

    rows = read_trainable(train_path)
    intervals: list[dict[str, Any]] = []
    for row in rows:
        start = parse_time(row["observation_time"])
        end = parse_time(row["outcome_known_at"])
        if end <= start:
            raise ValueError("Effective Sample outcome interval is not future-matured")
        intervals.append({
            "start": start,
            "end": end,
            "observation_time": row["observation_time"],
            "outcome_known_at": row["outcome_known_at"],
            "direction": row["direction"],
            "outcome": row["outcome"],
        })

    selected, excluded = maximum_non_overlapping(intervals)
    selected_directions = Counter(item["direction"] for item in selected)
    selected_outcomes = Counter(item["outcome"] for item in selected)
    effective = len(selected)
    return {
        "effective_sample_audit_schema_version": AUDIT_SCHEMA_VERSION,
        "audit_stage": "train_only_effective_setup_sample",
        "method": METHOD,
        "interval_semantics": "[observation_time,outcome_known_at)",
        "selection_rule": "earliest_outcome_known_at_greedy_optimal_interval_schedule",
        "source_train_sha256": actual,
        "raw_mature_records": len(rows),
        "effective_sample_records": effective,
        "overlap_discount_records": len(rows) - effective,
        "retention_rate": effective / len(rows),
        "minimum_effective_sample": minimum_effective_sample,
        "effective_sample_requirement_met": effective >= minimum_effective_sample,
        "duplicate_observation_times": 0,
        **overlap_diagnostics(intervals),
        "effective_by_direction": dict(sorted(selected_directions.items())),
        "effective_by_outcome": dict(sorted(selected_outcomes.items())),
        "excluded_intervals": excluded,
        "validation_dataset_read": False,
        "test_dataset_read": False,
        "model_training_performed": False,
        "runtime_changed": False,
        "risk_changed": False,
        "deployment_authorized": False,
        "model_status": "OBJECTIVE_STRUCTURAL_PLAN_RESEARCH_NO_GO",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", required=True, type=Path)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--output", required=True, type=Path)
    arguments = parser.parse_args()
    report = audit_effective_sample(arguments.train, arguments.expected_sha256)
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
