#!/usr/bin/env python3
"""Focused deterministic tests for IMP-100 causal M5 replay."""

from __future__ import annotations

from datetime import datetime, timedelta

from execute_imp100_causal_m5_replay import (
    TIME_FORMAT,
    derive_cost_points,
    replay_path,
    stressed_target_r,
)


def request(direction: str = "TRADE_SETUP_BUY") -> dict[str, str]:
    return {
        "request_id": "imp100__control__example",
        "base_opportunity_id": "example",
        "source_record_id": "example",
        "arm_id": "CONTROL",
        "direction": direction,
        "stop_price": "99" if direction == "TRADE_SETUP_BUY" else "101",
        "target_price": "103" if direction == "TRADE_SETUP_BUY" else "97",
    }


def raw() -> dict[str, str]:
    return {
        "stop_distance_points": "100",
        "target_distance_points": "300",
        "cost_adjusted_rr": "2",
    }


def bars(high: float = 100.5, low: float = 99.5) -> list[dict[str, str]]:
    start = datetime(2024, 1, 2)
    return [
        {
            "bar_open": (start + timedelta(minutes=5 * index)).strftime(TIME_FORMAT),
            "high": str(high),
            "low": str(low),
            "close": "100",
        }
        for index in range(192)
    ]


def main() -> int:
    target_path = bars()
    target_path[0]["high"] = "103"
    assert replay_path(request(), target_path, raw())["exit_reason"] == "TARGET_HIT"

    stop_path = bars()
    stop_path[0]["low"] = "99"
    assert replay_path(request(), stop_path, raw())["exit_reason"] == "STOP_HIT"

    collision_path = bars()
    collision_path[0]["high"] = "103"
    collision_path[0]["low"] = "99"
    collision = replay_path(request(), collision_path, raw())
    assert collision["exit_reason"] == "SAME_BAR_COLLISION"
    assert collision["quarantine_flag"] == "true"
    assert collision["realized_R"] == ""

    timeout = replay_path(request(), bars(), raw())
    assert timeout["exit_reason"] == "TIMEOUT"
    assert timeout["holding_bars"] == "192"
    assert timeout["realized_R"] == "0"

    assert abs(derive_cost_points(raw()) - (100 / 3)) < 1e-9
    assert stressed_target_r(raw(), 1.0) == 2.0
    assert stressed_target_r(raw(), 1.5) < 2.0
    print("IMP-100 causal M5 replay focused test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
