"""Focused checks for current-feed Entry/Stop diagnostics."""

from __future__ import annotations

from datetime import datetime, timedelta

from diagnose_current_feed_entry_stop import build_diagnostic, fixed_bucket


def main() -> None:
    if fixed_bucket(0.5, (0.5, 1.0, 2.0)) != "0.50_1.00":
        raise AssertionError("Entry/Stop fixed bucket boundary changed")
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
        "direction": "TRADE_SETUP_BUY",
        "entry": 100.0,
        "stop": 90.0,
        "cost_known": True,
        "candidates": {"current_target": 121.0},
    }]
    setup = {
        start: {
            "reference_poi": "99.0",
            "reclaim_distance_atr": "0.1",
            "trigger_engulfment_atr": "0.5",
        }
    }
    report = build_diagnostic(
        evidence, setup, [row["time"] for row in bars], bars
    )
    if report["accounting"]["valid_geometry"] != 1:
        raise AssertionError("Entry/Stop valid geometry accounting changed")
    if report["overall"]["outcomes"].get("TARGET_FIRST") != 1:
        raise AssertionError("Entry/Stop path outcome changed")
    if report["entry_candidate_selected"] or report["stop_candidate_selected"]:
        raise AssertionError("Entry/Stop diagnostic selected a candidate")
    if report["deployment_authorized"]:
        raise AssertionError("Entry/Stop diagnostic authorized deployment")
    print("Current-feed Entry/Stop focused test passed")


if __name__ == "__main__":
    main()
