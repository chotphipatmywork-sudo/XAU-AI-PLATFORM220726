"""Focused checks for current-feed lifecycle request construction."""

from __future__ import annotations

from datetime import datetime, timedelta

from build_current_feed_lifecycle_requests import build_requests


def main() -> None:
    start = datetime(2024, 6, 1)
    bars = [
        {
            "time": start + timedelta(minutes=15 * index),
            "high": 122.0,
            "low": 99.0,
        }
        for index in range(64)
    ]
    evidence = [{
        "observation": start,
        "symbol": "XAUUSD",
        "direction": "TRADE_SETUP_BUY",
        "entry": 100.0,
        "stop": 90.0,
        "cost_points": 0.0,
        "cost_known": True,
        "candidates": {"current_target": 121.0},
    }]
    requests, audit = build_requests(
        evidence, [row["time"] for row in bars], bars
    )
    if len(requests) != 1 or audit["requests"] != 1:
        raise AssertionError("Current-feed lifecycle request count changed")
    if requests[0]["baseline_outcome"] != "TARGET_FIRST":
        raise AssertionError("Current-feed lifecycle baseline changed")
    if requests[0]["deployment_authorized"] != "false":
        raise AssertionError("Current-feed lifecycle deployment lock changed")
    evidence[0]["candidates"]["current_target"] = 105.0
    rejected, rejected_audit = build_requests(
        [*evidence, {
            **evidence[0],
            "observation": start + timedelta(minutes=15),
            "candidates": {"current_target": 121.0},
        }],
        [row["time"] for row in bars],
        bars,
    )
    if len(rejected) != 1 or (
        rejected_audit["below_minimum_rr_or_invalid"] != 1
    ):
        raise AssertionError("Current-feed lifecycle RR lock changed")
    print("Current-feed lifecycle request focused test passed")


if __name__ == "__main__":
    main()
