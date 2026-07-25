"""Focused checks for the Train-only past-only Target replay."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta

from replay_past_only_targets import (
    geometry_and_rr,
    quality_dates_between,
    summarize_candidate,
)


def main() -> None:
    valid, rr = geometry_and_rr(
        "TRADE_SETUP_BUY", 100.0, 90.0, 121.0, 2.0
    )
    if not valid or rr is None or not 2.0 < rr < 2.1:
        raise AssertionError("Past-only Target cost-aware BUY RR changed")
    invalid, missing = geometry_and_rr(
        "TRADE_SETUP_SELL", 100.0, 90.0, 80.0, 2.0
    )
    if invalid or missing is not None:
        raise AssertionError("Past-only Target accepted invalid SELL geometry")

    start = datetime(2025, 7, 10, 23, 45)
    end = start + timedelta(minutes=30)
    if quality_dates_between(start, end) != {
        datetime(2025, 7, 10).date(), datetime(2025, 7, 11).date()
    }:
        raise AssertionError("Past-only Target quality-date span changed")

    outcomes = []
    for index in range(200):
        outcomes.append({
            "observation": start + timedelta(minutes=15 * index),
            "direction": (
                "TRADE_SETUP_BUY" if index % 2 == 0 else "TRADE_SETUP_SELL"
            ),
            "outcome": "TARGET_FIRST",
            "plan_rr": 2.0,
            "realized_r": 2.0,
        })
    passed = summarize_candidate(
        "synthetic", [{}] * 200, Counter({"minimum_rr_reached": 200}), outcomes
    )
    if not passed["train_gate_passed"]:
        raise AssertionError("Past-only Target positive stable gate failed")
    outcomes[0]["outcome"] = "STOP_FIRST"
    outcomes[0]["realized_r"] = -1000.0
    failed = summarize_candidate(
        "synthetic", [{}] * 200, Counter({"minimum_rr_reached": 200}), outcomes
    )
    if failed["train_gate_passed"]:
        raise AssertionError("Past-only Target negative block escaped gate")

    print("Past-only structural Target replay test passed")


if __name__ == "__main__":
    main()

