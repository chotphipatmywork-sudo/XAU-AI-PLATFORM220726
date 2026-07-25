"""Focused contract checks for IMP-096 M5 request selection."""

from datetime import datetime, timedelta

from build_current_feed_joint_m5_requests import build


def main() -> None:
    start = datetime(2024, 6, 1)
    bars = [{"time": start + timedelta(minutes=15 * i), "high": 121.0, "low": 99.0} for i in range(70)]
    common = {
        "direction": "TRADE_SETUP_BUY", "entry": 100.0, "cost_points": 0.0,
        "cost_known": True, "minimum_rr": 2.0,
        "stops": {"m5_stop_2": 90.0}, "targets": {"m15_target_1": 121.0},
    }
    evidence = [{**common, "observation": start + timedelta(seconds=i)} for i in range(76)]
    # Use distinct seconds only for the focused count contract; production
    # evidence remains exact M15 chronology.
    rows = build(evidence, [bar["time"] for bar in bars], bars)
    if len(rows) != 76 or any(row["deployment_authorized"] != "false" for row in rows):
        raise AssertionError("Joint M5 request lock changed")
    print("Current-feed joint M5 request focused test passed")


if __name__ == "__main__":
    main()
