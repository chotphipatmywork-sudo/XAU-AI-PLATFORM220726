"""XAU AI PLATFORM | Offline Research | Version 1.0.0.

Validate and replay current-feed past-only Target ladders on the same frozen
Train-only Decision path. Validation/Test remain unread.
"""

from __future__ import annotations

import argparse
import bisect
import json
from collections import Counter
from pathlib import Path
from typing import Any

from build_past_only_target_requests import REQUEST_COLUMNS
from build_setup_outcome_dataset import (
    MAX_HOLDING_BARS,
    evaluate_path,
    parse_time,
    read_exact_csv,
)
from build_current_feed_target_requests import REQUEST_STATUS
from diagnose_current_feed_setup_funnel import TRAIN_END_EXCLUSIVE, sha256
from replay_past_only_targets import (
    CANDIDATE_COLUMNS,
    geometry_and_rr,
    load_paths,
    read_export,
    summarize_candidate,
)


REPLAY_SCHEMA_VERSION = "1.0.0"
EXPECTED_DECISIONS_SHA256 = (
    "A20A7B5F1399541C271D46999433B8C69B650D27F48DC3480B59E15E9C4022EC"
)


def read_requests(
    path: Path, manifest_path: Path
) -> dict[str, dict[str, str]]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    if manifest.get("status") != REQUEST_STATUS:
        raise ValueError("Current-feed Target request status changed")
    if manifest.get("train_end_exclusive") != "2024.07.01 00:00":
        raise ValueError("Current-feed Target Train cutoff changed")
    for key in (
        "validation_dataset_used", "test_dataset_used",
        "outcome_label_in_request", "runtime_changed",
        "minimum_rr_changed", "deployment_authorized",
    ):
        if manifest.get(key) is not False:
            raise ValueError(f"Current-feed Target request lock changed: {key}")
    if manifest.get("request_file_sha256") != sha256(path):
        raise ValueError("Current-feed Target request SHA-256 mismatch")
    rows = read_exact_csv(path, REQUEST_COLUMNS)
    if manifest.get("requests") != len(rows):
        raise ValueError("Current-feed Target request count mismatch")
    indexed: dict[str, dict[str, str]] = {}
    previous = None
    for row in rows:
        observation = parse_time(row["observation_time"])
        if observation >= TRAIN_END_EXCLUSIVE:
            raise ValueError("Current-feed Target request crossed Train cutoff")
        if previous is not None and observation <= previous:
            raise ValueError("Current-feed Target requests are not chronological")
        previous = observation
        if row["request_id"] in indexed:
            raise ValueError("Current-feed Target request ID is duplicated")
        indexed[row["request_id"]] = row
    return indexed


def replay_candidate(
    evidence: list[dict[str, Any]],
    candidate: str,
    bar_times: list,
    bars: list[dict[str, Any]],
) -> dict[str, Any]:
    counts: Counter[str] = Counter()
    outcomes: list[dict[str, Any]] = []
    for row in evidence:
        target = float(row["candidates"][candidate])
        if target <= 0.0:
            counts["missing_target"] += 1
            continue
        counts["target_available"] += 1
        if not row["cost_known"]:
            counts["unknown_cost"] += 1
            continue
        geometry_valid, plan_rr = geometry_and_rr(
            str(row["direction"]), float(row["entry"]), float(row["stop"]),
            target, float(row["cost_points"])
        )
        if not geometry_valid or plan_rr is None:
            counts["invalid_geometry"] += 1
            continue
        counts["valid_cost_aware_geometry"] += 1
        if plan_rr + 1e-9 < float(row["minimum_rr"]):
            counts["below_minimum_rr"] += 1
            continue
        counts["minimum_rr_reached"] += 1
        start_index = bisect.bisect_left(bar_times, row["observation"])
        path = evaluate_path(
            str(row["direction"]), float(row["entry"]), float(row["stop"]),
            target, bars, start_index, 0.01
        )
        known_at = path["known_at"]
        if known_at is None or known_at >= TRAIN_END_EXCLUSIVE:
            counts["unmatured_before_cutoff"] += 1
            continue
        outcome = str(path["outcome"])
        if outcome not in {"TARGET_FIRST", "STOP_FIRST", "TIMEOUT"}:
            counts["ambiguous_outcome"] += 1
            continue
        realized_r = plan_rr if outcome == "TARGET_FIRST" else (
            -1.0 if outcome == "STOP_FIRST" else 0.0
        )
        outcomes.append({
            "observation": row["observation"],
            "direction": row["direction"],
            "outcome": outcome,
            "plan_rr": plan_rr,
            "realized_r": realized_r,
        })
    return summarize_candidate(candidate, evidence, counts, outcomes)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", required=True, type=Path)
    parser.add_argument("--request-manifest", required=True, type=Path)
    parser.add_argument("--export", required=True, type=Path)
    parser.add_argument("--decisions", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    arguments = parser.parse_args()
    if sha256(arguments.decisions) != EXPECTED_DECISIONS_SHA256:
        raise ValueError("Current-feed Decision path SHA-256 mismatch")
    requests = read_requests(arguments.request, arguments.request_manifest)
    evidence = read_export(arguments.export, requests)
    bar_times, bars = load_paths(arguments.decisions)
    candidates = {
        candidate: replay_candidate(evidence, candidate, bar_times, bars)
        for candidate in CANDIDATE_COLUMNS
    }
    passing = [
        name for name, value in candidates.items()
        if value["train_gate_passed"]
    ]
    report = {
        "replay_schema_version": REPLAY_SCHEMA_VERSION,
        "status": "CURRENT_FEED_TARGET_REPLAY_TRAIN_ONLY_NO_GO",
        "train_end_exclusive": "2024.07.01 00:00",
        "validation_dataset_used": False,
        "test_dataset_used": False,
        "model_training_performed": False,
        "runtime_changed": False,
        "risk_changed": False,
        "minimum_rr_changed": False,
        "deployment_authorized": False,
        "maximum_holding_bars": MAX_HOLDING_BARS,
        "same_bar_target_stop_collision": "AMBIGUOUS_QUARANTINE",
        "request_file_sha256": sha256(arguments.request),
        "export_file_sha256": sha256(arguments.export),
        "decision_file_sha256": sha256(arguments.decisions),
        "requests": len(evidence),
        "candidates": candidates,
        "train_gate_passing_candidates": passing,
        "runtime_candidate_proposal_ready": bool(passing),
        "runtime_change_request_authorized": False,
        "deployment_remains_no_go": True,
    }
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
