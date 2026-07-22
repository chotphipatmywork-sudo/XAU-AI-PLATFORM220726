"""Focused checks for the canonical Shadow Strategy Tester artifact audit."""

from __future__ import annotations

import csv
import tempfile
from pathlib import Path

from analyze_shadow_backtest import analyze
from analyze_shadow_run import DECISION_COLUMNS


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        report = root / "report.csv"
        decisions = root / "decisions.csv"
        audit = root / "audit.csv"
        write_csv(
            report,
            [
                "start_time", "end_time", "first_decision_bar", "last_decision_bar",
                "inference_provider", "model_status", "decisions", "risk_rejections", "shadow_executions",
                "closed_trades", "winning_trades", "losing_trades", "breakeven_trades",
                "cumulative_profit_points", "maximum_drawdown_points",
                "model_deployment_authorized", "live_execution_authorized",
                "broker_state_unchanged", "counts_consistent", "safety_valid",
            ],
            [{
                "start_time": "2026.07.01 00:00:00",
                "end_time": "2026.07.01 23:59:59",
                "first_decision_bar": "2026.07.01 00:00",
                "last_decision_bar": "2026.07.01 00:15",
                "inference_provider": "DEVELOPMENT_HEURISTIC_4_SCALAR_NO_GO",
                "model_status": "DEVELOPMENT_HEURISTIC_MODEL_NO_GO",
                "decisions": 2, "risk_rejections": 1, "shadow_executions": 1,
                "closed_trades": 1, "winning_trades": 1, "losing_trades": 0,
                "breakeven_trades": 0, "cumulative_profit_points": 100.0,
                "maximum_drawdown_points": 0.0, "model_deployment_authorized": "false",
                "live_execution_authorized": "false", "broker_state_unchanged": "true",
                "counts_consistent": "true", "safety_valid": "true",
            }],
        )
        decision_rows = []
        for closed_bar, success, decision, message in [
            ("2026.07.01 00:00", "true", "DECISION_BUY", "Risk evaluation passed."),
            ("2026.07.01 00:15", "false", "DECISION_SELL",
             "Risk blocked the Shadow drawdown limit."),
        ]:
            row = {column: 50 for column in DECISION_COLUMNS}
            row.update({
                "closed_bar": closed_bar, "execution_success": success,
                "decision": decision, "risk_message": message,
                "feature_schema_version": "4.0.0",
                "inference_provider": "DEVELOPMENT_HEURISTIC_4_SCALAR_NO_GO",
                "model_status": "DEVELOPMENT_HEURISTIC_MODEL_NO_GO",
                "model_deployment_authorized": "false",
            })
            decision_rows.append(row)
        write_csv(decisions, list(DECISION_COLUMNS), decision_rows)
        write_csv(
            audit,
            ["event", "message", "ticket", "profit_points"],
            [
                {"event": "OPENED", "message": "opened", "ticket": 900000001,
                 "profit_points": 0.0},
                {"event": "CLOSED", "message": "TAKE_PROFIT", "ticket": 900000001,
                 "profit_points": 100.0},
            ],
        )
        valid = analyze(report, decisions, audit)
        if not valid["backtest_evidence_valid"]:
            raise AssertionError(valid)
        if not valid["report"]["directional_coverage"]:
            raise AssertionError("Directional coverage diagnostic failed")
        if not valid["report"]["drawdown_halt_detected"]:
            raise AssertionError("Drawdown halt diagnostic failed")

        report_rows = list(csv.DictReader(report.open("r", encoding="utf-8", newline="")))
        report_rows[0]["inference_provider"] = (
            "DIRECTIONAL_FEATURE_RESEARCH_TESTER_ONLY"
        )
        report_rows[0]["model_status"] = "DIRECTIONAL_FEATURE_RESEARCH_NO_GO"
        write_csv(report, list(report_rows[0]), report_rows)

        rows = list(csv.DictReader(decisions.open("r", encoding="utf-8", newline="")))
        for row in rows:
            row["inference_provider"] = "DIRECTIONAL_FEATURE_RESEARCH_TESTER_ONLY"
            row["model_status"] = "DIRECTIONAL_FEATURE_RESEARCH_NO_GO"
        write_csv(decisions, list(DECISION_COLUMNS), rows)
        directional = analyze(report, decisions, audit)
        if not directional["backtest_evidence_valid"]:
            raise AssertionError("Directional provider evidence was rejected")

        rows[1]["closed_bar"] = rows[0]["closed_bar"]
        write_csv(
            decisions,
            list(DECISION_COLUMNS),
            rows,
        )
        duplicate = analyze(report, decisions, audit)
        if duplicate["backtest_evidence_valid"]:
            raise AssertionError("Duplicate closed bars did not invalidate evidence")

    print("Shadow backtest artifact audit test passed")


if __name__ == "__main__":
    main()
