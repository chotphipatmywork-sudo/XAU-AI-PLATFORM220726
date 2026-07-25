"""Focused checks for the past-only structural Target request builder."""

from __future__ import annotations

import csv
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from build_setup_outcome_dataset import SETUP_AUDIT_COLUMNS_V1
from build_past_only_target_requests import (
    REQUEST_COLUMNS,
    build_requests_from_setup,
    write_requests,
)


def format_time(value: datetime) -> str:
    return value.strftime("%Y.%m.%d %H:%M")


def setup_row(observation: datetime, known: bool = True) -> dict[str, object]:
    row = {column: "" for column in SETUP_AUDIT_COLUMNS_V1}
    row.update({
        "observation_time": format_time(observation),
        "entry_bar_open": format_time(observation - timedelta(minutes=5)),
        "symbol": "XAUUSD",
        "direction": "TRADE_SETUP_BUY",
        "trigger_confirmed": "true",
        "nearest_target": 121.0,
        "structural_stop": 90.0,
        "plan_entry": 100.0 if known else 0.0,
        "plan_stop": 90.0 if known else 0.0,
        "plan_target": 121.0 if known else 0.0,
        "estimated_cost_points": 2.0 if known else 0.0,
        "minimum_rr": 2.0 if known else 0.0,
    })
    return row


def write_setup(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=SETUP_AUDIT_COLUMNS_V1)
        writer.writeheader()
        writer.writerows(rows)


def expect_value_error(action, message: str) -> None:
    try:
        action()
    except ValueError:
        return
    raise AssertionError(message)


def main() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        source = root / "setup.csv"
        output = root / "requests.csv"
        start = datetime(2025, 7, 10, 0, 15)
        excluded = start + timedelta(days=1)
        unknown = start + timedelta(days=2)
        cutoff = start + timedelta(days=3)
        rows = [
            setup_row(start, True),
            setup_row(excluded, True),
            setup_row(unknown, False),
            setup_row(cutoff, True),
        ]
        write_setup(source, rows)
        decisions = {
            start: {},
            excluded: {},
            unknown: {},
        }
        requests, audit = build_requests_from_setup(
            source,
            decisions,
            cutoff,
            frozenset({excluded.date()}),
            "synthetic",
            True,
        )
        if len(requests) != 2 or audit["quality_excluded_triggers"] != 1:
            raise AssertionError("Target request date-level exclusion failed")

        requests, audit = build_requests_from_setup(
            source,
            decisions,
            cutoff,
            frozenset(),
            "synthetic",
            True,
        )
        if len(requests) != 3 or not audit["cutoff_reached"]:
            raise AssertionError("Target request cutoff accounting failed")
        if requests[0]["entry_known"] != "true" or requests[2]["cost_known"] != "false":
            raise AssertionError("Target request missing-evidence flags changed")
        digest = write_requests(output, requests)
        if len(digest) != 64:
            raise AssertionError("Target request SHA-256 was not emitted")
        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if tuple(reader.fieldnames or ()) != REQUEST_COLUMNS:
                raise AssertionError("Target request output schema changed")

        malformed = rows[:]
        malformed[0] = dict(malformed[0])
        malformed[0]["entry_bar_open"] = format_time(start - timedelta(minutes=10))
        write_setup(source, malformed)
        expect_value_error(
            lambda: build_requests_from_setup(
                source, decisions, cutoff, frozenset(), "synthetic", True
            ),
            "Target request accepted a non-causal trigger bar",
        )

    print("Past-only structural Target request test passed")


if __name__ == "__main__":
    main()
