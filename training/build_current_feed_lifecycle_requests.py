"""XAU AI PLATFORM | Offline Research | Version 1.0.0.

Build outcome-sealed current-feed M5 lifecycle requests for valid >=2R plans
whose M15 baseline path matured before the frozen Train cutoff.
"""

from __future__ import annotations

import argparse
import bisect
import csv
import json
from pathlib import Path
from typing import Any

from build_lifecycle_path_requests import (
    CANDIDATES,
    COST_MULTIPLIERS,
    MANIFEST_SCHEMA_VERSION,
    MAXIMUM_M5_PATH_BARS,
    REQUEST_COLUMNS,
    REQUEST_SCHEMA_VERSION,
)
from build_setup_outcome_dataset import evaluate_path
from diagnose_current_feed_setup_funnel import TRAIN_END_EXCLUSIVE, sha256
from replay_current_feed_targets import (
    EXPECTED_DECISIONS_SHA256,
    read_requests,
)
from replay_past_only_targets import geometry_and_rr, load_paths, read_export


STATUS = "CURRENT_FEED_LIFECYCLE_PATH_REQUESTS_TRAIN_ONLY_NO_GO"


def build_requests(
    evidence: list[dict[str, Any]],
    bar_times: list,
    bars: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    rows: list[dict[str, Any]] = []
    audit = {
        "source_contexts": len(evidence),
        "unknown_cost": 0,
        "below_minimum_rr_or_invalid": 0,
        "ambiguous_or_unmatured": 0,
        "requests": 0,
    }
    for row in evidence:
        if not row["cost_known"]:
            audit["unknown_cost"] += 1
            continue
        target = float(row["candidates"]["current_target"])
        valid, plan_rr = geometry_and_rr(
            str(row["direction"]), float(row["entry"]), float(row["stop"]),
            target, float(row["cost_points"])
        )
        if not valid or plan_rr is None or plan_rr + 1e-9 < 2.0:
            audit["below_minimum_rr_or_invalid"] += 1
            continue
        start_index = bisect.bisect_left(bar_times, row["observation"])
        path = evaluate_path(
            str(row["direction"]), float(row["entry"]), float(row["stop"]),
            target, bars, start_index, 0.01
        )
        known_at = path["known_at"]
        outcome = str(path["outcome"])
        if (
            known_at is None
            or known_at >= TRAIN_END_EXCLUSIVE
            or outcome not in {"TARGET_FIRST", "STOP_FIRST"}
        ):
            audit["ambiguous_or_unmatured"] += 1
            continue
        request_id = f"current_lifecycle_{row['observation'].strftime('%Y%m%d_%H%M')}"
        rows.append({
            "request_schema_version": REQUEST_SCHEMA_VERSION,
            "request_id": request_id,
            "observation_time": row["observation"].strftime("%Y.%m.%d %H:%M"),
            "outcome_known_at": known_at.strftime("%Y.%m.%d %H:%M"),
            "symbol": row["symbol"],
            "direction": row["direction"],
            "entry": row["entry"],
            "initial_stop": row["stop"],
            "target": target,
            "estimated_cost_points": row["cost_points"],
            "point_size": 0.01,
            "plan_rr": plan_rr,
            "baseline_outcome": outcome,
            "maximum_path_m5_bars": MAXIMUM_M5_PATH_BARS,
            "deployment_authorized": "false",
        })
    audit["requests"] = len(rows)
    if not rows:
        raise ValueError("Current-feed lifecycle request set is empty")
    if len({row["request_id"] for row in rows}) != len(rows):
        raise ValueError("Current-feed lifecycle request ID is duplicated")
    return rows, audit


def write_requests(
    rows: list[dict[str, Any]], path: Path, manifest_path: Path,
    source_hashes: dict[str, str], audit: dict[str, int]
) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REQUEST_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    manifest = {
        "lifecycle_request_manifest_schema_version": MANIFEST_SCHEMA_VERSION,
        "request_schema_version": REQUEST_SCHEMA_VERSION,
        "research_stage": "current_feed_train_causal_m5_lifecycle_path_request",
        "status": STATUS,
        "train_end_exclusive": "2024.07.01 00:00",
        "source_hashes": source_hashes,
        "source_audit": audit,
        "requests": len(rows),
        "first_observation": rows[0]["observation_time"],
        "last_observation": rows[-1]["observation_time"],
        "timeframe": "PERIOD_M5",
        "maximum_path_m5_bars": MAXIMUM_M5_PATH_BARS,
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
        "request_file_sha256": sha256(path),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-request", required=True, type=Path)
    parser.add_argument("--target-manifest", required=True, type=Path)
    parser.add_argument("--target-export", required=True, type=Path)
    parser.add_argument("--decisions", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    arguments = parser.parse_args()
    if sha256(arguments.decisions) != EXPECTED_DECISIONS_SHA256:
        raise ValueError("Current-feed lifecycle Decisions SHA-256 mismatch")
    target_requests = read_requests(
        arguments.target_request, arguments.target_manifest
    )
    evidence = read_export(arguments.target_export, target_requests)
    bar_times, bars = load_paths(arguments.decisions)
    rows, audit = build_requests(evidence, bar_times, bars)
    manifest = write_requests(
        rows, arguments.output, arguments.manifest,
        {
            "target_request": sha256(arguments.target_request),
            "target_export": sha256(arguments.target_export),
            "decisions": sha256(arguments.decisions),
        },
        audit,
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
