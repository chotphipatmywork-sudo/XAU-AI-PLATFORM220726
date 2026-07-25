"""XAU AI PLATFORM | Offline Research | Version 1.0.0.

Replay the preregistered 7x7 current-feed Stop/Target structural frontier on
Train only. Entry, cost, holding horizon, and minimum RR remain frozen.
"""

from __future__ import annotations

import argparse
import bisect
import json
from collections import Counter
from pathlib import Path
from typing import Any

from build_setup_outcome_dataset import MAX_HOLDING_BARS, evaluate_path
from diagnose_current_feed_setup_funnel import TRAIN_END_EXCLUSIVE, sha256
from replay_current_feed_stops import CANDIDATES as STOP_CANDIDATES, read_stop_export
from replay_current_feed_targets import EXPECTED_DECISIONS_SHA256, read_requests
from replay_past_only_targets import CANDIDATE_COLUMNS as TARGET_CANDIDATES, geometry_and_rr, load_paths, read_export, summarize_candidate


def join_evidence(stops: list[dict[str, Any]], targets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    target_index = {row["request_id"]: row for row in targets}
    if len(target_index) != len(stops):
        raise ValueError("Joint frontier export coverage differs")
    joined: list[dict[str, Any]] = []
    for stop in stops:
        target = target_index.get(stop["request_id"])
        if target is None:
            raise ValueError("Joint frontier request identifier differs")
        for field in ("observation", "direction", "entry", "cost_points", "cost_known", "minimum_rr"):
            if stop[field] != target[field]:
                raise ValueError(f"Joint frontier parity changed: {field}")
        joined.append({
            **{key: stop[key] for key in ("request_id", "observation", "direction", "entry", "cost_points", "cost_known", "minimum_rr")},
            "stops": stop["candidates"], "targets": target["candidates"],
        })
    return joined


def replay_combination(evidence: list[dict[str, Any]], stop_name: str, target_name: str, times: list, bars: list[dict[str, Any]]) -> dict[str, Any]:
    counts: Counter[str] = Counter()
    outcomes: list[dict[str, Any]] = []
    for row in evidence:
        stop = float(row["stops"][stop_name])
        target = float(row["targets"][target_name])
        if stop <= 0.0 or target <= 0.0:
            counts["missing_geometry"] += 1
            continue
        counts["geometry_available"] += 1
        if not row["cost_known"]:
            counts["unknown_cost"] += 1
            continue
        valid, plan_rr = geometry_and_rr(row["direction"], row["entry"], stop, target, row["cost_points"])
        if not valid or plan_rr is None:
            counts["invalid_geometry"] += 1
            continue
        counts["valid_cost_aware_geometry"] += 1
        if plan_rr + 1e-9 < row["minimum_rr"]:
            counts["below_minimum_rr"] += 1
            continue
        counts["minimum_rr_reached"] += 1
        result = evaluate_path(row["direction"], row["entry"], stop, target, bars, bisect.bisect_left(times, row["observation"]), 0.01)
        known_at = result["known_at"]
        if known_at is None or known_at >= TRAIN_END_EXCLUSIVE:
            counts["unmatured_before_cutoff"] += 1
            continue
        outcome = str(result["outcome"])
        if outcome not in {"TARGET_FIRST", "STOP_FIRST", "TIMEOUT"}:
            counts["ambiguous_outcome"] += 1
            continue
        realized_r = plan_rr if outcome == "TARGET_FIRST" else (-1.0 if outcome == "STOP_FIRST" else 0.0)
        outcomes.append({"observation": row["observation"], "direction": row["direction"], "outcome": outcome, "plan_rr": plan_rr, "realized_r": realized_r})
    return summarize_candidate(f"{stop_name}__{target_name}", evidence, counts, outcomes)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", required=True, type=Path)
    parser.add_argument("--request-manifest", required=True, type=Path)
    parser.add_argument("--stop-export", required=True, type=Path)
    parser.add_argument("--target-export", required=True, type=Path)
    parser.add_argument("--decisions", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    arguments = parser.parse_args()
    if sha256(arguments.decisions) != EXPECTED_DECISIONS_SHA256:
        raise ValueError("Joint frontier Decision path SHA-256 mismatch")
    requests = read_requests(arguments.request, arguments.request_manifest)
    evidence = join_evidence(
        read_stop_export(arguments.stop_export, requests),
        read_export(arguments.target_export, requests),
    )
    times, bars = load_paths(arguments.decisions)
    combinations: dict[str, dict] = {}
    for stop_name in STOP_CANDIDATES:
        for target_name in TARGET_CANDIDATES:
            name = f"{stop_name}__{target_name}"
            combinations[name] = replay_combination(evidence, stop_name, target_name, times, bars)
    passing = [name for name, value in combinations.items() if value["train_gate_passed"]]
    ranked = sorted(
        (
            {"candidate": name, "mature_records": value["mature_records"], "mean_cost_aware_r": value["mean_cost_aware_r"], "train_gate_passed": value["train_gate_passed"]}
            for name, value in combinations.items()
        ),
        key=lambda item: (item["mean_cost_aware_r"] is not None, item["mean_cost_aware_r"] or float("-inf")),
        reverse=True,
    )
    report = {
        "schema_version": "1.0.0",
        "status": "CURRENT_FEED_JOINT_GEOMETRY_TRAIN_ONLY_NO_GO",
        "train_end_exclusive": "2024.07.01 00:00",
        "frontier_preregistered_before_outcome_replay": True,
        "stop_candidates": list(STOP_CANDIDATES), "target_candidates": list(TARGET_CANDIDATES),
        "combination_count": len(combinations),
        "entry_changed": False, "cost_changed": False, "minimum_rr_changed": False,
        "validation_dataset_used": False, "test_dataset_used": False,
        "runtime_changed": False, "risk_changed": False, "deployment_authorized": False,
        "request_sha256": sha256(arguments.request),
        "stop_export_sha256": sha256(arguments.stop_export),
        "target_export_sha256": sha256(arguments.target_export),
        "decision_sha256": sha256(arguments.decisions),
        "maximum_holding_bars": MAX_HOLDING_BARS,
        "combinations": combinations, "ranked_descriptive_only": ranked,
        "train_gate_passing_combinations": passing,
        "runtime_candidate_proposal_ready": bool(passing),
        "runtime_change_request_authorized": False,
        "deployment_remains_no_go": True,
    }
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"status": report["status"], "combination_count": len(combinations), "passing": passing, "top_10_descriptive_only": ranked[:10]}, indent=2))


if __name__ == "__main__":
    main()
