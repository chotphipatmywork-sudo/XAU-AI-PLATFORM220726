"""Focused checks for current-feed Target replay locks and accounting."""

from __future__ import annotations

from datetime import datetime, timedelta

from replay_current_feed_targets import replay_candidate


def main() -> None:
    start = datetime(2024, 6, 1)
    bars = [
        {
            "time": start + timedelta(minutes=15 * index),
            "high": 125.0,
            "low": 99.0,
        }
        for index in range(70)
    ]
    times = [row["time"] for row in bars]
    evidence = [{
        "observation": start,
        "direction": "TRADE_SETUP_BUY",
        "entry": 100.0,
        "stop": 90.0,
        "cost_points": 0.0,
        "cost_known": True,
        "minimum_rr": 2.0,
        "candidates": {"synthetic": 121.0},
    }]
    report = replay_candidate(evidence, "synthetic", times, bars)
    if report["mature_records"] != 1:
        raise AssertionError("Current-feed Target replay lost mature evidence")
    if report["outcomes"].get("TARGET_FIRST") != 1:
        raise AssertionError("Current-feed Target outcome replay changed")
    evidence[0]["cost_known"] = False
    unknown = replay_candidate(evidence, "synthetic", times, bars)
    if unknown["accounting"].get("unknown_cost") != 1:
        raise AssertionError("Current-feed Target unknown cost was not quarantined")
    print("Current-feed Target replay focused test passed")


if __name__ == "__main__":
    main()
