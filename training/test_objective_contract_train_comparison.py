"""XAU AI PLATFORM | Offline Test | Version 1.0.0."""

from __future__ import annotations

import csv
import tempfile
from pathlib import Path

from build_setup_outcome_dataset import OUTCOME_AUDIT_COLUMNS
from compare_objective_contract_train import compare, read_train


def write_train(path: Path, outcomes: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTCOME_AUDIT_COLUMNS)
        writer.writeheader()
        for index, outcome in enumerate(outcomes):
            row = {column: "0" for column in OUTCOME_AUDIT_COLUMNS}
            row.update({"outcome": outcome, "plan_rr": "3.0"})
            writer.writerow(row)


def main() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        reference = root / "REFERENCE_TRAIN.csv"
        candidate = root / "CANDIDATE_TRAIN.csv"
        forbidden = root / "CANDIDATE_TEST.csv"
        write_train(reference, ["TARGET_FIRST", "STOP_FIRST", "STOP_FIRST"])
        write_train(candidate, ["TARGET_FIRST", "TARGET_FIRST", "STOP_FIRST"])
        write_train(forbidden, ["TARGET_FIRST"])
        report = compare(reference, candidate)
        if report["target_rate_change"] <= 0.0:
            raise AssertionError("Objective Train comparison missed improvement")
        if report["validation_dataset_used"] or report["test_dataset_used"]:
            raise AssertionError("Objective Train comparison opened sealed evidence")
        if report["deployment_authorized"]:
            raise AssertionError("Objective Train comparison authorized deployment")
        try:
            read_train(forbidden)
        except ValueError:
            pass
        else:
            raise AssertionError("Objective Train comparison accepted Test input")
    print("Objective contract Train-only comparison test passed")


if __name__ == "__main__":
    main()
