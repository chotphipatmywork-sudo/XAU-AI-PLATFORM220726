"""Focused checks for current-feed Stop replay accounting."""

from datetime import datetime, timedelta

from replay_current_feed_stops import replay_stop


def main() -> None:
    start = datetime(2024, 6, 1)
    bars = [{"time": start + timedelta(minutes=15 * index), "high": 121.0, "low": 99.0} for index in range(70)]
    times = [row["time"] for row in bars]
    evidence = [{
        "observation": start, "direction": "TRADE_SETUP_BUY", "entry": 100.0,
        "target": 121.0, "cost_points": 0.0, "cost_known": True,
        "minimum_rr": 2.0, "candidates": {"synthetic": 90.0},
    }]
    report = replay_stop(evidence, "synthetic", times, bars)
    if report["mature_records"] != 1 or report["outcomes"].get("TARGET_FIRST") != 1:
        raise AssertionError("Current-feed Stop replay changed a mature Target outcome")
    evidence[0]["candidates"]["synthetic"] = 80.0
    rejected = replay_stop(evidence, "synthetic", times, bars)
    if rejected["accounting"].get("below_minimum_rr") != 1:
        raise AssertionError("Current-feed Stop replay did not enforce minimum RR")
    print("Current-feed Stop replay focused test passed")


if __name__ == "__main__":
    main()
