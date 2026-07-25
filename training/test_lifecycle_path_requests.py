"""Focused checks for Effective-Train lifecycle-path request preparation."""

from __future__ import annotations

import csv
import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from audit_effective_setup_sample import audit_effective_sample
from augment_pretrain_history import sha256
from build_lifecycle_path_requests import build_requests, write_requests
from build_setup_outcome_dataset import OUTCOME_AUDIT_COLUMNS


def write_train(path: Path) -> None:
    origin = datetime(2025, 1, 1)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTCOME_AUDIT_COLUMNS)
        writer.writeheader()
        for index in range(4):
            observation = origin + timedelta(hours=index)
            target_first = index % 2 == 0
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
                    "TRADE_SETUP_BUY" if index < 2 else "TRADE_SETUP_SELL"
                ),
                "plan_entry": 100.0,
                "plan_stop": 90.0 if index < 2 else 110.0,
                "plan_target": 120.0 if index < 2 else 80.0,
                "plan_rr": 2.0,
                "minimum_rr": 2.0,
                "estimated_cost_points": 0.0,
                "point_size": 0.01,
                "risk_points": 1000.0,
                "bars_observed": 1,
                "outcome": "TARGET_FIRST" if target_first else "STOP_FIRST",
                "trainable": "true",
                "mfe_r": 2.1 if target_first else 0.5,
                "mae_r": 0.5 if target_first else 1.1,
                "realized_r": 2.0 if target_first else -1.0,
            })
            writer.writerow(row)


def main() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        train = root / "XAU_AI_SETUP_OUTCOME_AUGMENTED_TRAIN.csv"
        audit_path = root / "audit.json"
        request_path = root / "requests.csv"
        manifest_path = root / "manifest.json"
        write_train(train)
        audit = audit_effective_sample(train, sha256(train), 1)
        audit_path.write_text(json.dumps(audit, indent=2), encoding="utf-8")
        rows, manifest = build_requests(
            train, sha256(train), audit_path, sha256(audit_path)
        )
        if len(rows) != 4 or any(row["maximum_path_m5_bars"] != 192 for row in rows):
            raise AssertionError("Lifecycle request count/window changed")
        if not manifest["maximum_path_m5_bars_policy"].startswith(
            "ABSOLUTE_64_M15_X3_SAFETY_CEILING"
        ):
            raise AssertionError("Lifecycle absolute M5 safety ceiling changed")
        if any(row["deployment_authorized"] != "false" for row in rows):
            raise AssertionError("Lifecycle request authorized deployment")
        complete = write_requests(rows, manifest, request_path, manifest_path)
        if complete["request_file_sha256"] != sha256(request_path):
            raise AssertionError("Lifecycle request hash was not sealed")
        if complete["validation_dataset_read"] or complete["runtime_changed"]:
            raise AssertionError("Lifecycle request crossed a protected boundary")
        if complete["candidates"] != [
            "CURRENT_BASELINE",
            "COST_COVERED_BREAKEVEN_AFTER_CLOSE_1R",
            "TWO_STAGE_RATCHET_AFTER_CLOSE_1R_2R",
        ]:
            raise AssertionError("Lifecycle pre-registered candidates changed")

    print("Lifecycle path request test passed")


if __name__ == "__main__":
    main()
