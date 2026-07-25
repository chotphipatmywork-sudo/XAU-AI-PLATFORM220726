"""Build frozen M5 causal-path requests for the IMP-095 research lead."""

from __future__ import annotations

import argparse
import bisect
import csv
import json
from pathlib import Path

from analyze_current_feed_joint_geometry import join_evidence
from build_lifecycle_path_requests import MAXIMUM_M5_PATH_BARS, REQUEST_COLUMNS, REQUEST_SCHEMA_VERSION
from build_setup_outcome_dataset import evaluate_path
from diagnose_current_feed_setup_funnel import TRAIN_END_EXCLUSIVE, sha256
from replay_current_feed_stops import read_stop_export
from replay_current_feed_targets import EXPECTED_DECISIONS_SHA256, read_requests
from replay_past_only_targets import geometry_and_rr, load_paths, read_export

STOP_NAME = "m5_stop_2"
TARGET_NAME = "m15_target_1"


def build(evidence: list[dict], times: list, bars: list[dict]) -> list[dict]:
    rows: list[dict] = []
    for row in evidence:
        stop = float(row["stops"][STOP_NAME])
        target = float(row["targets"][TARGET_NAME])
        if stop <= 0.0 or target <= 0.0 or not row["cost_known"]:
            continue
        valid, plan_rr = geometry_and_rr(row["direction"], row["entry"], stop, target, row["cost_points"])
        if not valid or plan_rr is None or plan_rr + 1e-9 < row["minimum_rr"]:
            continue
        result = evaluate_path(row["direction"], row["entry"], stop, target, bars, bisect.bisect_left(times, row["observation"]), 0.01)
        known_at = result["known_at"]
        outcome = str(result["outcome"])
        if known_at is None or known_at >= TRAIN_END_EXCLUSIVE or outcome not in {"TARGET_FIRST", "STOP_FIRST"}:
            continue
        rows.append({
            "request_schema_version": REQUEST_SCHEMA_VERSION,
            "request_id": f"joint_m5_{row['observation'].strftime('%Y%m%d_%H%M')}",
            "observation_time": row["observation"].strftime("%Y.%m.%d %H:%M"),
            "outcome_known_at": known_at.strftime("%Y.%m.%d %H:%M"),
            "symbol": "XAUUSD", "direction": row["direction"], "entry": row["entry"],
            "initial_stop": stop, "target": target,
            "estimated_cost_points": row["cost_points"], "point_size": 0.01,
            "plan_rr": plan_rr, "baseline_outcome": outcome,
            "maximum_path_m5_bars": MAXIMUM_M5_PATH_BARS,
            "deployment_authorized": "false",
        })
    if len(rows) != 76:
        raise ValueError(f"Frozen joint M5 request count changed: {len(rows)}")
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("request", "request_manifest", "stop_export", "target_export", "decisions", "output", "manifest"):
        parser.add_argument(f"--{name.replace('_', '-')}", required=True, type=Path)
    args = parser.parse_args()
    if sha256(args.decisions) != EXPECTED_DECISIONS_SHA256:
        raise ValueError("Joint M5 Decision hash changed")
    requests = read_requests(args.request, args.request_manifest)
    evidence = join_evidence(read_stop_export(args.stop_export, requests), read_export(args.target_export, requests))
    times, bars = load_paths(args.decisions)
    rows = build(evidence, times, bars)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REQUEST_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    manifest = {
        "schema_version": "1.0.0",
        "status": "CURRENT_FEED_JOINT_M5_CAUSAL_DIAGNOSTIC_NO_GO",
        "selected_after_train_frontier": True,
        "independent_confirmation": False,
        "stop_candidate": STOP_NAME, "target_candidate": TARGET_NAME,
        "requests": len(rows), "train_end_exclusive": "2024.07.01 00:00",
        "validation_dataset_used": False, "test_dataset_used": False,
        "runtime_changed": False, "risk_changed": False,
        "deployment_authorized": False,
        "request_sha256": sha256(args.output),
        "source_hashes": {
            "stop_export": sha256(args.stop_export),
            "target_export": sha256(args.target_export),
            "decisions": sha256(args.decisions),
        },
    }
    args.manifest.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
