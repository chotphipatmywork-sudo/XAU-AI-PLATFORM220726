"""XAU AI PLATFORM | Offline Research | Version 1.0.0.

Describe current-feed Entry/Stop geometry and 64-bar paths for all valid
reversal contexts before the frozen Train cutoff. This selects no candidate.
"""

from __future__ import annotations

import argparse
import bisect
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from build_setup_outcome_dataset import (
    MAX_HOLDING_BARS,
    SETUP_AUDIT_COLUMNS_V3,
    evaluate_path,
    finite_float,
    parse_time,
)
from diagnose_current_feed_setup_funnel import (
    EXPECTED_SETUP_SHA256,
    TRAIN_END_EXCLUSIVE,
    sha256,
)
from replay_current_feed_targets import (
    EXPECTED_DECISIONS_SHA256,
    read_requests,
)
from replay_past_only_targets import load_paths, read_export


DIAGNOSTIC_SCHEMA_VERSION = "1.0.0"


def fixed_bucket(value: float, cuts: tuple[float, ...]) -> str:
    lower = 0.0
    for upper in cuts:
        if value < upper:
            return f"{lower:.2f}_{upper:.2f}"
        lower = upper
    return f"{lower:.2f}_plus"


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {"records": 0}
    outcomes = Counter(str(row["outcome"]) for row in rows)
    realized = [float(row["realized_r"]) for row in rows]
    return {
        "records": len(rows),
        "outcomes": dict(sorted(outcomes.items())),
        "target_rate": outcomes.get("TARGET_FIRST", 0) / len(rows),
        "mean_gross_r": sum(realized) / len(realized),
        "stop_first_with_mfe_at_least_0_5r": sum(
            row["outcome"] == "STOP_FIRST" and row["mfe_r"] >= 0.5
            for row in rows
        ),
        "stop_first_with_mfe_at_least_1_0r": sum(
            row["outcome"] == "STOP_FIRST" and row["mfe_r"] >= 1.0
            for row in rows
        ),
    }


