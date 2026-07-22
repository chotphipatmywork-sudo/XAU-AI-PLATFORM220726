"""Focused checks for Stage D Objective generation-model parity."""

from __future__ import annotations

import tempfile
from datetime import datetime
from pathlib import Path

from analyze_shadow_run import DECISION_COLUMNS
from build_setup_outcome_dataset import SETUP_AUDIT_COLUMNS
from compare_objective_generation_parity import compare
from test_setup_outcome_dataset import decision_rows, plan_row, write_csv


def main() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        reference_setup = root / "reference_setup.csv"
        reference_decisions = root / "reference_decisions.csv"
        candidate_setup = root / "candidate_setup.csv"
        candidate_decisions = root / "candidate_decisions.csv"
        start = datetime(2026, 7, 1, 0, 0)
        decisions = decision_rows(start, 8)
        setups = [
            plan_row(start, "TRADE_SETUP_BUY", 100.0, 90.0, 121.0),
            plan_row(start.replace(minute=15), "TRADE_SETUP_SELL", 200.0, 210.0, 179.0),
        ]
        write_csv(reference_setup, SETUP_AUDIT_COLUMNS, setups)
        write_csv(candidate_setup, SETUP_AUDIT_COLUMNS, [dict(row) for row in setups])
        write_csv(reference_decisions, DECISION_COLUMNS, decisions)
        write_csv(candidate_decisions, DECISION_COLUMNS, [dict(row) for row in decisions])
        valid = compare(
            reference_setup, reference_decisions, candidate_setup, candidate_decisions
        )
        if not valid["generation_parity_valid"]:
            raise AssertionError(valid)

        ignored = [dict(row) for row in setups]
        ignored[0]["risk_message"] = "Different paper-only Risk state."
        write_csv(candidate_setup, SETUP_AUDIT_COLUMNS, ignored)
        still_valid = compare(
            reference_setup, reference_decisions, candidate_setup, candidate_decisions
        )
        if not still_valid["generation_parity_valid"]:
            raise AssertionError("Risk-only difference invalidated generation parity")

        changed_decisions = [dict(row) for row in decisions]
        changed_decisions[0]["trend_regime"] = 99.0
        write_csv(candidate_decisions, DECISION_COLUMNS, changed_decisions)
        invalid_feature = compare(
            reference_setup, reference_decisions, candidate_setup, candidate_decisions
        )
        if invalid_feature["generation_parity_valid"]:
            raise AssertionError("Feature mismatch did not invalidate generation parity")

        write_csv(candidate_decisions, DECISION_COLUMNS, decisions)
        changed_setups = [dict(row) for row in setups]
        changed_setups[0]["plan_target"] = 122.0
        write_csv(candidate_setup, SETUP_AUDIT_COLUMNS, changed_setups)
        invalid_plan = compare(
            reference_setup, reference_decisions, candidate_setup, candidate_decisions
        )
        if invalid_plan["generation_parity_valid"]:
            raise AssertionError("Trade Plan mismatch did not invalidate generation parity")

    print("Stage D Objective generation parity test passed")


if __name__ == "__main__":
    main()
