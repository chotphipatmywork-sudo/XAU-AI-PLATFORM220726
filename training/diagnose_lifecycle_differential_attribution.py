"""XAU AI PLATFORM | Offline Research Diagnostic | Version 1.0.0.

Attribute paired Baseline/Candidate M5 lifecycle return changes without
selecting a strategy, reading sealed evidence, or changing Runtime/Deployment.
"""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

from augment_pretrain_history import sha256
from build_lifecycle_path_requests import CANDIDATES, COST_MULTIPLIERS
from replay_lifecycle_management import (
    REPLAY_SCHEMA_VERSION,
    read_paths,
    read_requests,
    simulate_path,
)


DIAGNOSTIC_SCHEMA_VERSION = "1.0.0"
ATTRIBUTION_CATEGORIES = (
    "TARGET_PRESERVED",
    "TARGET_CLIPPED_BY_MANAGEMENT",
    "STOP_LOSS_IMPROVED_BY_MANAGEMENT",
    "STOP_UNCHANGED",
    "AMBIGUOUS_QUARANTINE",
)


def valid_hash(value: str, name: str) -> str:
    normalized = value.strip().upper()
    if len(normalized) != 64 or any(
        character not in "0123456789ABCDEF" for character in normalized
    ):
        raise ValueError(f"Lifecycle attribution {name} SHA-256 is invalid")
    return normalized


def close(left: float, right: float) -> bool:
    return math.isclose(left, right, rel_tol=1e-12, abs_tol=1e-12)


def attribute_transition(
    baseline: dict[str, Any], candidate: dict[str, Any]
) -> dict[str, Any]:
    baseline_outcome = str(baseline["outcome"])
    candidate_outcome = str(candidate["outcome"])
    baseline_r = baseline["realized_r"]
    candidate_r = candidate["realized_r"]
    if baseline_outcome not in {"TARGET_FIRST", "STOP_FIRST"} or baseline_r is None:
        raise ValueError("Lifecycle attribution Baseline is unresolved")
    if candidate_outcome == "AMBIGUOUS" and candidate_r is None:
        return {
            "category": "AMBIGUOUS_QUARANTINE",
            "baseline_r": float(baseline_r),
            "candidate_r": None,
            "delta_r": None,
        }
    if candidate_r is None or candidate_outcome == "UNRESOLVED":
        raise ValueError("Lifecycle attribution Candidate is unresolved")

    transition = (baseline_outcome, candidate_outcome)
    categories = {
        ("TARGET_FIRST", "TARGET_FIRST"): "TARGET_PRESERVED",
        ("TARGET_FIRST", "MANAGED_STOP"): "TARGET_CLIPPED_BY_MANAGEMENT",
        ("STOP_FIRST", "MANAGED_STOP"): "STOP_LOSS_IMPROVED_BY_MANAGEMENT",
        ("STOP_FIRST", "STOP_FIRST"): "STOP_UNCHANGED",
    }
    if transition not in categories:
        raise ValueError(f"Lifecycle attribution transition is invalid: {transition}")
    category = categories[transition]
    delta = float(candidate_r) - float(baseline_r)
    if category in {"TARGET_PRESERVED", "STOP_UNCHANGED"} and not close(delta, 0.0):
        raise ValueError("Lifecycle attribution unchanged transition has Delta R")
    if category == "TARGET_CLIPPED_BY_MANAGEMENT" and delta >= 0.0:
        raise ValueError("Lifecycle attribution clipped Target has non-negative Delta R")
    if category == "STOP_LOSS_IMPROVED_BY_MANAGEMENT" and delta <= 0.0:
        raise ValueError("Lifecycle attribution improved Stop has non-positive Delta R")
    return {
        "category": category,
        "baseline_r": float(baseline_r),
        "candidate_r": float(candidate_r),
        "delta_r": delta,
    }


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    if not records:
        raise ValueError("Lifecycle attribution group is empty")
    categories = Counter(str(record["category"]) for record in records)
    if any(category not in ATTRIBUTION_CATEGORIES for category in categories):
        raise ValueError("Lifecycle attribution category changed")
    effective = [record for record in records if record["delta_r"] is not None]
    if not effective:
        raise ValueError("Lifecycle attribution group has no paired records")
    deltas = [float(record["delta_r"]) for record in effective]
    baseline_values = [float(record["baseline_r"]) for record in effective]
    candidate_values = [float(record["candidate_r"]) for record in effective]
    positive = sum(value for value in deltas if value > 0.0)
    negative = sum(value for value in deltas if value < 0.0)
    net = sum(deltas)
    return {
        "records": len(records),
        "effective_paired_records": len(effective),
        "ambiguous_quarantined": len(records)-len(effective),
        "categories": {
            category: categories.get(category, 0)
            for category in ATTRIBUTION_CATEGORIES
        },
        "baseline_outcomes": dict(sorted(Counter(
            str(record["baseline_outcome"]) for record in records
        ).items())),
        "candidate_outcomes": dict(sorted(Counter(
            str(record["candidate_outcome"]) for record in records
        ).items())),
        "paired_baseline_cumulative_r": sum(baseline_values),
        "paired_candidate_cumulative_r": sum(candidate_values),
        "paired_baseline_mean_r": sum(baseline_values)/len(effective),
        "paired_candidate_mean_r": sum(candidate_values)/len(effective),
        "positive_delta_r": positive,
        "negative_delta_r": negative,
        "net_delta_r": net,
        "mean_delta_r": net/len(effective),
        "positive_delta_records": sum(value > 0.0 for value in deltas),
        "negative_delta_records": sum(value < 0.0 for value in deltas),
        "zero_delta_records": sum(close(value, 0.0) for value in deltas),
        "benefit_to_harm_r_ratio": (
            positive/abs(negative) if negative < 0.0 else None
        ),
    }