def build_diagnostic(
    evidence: list[dict[str, Any]],
    setup_by_time: dict,
    bar_times: list,
    bars: list[dict[str, Any]],
) -> dict[str, Any]:
    accounting: Counter[str] = Counter()
    analyzed: list[dict[str, Any]] = []
    for row in evidence:
        accounting["requests"] += 1
        if not row["cost_known"]:
            accounting["unknown_entry_or_cost"] += 1
            continue
        setup = setup_by_time.get(row["observation"])
        if setup is None:
            raise ValueError("Entry/Stop context has no Setup Audit parity")
        entry = float(row["entry"])
        stop = float(row["stop"])
        target = float(row["candidates"]["current_target"])
        direction = str(row["direction"])
        if direction == "TRADE_SETUP_BUY":
            geometry_valid = stop < entry < target
        else:
            geometry_valid = target < entry < stop
        if not geometry_valid:
            accounting["invalid_geometry"] += 1
            continue
        risk = abs(entry - stop)
        reward = abs(target - entry)
        if risk <= 0.0 or reward <= 0.0:
            accounting["non_positive_geometry"] += 1
            continue
        accounting["valid_geometry"] += 1
        gross_rr = reward / risk
        reference_poi = finite_float(setup["reference_poi"], "reference_poi")
        reclaim_atr = finite_float(
            setup["reclaim_distance_atr"], "reclaim_distance_atr"
        )
        engulfment_atr = finite_float(
            setup["trigger_engulfment_atr"], "trigger_engulfment_atr"
        )
        if reclaim_atr <= 0.0:
            raise ValueError("Entry/Stop reclaim ATR is not positive")
        atr = abs(entry - reference_poi) / reclaim_atr
        if atr <= 0.0 or not math.isfinite(atr):
            raise ValueError("Entry/Stop derived ATR is invalid")
        stop_distance_atr = risk / atr
        start_index = bisect.bisect_left(bar_times, row["observation"])
        path = evaluate_path(
            direction, entry, stop, target, bars, start_index, 0.01
        )
        if path["known_at"] is None or path["known_at"] >= TRAIN_END_EXCLUSIVE:
            accounting["unmatured_before_cutoff"] += 1
            continue
        outcome = str(path["outcome"])
        if outcome not in {"TARGET_FIRST", "STOP_FIRST", "TIMEOUT"}:
            accounting["ambiguous"] += 1
            continue
        realized_r = gross_rr if outcome == "TARGET_FIRST" else (
            -1.0 if outcome == "STOP_FIRST" else 0.0
        )
        analyzed.append({
            "observation": row["observation"],
            "direction": direction,
            "outcome": outcome,
            "realized_r": realized_r,
            "mfe_r": float(path["mfe_r"]),
            "mae_r": float(path["mae_r"]),
            "gross_rr_bucket": fixed_bucket(gross_rr, (0.5, 1.0, 2.0)),
            "stop_atr_bucket": fixed_bucket(
                stop_distance_atr, (0.5, 1.0, 1.5)
            ),
            "engulfment_atr_bucket": fixed_bucket(
                engulfment_atr, (0.25, 0.5, 1.0)
            ),
            "reclaim_atr_bucket": fixed_bucket(
                reclaim_atr, (0.1, 0.25, 0.5)
            ),
        })
    groups: dict[str, dict[str, Any]] = {}
    for field in (
        "gross_rr_bucket", "stop_atr_bucket",
        "engulfment_atr_bucket", "reclaim_atr_bucket", "direction",
    ):
        values: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in analyzed:
            values[str(row[field])].append(row)
        groups[field] = {
            key: summarize(value) for key, value in sorted(values.items())
        }
    blocks = []
    for index in range(4):
        start = index * len(analyzed) // 4
        end = (index + 1) * len(analyzed) // 4
        blocks.append({"block": index + 1, **summarize(analyzed[start:end])})
    return {
        "diagnostic_schema_version": DIAGNOSTIC_SCHEMA_VERSION,
        "status": "CURRENT_FEED_ENTRY_STOP_DIAGNOSTIC_TRAIN_ONLY_NO_GO",
        "train_end_exclusive": "2024.07.01 00:00",
        "accounting": dict(accounting),
        "overall": summarize(analyzed),
        "groups": groups,
        "chronological_blocks": blocks,
        "entry_candidate_selected": False,
        "stop_candidate_selected": False,
        "minimum_rr_changed": False,
        "validation_dataset_used": False,
        "test_dataset_used": False,
        "training_performed": False,
        "runtime_changed": False,
        "risk_changed": False,
        "deployment_authorized": False,
        "limitations": [
            "Current Target/Stop outcomes are descriptive even when gross RR is below 2.0; they do not represent authorized trades.",
            "ATR is reconstructed from the frozen Entry-to-POI reclaim distance and the recorded reclaim_distance_atr.",
            "M15 bars cannot resolve same-bar Target/Stop ordering; those paths remain ambiguous.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", required=True, type=Path)
    parser.add_argument("--request-manifest", required=True, type=Path)
    parser.add_argument("--export", required=True, type=Path)
    parser.add_argument("--setup-audit", required=True, type=Path)
    parser.add_argument("--decisions", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    arguments = parser.parse_args()
    if sha256(arguments.setup_audit) != EXPECTED_SETUP_SHA256:
        raise ValueError("Entry/Stop Setup Audit SHA-256 mismatch")
    if sha256(arguments.decisions) != EXPECTED_DECISIONS_SHA256:
        raise ValueError("Entry/Stop Decisions SHA-256 mismatch")
    requests = read_requests(arguments.request, arguments.request_manifest)
    evidence = read_export(arguments.export, requests)
    setup_by_time = {}
    with arguments.setup_audit.open(
        "r", encoding="utf-8-sig", newline=""
    ) as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != SETUP_AUDIT_COLUMNS_V3:
            raise ValueError("Entry/Stop Setup Audit schema mismatch")
        for row in reader:
            observation = parse_time(row["observation_time"])
            if observation >= TRAIN_END_EXCLUSIVE:
                break
            if row["reversal_context_confirmed"] == "true":
                setup_by_time[observation] = row
    bar_times, bars = load_paths(arguments.decisions)
    report = build_diagnostic(evidence, setup_by_time, bar_times, bars)
    report["request_file_sha256"] = sha256(arguments.request)
    report["export_file_sha256"] = sha256(arguments.export)
    report["setup_audit_sha256"] = sha256(arguments.setup_audit)
    report["decision_file_sha256"] = sha256(arguments.decisions)
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
