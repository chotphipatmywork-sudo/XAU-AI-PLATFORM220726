"""Focused checks for the isolated Stage D Setup Outcome Dataset builder."""

from __future__ import annotations

import csv
import tempfile
from datetime import date, datetime, timedelta
from pathlib import Path

from analyze_shadow_run import DECISION_COLUMNS, FEATURE_COLUMNS
from build_setup_outcome_dataset import (
    FEATURE_SCHEMA_VERSION,
    MAX_DECISION_LAG_SECONDS,
    MAX_HOLDING_BARS,
    OBJECTIVE_MODEL_STATUS,
    OBJECTIVE_PROVIDER,
    SETUP_AUDIT_COLUMNS,
    build_dataset,
)


def format_seconds(value: datetime) -> str:
    return value.strftime("%Y.%m.%d %H:%M:%S")


def format_minutes(value: datetime) -> str:
    return value.strftime("%Y.%m.%d %H:%M")


def write_csv(path: Path, columns: tuple[str, ...], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def decision_rows(start: datetime, count: int) -> list[dict[str, object]]:
    special_bars = {
        start + timedelta(minutes=15): (100.0, 121.5, 99.0, 105.0),
        start + timedelta(minutes=30): (200.0, 211.0, 199.0, 205.0),
        start + timedelta(minutes=60): (400.0, 422.0, 389.0, 400.0),
    }
    rows: list[dict[str, object]] = []
    for index in range(count):
        recorded = start + timedelta(minutes=15 * index)
        closed = recorded - timedelta(minutes=15)
        bar_open, bar_high, bar_low, bar_close = special_bars.get(
            closed, (1000.0, 1001.0, 999.0, 1000.0)
        )
        row = {column: "" for column in DECISION_COLUMNS}
        row.update({
            "recorded_at": format_seconds(recorded),
            "closed_bar": format_minutes(closed),
            "symbol": "XAUUSD",
            "timeframe": "PERIOD_M15",
            "feature_schema_version": FEATURE_SCHEMA_VERSION,
            "inference_provider": OBJECTIVE_PROVIDER,
            "model_status": OBJECTIVE_MODEL_STATUS,
            "model_deployment_authorized": "false",
            "bar_open": bar_open,
            "bar_high": bar_high,
            "bar_low": bar_low,
            "bar_close": bar_close,
            "atr": 5.0,
            "ai_action": "AI_ACTION_HOLD",
            "ai_confidence": 0.0,
            "decision": "DECISION_WAIT",
            "risk_valid": "true",
            "risk_allowed": "false",
            "risk_score": 0.0,
            "risk_message": "Risk rejected a non-actionable Decision.",
            "execution_success": "false",
            "execution_status": "EXECUTION_REJECTED",
            "execution_message": "Shadow execution requires explicit Risk approval.",
            "synthetic_ticket": 0,
        })
        for feature_index, feature in enumerate(FEATURE_COLUMNS):
            row[feature] = 40.0 + feature_index
        for legacy in (
            "legacy_trend_score", "legacy_volatility_score",
            "legacy_liquidity_score", "legacy_session_score",
        ):
            row[legacy] = 50.0
        rows.append(row)
    return rows


def plan_row(
    observation: datetime,
    direction: str,
    entry: float,
    stop: float,
    target: float,
) -> dict[str, object]:
    cost_points = 2.0
    cost_price = cost_points * 0.01
    plan_rr = (abs(target - entry) - cost_price) / (
        abs(entry - stop) + cost_price
    )
    row = {column: "" for column in SETUP_AUDIT_COLUMNS}
    row.update({
        "recorded_at": format_seconds(observation),
        "observation_time": format_minutes(observation),
        "symbol": "XAUUSD",
        "higher_bar_open": format_minutes(observation - timedelta(minutes=15)),
        "entry_bar_open": format_minutes(observation - timedelta(minutes=5)),
        "direction": direction,
        "poi_confirmed": "true",
        "trigger_confirmed": "true",
        "reference_poi": entry,
        "nearest_target": target,
        "structural_stop": stop,
        "sweep_penetration_atr": 0.2,
        "reclaim_distance_atr": 0.2,
        "plan_available": "true",
        "plan_entry": entry,
        "plan_stop": stop,
        "plan_target": target,
        "plan_rr": plan_rr,
        "minimum_rr": 2.0,
        "estimated_cost_points": cost_points,
        "setup_reason": "Structure-aware Trade Plan accepted; Risk approval remains required.",
        "ai_action": "AI_ACTION_BUY" if direction == "TRADE_SETUP_BUY" else "AI_ACTION_SELL",
        "ai_confidence": 50.0,
        "risk_valid": "true",
        "risk_allowed": "false",
        "risk_message": "Risk blocked for synthetic test.",
        "execution_success": "false",
        "execution_message": "No synthetic execution.",
        "synthetic_ticket": 0,
    })
    return row


def expect_failure(setup_path: Path, decisions_path: Path, message: str) -> None:
    try:
        build_dataset(setup_path, decisions_path)
    except ValueError:
        return
    raise AssertionError(message)


def main() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        setup_path = root / "setup.csv"
        decisions_path = root / "decisions.csv"
        start = datetime(2026, 7, 1, 0, 0)
        decisions = decision_rows(start, 76)
        setups = [
            plan_row(start + timedelta(minutes=15), "TRADE_SETUP_BUY", 100.0, 90.0, 121.0),
            plan_row(start + timedelta(minutes=30), "TRADE_SETUP_SELL", 200.0, 210.0, 179.0),
            plan_row(start + timedelta(minutes=45), "TRADE_SETUP_BUY", 1000.0, 0.0, 3101.0),
            plan_row(start + timedelta(minutes=60), "TRADE_SETUP_BUY", 400.0, 390.0, 421.0),
            plan_row(start + timedelta(minutes=15 * 75), "TRADE_SETUP_BUY", 1000.0, 0.0, 3101.0),
        ]
        write_csv(decisions_path, DECISION_COLUMNS, decisions)
        write_csv(setup_path, SETUP_AUDIT_COLUMNS, setups)
        rows, summary = build_dataset(setup_path, decisions_path)
        outcomes = [row["outcome"] for row in rows]
        expected = [
            "TARGET_FIRST", "STOP_FIRST", "TIMEOUT", "AMBIGUOUS", "UNMATURED"
        ]
        if outcomes != expected:
            raise AssertionError(f"Unexpected Setup outcomes: {outcomes}")
        if summary["trainable_rows"] != 3 or summary["ready_for_train_split"]:
            raise AssertionError(f"Unexpected Stage D readiness: {summary}")
        if rows[2]["bars_observed"] != MAX_HOLDING_BARS:
            raise AssertionError("TIMEOUT did not observe the frozen 64-bar horizon")
        if rows[3]["trainable"] != "false" or rows[4]["trainable"] != "false":
            raise AssertionError("Ambiguous or unmatured Setup entered the training set")

        quality_rows, quality_summary = build_dataset(
            setup_path,
            decisions_path,
            excluded_dates=frozenset({date(2026, 7, 2)}),
        )
        if len(quality_rows) != 4:
            raise AssertionError("Source-quality exclusion did not quarantine one plan")
        if quality_summary["source_quality_excluded_plans"] != 1:
            raise AssertionError("Source-quality exclusion was not audited")

        delayed_decisions = [dict(row) for row in decisions]
        delayed_decisions[1]["recorded_at"] = format_seconds(
            start + timedelta(minutes=15, seconds=1)
        )
        delayed_decisions[2]["recorded_at"] = format_seconds(
            start + timedelta(minutes=30, seconds=MAX_DECISION_LAG_SECONDS)
        )
        write_csv(decisions_path, DECISION_COLUMNS, delayed_decisions)
        delayed_rows, _ = build_dataset(setup_path, decisions_path)
        if [row["outcome"] for row in delayed_rows] != expected:
            raise AssertionError("Fresh first-tick delay changed canonical Setup outcomes")

        stale_decisions = [dict(row) for row in decisions]
        stale_decisions[1]["recorded_at"] = format_seconds(
            start + timedelta(
                minutes=15, seconds=MAX_DECISION_LAG_SECONDS + 1
            )
        )
        write_csv(decisions_path, DECISION_COLUMNS, stale_decisions)
        expect_failure(setup_path, decisions_path, "Stale Decision timestamp was accepted")

        early_decisions = [dict(row) for row in decisions]
        early_decisions[1]["recorded_at"] = format_seconds(
            start + timedelta(minutes=15, seconds=-1)
        )
        write_csv(decisions_path, DECISION_COLUMNS, early_decisions)
        expect_failure(setup_path, decisions_path, "Early Decision timestamp was accepted")

        invalid_decisions = [dict(row) for row in decisions]
        invalid_decisions[1][FEATURE_COLUMNS[0]] = 101.0
        write_csv(decisions_path, DECISION_COLUMNS, invalid_decisions)
        expect_failure(setup_path, decisions_path, "Out-of-range feature was accepted")

        write_csv(decisions_path, DECISION_COLUMNS, decisions)
        write_csv(setup_path, SETUP_AUDIT_COLUMNS, setups + [dict(setups[0])])
        expect_failure(setup_path, decisions_path, "Duplicate Setup observation was accepted")

        invalid_plan = [dict(row) for row in setups]
        invalid_plan[0]["plan_rr"] = 9.0
        write_csv(setup_path, SETUP_AUDIT_COLUMNS, invalid_plan)
        expect_failure(setup_path, decisions_path, "Inconsistent structural RR was accepted")

    print("Stage D Setup Outcome Dataset test passed")


if __name__ == "__main__":
    main()
