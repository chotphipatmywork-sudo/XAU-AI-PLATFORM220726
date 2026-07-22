"""XAU AI PLATFORM | Offline Test | Version 1.0.0.

File: test_setup_v2_hypothesis_diagnostic.py
Purpose: Verify CR-014 directional projection, purge, stability, and NO-GO locks.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from analyze_shadow_run import FEATURE_COLUMNS
from diagnose_setup_v2_hypotheses import (
    directional,
    run_diagnostic,
)


def synthetic_samples(count: int = 300) -> list[dict[str, object]]:
    start = datetime(2025, 1, 1)
    rows: list[dict[str, object]] = []
    for index in range(count):
        observation = start + timedelta(hours=6 * index)
        target = index % 3 == 0
        direction = "TRADE_SETUP_BUY" if index % 2 == 0 else "TRADE_SETUP_SELL"
        directional_trend = [80.0, 80.0, 80.0] if target else [60.0, 85.0, 60.0]
        raw_trend = [
            value if direction == "TRADE_SETUP_BUY" else 100.0 - value
            for value in directional_trend
        ]
        feature_map = {column: 50.0 for column in FEATURE_COLUMNS}
        for column, value in zip(FEATURE_COLUMNS[:3], raw_trend):
            feature_map[column] = value
        feature_map["liquidity_sweep_direction"] = (
            100.0 if direction == "TRADE_SETUP_BUY" else 0.0
        ) if target else (
            0.0 if direction == "TRADE_SETUP_BUY" else 100.0
        )
        rows.append({
            "observation": observation,
            "known_at": observation + timedelta(hours=1),
            "direction": direction,
            "feature_map": feature_map,
            "features": [feature_map[column] for column in FEATURE_COLUMNS],
            "label": 1 if target else 0,
        })
    return rows


def main() -> None:
    if directional(82.0, "TRADE_SETUP_BUY") != 82.0:
        raise AssertionError("BUY directional projection changed")
    if directional(18.0, "TRADE_SETUP_SELL") != 82.0:
        raise AssertionError("SELL directional projection is not symmetric")

    insufficient = run_diagnostic(synthetic_samples(60))
    if insufficient["readiness"]["ready"] or insufficient["hypotheses"]:
        raise AssertionError("CR-014 diagnostic bypassed Train readiness")

    report = run_diagnostic(synthetic_samples())
    if report["fold_count"] != 4:
        raise AssertionError("CR-014 diagnostic did not retain four purged folds")
    by_name = {entry["name"]: entry for entry in report["hypotheses"]}
    positive = by_name["continuation_trend_coherent"]
    if not positive["eligible_to_request_stage_2_contract"]:
        raise AssertionError(f"Stable positive synthetic signal failed: {positive}")
    negative = by_name["trend_component_disagreement"]
    if not negative["eligible_to_request_stage_2_contract"]:
        raise AssertionError(f"Stable negative synthetic signal failed: {negative}")
    if "continuation_trend_coherent" not in report["stable_train_only_associations"]:
        raise AssertionError("Stable synthetic association was not summarized")
    if report["validation_dataset_used"] or report["test_dataset_used"]:
        raise AssertionError("CR-014 diagnostic used a sealed partition")
    if report["model_training_performed"]:
        raise AssertionError("CR-014 association diagnostic trained a model")
    if report["stage_2_contract_authorized"]:
        raise AssertionError("CR-014 diagnostic self-authorized Stage 2")
    if report["runtime_integration_authorized"] or report["deployment_authorized"]:
        raise AssertionError("CR-014 diagnostic authorized Runtime or deployment")

    print("CR-014 Setup V2 Train-only hypothesis diagnostic test passed")


if __name__ == "__main__":
    main()
