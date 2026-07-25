"""XAU AI PLATFORM | Offline Research | Version 1.0.0.

Validate and replay outcome-blind current-feed structural Stop ladders on the
frozen Train-only Decision path. Validation/Test and Deployment remain locked.
"""

from __future__ import annotations

import argparse
import bisect
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

from build_setup_outcome_dataset import MAX_HOLDING_BARS, as_bool, evaluate_path, finite_float, parse_time, read_exact_csv
from diagnose_current_feed_setup_funnel import TRAIN_END_EXCLUSIVE, sha256
from replay_current_feed_targets import EXPECTED_DECISIONS_SHA256, read_requests
from replay_past_only_targets import geometry_and_rr, load_paths, summarize_candidate

EXPORT_COLUMNS = (
    "export_schema_version", "request_id", "observation_time", "symbol",
    "direction", "entry", "current_stop", "current_target",
    "estimated_cost_points", "cost_known", "minimum_rr",
    "m5_stop_1", "m5_stop_2", "m5_stop_3", "m5_stop_count",
    "m15_stop_1", "m15_stop_2", "m15_stop_3", "m15_stop_count",
    "known_time_valid", "deployment_authorized",
)
CANDIDATES = (
    "current_stop", "m5_stop_1", "m5_stop_2", "m5_stop_3",
    "m15_stop_1", "m15_stop_2", "m15_stop_3",
)


def read_stop_export(path: Path, requests: dict[str, dict[str, str]]) -> list[dict[str, Any]]:
    rows = read_exact_csv(path, EXPORT_COLUMNS)
    if len(rows) != len(requests):
        raise ValueError("Current-feed Stop export is incomplete")
    evidence: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in rows:
        request_id = row["request_id"]
        if request_id in seen or request_id not in requests:
            raise ValueError("Current-feed Stop export identifier is invalid")
        seen.add(request_id)
        request = requests[request_id]
        for field in ("observation_time", "symbol", "direction"):
            if row[field] != request[field]:
                raise ValueError(f"Current-feed Stop request mismatch: {field}")
        if row["export_schema_version"] != "1.0.0":
            raise ValueError("Current-feed Stop export schema changed")
        if not as_bool(row["known_time_valid"]) or as_bool(row["deployment_authorized"]):
            raise ValueError("Current-feed Stop causal/deployment lock changed")
        entry = finite_float(row["entry"], "entry")
        target = finite_float(row["current_target"], "current_target")
        cost = finite_float(row["estimated_cost_points"], "estimated_cost_points")
        minimum_rr = finite_float(row["minimum_rr"], "minimum_rr")
        baseline = finite_float(row["current_stop"], "current_stop")
        if not math.isclose(baseline, finite_float(request["structural_stop"], "structural_stop"), abs_tol=1e-6):
            raise ValueError("Current-feed Stop baseline changed")
        if not math.isclose(target, finite_float(request["current_target"], "current_target"), abs_tol=1e-6):
            raise ValueError("Current-feed Stop Target changed")
        if not math.isclose(cost, finite_float(request["estimated_cost_points"], "cost"), abs_tol=1e-6):
            raise ValueError("Current-feed Stop cost changed")
        if not math.isclose(minimum_rr, finite_float(request["minimum_rr"], "minimum_rr"), abs_tol=1e-6):
            raise ValueError("Current-feed Stop minimum RR changed")
        candidates = {name: finite_float(row[name], name) for name in CANDIDATES}
        for prefix in ("m5", "m15"):
            values = [candidates[f"{prefix}_stop_{index}"] for index in range(1, 4)]
            count = int(finite_float(row[f"{prefix}_stop_count"], "stop_count"))
            positive = [value for value in values if value > 0.0]
            if count != len(positive) or not 0 <= count <= 3:
                raise ValueError("Current-feed Stop ladder count is inconsistent")
            if row["direction"] == "TRADE_SETUP_BUY":
                ordered = all(value < entry for value in positive) and all(
                    positive[index] > positive[index + 1] for index in range(len(positive) - 1)
                )
            else:
                ordered = all(value > entry for value in positive) and all(
                    positive[index] < positive[index + 1] for index in range(len(positive) - 1)
                )
            if not ordered:
                raise ValueError("Current-feed Stop ladder order is invalid")
        evidence.append({
            "request_id": request_id, "observation": parse_time(row["observation_time"]),
            "direction": row["direction"], "entry": entry, "target": target,
            "cost_points": cost, "cost_known": as_bool(row["cost_known"]),
            "minimum_rr": minimum_rr, "candidates": candidates,
        })
    if seen != set(requests):
        raise ValueError("Current-feed Stop export coverage changed")
    return sorted(evidence, key=lambda item: item["observation"])


def replay_stop(evidence: list[dict[str, Any]], candidate: str, times: list, bars: list[dict[str, Any]]) -> dict[str, Any]:
    counts: Counter[str] = Counter()
    outcomes: list[dict[str, Any]] = []
    for row in evidence:
        stop = float(row["candidates"][candidate])
        if stop <= 0.0:
            counts["missing_stop"] += 1
            continue
        counts["stop_available"] += 1
        if not row["cost_known"]:
            counts["unknown_cost"] += 1
            continue
        valid, plan_rr = geometry_and_rr(row["direction"], row["entry"], stop, row["target"], row["cost_points"])
        if not valid or plan_rr is None:
            counts["invalid_geometry"] += 1
            continue
        counts["valid_cost_aware_geometry"] += 1
        if plan_rr + 1e-9 < row["minimum_rr"]:
            counts["below_minimum_rr"] += 1
            continue
        counts["minimum_rr_reached"] += 1
        path = evaluate_path(row["direction"], row["entry"], stop, row["target"], bars, bisect.bisect_left(times, row["observation"]), 0.01)
        known_at = path["known_at"]
        if known_at is None or known_at >= TRAIN_END_EXCLUSIVE:
            counts["unmatured_before_cutoff"] += 1
            continue
        outcome = str(path["outcome"])
        if outcome not in {"TARGET_FIRST", "STOP_FIRST", "TIMEOUT"}:
            counts["ambiguous_outcome"] += 1
            continue
        realized_r = plan_rr if outcome == "TARGET_FIRST" else (-1.0 if outcome == "STOP_FIRST" else 0.0)
        outcomes.append({"observation": row["observation"], "direction": row["direction"], "outcome": outcome, "plan_rr": plan_rr, "realized_r": realized_r})
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
    evidence = read_stop_export(arguments.export, requests)
    times, bars = load_paths(arguments.decisions)
    candidates = {name: replay_stop(evidence, name, times, bars) for name in CANDIDATES}
    passing = [name for name, value in candidates.items() if value["train_gate_passed"]]
    report = {
        "replay_schema_version": "1.0.0",
        "status": "CURRENT_FEED_STOP_REPLAY_TRAIN_ONLY_NO_GO",
        "train_end_exclusive": "2024.07.01 00:00",
        "validation_dataset_used": False, "test_dataset_used": False,
        "model_training_performed": False, "runtime_changed": False,
        "risk_changed": False, "minimum_rr_changed": False,
        "deployment_authorized": False, "maximum_holding_bars": MAX_HOLDING_BARS,
        "same_bar_target_stop_collision": "AMBIGUOUS_QUARANTINE",
        "request_file_sha256": sha256(arguments.request),
        "export_file_sha256": sha256(arguments.export),
        "decision_file_sha256": sha256(arguments.decisions),
        "requests": len(evidence), "candidates": candidates,
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
