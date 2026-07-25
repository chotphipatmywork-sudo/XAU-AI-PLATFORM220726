"""Focused checks for the Train-only structural opportunity diagnostic."""

from __future__ import annotations

import csv
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from analyze_shadow_run import DECISION_COLUMNS, FEATURE_COLUMNS
from build_setup_outcome_dataset import (
    FEATURE_SCHEMA_VERSION,
    OBJECTIVE_MODEL_STATUS,
    OBJECTIVE_PROVIDER,
    OUTCOME_AUDIT_COLUMNS,
    SETUP_AUDIT_COLUMNS_V1,
    SETUP_OUTCOME_SCHEMA_VERSION,
)
from diagnose_structural_opportunity import (
    build_report,
    read_augmented_train,
    read_decision_context,
    read_trigger_samples,
)


def format_seconds(value: datetime) -> str:
    return value.strftime("%Y.%m.%d %H:%M:%S")


def format_minutes(value: datetime) -> str:
    return value.strftime("%Y.%m.%d %H:%M")


def write_csv(
    path: Path, columns: tuple[str, ...], rows: list[dict[str, object]]
) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def decision_row(observation: datetime, progress: float = 50.0) -> dict[str, object]:
    row = {column: "" for column in DECISION_COLUMNS}
    row.update({
        "recorded_at": format_seconds(observation),
        "closed_bar": format_minutes(observation - timedelta(minutes=15)),
        "symbol": "XAUUSD",
        "timeframe": "PERIOD_M15",
        "feature_schema_version": FEATURE_SCHEMA_VERSION,
        "inference_provider": OBJECTIVE_PROVIDER,
        "model_status": OBJECTIVE_MODEL_STATUS,
        "model_deployment_authorized": "false",
        "bar_open": 100.0,
        "bar_high": 101.0,
        "bar_low": 99.0,
        "bar_close": 100.0,
        "atr": 5.0,
        "session_progress": progress,
        "ai_action": "AI_ACTION_HOLD",
        "ai_confidence": 0.0,
        "decision": "DECISION_WAIT",
        "risk_valid": "true",
        "risk_allowed": "false",
        "risk_score": 0.0,
        "risk_message": "Synthetic Risk rejection.",
        "execution_success": "false",
        "execution_status": "EXECUTION_REJECTED",
        "execution_message": "Synthetic execution rejection.",
        "synthetic_ticket": 0,
    })
    for feature in FEATURE_COLUMNS:
        if row[feature] == "":
            row[feature] = 50.0
    for legacy in (
        "legacy_trend_score", "legacy_volatility_score",
        "legacy_liquidity_score", "legacy_session_score",
    ):
        row[legacy] = 50.0
    return row


def setup_row(
    observation: datetime,
    disposition: str,
    entry: float = 100.0,
    stop: float = 90.0,
    target: float = 121.0,
) -> dict[str, object]:
    row = {column: "" for column in SETUP_AUDIT_COLUMNS_V1}
    cost_points = 2.0
    plan_rr = ((target - entry) - cost_points * 0.01) / (
        (entry - stop) + cost_points * 0.01
    )
    plan_available = disposition == "accepted_plan"
    if disposition == "accepted_plan":
        reason = "Structure-aware Trade Plan accepted; Risk approval remains required."
    elif disposition == "below_minimum_rr":
        reason = "Trade Plan rejected: nearest structural Target is below minimum RR."
    elif disposition == "invalid_geometry":
        reason = "Setup structural Stop or Target geometry is invalid."
        entry = stop = target = plan_rr = 0.0
    else:
        reason = "Synthetic fail-closed disposition."
        entry = stop = target = plan_rr = 0.0
    row.update({
        "recorded_at": format_seconds(observation),
        "observation_time": format_minutes(observation),
        "symbol": "XAUUSD",
        "higher_bar_open": format_minutes(observation - timedelta(minutes=15)),
        "entry_bar_open": format_minutes(observation - timedelta(minutes=5)),
        "direction": "TRADE_SETUP_BUY",
        "poi_confirmed": "true",
        "trigger_confirmed": "true",
        "reference_poi": 99.0,
        "nearest_target": target,
        "structural_stop": stop,
        "sweep_penetration_atr": 0.2,
        "reclaim_distance_atr": 0.2,
        "plan_available": str(plan_available).lower(),
        "plan_entry": entry,
        "plan_stop": stop,
        "plan_target": target,
        "plan_rr": plan_rr,
        "minimum_rr": 2.0 if disposition in {"accepted_plan", "below_minimum_rr"} else 0.0,
        "estimated_cost_points": cost_points if disposition in {"accepted_plan", "below_minimum_rr"} else 0.0,
        "setup_reason": reason,
        "ai_action": "AI_ACTION_BUY" if plan_available else "AI_ACTION_HOLD",
        "ai_confidence": 50.0 if plan_available else 0.0,
        "risk_valid": "true",
        "risk_allowed": "false",
        "risk_message": "Synthetic Risk rejection.",
        "execution_success": "false",
        "execution_message": "Synthetic execution rejection.",
        "synthetic_ticket": 0,
    })
    return row


