"""XAU AI PLATFORM | Offline Test | Version 1.0.0.

File: test_setup_v2_session_confirmation.py
Purpose: Verify CR-014 Stage 1B cutoff, readiness, stability, and NO-GO locks.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from analyze_shadow_run import FEATURE_COLUMNS
from confirm_setup_v2_session_hypotheses import (
    FRESH_PERIOD_AFTER,
    run_confirmation,
    validate_confirmation_filename,
)


def synthetic_samples(count: int = 120, fresh: bool = True) -> list[dict[str, object]]:
    start = (
        FRESH_PERIOD_AFTER + timedelta(days=1)
        if fresh
        else datetime(2025, 1, 1)
    )
    rows: list[dict[str, object]] = []
    for index in range(count):
        observation = start + timedelta(hours=6 * index)
        phase = (25.0, 50.0, 75.0)[index % 3]
        target = phase == 25.0
        feature_map = {column: 50.0 for column in FEATURE_COLUMNS}
        feature_map["session_progress"] = phase
        feature_map["session_asia"] = 100.0
        rows.append({
            "observation": observation,
            "known_at": observation + timedelta(hours=1),
            "direction": (
                "TRADE_SETUP_BUY" if index % 2 == 0 else "TRADE_SETUP_SELL"
            ),
            "feature_map": feature_map,
            "features": [feature_map[column] for column in FEATURE_COLUMNS],
            "label": 1 if target else 0,
        })
    return rows


def main() -> None:
    validate_confirmation_filename(Path("XAU_AI_SETUP_OUTCOME_CONFIRMATION.csv"))
    try:
        validate_confirmation_filename(Path("XAU_AI_SETUP_OUTCOME_VALIDATION.csv"))
    except ValueError:
        pass
    else:
        raise AssertionError("CR-014 confirmation accepted a sealed filename")

    try:
        run_confirmation(synthetic_samples(fresh=False))
    except ValueError:
        pass
    else:
        raise AssertionError("CR-014 confirmation accepted pre-cutoff evidence")

    insufficient = run_confirmation(synthetic_samples(count=60))
    if insufficient["readiness"]["ready"] or insufficient["hypotheses"]:
        raise AssertionError("CR-014 confirmation bypassed fresh readiness")

    report = run_confirmation(synthetic_samples())
    expected = {
        "session_early_phase_positive",
        "session_late_phase_negative",
    }
    if set(report["confirmed_hypotheses"]) != expected:
        raise AssertionError(f"Frozen Session hypotheses failed: {report}")
    if not report["confirmation_gate_met"]:
        raise AssertionError("CR-014 fresh confirmation gate did not pass")
    if report["validation_dataset_used"] or report["test_dataset_used"]:
        raise AssertionError("CR-014 fresh confirmation used a sealed partition")
    if report["model_training_performed"]:
        raise AssertionError("CR-014 fresh confirmation trained a model")
    if report["stage_2_contract_authorized"]:
        raise AssertionError("CR-014 confirmation self-authorized Stage 2")
    if report["runtime_integration_authorized"] or report["deployment_authorized"]:
        raise AssertionError("CR-014 confirmation authorized Runtime or deployment")

    print("CR-014 Setup V2 fresh Session confirmation test passed")


if __name__ == "__main__":
    main()
