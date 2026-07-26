#!/usr/bin/env python3
"""Focused tests for the IMP-100 outcome-free M5 export boundary."""

from __future__ import annotations

import csv
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from validate_imp100_outcome_free_m5_export import (
    EXPORT_HEADER,
    REQUEST_HEADER,
    TIME_FORMAT,
    load_requests,
    validate_export,
)


ROOT = Path(__file__).resolve().parents[1]
REQUESTS = ROOT / "training/output/imp100_train_only_replay_preparation/active_replay_requests.csv"


def write_synthetic_export(requests: list[dict[str, str]], path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=EXPORT_HEADER)
        writer.writeheader()
        for request in requests:
            observation = datetime.strptime(request["observation_time"], TIME_FORMAT)
            path_end = observation + timedelta(minutes=192 * 5)
            for sequence in range(1, 193):
                bar_open = observation + timedelta(minutes=(sequence - 1) * 5)
                writer.writerow({
                    "export_schema_version": "1.0.0",
                    "request_id": request["request_id"],
                    "base_opportunity_id": request["base_opportunity_id"],
                    "source_record_id": request["source_record_id"],
                    "arm_id": request["arm_id"],
                    "observation_time": request["observation_time"],
                    "path_end_exclusive": path_end.strftime(TIME_FORMAT),
                    "symbol": request["symbol"],
                    "direction": request["direction"],
                    "sequence": sequence,
                    "bar_open": bar_open.strftime(TIME_FORMAT),
                    "open": "100.0", "high": "101.0", "low": "99.0",
                    "close": "100.5", "tick_volume": "1", "spread": "1",
                    "real_volume": "0", "entry_price": request["entry_price"],
                    "stop_identity": request["stop_identity"],
                    "stop_price": request["stop_price"],
                    "target_identity": request["target_identity"],
                    "target_price": request["target_price"],
                    "minimum_rr": request["minimum_rr"],
                    "common_support": request["common_support"],
                    "source_sha256": request["source_sha256"],
                    "closed_m5_only": "true",
                    "deployment_authorized": "false",
                })


def expect_failure(action, message: str) -> None:
    try:
        action()
    except ValueError:
        return
    raise AssertionError(message)


def main() -> int:
    requests = load_requests(REQUESTS, 685)
    assert len(requests) == 685
    assert len({row["request_id"] for row in requests}) == 685
    assert {row["arm_id"] for row in requests} == {
        "CONTROL", "STOP_ONLY", "TARGET_ONLY", "COMBINED"
    }
    assert not any(
        "outcome" in column.lower() or "realized" in column.lower()
        for column in REQUEST_HEADER + EXPORT_HEADER
    )

    with tempfile.TemporaryDirectory() as temporary:
        directory = Path(temporary)
        export_a = directory / "export_a.csv"
        export_b = directory / "export_b.csv"
        write_synthetic_export(requests, export_a)
        write_synthetic_export(requests, export_b)
        assert export_a.read_bytes() == export_b.read_bytes()
        result = validate_export(
            REQUESTS, export_a, datetime(2024, 7, 1), 685, 192
        )
        assert result["status"] == "PASS"
        assert result["export_record_count"] == 131_520

        duplicate_requests = directory / "duplicate_requests.csv"
        with duplicate_requests.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=REQUEST_HEADER)
            writer.writeheader()
            duplicate = [dict(row) for row in requests]
            duplicate[-1]["request_id"] = duplicate[0]["request_id"]
            writer.writerows(duplicate)
        expect_failure(
            lambda: load_requests(duplicate_requests, 685),
            "duplicate request ID was accepted",
        )

        missing_export = directory / "missing_export.csv"
        with export_a.open("r", encoding="utf-8", newline="") as source:
            rows = list(csv.DictReader(source))
        with missing_export.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=EXPORT_HEADER)
            writer.writeheader()
            writer.writerows(rows[:-192])
        expect_failure(
            lambda: validate_export(
                REQUESTS, missing_export, datetime(2024, 7, 1), 685, 192
            ),
            "missing request output was accepted",
        )

    print("IMP-100 outcome-free M5 export focused test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
