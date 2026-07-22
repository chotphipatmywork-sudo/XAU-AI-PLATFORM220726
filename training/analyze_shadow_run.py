"""Audit Shadow Runtime observations without training or deployment."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime
from pathlib import Path


DECISION_COLUMNS = (
    "recorded_at",
    "closed_bar",
    "symbol",
    "timeframe",
    "feature_schema_version",
    "inference_provider",
    "model_status",
    "model_deployment_authorized",
    "bar_open",
    "bar_high",
    "bar_low",
    "bar_close",
    "atr",
    "trend_regime",
    "trend_momentum",
    "trend_slope",
    "volatility_regime",
    "volatility_change",
    "liquidity_activity",
    "liquidity_range_position",
    "liquidity_sweep_direction",
    "session_asia",
    "session_london",
    "session_new_york",
    "session_progress",
    "legacy_trend_score",
    "legacy_volatility_score",
    "legacy_liquidity_score",
    "legacy_session_score",
    "ai_action",
    "ai_confidence",
    "decision",
    "risk_valid",
    "risk_allowed",
    "risk_score",
    "risk_message",
    "execution_success",
    "execution_status",
    "execution_message",
    "synthetic_ticket",
)

FEATURE_COLUMNS = (
    "trend_regime", "trend_momentum", "trend_slope",
    "volatility_regime", "volatility_change", "liquidity_activity",
    "liquidity_range_position", "liquidity_sweep_direction", "session_asia",
    "session_london", "session_new_york", "session_progress",
)

AUDIT_COLUMNS = (
    "timestamp",
    "event",
    "message",
    "ticket",
    "symbol",
    "order_type",
    "volume",
    "entry_price",
    "current_price",
    "stop_loss",
    "take_profit",
    "profit_points",
    "active",
    "risk_score",
    "confidence",
)


def boolean(value: str) -> bool:
    if value == "true":
        return True
    if value == "false":
        return False
    raise ValueError(f"Invalid Boolean value: {value}")


def read_rows(path: Path, columns: tuple[str, ...]) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames is None or tuple(reader.fieldnames) != columns:
            raise ValueError(f"Unexpected Shadow CSV schema in {path}")
        rows = list(reader)
    if not rows:
        raise ValueError(f"Shadow CSV is empty: {path}")
    return rows


def analyze(
    decision_path: Path,
    audit_path: Path,
    minimum_observations: int,
    minimum_closed_trades: int,
    minimum_days: int,
) -> dict[str, object]:
    decisions = read_rows(decision_path, DECISION_COLUMNS)
    events = read_rows(audit_path, AUDIT_COLUMNS)
    keys = [(row["symbol"], row["timeframe"], row["closed_bar"]) for row in decisions]
    duplicate_bars = len(keys) - len(set(keys))
    days = {
        datetime.strptime(row["closed_bar"], "%Y.%m.%d %H:%M").date()
        for row in decisions
    }
    safety_violations: list[str] = []
    for index, row in enumerate(decisions, start=2):
        risk_allowed = boolean(row["risk_allowed"])
        execution_success = boolean(row["execution_success"])
        ticket = int(row["synthetic_ticket"])
        if execution_success and not risk_allowed:
            safety_violations.append(f"row {index}: execution bypassed Risk")
        if execution_success and ticket < 900000001:
            safety_violations.append(f"row {index}: ticket is not synthetic")
        if row["model_status"] != "DEVELOPMENT_HEURISTIC_MODEL_NO_GO":
            safety_violations.append(f"row {index}: unexpected model authorization")
        if row["feature_schema_version"] != "4.0.0":
            safety_violations.append(f"row {index}: unexpected feature schema")
        if row["inference_provider"] != "DEVELOPMENT_HEURISTIC_4_SCALAR_NO_GO":
            safety_violations.append(f"row {index}: unexpected inference provider")
        if boolean(row["model_deployment_authorized"]):
            safety_violations.append(f"row {index}: model deployment was authorized")
        for feature in FEATURE_COLUMNS:
            value = float(row[feature])
            if not 0.0 <= value <= 100.0:
                safety_violations.append(
                    f"row {index}: {feature} is outside Feature Schema 4.0"
                )

    event_counts = Counter(row["event"] for row in events)
    closed = [row for row in events if row["event"] == "CLOSED"]
    closed_points = [float(row["profit_points"]) for row in closed]
    open_balance = event_counts["OPENED"] - event_counts["CLOSED"]
    if open_balance not in (0, 1):
        safety_violations.append("paper lifecycle has more than one unmatched open")
    for index, row in enumerate(events, start=2):
        ticket = int(row["ticket"])
        if row["event"] in {"OPENED", "CLOSED"} and ticket < 900000001:
            safety_violations.append(f"audit row {index}: non-synthetic ticket")

    ready = (
        len(decisions) >= minimum_observations
        and len(closed) >= minimum_closed_trades
        and len(days) >= minimum_days
        and duplicate_bars == 0
        and not safety_violations
    )
    return {
        "analysis_stage": "shadow_observation_audit_only",
        "training_performed": False,
        "validation_dataset_used": False,
        "test_dataset_used": False,
        "deployment_authorized": False,
        "decision_observations": len(decisions),
        "unique_observation_days": len(days),
        "duplicate_closed_bars": duplicate_bars,
        "decision_distribution": dict(Counter(row["decision"] for row in decisions)),
        "feature_schema_version": "4.0.0",
        "inference_provider": "DEVELOPMENT_HEURISTIC_4_SCALAR_NO_GO",
        "risk_allowed": sum(boolean(row["risk_allowed"]) for row in decisions),
        "risk_rejected": sum(not boolean(row["risk_allowed"]) for row in decisions),
        "shadow_execution_successes": sum(
            boolean(row["execution_success"]) for row in decisions
        ),
        "event_distribution": dict(event_counts),
        "closed_trades": len(closed),
        "winning_trades": sum(value > 0.0 for value in closed_points),
        "losing_trades": sum(value < 0.0 for value in closed_points),
        "realized_profit_points": sum(closed_points),
        "paper_open_balance": open_balance,
        "safety_violations": safety_violations,
        "research_readiness_requirements": {
            "minimum_observations": minimum_observations,
            "minimum_closed_trades": minimum_closed_trades,
            "minimum_days": minimum_days,
        },
        "ready_for_model_research": ready,
        "ready_for_shadow_deployment": False,
        "ready_for_live_deployment": False,
        "limitations": [
            "This audit validates Shadow operations; it does not prove model accuracy.",
            "The active Runtime output is explicitly marked as a development heuristic.",
            "Fresh labels and a separately approved offline evaluation are required.",
        ],
    }


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--decisions", required=True, type=Path)
    parser.add_argument("--audit", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--minimum-observations", type=int, default=1000)
    parser.add_argument("--minimum-closed-trades", type=int, default=100)
    parser.add_argument("--minimum-days", type=int, default=20)
    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()
    report = analyze(
        arguments.decisions,
        arguments.audit,
        arguments.minimum_observations,
        arguments.minimum_closed_trades,
        arguments.minimum_days,
    )
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
