"""Audit canonical Shadow Strategy Tester artifacts without training a model."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

from analyze_shadow_run import FEATURE_COLUMNS


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Shadow backtest artifact not found: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def as_bool(value: str) -> bool:
    return value.strip().lower() == "true"


def as_int(value: str) -> int:
    return int(float(value))


def as_float(value: str) -> float:
    return float(value)


def as_datetime(value: str) -> datetime:
    return datetime.strptime(value.strip(), "%Y.%m.%d %H:%M:%S")


def analyze(report_path: Path, decisions_path: Path, audit_path: Path) -> dict[str, Any]:
    report_rows = read_rows(report_path)
    decision_rows = read_rows(decisions_path)
    audit_rows = read_rows(audit_path)
    if len(report_rows) != 1:
        raise ValueError("Shadow backtest report must contain exactly one data row")

    report = report_rows[0]
    report_provider = report["inference_provider"]
    opened = [row for row in audit_rows if row["event"] == "OPENED"]
    closed = [row for row in audit_rows if row["event"] == "CLOSED"]
    successful_decisions = [
        row for row in decision_rows if as_bool(row["execution_success"])
    ]
    closed_points = [as_float(row["profit_points"]) for row in closed]
    wins = sum(value > 0.0 for value in closed_points)
    losses = sum(value < 0.0 for value in closed_points)
    breakeven = sum(value == 0.0 for value in closed_points)
    synthetic_tickets_valid = all(
        as_int(row["ticket"]) >= 900000001 for row in opened + closed
    )
    closed_bar_values = [row["closed_bar"] for row in decision_rows]
    duplicate_closed_bars = len(closed_bar_values) - len(set(closed_bar_values))
    distinct_days = len({value[:10] for value in closed_bar_values})
    decision_distribution = Counter(row["decision"] for row in decision_rows)
    risk_message_distribution = Counter(row["risk_message"] for row in decision_rows)
    close_reason_distribution = Counter(row["message"] for row in closed)
    gross_profit_points = sum(value for value in closed_points if value > 0.0)
    gross_loss_points = sum(value for value in closed_points if value < 0.0)
    win_rate = wins / len(closed_points) if closed_points else 0.0
    profit_factor = (
        gross_profit_points / abs(gross_loss_points)
        if gross_loss_points < 0.0
        else 0.0
    )
    expectancy_points = (
        sum(closed_points) / len(closed_points) if closed_points else 0.0
    )
    directional_coverage = (
        decision_distribution.get("DECISION_BUY", 0) > 0
        and decision_distribution.get("DECISION_SELL", 0) > 0
    )
    drawdown_halt_detected = (
        risk_message_distribution.get("Risk blocked the Shadow drawdown limit.", 0) > 0
    )
    decision_times = [as_datetime(value + ":00") for value in closed_bar_values]
    report_start = as_datetime(report["start_time"])
    report_end = as_datetime(report["end_time"])
    report_first = as_datetime(report["first_decision_bar"] + ":00")
    report_last = as_datetime(report["last_decision_bar"] + ":00")
    schema4_rows_valid = all(
        row.get("feature_schema_version") == "4.0.0"
        and row.get("inference_provider") == report_provider
        and row.get("model_status") == report["model_status"]
        and not as_bool(row.get("model_deployment_authorized", "true"))
        and all(0.0 <= as_float(row[feature]) <= 100.0 for feature in FEATURE_COLUMNS)
        for row in decision_rows
    )

    checks = {
        "report_safety_valid": as_bool(report["safety_valid"]),
        "report_counts_consistent": as_bool(report["counts_consistent"]),
        "model_deployment_locked": not as_bool(report["model_deployment_authorized"]),
        "live_execution_locked": not as_bool(report["live_execution_authorized"]),
        "broker_state_unchanged": as_bool(report["broker_state_unchanged"]),
        "decision_count_agrees": as_int(report["decisions"]) == len(decision_rows),
        "execution_count_agrees": (
            as_int(report["shadow_executions"]) == len(successful_decisions) == len(opened)
        ),
        "closed_trade_count_agrees": as_int(report["closed_trades"]) == len(closed),
        "win_loss_counts_agree": (
            as_int(report["winning_trades"]) == wins
            and as_int(report["losing_trades"]) == losses
            and as_int(report["breakeven_trades"]) == breakeven
        ),
        "realized_points_agree": abs(
            as_float(report["cumulative_profit_points"]) - sum(closed_points)
        ) < 1e-6,
        "synthetic_tickets_valid": synthetic_tickets_valid,
        "duplicate_closed_bars_zero": duplicate_closed_bars == 0,
        "decision_boundaries_agree": (
            bool(decision_times)
            and min(decision_times) == report_first
            and max(decision_times) == report_last
        ),
        "decisions_within_test_period": (
            bool(decision_times)
            and all(report_start <= value <= report_end for value in decision_times)
        ),
        "inference_provider_agrees": (
            bool(decision_rows)
            and {row["inference_provider"] for row in decision_rows}
            == {report_provider}
        ),
        "model_status_agrees": (
            bool(decision_rows)
            and {row["model_status"] for row in decision_rows}
            == {report["model_status"]}
        ),
        "model_status_no_go": report["model_status"].endswith("NO_GO"),
        "schema4_inference_evidence_valid": schema4_rows_valid,
    }
    evidence_valid = bool(checks) and all(checks.values())
    result: dict[str, Any] = {
        "analysis_stage": "canonical_shadow_strategy_tester_audit_only",
        "training_performed": False,
        "deployment_authorized": False,
        "report": {
            "inference_provider": report_provider,
            "model_status": report["model_status"],
            "decisions": as_int(report["decisions"]),
            "risk_rejections": as_int(report["risk_rejections"]),
            "shadow_executions": as_int(report["shadow_executions"]),
            "closed_trades": as_int(report["closed_trades"]),
            "winning_trades": wins,
            "losing_trades": losses,
            "breakeven_trades": breakeven,
            "cumulative_profit_points": as_float(report["cumulative_profit_points"]),
            "maximum_drawdown_points": as_float(report["maximum_drawdown_points"]),
            "duplicate_closed_bars": duplicate_closed_bars,
            "distinct_observation_days": distinct_days,
            "decision_distribution": dict(decision_distribution),
            "risk_message_distribution": dict(risk_message_distribution),
            "close_reason_distribution": dict(close_reason_distribution),
            "win_rate": win_rate,
            "gross_profit_points": gross_profit_points,
            "gross_loss_points": gross_loss_points,
            "profit_factor": profit_factor,
            "expectancy_points": expectancy_points,
            "directional_coverage": directional_coverage,
            "drawdown_halt_detected": drawdown_halt_detected,
        },
        "checks": checks,
        "backtest_evidence_valid": evidence_valid,
        "model_quality_observation": {
            "status": "NO_GO",
            "reason": (
            "Runtime is explicitly a NO-GO research provider; this run also requires "
                "two-sided directional coverage and profitable out-of-sample evidence."
            ),
        },
        "ready_for_shadow_deployment": False,
        "ready_for_live_deployment": False,
        "limitations": [
            "This audit validates Strategy Tester integration and safety only.",
            "The active Runtime artifact is a research provider with model NO-GO status.",
            "Profitability requires separately approved model evaluation evidence.",
        ],
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--decisions", required=True, type=Path)
    parser.add_argument("--audit", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    arguments = parser.parse_args()
    result = analyze(arguments.report, arguments.decisions, arguments.audit)
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
