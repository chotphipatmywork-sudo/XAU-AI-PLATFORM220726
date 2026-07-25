"""XAU AI PLATFORM | Offline Research | Version 1.0.0.

Replay frozen past-only structural Target ladders on quality-admissible Train
evidence. The tool cannot read Validation/Test or authorize deployment.
"""

from __future__ import annotations

import argparse
import bisect
import csv
import json
import math
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from analyze_shadow_run import DECISION_COLUMNS
from build_setup_outcome_dataset import (
    MAX_HOLDING_BARS,
    as_bool,
    evaluate_path,
    finite_float,
    parse_time,
    read_exact_csv,
    validate_decisions,
)
from build_past_only_target_requests import REQUEST_COLUMNS
from diagnose_structural_opportunity import (
    MINIMUM_RR,
    POINT_SIZE,
    TRAIN_END_EXCLUSIVE,
    load_excluded_dates,
    sha256,
    validate_split_summary,
)


REPLAY_SCHEMA_VERSION = "1.0.0"
MINIMUM_MATURE_RECORDS = 200
EXPORT_COLUMNS = (
    "export_schema_version",
    "request_id",
    "source",
    "observation_time",
    "symbol",
    "direction",
    "entry_bar_open",
    "entry_price",
    "expected_entry",
    "entry_parity_required",
    "entry_parity_valid",
    "structural_stop",
    "current_target",
    "estimated_cost_points",
    "cost_known",
    "minimum_rr",
    "m5_target_1",
    "m5_target_2",
    "m5_target_3",
    "m5_target_count",
    "m15_target_1",
    "m15_target_2",
    "m15_target_3",
    "m15_target_count",
    "known_time_valid",
    "deployment_authorized",
)
CANDIDATE_COLUMNS = (
    "current_target",
    "m5_target_1",
    "m5_target_2",
    "m5_target_3",
    "m15_target_1",
    "m15_target_2",
    "m15_target_3",
)


def read_request_file(path: Path, manifest_path: Path) -> dict[str, dict[str, str]]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    if manifest.get("request_schema_version") != "1.0.0":
        raise ValueError("Past-only Target request manifest schema changed")
    if manifest.get("validation_dataset_used") is not False or (
        manifest.get("test_dataset_used") is not False
    ):
        raise ValueError("Past-only Target request manifest opened sealed data")
    if manifest.get("deployment_authorized") is not False:
        raise ValueError("Deployable Target request manifest is forbidden")
    if manifest.get("request_file_sha256") != sha256(path):
        raise ValueError("Past-only Target request hash mismatch")
    rows = read_exact_csv(path, REQUEST_COLUMNS)
    if manifest.get("requests") != len(rows):
        raise ValueError("Past-only Target request count mismatch")
    indexed: dict[str, dict[str, str]] = {}
    for row in rows:
        request_id = row["request_id"]
        if request_id in indexed:
            raise ValueError("Past-only Target request identifier is duplicated")
        observation = parse_time(row["observation_time"])
        if observation >= TRAIN_END_EXCLUSIVE:
            raise ValueError("Past-only Target request crossed Train cutoff")
        indexed[request_id] = row
    return indexed


