"""Focused deterministic checks for the IMP-097 RR rejection analyzer."""

from datetime import datetime

from analyze_current_feed_rr_rejections import (
    build_records,
    factor_analysis,
    numeric_summary,
)


def evidence_row(
    request_id: str,
    raw_target: float,
    cost_points: float,
) -> dict:
    return {
        "request_id": request_id,
        "observation": datetime(2024, 6, 1, 12, 0),
        "direction": "TRADE_SETUP_BUY",
        "entry": 100.0,
        "cost_points": cost_points,
        "cost_known": True,
        "minimum_rr": 2.0,
        "stops": {"m5_stop_2": 90.0},
        "targets": {"m15_target_1": raw_target},
    }


def main() -> None:
    observation = datetime(2024, 6, 1, 12, 0)
    context = {
        observation: {
            "bar_close": 101.0,
            "atr": 5.0,
            "trend_regime": 80.0,
            "volatility_regime": 50.0,
            "session_asia": 0.0,
            "session_london": 100.0,
            "session_new_york": 0.0,
        }
    }
    records, accounting = build_records(
        [
            evidence_row("raw_below", 119.0, 0.0),
            evidence_row("cost_eroded", 121.0, 40.0),
            evidence_row("accepted", 121.0, 0.0),
        ],
        context,
    )
    causes = {row["request_id"]: row["rejection_cause"] for row in records}
    if causes["raw_below"] != "STRUCTURAL_RAW_RR_BELOW_MINIMUM":
        raise AssertionError("IMP-097 raw-RR rejection attribution changed")
    if causes["cost_eroded"] != "COST_EROSION_BELOW_MINIMUM":
        raise AssertionError("IMP-097 cost-erosion attribution changed")
    if causes["accepted"] != "NOT_REJECTED":
        raise AssertionError("IMP-097 accepted geometry attribution changed")
    if accounting["below_minimum_rr"] != 2:
        raise AssertionError("IMP-097 rejection accounting changed")
    summary = numeric_summary([1.0, 2.0, 3.0])
    if summary["median"] != 2.0 or summary["mean"] != 2.0:
        raise AssertionError("IMP-097 numeric summary changed")
    factors, comparisons = factor_analysis(records, ("direction",))
    if len(factors["direction"]) != 1 or len(comparisons) != 1:
        raise AssertionError("IMP-097 factor accounting changed")
    print("IMP-097 RR rejection focused test passed")


if __name__ == "__main__":
    main()
