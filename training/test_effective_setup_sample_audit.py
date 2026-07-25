"""Focused checks for the Train-only Effective Setup Sample audit."""

from __future__ import annotations

import csv
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from audit_effective_setup_sample import audit_effective_sample
from augment_pretrain_history import sha256
from build_setup_outcome_dataset import OUTCOME_AUDIT_COLUMNS


def write_rows(path: Path, intervals: list[tuple[int, int]]) -> None:
    origin = datetime(2025, 1, 1)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTCOME_AUDIT_COLUMNS)
        writer.writeheader()
        for index, (start_minutes, end_minutes) in enumerate(intervals):
            observation = origin + timedelta(minutes=start_minutes)
            known_at = origin + timedelta(minutes=end_minutes)
            row = {column: "50" for column in OUTCOME_AUDIT_COLUMNS}
            row.update({
                "setup_outcome_schema_version": "1.0.0",
                "feature_schema_version": "4.0.0",
                "observation_time": observation.strftime("%Y.%m.%d %H:%M"),
                "outcome_known_at": known_at.strftime("%Y.%m.%d %H:%M"),
                "symbol": "XAUUSD",
                "timeframe": "PERIOD_M15",
                "direction": (
                    "TRADE_SETUP_BUY" if index % 2 == 0 else "TRADE_SETUP_SELL"
                ),
                "outcome": "TARGET_FIRST" if index == 1 else "STOP_FIRST",
                "trainable": "true",
            })
            writer.writerow(row)


def main() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        source = Path(temporary) / "train.csv"
        write_rows(source, [(0, 60), (15, 30), (30, 45), (60, 75), (90, 105)])
        report = audit_effective_sample(source, sha256(source), 4)
        if report["raw_mature_records"] != 5 or report["effective_sample_records"] != 4:
            raise AssertionError("Effective Sample maximum interval schedule changed")
        if report["overlap_discount_records"] != 1:
            raise AssertionError("Effective Sample overlap discount changed")
        if report["maximum_concurrent_intervals"] != 2:
            raise AssertionError("Effective Sample concurrency audit changed")
        if report["maximum_overlap_cluster_size"] != 3:
            raise AssertionError("Effective Sample cluster audit changed")
        if not report["effective_sample_requirement_met"]:
            raise AssertionError("Effective Sample valid threshold failed")
        if report["validation_dataset_read"] or report["test_dataset_read"]:
            raise AssertionError("Effective Sample audit opened sealed evidence")
        if report["deployment_authorized"] or report["model_training_performed"]:
            raise AssertionError("Effective Sample audit changed protected state")

        try:
            audit_effective_sample(source, "A" * 64, 4)
        except ValueError as error:
            if "SHA-256 mismatch" not in str(error):
                raise
        else:
            raise AssertionError("Effective Sample audit accepted source hash drift")

        write_rows(source, [(0, 60), (0, 30)])
        try:
            audit_effective_sample(source, sha256(source), 1)
        except ValueError as error:
            if "unique and chronological" not in str(error):
                raise
        else:
            raise AssertionError("Effective Sample audit accepted duplicate observations")

    print("Effective Setup Sample audit test passed")


if __name__ == "__main__":
    main()
