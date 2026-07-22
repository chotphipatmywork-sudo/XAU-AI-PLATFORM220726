"""Chronologically split Stage D Setup outcomes with outcome-time purging."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

from analyze_shadow_run import FEATURE_COLUMNS
from build_setup_outcome_dataset import (
    FEATURE_SCHEMA_VERSION,
    MINIMUM_NON_TARGET_ROWS,
    MINIMUM_TARGET_ROWS,
    MINIMUM_TRAINABLE_ROWS,
    OUTCOME_AUDIT_COLUMNS,
    SETUP_OUTCOME_SCHEMA_VERSION,
    TRAINABLE_OUTCOMES,
    as_bool,
    parse_time,
)


def read_trainable_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Setup Outcome Dataset not found: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or tuple(reader.fieldnames) != OUTCOME_AUDIT_COLUMNS:
            raise ValueError(f"Unexpected Setup Outcome schema in {path}")
        source_rows = list(reader)
    rows: list[dict[str, str]] = []
    previous_observation = None
    seen: set[str] = set()
    for row in source_rows:
        if row["setup_outcome_schema_version"] != SETUP_OUTCOME_SCHEMA_VERSION:
            raise ValueError("Setup Outcome Schema version mismatch")
        if row["feature_schema_version"] != FEATURE_SCHEMA_VERSION:
            raise ValueError("Feature Schema version mismatch")
        observation = parse_time(row["observation_time"])
        if row["observation_time"] in seen:
            raise ValueError(f"Duplicate Setup Outcome observation: {row['observation_time']}")
        seen.add(row["observation_time"])
        if previous_observation is not None and observation <= previous_observation:
            raise ValueError("Setup Outcome rows are not strictly chronological")
        previous_observation = observation
        trainable = as_bool(row["trainable"])
        if trainable:
            if row["outcome"] not in TRAINABLE_OUTCOMES:
                raise ValueError("A quarantined outcome is marked trainable")
            if not row["outcome_known_at"]:
                raise ValueError("A trainable Setup has no outcome-known time")
            known_at = parse_time(row["outcome_known_at"])
            if known_at <= observation:
                raise ValueError("Setup outcome was known at or before observation")
            for feature in FEATURE_COLUMNS:
                value = float(row[feature])
                if not 0.0 <= value <= 100.0:
                    raise ValueError(f"Feature outside [0,100]: {feature}={value}")
            rows.append(row)
    if len(rows) < 3:
        raise ValueError("At least three trainable Setup outcomes are required to split")
    return rows


def distribution(rows: list[dict[str, str]]) -> dict[str, int]:
    return dict(Counter(row["outcome"] for row in rows))


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTCOME_AUDIT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def split_rows(rows: list[dict[str, str]]) -> tuple[
    list[dict[str, str]], list[dict[str, str]], list[dict[str, str]], dict[str, Any]
]:
    total = len(rows)
    train_boundary = int(round(total * 0.70))
    validation_boundary = int(round(total * 0.85))
    if train_boundary < 1 or validation_boundary <= train_boundary or validation_boundary >= total:
        raise ValueError("Setup Outcome Dataset is too small for 70/15/15 splitting")

    raw_train = rows[:train_boundary]
    raw_validation = rows[train_boundary:validation_boundary]
    test = rows[validation_boundary:]
    validation_start = parse_time(raw_validation[0]["observation_time"])
    test_start = parse_time(test[0]["observation_time"])
    train = [
        row for row in raw_train
        if parse_time(row["outcome_known_at"]) < validation_start
    ]
    validation = [
        row for row in raw_validation
        if parse_time(row["outcome_known_at"]) < test_start
    ]
    if not train or not validation or not test:
        raise ValueError("Temporal purging emptied a Setup Outcome partition")

    temporal_valid = (
        max(parse_time(row["outcome_known_at"]) for row in train) < validation_start
        and max(parse_time(row["outcome_known_at"]) for row in validation) < test_start
        and max(parse_time(row["observation_time"]) for row in train)
        < min(parse_time(row["observation_time"]) for row in validation)
        < min(parse_time(row["observation_time"]) for row in test)
    )
    train_distribution = Counter(row["outcome"] for row in train)
    train_targets = train_distribution.get("TARGET_FIRST", 0)
    train_non_targets = (
        train_distribution.get("STOP_FIRST", 0)
        + train_distribution.get("TIMEOUT", 0)
    )
    summary = {
        "split_stage": "stage_d_setup_outcome_chronological_split",
        "setup_outcome_schema_version": SETUP_OUTCOME_SCHEMA_VERSION,
        "feature_schema_version": FEATURE_SCHEMA_VERSION,
        "training_performed": False,
        "validation_dataset_used_for_selection": False,
        "test_dataset_used_for_selection": False,
        "raw_train_records": len(raw_train),
        "raw_validation_records": len(raw_validation),
        "raw_test_records": len(test),
        "train_records": len(train),
        "validation_records": len(validation),
        "test_records": len(test),
        "purged_train_records": len(raw_train) - len(train),
        "purged_validation_records": len(raw_validation) - len(validation),
        "train_distribution": distribution(train),
        "validation_distribution": distribution(validation),
        "test_distribution": distribution(test),
        "validation_start": raw_validation[0]["observation_time"],
        "test_start": test[0]["observation_time"],
        "outcome_time_purge_valid": temporal_valid,
        "train_sample_size_requirement_met": len(train) >= MINIMUM_TRAINABLE_ROWS,
        "train_target_coverage_met": train_targets >= MINIMUM_TARGET_ROWS,
        "train_non_target_coverage_met": train_non_targets >= MINIMUM_NON_TARGET_ROWS,
        "ready_for_train_only_ranking": (
            temporal_valid
            and len(train) >= MINIMUM_TRAINABLE_ROWS
            and train_targets >= MINIMUM_TARGET_ROWS
            and train_non_targets >= MINIMUM_NON_TARGET_ROWS
        ),
        "deployment_authorized": False,
    }
    return train, validation, test, summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", required=True, type=Path)
    parser.add_argument("--train", required=True, type=Path)
    parser.add_argument("--validation", required=True, type=Path)
    parser.add_argument("--test", required=True, type=Path)
    parser.add_argument("--summary", required=True, type=Path)
    arguments = parser.parse_args()
    rows = read_trainable_rows(arguments.dataset)
    train, validation, test, summary = split_rows(rows)
    write_rows(arguments.train, train)
    write_rows(arguments.validation, validation)
    write_rows(arguments.test, test)
    arguments.summary.parent.mkdir(parents=True, exist_ok=True)
    arguments.summary.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({
        **summary,
        "train_file": str(arguments.train),
        "validation_file": str(arguments.validation),
        "test_file": str(arguments.test),
        "summary_file": str(arguments.summary),
    }, indent=2))


if __name__ == "__main__":
    main()
