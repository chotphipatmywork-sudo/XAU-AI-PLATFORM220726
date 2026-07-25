"""XAU AI PLATFORM | Offline Evidence Preparation | Version 1.1.0.

Build frozen Effective-Train M5 lifecycle-path requests without reading sealed
Validation/Test evidence or authorizing Runtime/Deployment changes.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from augment_pretrain_history import sha256
from diagnose_entry_stop_expectancy import load_audited_effective_rows


REQUEST_SCHEMA_VERSION = "1.1.0"
MANIFEST_SCHEMA_VERSION = "1.1.0"
MAXIMUM_M5_PATH_BARS = 64 * 3
REQUEST_COLUMNS = (
    "request_schema_version", "request_id", "observation_time",
    "outcome_known_at", "symbol", "direction", "entry", "initial_stop",
    "target", "estimated_cost_points", "point_size", "plan_rr",
    "baseline_outcome", "maximum_path_m5_bars", "deployment_authorized",
)
CANDIDATES = (
    "CURRENT_BASELINE",
    "COST_COVERED_BREAKEVEN_AFTER_CLOSE_1R",
    "TWO_STAGE_RATCHET_AFTER_CLOSE_1R_2R",
)
COST_MULTIPLIERS = (1.0, 1.25, 1.5)


def build_requests(
    train_path: Path,
    expected_train_sha256: str,
    audit_path: Path,
    expected_audit_sha256: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows, _, train_hash, audit_hash = load_audited_effective_rows(
        train_path, expected_train_sha256, audit_path, expected_audit_sha256
    )
    requests: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in rows:
        observation = row["start"]
        known_at = row["end"]
        seconds = int((known_at - observation).total_seconds())
        if seconds <= 0 or seconds % 300 != 0:
            raise ValueError("Lifecycle request outcome window is not M5-aligned")
        source_m15_bars = int(row["bars_observed"])
        if source_m15_bars < 1 or source_m15_bars > 64:
            raise ValueError("Lifecycle request outcome window exceeds 64 M15 bars")
        request_id = f"lifecycle_{observation.strftime('%Y%m%d_%H%M')}"
        if request_id in seen:
            raise ValueError("Lifecycle request identifier is duplicated")
        seen.add(request_id)
        requests.append({
            "request_schema_version": REQUEST_SCHEMA_VERSION,
            "request_id": request_id,
            "observation_time": row["observation_time"],
            "outcome_known_at": row["outcome_known_at"],
            "symbol": "XAUUSD",
            "direction": row["direction"],
            "entry": row["entry"],
            "initial_stop": row["stop"],
            "target": row["target"],
            "estimated_cost_points": row["estimated_cost_points"],
            "point_size": row["point_size"],
            "plan_rr": row["plan_rr"],
            "baseline_outcome": row["outcome"],
            "maximum_path_m5_bars": MAXIMUM_M5_PATH_BARS,
            "deployment_authorized": "false",
        })
    manifest = {
        "lifecycle_request_manifest_schema_version": MANIFEST_SCHEMA_VERSION,
        "request_schema_version": REQUEST_SCHEMA_VERSION,
        "research_stage": "effective_train_causal_m5_lifecycle_path_request",
        "source_train_sha256": train_hash,
        "effective_sample_audit_sha256": audit_hash,
        "requests": len(requests),
        "first_observation": requests[0]["observation_time"],
        "last_observation": requests[-1]["observation_time"],
        "timeframe": "PERIOD_M5",
        "maximum_path_m5_bars_policy": (
            "ABSOLUTE_64_M15_X3_SAFETY_CEILING; exact mature-window timestamps "
            "remain authoritative because broker M15/M5 bar calendars may differ"
        ),
        "same_bar_collision_policy": "AMBIGUOUS_QUARANTINE",
        "management_activation_policy": "COMPLETED_M5_CLOSE_EFFECTIVE_NEXT_BAR",
        "candidates": list(CANDIDATES),
        "cost_multipliers": list(COST_MULTIPLIERS),
        "frozen_train_gates": {
            "minimum_effective_records": 200,
            "mean_r_positive": True,
            "moving_block_ci95_lower_positive": True,
            "all_four_chronological_blocks_positive": True,
            "both_directions_positive": True,
            "profit_factor_minimum": 1.10,
            "maximum_drawdown_r_maximum": 25.0,
            "longest_loss_sequence_maximum": 10,
            "all_cost_stress_intervals_positive": True,
        },
        "validation_dataset_read": False,
        "test_dataset_read": False,
        "model_training_performed": False,
        "runtime_changed": False,
        "risk_changed": False,
        "deployment_authorized": False,
        "status": "LIFECYCLE_PATH_REQUESTS_TRAIN_ONLY_NO_GO",
    }
    return requests, manifest


def write_requests(
    rows: list[dict[str, Any]],
    manifest: dict[str, Any],
    output_path: Path,
    manifest_path: Path,
) -> dict[str, Any]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REQUEST_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    complete = dict(manifest)
    complete["request_file_sha256"] = sha256(output_path)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(complete, indent=2), encoding="utf-8")
    return complete


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", required=True, type=Path)
    parser.add_argument("--expected-train-sha256", required=True)
    parser.add_argument("--effective-sample-audit", required=True, type=Path)
    parser.add_argument("--expected-audit-sha256", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    arguments = parser.parse_args()
    rows, manifest = build_requests(
        arguments.train,
        arguments.expected_train_sha256,
        arguments.effective_sample_audit,
        arguments.expected_audit_sha256,
    )
    complete = write_requests(rows, manifest, arguments.output, arguments.manifest)
    print(json.dumps(complete, indent=2))


if __name__ == "__main__":
    main()
