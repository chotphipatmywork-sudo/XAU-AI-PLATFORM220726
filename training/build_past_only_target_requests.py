"""XAU AI PLATFORM | Offline Research | Version 1.0.0.

Build a frozen Train-only request file for the isolated MT5 past-only
structural Target-ladder exporter. Validation/Test are never read.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from build_setup_outcome_dataset import (
    SETUP_AUDIT_COLUMNS_V1,
    as_bool,
    finite_float,
    parse_time,
)
from diagnose_structural_opportunity import (
    MINIMUM_RR,
    TRAIN_END_EXCLUSIVE,
    load_excluded_dates,
    read_decision_context,
    sha256,
    validate_split_summary,
    verify_frozen_hashes,
)


REQUEST_SCHEMA_VERSION = "1.0.0"
REQUEST_COLUMNS = (
    "request_schema_version",
    "request_id",
    "source",
    "observation_time",
    "symbol",
    "direction",
    "entry_bar_open",
    "expected_entry",
    "entry_known",
    "structural_stop",
    "current_target",
    "estimated_cost_points",
    "cost_known",
    "minimum_rr",
)


def format_time(value: datetime) -> str:
    return value.strftime("%Y.%m.%d %H:%M")


def _plan_evidence(row: dict[str, str]) -> tuple[float, bool, float, bool]:
    entry = finite_float(row["plan_entry"], "plan_entry")
    stop = finite_float(row["plan_stop"], "plan_stop")
    target = finite_float(row["plan_target"], "plan_target")
    cost = finite_float(row["estimated_cost_points"], "estimated_cost_points")
    minimum_rr = finite_float(row["minimum_rr"], "minimum_rr")
    plan_values = (entry, stop, target)
    if all(value > 0.0 for value in plan_values):
        if cost < 0.0 or minimum_rr < MINIMUM_RR:
            raise ValueError("Known Target request plan evidence is invalid")
        return entry, True, cost, True
    if any(value != 0.0 for value in plan_values) or cost != 0.0 or minimum_rr != 0.0:
        raise ValueError("Unknown Target request plan evidence is inconsistent")
    return 0.0, False, 0.0, False


def build_requests_from_setup(
    path: Path,
    decisions: dict[datetime, dict[str, Any]],
    cutoff: datetime,
    excluded_dates: frozenset[date],
    source_name: str,
    require_cutoff: bool,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    requests: list[dict[str, object]] = []
    counts: Counter[str] = Counter()
    previous: datetime | None = None
    cutoff_reached = False
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or tuple(reader.fieldnames) != (
            SETUP_AUDIT_COLUMNS_V1
        ):
            raise ValueError("Unexpected Target request Setup Audit schema")
        for row in reader:
            observation = parse_time(row["observation_time"])
            if previous is not None and observation <= previous:
                raise ValueError("Target request Setup Audit is not chronological")
            previous = observation
            if observation >= cutoff:
                cutoff_reached = True
                break
            counts["source_rows"] += 1
            trigger = as_bool(row["trigger_confirmed"])
            if observation.date() in excluded_dates:
                counts["quality_excluded_rows"] += 1
                if trigger:
                    counts["quality_excluded_triggers"] += 1
                continue
            if not trigger:
                continue
            counts["trigger_rows"] += 1
            if observation not in decisions:
                raise ValueError("Target request trigger has no Train Decision")
            direction = row["direction"]
            if direction not in {"TRADE_SETUP_BUY", "TRADE_SETUP_SELL"}:
                raise ValueError("Target request direction is invalid")
            entry_bar_open = parse_time(row["entry_bar_open"])
            if entry_bar_open + timedelta(minutes=5) != observation:
                raise ValueError("Target request M5 trigger bar is not exactly closed")
            stop = finite_float(row["structural_stop"], "structural_stop")
            target = finite_float(row["nearest_target"], "nearest_target")
            if stop <= 0.0 or target <= 0.0:
                raise ValueError("Target request raw structural evidence is invalid")
            expected_entry, entry_known, cost, cost_known = _plan_evidence(row)
            if entry_known:
                counts["known_entry_and_cost_rows"] += 1
            else:
                counts["unknown_entry_and_cost_rows"] += 1
            request_id = f"{source_name}_{observation.strftime('%Y%m%d_%H%M')}"
            requests.append({
                "request_schema_version": REQUEST_SCHEMA_VERSION,
                "request_id": request_id,
                "source": source_name,
                "observation_time": format_time(observation),
                "symbol": row["symbol"],
                "direction": direction,
                "entry_bar_open": format_time(entry_bar_open),
                "expected_entry": expected_entry,
                "entry_known": str(entry_known).lower(),
                "structural_stop": stop,
                "current_target": target,
                "estimated_cost_points": cost,
                "cost_known": str(cost_known).lower(),
                "minimum_rr": MINIMUM_RR,
            })
    if require_cutoff and not cutoff_reached:
        raise ValueError("Target request main Setup Audit did not reach cutoff")
    if not requests:
        raise ValueError("Target request evidence is empty")
    return requests, {**counts, "cutoff_reached": cutoff_reached}


def write_requests(path: Path, rows: list[dict[str, object]]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REQUEST_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return sha256(path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pretrain-setup", required=True, type=Path)
    parser.add_argument("--pretrain-decisions", required=True, type=Path)
    parser.add_argument("--main-setup", required=True, type=Path)
    parser.add_argument("--main-decisions", required=True, type=Path)
    parser.add_argument("--augmented-train", required=True, type=Path)
    parser.add_argument("--pretrain-exclusions", required=True, type=Path)
    parser.add_argument("--main-exclusions", required=True, type=Path)
    parser.add_argument("--split-summary", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    arguments = parser.parse_args()

    paths = {
        "pretrain_setup": arguments.pretrain_setup,
        "pretrain_decisions": arguments.pretrain_decisions,
        "main_setup": arguments.main_setup,
        "main_decisions": arguments.main_decisions,
        "augmented_train": arguments.augmented_train,
        "pretrain_exclusions": arguments.pretrain_exclusions,
        "main_exclusions": arguments.main_exclusions,
        "split_summary": arguments.split_summary,
    }
    source_hashes = verify_frozen_hashes(paths)
    cutoff = validate_split_summary(arguments.split_summary)
    pretrain_exclusions = load_excluded_dates(arguments.pretrain_exclusions)
    main_exclusions = load_excluded_dates(arguments.main_exclusions)
    pretrain_decisions, pretrain_decision_audit = read_decision_context(
        arguments.pretrain_decisions, cutoff, pretrain_exclusions, False
    )
    main_decisions, main_decision_audit = read_decision_context(
        arguments.main_decisions, cutoff, main_exclusions, True
    )
    pretrain, pretrain_audit = build_requests_from_setup(
        arguments.pretrain_setup,
        pretrain_decisions,
        cutoff,
        pretrain_exclusions,
        "pretrain_202001_202106",
        False,
    )
    main, main_audit = build_requests_from_setup(
        arguments.main_setup,
        main_decisions,
        cutoff,
        main_exclusions,
        "train_202107_202507",
        True,
    )
    rows = sorted([*pretrain, *main], key=lambda row: str(row["observation_time"]))
    if len({row["request_id"] for row in rows}) != len(rows):
        raise ValueError("Target request identifiers are duplicated")
    if any(
        str(rows[index]["observation_time"])
        >= str(rows[index + 1]["observation_time"])
        for index in range(len(rows) - 1)
    ):
        raise ValueError("Target requests overlap or are not chronological")
    output_hash = write_requests(arguments.output, rows)
    manifest = {
        "request_schema_version": REQUEST_SCHEMA_VERSION,
        "status": "PAST_ONLY_TARGET_REQUESTS_TRAIN_ONLY_NO_GO",
        "train_end_exclusive": format_time(TRAIN_END_EXCLUSIVE),
        "validation_dataset_used": False,
        "test_dataset_used": False,
        "runtime_changed": False,
        "deployment_authorized": False,
        "source_hashes": source_hashes,
        "source_audits": {"pretrain": pretrain_audit, "main": main_audit},
        "decision_audits": {
            "pretrain": pretrain_decision_audit,
            "main": main_decision_audit,
        },
        "requests": len(rows),
        "request_file_sha256": output_hash,
    }
    arguments.manifest.parent.mkdir(parents=True, exist_ok=True)
    arguments.manifest.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()

