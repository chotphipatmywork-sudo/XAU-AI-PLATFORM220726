#!/usr/bin/env python3
"""Validate the deterministic outcome-free IMP-100 M5 export boundary."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

REQUEST_HEADER = [
    "request_schema_version", "request_id", "base_opportunity_id",
    "source_record_id", "arm_id", "observation_time", "symbol", "direction",
    "entry_price", "stop_identity", "stop_price", "target_identity",
    "target_price", "minimum_rr", "geometry_eligible", "common_support",
    "train_cutoff_compliant", "source_sha256", "deployment_authorized",
]
EXPORT_HEADER = [
    "export_schema_version", "request_id", "base_opportunity_id",
    "source_record_id", "arm_id", "observation_time", "path_end_exclusive",
    "symbol", "direction", "sequence", "bar_open", "open", "high", "low",
    "close", "tick_volume", "spread", "real_volume", "entry_price",
    "stop_identity", "stop_price", "target_identity", "target_price",
    "minimum_rr", "common_support", "source_sha256", "closed_m5_only",
    "deployment_authorized",
]
FORBIDDEN_FRAGMENTS = (
    "outcome", "realized", "winner", "loser", "win_loss", "stop_first",
    "target_first", "expectancy", "scorecard",
)
TIME_FORMAT = "%Y.%m.%d %H:%M"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _read_csv(path: Path, expected_header: list[str]) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != expected_header:
            raise ValueError(f"{path.name} schema mismatch")
        lowered = [field.lower() for field in reader.fieldnames]
        if any(fragment in field for field in lowered for fragment in FORBIDDEN_FRAGMENTS):
            raise ValueError(f"{path.name} contains prohibited outcome/replay fields")
        return list(reader)


def load_requests(path: Path, expected_count: int = 685) -> list[dict[str, str]]:
    rows = _read_csv(path, REQUEST_HEADER)
    if len(rows) != expected_count:
        raise ValueError(f"request count {len(rows)} != {expected_count}")
    ids = [row["request_id"] for row in rows]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate request_id detected")
    if any(
        row["request_schema_version"] != "1.0.0"
        or row["geometry_eligible"] != "true"
        or row["train_cutoff_compliant"] != "true"
        or row["deployment_authorized"] != "false"
        or float(row["minimum_rr"]) != 2.0
        for row in rows
    ):
        raise ValueError("frozen request boundary violation")
    ordering = [
        datetime.strptime(row["observation_time"], TIME_FORMAT) for row in rows
    ]
    if ordering != sorted(ordering):
        raise ValueError("request chronology/order violation")
    return rows


def validate_export(
    request_path: Path,
    export_path: Path,
    train_cutoff: datetime,
    expected_requests: int = 685,
    path_bars: int = 192,
) -> dict[str, Any]:
    requests = load_requests(request_path, expected_requests)
    exported = _read_csv(export_path, EXPORT_HEADER)
    expected_rows = expected_requests * path_bars
    if len(exported) != expected_rows:
        raise ValueError(f"export row count {len(exported)} != {expected_rows}")

    request_by_id = {row["request_id"]: row for row in requests}
    rows_by_id: dict[str, list[dict[str, str]]] = defaultdict(list)
    output_order: list[str] = []
    previous_id = ""
    for row in exported:
        request_id = row["request_id"]
        if request_id not in request_by_id:
            raise ValueError(f"unknown output request {request_id}")
        if request_id != previous_id:
            output_order.append(request_id)
            previous_id = request_id
        rows_by_id[request_id].append(row)

    request_order = [row["request_id"] for row in requests]
    if output_order != request_order:
        raise ValueError("request-to-output deterministic order mismatch")
    if set(rows_by_id) != set(request_by_id):
        raise ValueError("missing request output detected")

    for request_id in request_order:
        request = request_by_id[request_id]
        path = rows_by_id[request_id]
        if len(path) != path_bars:
            raise ValueError(f"{request_id} path count {len(path)} != {path_bars}")
        observation = datetime.strptime(request["observation_time"], TIME_FORMAT)
        seen_sequences: set[int] = set()
        previous_open: datetime | None = None
        expected_path_end = datetime.strptime(path[0]["path_end_exclusive"], TIME_FORMAT)
        for index, row in enumerate(path, start=1):
            sequence = int(row["sequence"])
            if sequence != index or sequence in seen_sequences:
                raise ValueError(f"{request_id} duplicate/non-contiguous sequence")
            seen_sequences.add(sequence)
            bar_open = datetime.strptime(row["bar_open"], TIME_FORMAT)
            if bar_open < observation or bar_open + timedelta(minutes=5) > train_cutoff:
                raise ValueError(f"{request_id} future/cutoff boundary violation")
            if previous_open is not None:
                delta = int((bar_open - previous_open).total_seconds())
                if delta <= 0 or delta % 300 != 0:
                    raise ValueError(f"{request_id} M5 chronology violation")
            previous_open = bar_open
            if (
                row["export_schema_version"] != "1.0.0"
                or row["base_opportunity_id"] != request["base_opportunity_id"]
                or row["source_record_id"] != request["source_record_id"]
                or row["arm_id"] != request["arm_id"]
                or row["observation_time"] != request["observation_time"]
                or row["symbol"] != request["symbol"]
                or row["direction"] != request["direction"]
                or row["entry_price"] != request["entry_price"]
                or row["stop_identity"] != request["stop_identity"]
                or row["stop_price"] != request["stop_price"]
                or row["target_identity"] != request["target_identity"]
                or row["target_price"] != request["target_price"]
                or row["minimum_rr"] != request["minimum_rr"]
                or row["common_support"] != request["common_support"]
                or row["source_sha256"] != request["source_sha256"]
                or row["closed_m5_only"] != "true"
                or row["deployment_authorized"] != "false"
                or datetime.strptime(row["path_end_exclusive"], TIME_FORMAT)
                != expected_path_end
            ):
                raise ValueError(f"{request_id} request/output mapping violation")
            open_price = float(row["open"])
            high = float(row["high"])
            low = float(row["low"])
            close = float(row["close"])
            if min(open_price, high, low, close) <= 0 or high < max(open_price, close) or low > min(open_price, close):
                raise ValueError(f"{request_id} invalid OHLC")
        if previous_open is None or expected_path_end != previous_open + timedelta(minutes=5):
            raise ValueError(f"{request_id} path end mismatch")

    return {
        "validation_schema_version": "1.0.0",
        "experiment_id": "IMP-100",
        "phase": "OUTCOME_FREE_M5_EXPORT_BOUNDARY",
        "status": "PASS",
        "request_count": expected_requests,
        "export_record_count": expected_rows,
        "path_bars_per_request": path_bars,
        "request_sha256": sha256_file(request_path),
        "export_sha256": sha256_file(export_path),
        "unique_request_mapping": True,
        "chronology_valid": True,
        "train_cutoff_preserved": True,
        "outcome_fields_present": False,
        "replay_executed": False,
        "deployment_authorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--requests", type=Path, required=True)
    parser.add_argument("--export", type=Path, required=True)
    parser.add_argument("--train-cutoff", default="2024.07.01 00:00")
    parser.add_argument("--expected-requests", type=int, default=685)
    parser.add_argument("--path-bars", type=int, default=192)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = validate_export(
        args.requests,
        args.export,
        datetime.strptime(args.train_cutoff, TIME_FORMAT),
        args.expected_requests,
        args.path_bars,
    )
    text = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
