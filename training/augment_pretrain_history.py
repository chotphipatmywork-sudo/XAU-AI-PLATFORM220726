"""XAU AI PLATFORM | Offline Evidence | Version 1.0.0.

Prepend quality-controlled pre-Train outcomes without opening sealed evidence.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

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


FROZEN_HASHES = {
    "train": "5DB2A62D26471E3061D55B934BAFD6B004FE15AF065B278F42DC435E65E7334B",
    "validation": "0A741F1D8202DA749F5D94C4045C10BFE7C8EEEF9E7096FE81B9B32CECB7F683",
    "test": "8F5C596352946A5A13B82A5BB172A29B6852791FBF8B81614FB255912E57A446",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def read_trainable(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or tuple(reader.fieldnames) != OUTCOME_AUDIT_COLUMNS:
            raise ValueError(f"Unexpected Setup Outcome schema in {path}")
        rows = list(reader)
    if not rows:
        raise ValueError(f"Setup Outcome source is empty: {path}")

    previous = None
    seen = set()
    for row in rows:
        if row["setup_outcome_schema_version"] != SETUP_OUTCOME_SCHEMA_VERSION:
            raise ValueError("Setup Outcome Schema version mismatch")
        if row["feature_schema_version"] != FEATURE_SCHEMA_VERSION:
            raise ValueError("Feature Schema version mismatch")
        if not as_bool(row["trainable"]) or row["outcome"] not in TRAINABLE_OUTCOMES:
            raise ValueError("Pre-Train augmentation accepts only mature trainable rows")
        if row["symbol"] != "XAUUSD" or row["timeframe"] != "PERIOD_M15":
            raise ValueError("Pre-Train augmentation accepts only XAUUSD PERIOD_M15")
        feature_names = (
            "trend_regime", "trend_momentum", "trend_slope",
            "volatility_regime", "volatility_change", "liquidity_activity",
            "liquidity_range_position", "liquidity_sweep_direction",
            "session_asia", "session_london", "session_new_york",
            "session_progress",
        )
        feature_values = [float(row[name]) for name in feature_names]
        if any(not math.isfinite(value) or not 0.0 <= value <= 100.0
               for value in feature_values):
            raise ValueError("Pre-Train feature is outside [0,100]")
        observation = parse_time(row["observation_time"])
        known_at = parse_time(row["outcome_known_at"])
        if observation in seen or (previous is not None and observation <= previous):
            raise ValueError("Setup Outcome observations are not unique and chronological")
        if known_at <= observation:
            raise ValueError("Setup Outcome is not future-matured")
        seen.add(observation)
        previous = observation
    return rows


def readiness(rows: list[dict[str, str]]) -> dict[str, Any]:
    counts = Counter(row["outcome"] for row in rows)
    targets = counts.get("TARGET_FIRST", 0)
    non_targets = counts.get("STOP_FIRST", 0) + counts.get("TIMEOUT", 0)
    return {
        "train_records": len(rows),
        "target_records": targets,
        "non_target_records": non_targets,
        "minimum_train_records": MINIMUM_TRAINABLE_ROWS,
        "minimum_target_records": MINIMUM_TARGET_ROWS,
        "minimum_non_target_records": MINIMUM_NON_TARGET_ROWS,
        "sample_size_requirement_met": len(rows) >= MINIMUM_TRAINABLE_ROWS,
        "target_coverage_met": targets >= MINIMUM_TARGET_ROWS,
        "non_target_coverage_met": non_targets >= MINIMUM_NON_TARGET_ROWS,
        "ready_for_train_only_ranking": (
            len(rows) >= MINIMUM_TRAINABLE_ROWS
            and targets >= MINIMUM_TARGET_ROWS
            and non_targets >= MINIMUM_NON_TARGET_ROWS
        ),
    }


def augment(
    pretrain_path: Path,
    train_path: Path,
    validation_path: Path,
    test_path: Path,
    output_path: Path,
    summary_path: Path,
    quality_audit_path: Path,
    build_summary_path: Path,
    expected_hashes: dict[str, str] = FROZEN_HASHES,
) -> dict[str, Any]:
    paths = {"train": train_path, "validation": validation_path, "test": test_path}
    hashes_before = {name: sha256(path) for name, path in paths.items()}
    for name, expected in expected_hashes.items():
        if hashes_before[name] != expected.upper():
            raise ValueError(f"Frozen {name} SHA-256 mismatch")

    quality = json.loads(quality_audit_path.read_text(encoding="utf-8-sig"))
    if (not quality.get("all_warned_dates_quarantined")
            or quality.get("missing_exclusion_dates")
            or quality.get("deployment_authorized")):
        raise ValueError("CR-015 real-tick quality gate is not met")
    build = json.loads(build_summary_path.read_text(encoding="utf-8-sig"))
    if (build.get("dataset_stage") != "stage_d_setup_outcome_build_only"
            or build.get("training_performed")
            or build.get("deployment_authorized")
            or not build.get("quality_exclusion_file")):
        raise ValueError("CR-015 Setup Outcome build summary is not admissible")
    if Path(str(quality.get("quality_exclusion_file", ""))).name != Path(
        str(build["quality_exclusion_file"])
    ).name:
        raise ValueError("CR-015 quality audit and Dataset exclusion files differ")

    pretrain = read_trainable(pretrain_path)
    if int(build.get("trainable_rows", -1)) != len(pretrain):
        raise ValueError("CR-015 Dataset row count does not match its build summary")
    existing = read_trainable(train_path)
    first_existing = parse_time(existing[0]["observation_time"])
    last_pretrain_observation = parse_time(pretrain[-1]["observation_time"])
    last_pretrain_known = max(parse_time(row["outcome_known_at"]) for row in pretrain)
    if last_pretrain_observation >= first_existing or last_pretrain_known >= first_existing:
        raise ValueError("Pre-Train evidence overlaps the frozen Train boundary")

    combined = pretrain + existing
    if len({row["observation_time"] for row in combined}) != len(combined):
        raise ValueError("Pre-Train augmentation introduced duplicate observations")
    state = readiness(combined)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTCOME_AUDIT_COLUMNS)
        writer.writeheader()
        writer.writerows(combined)

    hashes_after = {name: sha256(path) for name, path in paths.items()}
    if hashes_after != hashes_before:
        output_path.unlink(missing_ok=True)
        raise ValueError("A frozen partition changed during augmentation")

    report = {
        "augmentation_stage": "cr015_pretrain_to_frozen_train_only",
        "setup_outcome_schema_version": SETUP_OUTCOME_SCHEMA_VERSION,
        "feature_schema_version": FEATURE_SCHEMA_VERSION,
        "pretrain_records": len(pretrain),
        "existing_train_records": len(existing),
        **state,
        "first_pretrain_observation": pretrain[0]["observation_time"],
        "last_pretrain_observation": pretrain[-1]["observation_time"],
        "first_existing_train_observation": existing[0]["observation_time"],
        "frozen_partition_sha256_before": hashes_before,
        "frozen_partition_sha256_after": hashes_after,
        "augmented_train_sha256": sha256(output_path),
        "pretrain_sha256": sha256(pretrain_path),
        "quality_audit_sha256": sha256(quality_audit_path),
        "build_summary_sha256": sha256(build_summary_path),
        "validation_dataset_read": False,
        "test_dataset_read": False,
        "training_performed": False,
        "deployment_authorized": False,
        "model_status": "OBJECTIVE_STRUCTURAL_PLAN_RESEARCH_NO_GO",
    }
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pretrain", required=True, type=Path)
    parser.add_argument("--train", required=True, type=Path)
    parser.add_argument("--validation", required=True, type=Path)
    parser.add_argument("--test", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--summary", required=True, type=Path)
    parser.add_argument("--quality-audit", required=True, type=Path)
    parser.add_argument("--build-summary", required=True, type=Path)
    arguments = parser.parse_args()
    report = augment(
        arguments.pretrain,
        arguments.train,
        arguments.validation,
        arguments.test,
        arguments.output,
        arguments.summary,
        arguments.quality_audit,
        arguments.build_summary,
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
