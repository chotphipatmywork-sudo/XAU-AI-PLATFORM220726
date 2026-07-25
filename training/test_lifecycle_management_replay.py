"""Focused checks for causal M5 lifecycle-management replay."""

from __future__ import annotations

import math

from replay_lifecycle_management import simulate_path


def request(target: float = 120.0) -> dict:
    return {
        "direction": "TRADE_SETUP_BUY",
        "entry": 100.0,
        "initial_stop": 90.0,
        "target": target,
        "estimated_cost_points": 0.0,
        "point_size": 0.01,
    }


def bar(open_price: float, high: float, low: float, close: float) -> dict:
    return {"open": open_price, "high": high, "low": low, "close": close}


def main() -> None:
    giveback = [
        bar(100.0, 111.0, 99.0, 110.0),
        bar(110.0, 111.0, 99.0, 100.0),
        bar(100.0, 101.0, 89.0, 90.0),
    ]
    baseline = simulate_path(request(), giveback, "CURRENT_BASELINE", 1.0)
    breakeven = simulate_path(
        request(), giveback, "COST_COVERED_BREAKEVEN_AFTER_CLOSE_1R", 1.0
    )
    if baseline["outcome"] != "STOP_FIRST" or baseline["realized_r"] != -1.0:
        raise AssertionError("Lifecycle baseline giveback changed")
    if breakeven["outcome"] != "MANAGED_STOP" or breakeven["realized_r"] != 0.0:
        raise AssertionError("Lifecycle cost-covered Breakeven changed")

    ratchet_path = [
        bar(100.0, 111.0, 99.0, 110.0),
        bar(110.0, 121.0, 109.0, 120.0),
        bar(120.0, 121.0, 109.0, 110.0),
    ]
    ratchet = simulate_path(
        request(130.0), ratchet_path,
        "TWO_STAGE_RATCHET_AFTER_CLOSE_1R_2R", 1.0,
    )
    if ratchet["outcome"] != "MANAGED_STOP" or ratchet["realized_r"] != 1.0:
        raise AssertionError("Lifecycle two-stage Ratchet changed")

    collision = [
        bar(100.0, 111.0, 99.0, 110.0),
        bar(110.0, 121.0, 99.0, 110.0),
    ]
    ambiguous = simulate_path(
        request(), collision, "COST_COVERED_BREAKEVEN_AFTER_CLOSE_1R", 1.0
    )
    if ambiguous["outcome"] != "AMBIGUOUS" or ambiguous["realized_r"] is not None:
        raise AssertionError("Lifecycle same-M5 collision escaped quarantine")

    stressed = simulate_path(
        {**request(), "estimated_cost_points": 10.0},
        giveback,
        "COST_COVERED_BREAKEVEN_AFTER_CLOSE_1R",
        1.5,
    )
    if not math.isclose(stressed["realized_r"], 0.0, abs_tol=1e-12):
        raise AssertionError("Lifecycle cost-covered stop failed stress parity")

    print("Lifecycle management M5 replay test passed")


if __name__ == "__main__":
    main()
