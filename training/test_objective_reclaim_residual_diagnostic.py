"""XAU AI PLATFORM | Offline Test | Version 1.0.0."""

from __future__ import annotations

from datetime import datetime, timedelta

from diagnose_objective_reclaim_residuals import run_diagnostic


def samples(count: int = 90) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    start = datetime(2025, 1, 1)
    for index in range(count):
        target = index % 3 == 0
        rows.append({
            "observation": start + timedelta(hours=index),
            "direction": "TRADE_SETUP_BUY" if index % 2 == 0 else "TRADE_SETUP_SELL",
            "features": {
                "trend_regime": 80.0, "trend_momentum": 80.0,
                "trend_slope": 80.0, "volatility_regime": 50.0,
                "volatility_change": 50.0,
                "liquidity_activity": 80.0 if target else 30.0,
                "liquidity_range_position": 50.0,
                "liquidity_sweep_direction": 50.0,
                "session_asia": 100.0, "session_london": 0.0,
                "session_new_york": 0.0, "session_progress": 20.0,
            },
            "plan_rr": 3.0,
            "target": target,
            "return_r": 3.0 if target else -1.0,
            "sweep_penetration_atr": 0.10,
            "reclaim_distance_atr": 0.25 if target else 0.11,
            "reclaim_to_sweep": 2.5 if target else 1.1,
        })
    return rows


def main() -> None:
    report = run_diagnostic(samples())
    if "stronger_reclaim" not in report["fresh_confirmation_priorities"]:
        raise AssertionError("Residual diagnostic missed synthetic reclaim priority")
    if "high_liquidity_activity" not in report["fresh_confirmation_priorities"]:
        raise AssertionError("Residual diagnostic missed synthetic liquidity priority")
    if report["validation_dataset_used"] or report["test_dataset_used"]:
        raise AssertionError("Residual diagnostic opened sealed evidence")
    if report["setup_contract_change_authorized"] or report["deployment_authorized"]:
        raise AssertionError("Residual diagnostic authorized a protected change")
    print("Objective reclaim residual diagnostic test passed")


if __name__ == "__main__":
    main()