def read_export(
    path: Path, requests: dict[str, dict[str, str]]
) -> list[dict[str, Any]]:
    rows = read_exact_csv(path, EXPORT_COLUMNS)
    if len(rows) != len(requests):
        raise ValueError("Past-only Target export is incomplete")
    parsed: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in rows:
        request_id = row["request_id"]
        if request_id in seen or request_id not in requests:
            raise ValueError("Past-only Target export identifier is invalid")
        seen.add(request_id)
        request = requests[request_id]
        for field in (
            "source", "observation_time", "symbol", "direction", "entry_bar_open"
        ):
            if row[field] != request[field]:
                raise ValueError(f"Past-only Target export request mismatch: {field}")
        if row["export_schema_version"] != "1.0.0":
            raise ValueError("Past-only Target export schema changed")
        if not as_bool(row["known_time_valid"]):
            raise ValueError("Past-only Target export contains non-causal evidence")
        if not as_bool(row["entry_parity_valid"]):
            raise ValueError("Past-only Target Entry parity failed")
        if as_bool(row["deployment_authorized"]):
            raise ValueError("Deployable past-only Target export is forbidden")
        entry = finite_float(row["entry_price"], "entry_price")
        stop = finite_float(row["structural_stop"], "structural_stop")
        cost = finite_float(row["estimated_cost_points"], "estimated_cost_points")
        minimum_rr = finite_float(row["minimum_rr"], "minimum_rr")
        cost_known = as_bool(row["cost_known"])
        if entry <= 0.0 or stop <= 0.0 or cost < 0.0 or minimum_rr < MINIMUM_RR:
            raise ValueError("Past-only Target export plan evidence is invalid")
        if cost_known != as_bool(request["cost_known"]):
            raise ValueError("Past-only Target cost-known flag changed")
        if as_bool(row["entry_parity_required"]) != as_bool(
            request["entry_known"]
        ):
            raise ValueError("Past-only Target Entry parity requirement changed")
        if not math.isclose(
            cost,
            finite_float(request["estimated_cost_points"], "estimated_cost_points"),
            rel_tol=1e-9,
            abs_tol=1e-6,
        ):
            raise ValueError("Past-only Target estimated cost changed")
        if not math.isclose(
            minimum_rr,
            finite_float(request["minimum_rr"], "minimum_rr"),
            rel_tol=1e-9,
            abs_tol=1e-6,
        ):
            raise ValueError("Past-only Target minimum RR changed")
        if not math.isclose(
            stop,
            finite_float(request["structural_stop"], "structural_stop"),
            rel_tol=1e-9,
            abs_tol=1e-6,
        ):
            raise ValueError("Past-only Target structural Stop changed")
        candidate_values = {
            candidate: finite_float(row[candidate], candidate)
            for candidate in CANDIDATE_COLUMNS
        }
        if any(value < 0.0 for value in candidate_values.values()):
            raise ValueError("Past-only Target candidate is negative")
        if not math.isclose(
            candidate_values["current_target"],
            finite_float(request["current_target"], "current_target"),
            rel_tol=1e-9,
            abs_tol=1e-6,
        ):
            raise ValueError("Past-only Target V1 baseline changed")
        for prefix in ("m5", "m15"):
            values = [candidate_values[f"{prefix}_target_{index}"] for index in range(1, 4)]
            count = int(finite_float(row[f"{prefix}_target_count"], f"{prefix}_target_count"))
            positive = [value for value in values if value > 0.0]
            if count != len(positive) or not 0 <= count <= 3:
                raise ValueError("Past-only Target ladder count is inconsistent")
            if row["direction"] == "TRADE_SETUP_BUY":
                ordered = all(entry < value for value in positive) and all(
                    positive[index] < positive[index + 1]
                    for index in range(len(positive) - 1)
                )
            else:
                ordered = all(entry > value for value in positive) and all(
                    positive[index] > positive[index + 1]
                    for index in range(len(positive) - 1)
                )
            if not ordered:
                raise ValueError("Past-only Target ladder order is invalid")
        parsed.append({
            "request_id": request_id,
            "source": row["source"],
            "observation": parse_time(row["observation_time"]),
            "symbol": row["symbol"],
            "direction": row["direction"],
            "entry": entry,
            "stop": stop,
            "cost_points": cost,
            "cost_known": cost_known,
            "minimum_rr": minimum_rr,
            "candidates": candidate_values,
        })
    parsed.sort(key=lambda value: value["observation"])
    if set(seen) != set(requests):
        raise ValueError("Past-only Target export did not cover every request")
    return parsed


def load_paths(path: Path) -> tuple[list[datetime], list[dict[str, Any]]]:
    rows = read_exact_csv(path, DECISION_COLUMNS)
    _, bars = validate_decisions(rows)
    return [bar["time"] for bar in bars], bars


def geometry_and_rr(
    direction: str,
    entry: float,
    stop: float,
    target: float,
    cost_points: float,
) -> tuple[bool, float | None]:
    if direction == "TRADE_SETUP_BUY":
        valid = stop < entry < target
    elif direction == "TRADE_SETUP_SELL":
        valid = target < entry < stop
    else:
        raise ValueError("Past-only Target direction is invalid")
    if not valid:
        return False, None
    cost_price = cost_points * POINT_SIZE
    effective_risk = abs(entry - stop) + cost_price
    net_reward = abs(target - entry) - cost_price
    if effective_risk <= 0.0 or net_reward <= 0.0:
        return False, None
    return True, net_reward / effective_risk


def quality_dates_between(start: datetime, end: datetime) -> set[date]:
    dates: set[date] = set()
    current = start.date()
    while current <= end.date():
        dates.add(current)
        current += timedelta(days=1)
    return dates


