"""Focused checks for the effective Train Entry/Stop expectancy diagnostic."""

from __future__ import annotations

import csv
import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from audit_effective_setup_sample import audit_effective_sample
from augment_pretrain_history import sha256
from build_setup_outcome_dataset import OUTCOME_AUDIT_COLUMNS
from diagnose_entry_stop_expectancy import diagnose


def write_train(path: Path, corrupt_return: bool = False) -> None:
    origin = datetime(2025, 1, 1)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTCOME_AUDIT_COLUMNS)
        writer.writeheader()
        for index in range(8):
            observation = origin + timedelta(hours=index)
            target = index in {0, 3, 6}
            plan_rr = 2.0
            row = {column: "50" for column in OUTCOME_AUDIT_COLUMNS}
            row.update({
                "setup_outcome_schema_version": "1.0.0",
                "feature_schema_version": "4.0.0",
                "observation_time": observation.strftime("%Y.%m.%d %H:%M"),
                "outcome_known_at": (observation + timedelta(minutes=15)).strftime(
                    "%Y.%m.%d %H:%M"
                ),
                "symbol": "XAUUSD",
                "timeframe": "PERIOD_M15",
                "direction": (
                    "TRADE_SETUP_BUY" if index % 2 == 0 else "TRADE_SETUP_SELL"
                ),
                "plan_entry": 100.0,
                "plan_stop": 90.0,
                "plan_target": 120.0,
                "plan_rr": plan_rr,
                "minimum_rr": 2.0,
                "estimated_cost_points": 0.0,
                "point_size": 0.01,
                "risk_points": 1000.0,
                "outcome": "TARGET_FIRST" if target else "STOP_FIRST",
                "trainable": "true",
                "mfe_r": 2.1 if target else index / 10.0,
                "mae_r": 0.4 if target else 1.1,
                "realized_r": (
                    99.0 if corrupt_return and index == 0 else plan_rr if target else -1.0
                ),
            })
            writer.writerow(row)


def write_audit(train: Path, audit_path: Path) -> str:
    report = audit_effective_sample(train, sha256(train), 1)
    audit_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return sha256(audit_path)


def main() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        train = root / "XAU_AI_SETUP_OUTCOME_AUGMENTED_TRAIN.csv"
        audit = root / "effective_sample_audit.json"
        write_train(train)
        audit_hash = write_audit(train, audit)
        report = diagnose(train, sha256(train), audit, audit_hash, 500)
        if report["effective_sample_records"] != 8:
            raise AssertionError("Entry/Stop effective sample changed")
        if report["overall"]["mean_cost_aware_r"] != 0.125:
            raise AssertionError("Entry/Stop expectancy changed")
        if report["overall"]["longest_loss_sequence"] != 2:
            raise AssertionError("Entry/Stop loss-tail sequence changed")
        if report["stop_first_path"]["mfe_at_least_0_5r"] != 2:
            raise AssertionError("Entry/Stop losing-path MFE changed")
        if report["mean_r_ci95"]["lower"] >= report["mean_r_ci95"]["upper"]:
            raise AssertionError("Entry/Stop confidence interval is invalid")
        if report["entry_stop_candidate_selected"] or report["deployment_authorized"]:
            raise AssertionError("Entry/Stop diagnostic selected or deployed a candidate")

        try:
            diagnose(train, sha256(train), audit, "A" * 64, 500)
        except ValueError as error:
            if "audit SHA-256 mismatch" not in str(error):
                raise
        else:
            raise AssertionError("Entry/Stop diagnostic accepted audit hash drift")

        write_train(train, corrupt_return=True)
        audit_hash = write_audit(train, audit)
        try:
            diagnose(train, sha256(train), audit, audit_hash, 500)
        except ValueError as error:
            if "stored gross R is inconsistent" not in str(error):
                raise
        else:
            raise AssertionError("Entry/Stop diagnostic accepted corrupt realized R")

    print("Entry/Stop expectancy-tail diagnostic test passed")


if __name__ == "__main__":
    main()