def outcome_row(
    observation: datetime, outcome: str, plan_rr: float
) -> dict[str, object]:
    row = {column: "" for column in OUTCOME_AUDIT_COLUMNS}
    row.update({
        "setup_outcome_schema_version": SETUP_OUTCOME_SCHEMA_VERSION,
        "feature_schema_version": FEATURE_SCHEMA_VERSION,
        "observation_time": format_minutes(observation),
        "outcome_known_at": format_minutes(observation + timedelta(minutes=15)),
        "symbol": "XAUUSD",
        "timeframe": "PERIOD_M15",
        "direction": "TRADE_SETUP_BUY",
        "plan_entry": 100.0,
        "plan_stop": 90.0,
        "plan_target": 121.0,
        "plan_rr": plan_rr,
        "minimum_rr": 2.0,
        "estimated_cost_points": 2.0,
        "point_size": 0.01,
        "risk_points": 1000.0,
        "bars_observed": 1,
        "outcome": outcome,
        "trainable": "true",
        "mfe_points": 100.0,
        "mae_points": 100.0,
        "mfe_r": 0.1,
        "mae_r": 0.1,
        "realized_r": plan_rr if outcome == "TARGET_FIRST" else -1.0,
    })
    for feature in FEATURE_COLUMNS:
        row[feature] = 50.0
    return row


def expect_value_error(action, message: str) -> None:
    try:
        action()
    except ValueError:
        return
    raise AssertionError(message)


def main() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        decisions_path = root / "decisions.csv"
        setup_path = root / "setup.csv"
        train_path = root / "XAU_AI_SETUP_OUTCOME_AUGMENTED_TRAIN.csv"
        start = datetime(2025, 7, 10, 0, 15)
        cutoff = datetime(2025, 7, 12, 0, 0)
        observations = [
            start,
            start + timedelta(minutes=15),
            start + timedelta(minutes=30),
            start + timedelta(minutes=45),
            datetime(2025, 7, 11, 0, 15),
        ]
        decisions = [
            decision_row(observations[0], 10.0),
            decision_row(observations[1], 40.0),
            decision_row(observations[2], 80.0),
            decision_row(observations[3], 50.0),
            decision_row(observations[4], 20.0),
            decision_row(cutoff, 101.0),
        ]
        setups = [
            setup_row(observations[0], "accepted_plan"),
            setup_row(observations[1], "below_minimum_rr", target=108.0),
            setup_row(observations[2], "invalid_geometry"),
            setup_row(observations[3], "other_fail_closed"),
            setup_row(observations[4], "accepted_plan"),
            setup_row(cutoff, "accepted_plan"),
        ]
        write_csv(decisions_path, DECISION_COLUMNS, decisions)
        write_csv(setup_path, SETUP_AUDIT_COLUMNS_V1, setups)

        exclusions = frozenset({observations[4].date()})
        contexts, decision_audit = read_decision_context(
            decisions_path, cutoff, exclusions, True
        )
        samples, source_audit = read_trigger_samples(
            setup_path, contexts, cutoff, exclusions, "synthetic", True
        )
        if len(samples) != 4 or source_audit["quality_excluded_triggers"] != 1:
            raise AssertionError("Structural opportunity exclusion/cutoff failed")
        dispositions = {sample["disposition"] for sample in samples}
        if dispositions != {
            "accepted_plan", "below_minimum_rr", "invalid_geometry",
            "other_fail_closed",
        }:
            raise AssertionError("Structural opportunity dispositions changed")
        if not decision_audit["cutoff_reached"] or not source_audit["cutoff_reached"]:
            raise AssertionError("Structural opportunity did not enforce cutoff")

        write_csv(train_path, OUTCOME_AUDIT_COLUMNS, [
            outcome_row(observations[0], "TARGET_FIRST", 2.1),
            outcome_row(observations[1], "STOP_FIRST", 2.1),
        ])
        outcome_baseline = read_augmented_train(train_path)
        report = build_report(
            samples,
            {"synthetic": source_audit},
            {"synthetic": decision_audit},
            outcome_baseline,
            {"synthetic": "FROZEN"},
        )
        combined = report["combined_trigger_geometry"]
        if combined["triggers"] != 4 or combined["rr_bands"]["below_1r"] != 1:
            raise AssertionError("Structural opportunity RR accounting failed")
        if combined["rr_bands"]["at_least_2r"] != 1:
            raise AssertionError("Structural opportunity accepted-plan accounting failed")
        if report["runtime_candidate_ready"] or report["deployment_authorized"]:
            raise AssertionError("Structural opportunity escaped NO-GO")
        if outcome_baseline["overall"]["mean_cost_aware_r"] != 0.55:
            raise AssertionError("Structural opportunity outcome baseline changed")

        invalid_schema = root / "invalid_setup.csv"
        write_csv(invalid_schema, SETUP_AUDIT_COLUMNS_V1[:-1], [
            {key: setups[0][key] for key in SETUP_AUDIT_COLUMNS_V1[:-1]}
        ])
        expect_value_error(
            lambda: read_trigger_samples(
                invalid_schema, contexts, cutoff, exclusions, "synthetic", False
            ),
            "Structural opportunity accepted an invalid Setup schema",
        )

    print("Structural opportunity Train-only diagnostic test passed")


if __name__ == "__main__":
    main()