def block_numbers(size: int) -> list[int]:
    if size < 4:
        raise ValueError("Lifecycle attribution requires four chronological blocks")
    result = [0] * size
    for block in range(4):
        start = block * size // 4
        end = (block + 1) * size // 4
        for index in range(start, end):
            result[index] = block + 1
    if any(number == 0 for number in result):
        raise AssertionError("Lifecycle attribution block assignment is incomplete")
    return result


def summarize_candidate(
    requests: list[dict[str, Any]],
    paths: dict[str, list[dict[str, Any]]],
    candidate: str,
    multiplier: float,
) -> dict[str, Any]:
    if candidate not in CANDIDATES[1:] or multiplier not in COST_MULTIPLIERS:
        raise ValueError("Lifecycle attribution Candidate/cost changed")
    blocks = block_numbers(len(requests))
    records: list[dict[str, Any]] = []
    for index, request in enumerate(requests):
        path = paths[request["request_id"]]
        baseline = simulate_path(request, path, CANDIDATES[0], multiplier)
        managed = simulate_path(request, path, candidate, multiplier)
        attribution = attribute_transition(baseline, managed)
        records.append({
            "request_id": request["request_id"],
            "observation_time": request["observation_time"],
            "direction": request["direction"],
            "chronological_block": blocks[index],
            "baseline_outcome": baseline["outcome"],
            "candidate_outcome": managed["outcome"],
            "candidate_reason": managed["reason"],
            **attribution,
        })
    directions = {
        direction: summarize([
            record for record in records if record["direction"] == direction
        ])
        for direction in ("TRADE_SETUP_BUY", "TRADE_SETUP_SELL")
    }
    chronological = []
    for number in range(1, 5):
        selected = [
            record for record in records
            if record["chronological_block"] == number
        ]
        chronological.append({
            "block": number,
            "first_observation": selected[0]["observation_time"],
            "last_observation": selected[-1]["observation_time"],
            **summarize(selected),
        })
    return {
        "overall": summarize(records),
        "by_direction": directions,
        "chronological_blocks": chronological,
    }


