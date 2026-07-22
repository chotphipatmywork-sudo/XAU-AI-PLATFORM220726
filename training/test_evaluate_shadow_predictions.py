"""Focused checks for matured forward Shadow labeling and evaluation."""

from __future__ import annotations

import csv
import tempfile
from pathlib import Path

from analyze_shadow_run import DECISION_COLUMNS
from evaluate_shadow_predictions import evaluate


def row(index: int, high: float, low: float, decision: str = "DECISION_BUY") -> list[object]:
    values = {column: 50 for column in DECISION_COLUMNS}
    values.update({
        "recorded_at": f"2026.07.16 {index:02d}:15:01",
        "closed_bar": f"2026.07.16 {index:02d}:00",
        "symbol": "XAUUSD", "timeframe": "PERIOD_M15",
        "feature_schema_version": "4.0.0",
        "inference_provider": "DEVELOPMENT_HEURISTIC_4_SCALAR_NO_GO",
        "model_status": "DEVELOPMENT_HEURISTIC_MODEL_NO_GO",
        "model_deployment_authorized": "false",
        "bar_open": 99, "bar_high": high, "bar_low": low,
        "bar_close": 100, "atr": 1, "ai_action": "AI_ACTION_BUY",
        "ai_confidence": 75, "decision": decision, "risk_valid": "true",
        "risk_allowed": "true", "risk_score": 100,
        "risk_message": "approved", "execution_success": "true",
        "execution_status": "EXECUTION_SUCCESS",
        "execution_message": "paper", "synthetic_ticket": 900000001 + index,
    })
    return [values[column] for column in DECISION_COLUMNS]


def main() -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "decisions.csv"
        rows = [row(index, 101, 99) for index in range(17)]
        rows[1][DECISION_COLUMNS.index("bar_high")] = 102
        with path.open("w", newline="", encoding="utf-8") as target:
            writer = csv.writer(target)
            writer.writerow(DECISION_COLUMNS)
            writer.writerows(rows)
        report = evaluate(path)
        if report["matured_evaluation_rows"] != 1:
            raise AssertionError("Matured Shadow horizon count changed")
        if report["label_reason_distribution"]["upper_barrier"] != 1:
            raise AssertionError("Upper triple barrier was not detected")
        if report["shadow_deployment_authorized"] or report["live_deployment_authorized"]:
            raise AssertionError("Forward Shadow evaluation authorized deployment")
        print("Shadow prediction evaluation test passed")


if __name__ == "__main__":
    main()
