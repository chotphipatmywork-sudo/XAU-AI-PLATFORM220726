"""Focused checks for joint Stop/Target geometry replay."""

from datetime import datetime, timedelta

from analyze_current_feed_joint_geometry import join_evidence, replay_combination


def main() -> None:
    start = datetime(2024, 6, 1)
    common = {"request_id": "one", "observation": start, "direction": "TRADE_SETUP_BUY", "entry": 100.0, "cost_points": 0.0, "cost_known": True, "minimum_rr": 2.0}
    stops = [{**common, "candidates": {"s": 90.0}}]
    targets = [{**common, "candidates": {"t": 121.0}}]
    evidence = join_evidence(stops, targets)
    bars = [{"time": start + timedelta(minutes=15 * index), "high": 121.0, "low": 99.0} for index in range(70)]
    report = replay_combination(evidence, "s", "t", [row["time"] for row in bars], bars)
    if report["mature_records"] != 1 or report["outcomes"].get("TARGET_FIRST") != 1:
        raise AssertionError("Joint frontier valid outcome changed")
    targets[0]["entry"] = 100.01
    try:
        join_evidence(stops, targets)
    except ValueError:
        pass
    else:
        raise AssertionError("Joint frontier accepted Entry drift")
    print("Current-feed joint-geometry focused test passed")


if __name__ == "__main__":
    main()
