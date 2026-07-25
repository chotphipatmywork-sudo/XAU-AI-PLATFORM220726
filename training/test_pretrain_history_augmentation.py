"""XAU AI PLATFORM | Offline Test | Version 1.0.0."""

from __future__ import annotations

import csv
import hashlib
import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from augment_pretrain_history import augment
from build_setup_outcome_dataset import OUTCOME_AUDIT_COLUMNS


def write_rows(path: Path, start: datetime, count: int, target_every: int) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTCOME_AUDIT_COLUMNS)
        writer.writeheader()
        for index in range(count):
            observation = start + timedelta(days=index)
            outcome = "TARGET_FIRST" if index % target_every == 0 else "STOP_FIRST"
            row = {column: "50" for column in OUTCOME_AUDIT_COLUMNS}
            row.update({
                "setup_outcome_schema_version": "1.0.0",
                "feature_schema_version": "4.0.0",
                "observation_time": observation.strftime("%Y.%m.%d %H:%M"),
                "outcome_known_at": (observation + timedelta(hours=1)).strftime(
                    "%Y.%m.%d %H:%M"
                ),
                "symbol": "XAUUSD",
                "timeframe": "PERIOD_M15",
                "direction": "TRADE_SETUP_BUY",
                "outcome": outcome,
                "trainable": "true",
            })
            writer.writerow(row)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        pretrain = root / "pretrain.csv"
        train = root / "train.csv"
        validation = root / "validation.csv"
        test = root / "test.csv"
        output = root / "augmented.csv"
        summary = root / "summary.json"
        quality = root / "quality.json"
        build = root / "build.json"
        write_rows(pretrain, datetime(2020, 1, 1), 60, 2)
        write_rows(train, datetime(2021, 1, 1), 150, 5)
        validation.write_text("sealed-validation", encoding="utf-8")
        test.write_text("sealed-test", encoding="utf-8")
        expected = {
            "train": digest(train),
            "validation": digest(validation),
            "test": digest(test),
        }
        quality.write_text(json.dumps({
            "quality_exclusion_file": "quality-exclusions.json",
            "missing_exclusion_dates": [],
            "all_warned_dates_quarantined": True,
            "deployment_authorized": False,
        }), encoding="utf-8")
        build.write_text(json.dumps({
            "dataset_stage": "stage_d_setup_outcome_build_only",
            "quality_exclusion_file": "quality-exclusions.json",
            "trainable_rows": 60,
            "training_performed": False,
            "deployment_authorized": False,
        }), encoding="utf-8")
        report = augment(
            pretrain, train, validation, test, output, summary,
            quality, build, expected
        )
        if report["train_records"] != 210 or not report["ready_for_train_only_ranking"]:
            raise AssertionError("Valid pre-Train evidence failed the readiness gate")
        if report["validation_dataset_read"] or report["test_dataset_read"]:
            raise AssertionError("A sealed partition was opened")

        validation.write_text("drift", encoding="utf-8")
        try:
            augment(
                pretrain, train, validation, test, output, summary,
                quality, build, expected
            )
        except ValueError as error:
            if "validation SHA-256 mismatch" not in str(error):
                raise
        else:
            raise AssertionError("Sealed Validation drift was accepted")

        validation.write_text("sealed-validation", encoding="utf-8")
        write_rows(pretrain, datetime(2020, 11, 15), 60, 2)
        try:
            augment(
                pretrain, train, validation, test, output, summary,
                quality, build, expected
            )
        except ValueError as error:
            if "overlaps" not in str(error):
                raise
        else:
            raise AssertionError("Overlapping pre-Train evidence was accepted")
    print("CR-015 pre-Train augmentation test passed")


if __name__ == "__main__":
    main()