def replay_candidate(
    evidence: list[dict[str, Any]],
    candidate: str,
    paths: dict[str, tuple[list[datetime], list[dict[str, Any]]]],
    exclusions: dict[str, frozenset[date]],
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
            str(row["direction"]),
            float(row["entry"]),
            float(row["stop"]),
            target,
            float(row["cost_points"]),
        )
        if not geometry_valid or plan_rr is None:
            counts["invalid_geometry"] += 1
            continue
        counts["valid_cost_aware_geometry"] += 1
        if plan_rr + 1e-9 < float(row["minimum_rr"]):
            counts["below_minimum_rr"] += 1
            continue
        counts["minimum_rr_reached"] += 1
        source = str(row["source"])
        bar_times, bars = paths[source]
        start_index = bisect.bisect_left(bar_times, row["observation"])
        path = evaluate_path(
            str(row["direction"]),
            float(row["entry"]),
            float(row["stop"]),
            target,
            bars,
            start_index,
            POINT_SIZE,
        )
        known_at = path["known_at"]
        if known_at is None or known_at >= TRAIN_END_EXCLUSIVE:
            counts["unmatured_before_cutoff"] += 1
            continue
        if quality_dates_between(row["observation"], known_at) & exclusions[source]:
            counts["quality_quarantined_outcome"] += 1
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


def chronological_block_metrics(outcomes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ordered = sorted(outcomes, key=lambda row: row["observation"])
    blocks: list[dict[str, Any]] = []
    for index in range(4):
        start = index * len(ordered) // 4
        end = (index + 1) * len(ordered) // 4
        block = ordered[start:end]
        blocks.append({
            "block": index + 1,
            "records": len(block),
            "mean_cost_aware_r": (
                sum(float(row["realized_r"]) for row in block) / len(block)
                if block else None
            ),
        })
    return blocks


def summarize_candidate(
    candidate: str,
    evidence: list[dict[str, Any]],
    counts: Counter[str],
    outcomes: list[dict[str, Any]],
) -> dict[str, Any]:
    outcome_counts = Counter(str(row["outcome"]) for row in outcomes)
    mean_r = (
        sum(float(row["realized_r"]) for row in outcomes) / len(outcomes)
        if outcomes else None
    )
    blocks = chronological_block_metrics(outcomes)
    direction_metrics: dict[str, Any] = {}
    for direction in ("TRADE_SETUP_BUY", "TRADE_SETUP_SELL"):
        subset = [row for row in outcomes if row["direction"] == direction]
        direction_metrics[direction] = {
            "records": len(subset),
            "mean_cost_aware_r": (
                sum(float(row["realized_r"]) for row in subset) / len(subset)
                if subset else None
            ),
        }
    gate_passed = (
        len(outcomes) >= MINIMUM_MATURE_RECORDS
        and mean_r is not None
        and mean_r > 0.0
        and all(
            block["records"] > 0
            and block["mean_cost_aware_r"] is not None
            and float(block["mean_cost_aware_r"]) > 0.0
            for block in blocks
        )
    )
    return {
        "candidate": candidate,
        "requests": len(evidence),
        "accounting": dict(sorted(counts.items())),
        "mature_records": len(outcomes),
        "outcomes": dict(sorted(outcome_counts.items())),
        "target_rate": (
            outcome_counts.get("TARGET_FIRST", 0) / len(outcomes)
            if outcomes else None
        ),
        "mean_cost_aware_r": mean_r,
        "by_direction": direction_metrics,
        "chronological_blocks": blocks,
        "train_gate_passed": gate_passed,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", required=True, type=Path)
    parser.add_argument("--request-manifest", required=True, type=Path)
    parser.add_argument("--export", required=True, type=Path)
    parser.add_argument("--pretrain-decisions", required=True, type=Path)
    parser.add_argument("--main-decisions", required=True, type=Path)
    parser.add_argument("--pretrain-exclusions", required=True, type=Path)
    parser.add_argument("--main-exclusions", required=True, type=Path)
    parser.add_argument("--split-summary", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    arguments = parser.parse_args()

    if validate_split_summary(arguments.split_summary) != TRAIN_END_EXCLUSIVE:
        raise ValueError("Past-only Target replay Train cutoff changed")
    requests = read_request_file(arguments.request, arguments.request_manifest)
    evidence = read_export(arguments.export, requests)
    paths = {
        "pretrain_202001_202106": load_paths(arguments.pretrain_decisions),
        "train_202107_202507": load_paths(arguments.main_decisions),
    }
    exclusions = {
        "pretrain_202001_202106": load_excluded_dates(
            arguments.pretrain_exclusions
        ),
        "train_202107_202507": load_excluded_dates(arguments.main_exclusions),
    }
    candidates = {
        candidate: replay_candidate(evidence, candidate, paths, exclusions)
        for candidate in CANDIDATE_COLUMNS
    }
    passing = [
        candidate for candidate, report in candidates.items()
        if report["train_gate_passed"]
    ]
    report = {
        "replay_schema_version": REPLAY_SCHEMA_VERSION,
        "status": "PAST_ONLY_TARGET_REPLAY_TRAIN_ONLY_NO_GO",
        "train_end_exclusive": TRAIN_END_EXCLUSIVE.strftime("%Y.%m.%d %H:%M"),
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
