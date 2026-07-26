"""Build outcome-free IMP-100 Train-only causal M5 replay requests."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from build_setup_outcome_dataset import parse_time
from diagnose_current_feed_setup_funnel import TRAIN_END_EXCLUSIVE, sha256
from validate_imp100_replay_contract import load_and_validate


ACTIVE_COLUMNS = (
    "request_schema_version",
    "request_id",
    "base_opportunity_id",
    "source_record_id",
    "arm_id",
    "observation_time",
    "symbol",
    "direction",
    "entry_price",
    "stop_identity",
    "stop_price",
    "target_identity",
    "target_price",
    "minimum_rr",
    "geometry_eligible",
    "common_support",
    "train_cutoff_compliant",
    "source_sha256",
    "deployment_authorized",
)
LEDGER_COLUMNS = (
    "ledger_schema_version",
    "request_id",
    "base_opportunity_id",
    "source_record_id",
    "arm_id",
    "observation_time",
    "direction",
    "entry_price",
    "stop_identity",
    "stop_price",
    "target_identity",
    "target_price",
    "minimum_rr",
    "structurally_valid",
    "cost_known",
    "geometry_eligible",
    "rr_pass",
    "replay_requested",
    "common_support",
    "no_trade_reason",
    "train_cutoff_compliant",
    "source_sha256",
    "validation_dataset_used",
    "test_dataset_used",
    "deployment_authorized",
)
FORBIDDEN_OUTCOME_FIELDS = {
    "outcome", "baseline_outcome", "realized_r", "expectancy",
    "target_first", "stop_first",
}


def truth(value: str) -> bool:
    return value.lower() == "true"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("IMP-100 raw experiment header missing")
        if FORBIDDEN_OUTCOME_FIELDS.intersection(reader.fieldnames):
            raise ValueError("IMP-100 source unexpectedly contains replay outcomes")
        return list(reader)


def unique_request_id(arm_id: str, base_id: str) -> str:
    return f"imp100__{arm_id.lower()}__{base_id}"


def no_trade_reason(row: dict[str, str]) -> str:
    if float(row["stop"]) <= 0.0 or float(row["target"]) <= 0.0:
        return "MISSING_GEOMETRY"
    if not truth(row["structurally_valid"]):
        return "STRUCTURALLY_INVALID"
    if not truth(row["cost_known"]):
        return "COST_UNKNOWN"
    if not truth(row["eligible"]):
        return "FAILED_ELIGIBILITY"
    if not truth(row["rr_pass"]):
        return "BELOW_MINIMUM_RR"
    return "ACTIVE_REPLAY_REQUEST"


def build(
    contract: dict[str, Any],
    raw_rows: list[dict[str, str]],
    raw_sha256: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    expected_arms = {
        arm["arm_id"]: (arm["stop_identity"], arm["target_identity"])
        for arm in contract["arms"]
    }
    if len(raw_rows) != 2388:
        raise ValueError("IMP-100 arm-record accounting changed")
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in raw_rows:
        grouped[row["request_id"]].append(row)
    if len(grouped) != 597 or any(len(rows) != 4 for rows in grouped.values()):
        raise ValueError("IMP-100 request-level pairing changed")
    common_ids = {
        base_id for base_id, rows in grouped.items()
        if all(truth(row["common_support"]) for row in rows)
    }
    if len(common_ids) != 362:
        raise ValueError("IMP-100 common-support accounting changed")

    ledger: list[dict[str, Any]] = []
    active: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    arm_passes: Counter[str] = Counter()
    arm_order = {
        arm["arm_id"]: index for index, arm in enumerate(contract["arms"])
    }
    ordered = sorted(
        raw_rows,
        key=lambda row: (
            parse_time(row["observation_time"]),
            row["request_id"],
            arm_order[row["arm_id"]],
        ),
    )
    for row in ordered:
        arm_id = row["arm_id"]
        if arm_id not in expected_arms:
            raise ValueError(f"IMP-100 unknown arm: {arm_id}")
        stop_identity, target_identity = expected_arms[arm_id]
        if (row["stop_name"], row["target_name"]) != (
            stop_identity, target_identity
        ):
            raise ValueError("IMP-100 arm geometry mapping changed")
        observation = parse_time(row["observation_time"])
        cutoff_compliant = observation < TRAIN_END_EXCLUSIVE
        if not cutoff_compliant:
            raise ValueError("IMP-100 Train cutoff violated")
        request_id = unique_request_id(arm_id, row["request_id"])
        if request_id in seen_ids:
            raise ValueError("IMP-100 duplicate arm-specific request ID")
        seen_ids.add(request_id)
        replay_requested = truth(row["rr_pass"])
        reason = no_trade_reason(row)
        common_support = row["request_id"] in common_ids
        ledger_row = {
            "ledger_schema_version": "1.0.0",
            "request_id": request_id,
            "base_opportunity_id": row["request_id"],
            "source_record_id": row["request_id"],
            "arm_id": arm_id,
            "observation_time": row["observation_time"],
            "direction": row["direction"],
            "entry_price": row["entry"],
            "stop_identity": row["stop_name"],
            "stop_price": row["stop"],
            "target_identity": row["target_name"],
            "target_price": row["target"],
            "minimum_rr": row["minimum_rr"],
            "structurally_valid": row["structurally_valid"],
            "cost_known": row["cost_known"],
            "geometry_eligible": row["eligible"],
            "rr_pass": row["rr_pass"],
            "replay_requested": str(replay_requested).lower(),
            "common_support": str(common_support).lower(),
            "no_trade_reason": reason,
            "train_cutoff_compliant": "true",
            "source_sha256": raw_sha256,
            "validation_dataset_used": "false",
            "test_dataset_used": "false",
            "deployment_authorized": "false",
        }
        ledger.append(ledger_row)
        if not replay_requested:
            continue
        arm_passes[arm_id] += 1
        active.append({
            "request_schema_version": "1.0.0",
            "request_id": request_id,
            "base_opportunity_id": row["request_id"],
            "source_record_id": row["request_id"],
            "arm_id": arm_id,
            "observation_time": row["observation_time"],
            "symbol": "XAUUSD",
            "direction": row["direction"],
            "entry_price": row["entry"],
            "stop_identity": row["stop_name"],
            "stop_price": row["stop"],
            "target_identity": row["target_name"],
            "target_price": row["target"],
            "minimum_rr": row["minimum_rr"],
            "geometry_eligible": row["eligible"],
            "common_support": str(common_support).lower(),
            "train_cutoff_compliant": "true",
            "source_sha256": raw_sha256,
            "deployment_authorized": "false",
        })
    expected_passes = {
        arm["arm_id"]: arm["rr_passing_requests"] for arm in contract["arms"]
    }
    if dict(arm_passes) != expected_passes:
        raise ValueError(f"IMP-100 active request accounting changed: {arm_passes}")
    if len(active) != 685 or len(ledger) != 2388:
        raise ValueError("IMP-100 output accounting changed")
    manifest = {
        "manifest_schema_version": "1.0.0",
        "experiment_id": "IMP-100",
        "phase": "CONTRACT_AND_REQUEST_PREPARATION",
        "contract_sha256": (
            "9D0142D1671E80C1263D93A61E1CB53316EC8E816040B251F477F974540494A9"
        ),
        "source_raw_sha256": raw_sha256,
        "base_opportunities": len(grouped),
        "opportunity_ledger_records": len(ledger),
        "common_support_opportunities": len(common_ids),
        "active_replay_requests": len(active),
        "active_requests_by_arm": dict(arm_passes),
        "deterministic_order": "OBSERVATION_BASE_ID_CONTRACT_ARM_ORDER",
        "outcome_fields_populated": False,
        "future_m5_path_data_read": False,
        "validation_dataset_used": False,
        "test_dataset_used": False,
        "runtime_changed": False,
        "protected_modules_changed": False,
        "deployment_authorized": False,
    }
    return active, ledger, manifest


def write_csv(path: Path, columns: tuple[str, ...],
              rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--repository", required=True, type=Path)
    parser.add_argument("--requests", required=True, type=Path)
    parser.add_argument("--ledger", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    arguments = parser.parse_args()
    contract = load_and_validate(arguments.contract, arguments.repository)
    raw_source = (
        arguments.repository
        / contract["frozen_inputs"]["imp099_raw_experiment_records"]["path"]
    )
    raw_hash = sha256(raw_source)
    active, ledger, manifest = build(
        contract, read_rows(raw_source), raw_hash
    )
    write_csv(arguments.requests, ACTIVE_COLUMNS, active)
    write_csv(arguments.ledger, LEDGER_COLUMNS, ledger)
    complete = {
        **manifest,
        "active_request_sha256": sha256(arguments.requests),
        "opportunity_ledger_sha256": sha256(arguments.ledger),
    }
    arguments.manifest.parent.mkdir(parents=True, exist_ok=True)
    arguments.manifest.write_text(
        json.dumps(complete, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(json.dumps(complete, indent=2))


if __name__ == "__main__":
    main()
