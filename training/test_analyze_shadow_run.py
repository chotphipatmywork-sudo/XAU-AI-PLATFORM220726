"""Focused safety checks for the Shadow observation auditor."""

from __future__ import annotations

import csv
import tempfile
from pathlib import Path

from analyze_shadow_run import AUDIT_COLUMNS, DECISION_COLUMNS, analyze


def write_csv(path: Path, columns: tuple[str, ...], rows: list[list[object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as target:
        writer = csv.writer(target)
        writer.writerow(columns)
        writer.writerows(rows)


def main() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        decisions = root / "decisions.csv"
        audit = root / "audit.csv"
        values = {column: 50 for column in DECISION_COLUMNS}
        values.update({
            "recorded_at": "2026.07.16 12:15:01",
            "closed_bar": "2026.07.16 12:00",
            "symbol": "XAUUSD",
            "timeframe": "PERIOD_M15",
            "feature_schema_version": "4.0.0",
            "inference_provider": "DEVELOPMENT_HEURISTIC_4_SCALAR_NO_GO",
            "model_status": "DEVELOPMENT_HEURISTIC_MODEL_NO_GO",
            "model_deployment_authorized": "false",
            "bar_open": 1999, "bar_high": 2001, "bar_low": 1998,
            "bar_close": 2000, "atr": 5,
            "ai_action": "AI_ACTION_BUY", "ai_confidence": 75,
            "decision": "DECISION_BUY", "risk_valid": "true",
            "risk_allowed": "true", "risk_score": 100,
            "risk_message": "approved", "execution_success": "true",
            "execution_status": "EXECUTION_SUCCESS",
            "execution_message": "paper", "synthetic_ticket": 900000001,
        })
        decision_row = [values[column] for column in DECISION_COLUMNS]
        audit_open = [
            "2026.07.16 12:15:01",
            "OPENED",
            "paper",
            900000001,
            "XAUUSD",
            "ORDER_TYPE_BUY",
            0.01,
            2000,
            2000,
            1999,
            2002,
            0,
            "true",
            100,
            75,
        ]
        audit_close = [
            "2026.07.16 13:00:00",
            "CLOSED",
            "TAKE_PROFIT",
            900000001,
            "XAUUSD",
            "ORDER_TYPE_BUY",
            0.01,
            2000,
            2002,
            1999,
            2002,
            200,
            "false",
            0,
            0,
        ]
        write_csv(decisions, DECISION_COLUMNS, [decision_row])
        write_csv(audit, AUDIT_COLUMNS, [audit_open, audit_close])
        report = analyze(decisions, audit, 1, 1, 1)
        if not report["ready_for_model_research"]:
            raise AssertionError("Valid Shadow evidence was not research-ready")
        if report["ready_for_live_deployment"]:
            raise AssertionError("Shadow audit authorized live deployment")

        decision_row[DECISION_COLUMNS.index("risk_allowed")] = "false"
        write_csv(decisions, DECISION_COLUMNS, [decision_row])
        unsafe = analyze(decisions, audit, 1, 1, 1)
        if not unsafe["safety_violations"]:
            raise AssertionError("Risk bypass was not detected")
        print("Shadow observation audit test passed")


if __name__ == "__main__":
    main()