def diagnose(
    request_path: Path,
    manifest_path: Path,
    export_path: Path,
    replay_path: Path,
    expected_replay_sha256: str,
) -> dict[str, Any]:
    replay_hash = sha256(replay_path)
    if replay_hash != valid_hash(expected_replay_sha256, "replay"):
        raise ValueError("Lifecycle attribution replay SHA-256 mismatch")
    replay = json.loads(replay_path.read_text(encoding="utf-8-sig"))
    protected_false = (
        "validation_dataset_read", "test_dataset_read", "model_training_performed",
        "runtime_changed", "risk_changed", "runtime_change_request_authorized",
        "deployment_authorized",
    )
    if replay.get("lifecycle_replay_schema_version") != REPLAY_SCHEMA_VERSION or (
        replay.get("baseline_parity_valid") is not True
    ) or replay.get("deployment_remains_no_go") is not True or any(
        replay.get(flag) is not False for flag in protected_false
    ) or replay.get("train_gate_passing_candidates") != []:
        raise ValueError("Lifecycle attribution replay protected state changed")

    requests, _ = read_requests(request_path, manifest_path)
    paths = read_paths(export_path, requests)
    evidence_parity = {
        "request_file_sha256": sha256(request_path),
        "request_manifest_sha256": sha256(manifest_path),
        "m5_path_export_sha256": sha256(export_path),
    }
    if any(replay.get(name) != value for name, value in evidence_parity.items()):
        raise ValueError("Lifecycle attribution evidence/replay hash parity failed")
    if replay.get("requests") != len(requests):
        raise ValueError("Lifecycle attribution request count changed")

    results: dict[str, dict[str, Any]] = {}
    for candidate in CANDIDATES[1:]:
        results[candidate] = {}
        for multiplier in COST_MULTIPLIERS:
            summary = summarize_candidate(requests, paths, candidate, multiplier)
            replay_summary = replay["candidate_results"][candidate][str(multiplier)]
            overall = summary["overall"]
            if overall["effective_paired_records"] != replay_summary[
                "effective_records"
            ] or not close(
                overall["paired_candidate_mean_r"],
                replay_summary["metrics"]["mean_cost_aware_r"],
            ) or overall["candidate_outcomes"] != replay_summary["accounting"]:
                raise ValueError("Lifecycle attribution/replay result parity failed")
            results[candidate][str(multiplier)] = summary

    return {
        "lifecycle_differential_attribution_schema_version": DIAGNOSTIC_SCHEMA_VERSION,
        "status": "LIFECYCLE_DIFFERENTIAL_ATTRIBUTION_TRAIN_ONLY_NO_GO",
        **evidence_parity,
        "lifecycle_replay_sha256": replay_hash,
        "requests": len(requests),
        "attribution_categories": list(ATTRIBUTION_CATEGORIES),
        "candidate_results": results,
        "candidate_selected": False,
        "subgroup_filter_authorized": False,
        "validation_dataset_read": False,
        "test_dataset_read": False,
        "model_training_performed": False,
        "runtime_changed": False,
        "risk_changed": False,
        "runtime_change_request_authorized": False,
        "deployment_authorized": False,
        "deployment_remains_no_go": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", required=True, type=Path)
    parser.add_argument("--request-manifest", required=True, type=Path)
    parser.add_argument("--m5-path-export", required=True, type=Path)
    parser.add_argument("--lifecycle-replay", required=True, type=Path)
    parser.add_argument("--expected-replay-sha256", required=True)
    parser.add_argument("--output", required=True, type=Path)
    arguments = parser.parse_args()
    report = diagnose(
        arguments.request,
        arguments.request_manifest,
        arguments.m5_path_export,
        arguments.lifecycle_replay,
        arguments.expected_replay_sha256,
    )
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

