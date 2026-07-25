"""XAU AI PLATFORM | Offline Evidence Preparation | Version 1.0.0.

Build outcome-blind Effective-Train requests for the isolated past-only M5
trigger-event exporter. Validation/Test are never read.
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import timedelta
from pathlib import Path
from typing import Any

from augment_pretrain_history import sha256
from build_setup_outcome_dataset import parse_time
from entry_geometry_outcome_attribution import load_records, valid_hash


REQUEST_SCHEMA_VERSION = "1.0.0"
MANIFEST_SCHEMA_VERSION = "1.0.0"
LOOKBACK_M5_BARS = 64
REQUEST_COLUMNS = (
    "request_schema_version",
    "request_id",
    "observation_time",
    "symbol",
    "direction",
    "entry_bar_open",
    "context_bar_open",
    "expected_entry",
    "reference_poi",
    "structural_stop",
    "nearest_target",
    "expected_sweep_penetration_atr",
    "expected_reclaim_distance_atr",
    "point_size",
    "lookback_m5_bars",
    "deployment_authorized",
)


def build_request_rows(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if len(records) != 232:
        raise ValueError("Trigger-event request requires exactly 232 records")
    requests: list[dict[str, Any]] = []
    seen: set[str] = set()
    previous = None
    for record in records:
        observation = record["observation"]
        entry_bar = parse_time(str(record["entry_bar_open"]))
        context_bar = entry_bar - timedelta(minutes=5)
        if entry_bar + timedelta(minutes=5) != observation:
            raise ValueError("Trigger-event request timing is invalid")
        if previous is not None and observation <= previous:
            raise ValueError("Trigger-event requests are not chronological")
        previous = observation
        request_id = f"trigger_event_{observation.strftime('%Y%m%d_%H%M')}"
        if request_id in seen:
            raise ValueError("Trigger-event request identifier is duplicated")
        seen.add(request_id)
        requests.append({
            "request_schema_version": REQUEST_SCHEMA_VERSION,
            "request_id": request_id,
            "observation_time": record["observation_time"],
            "symbol": record["symbol"],
            "direction": record["direction"],
            "entry_bar_open": entry_bar.strftime("%Y.%m.%d %H:%M"),
            "context_bar_open": context_bar.strftime("%Y.%m.%d %H:%M"),
            "expected_entry": record["entry"],
            "reference_poi": record["reference_poi"],
            "structural_stop": record["structural_stop"],
            "nearest_target": record["nearest_target"],
            "expected_sweep_penetration_atr": record["features"][0],
            "expected_reclaim_distance_atr": record["features"][1],
            "point_size": record["point_size"],
            "lookback_m5_bars": LOOKBACK_M5_BARS,
            "deployment_authorized": "false",
        })
    if set(requests[0]) != set(REQUEST_COLUMNS) or any(
        "outcome" in key.lower() for key in REQUEST_COLUMNS
    ):
        raise ValueError("Trigger-event request leaked an outcome field")
    return requests


def verify_imp087(path: Path, expected_sha256: str) -> str:
    actual = sha256(path)
    if actual != valid_hash(expected_sha256, "IMP-087"):
        raise ValueError("Trigger-event IMP-087 SHA-256 mismatch")
    report = json.loads(path.read_text(encoding="utf-8-sig"))
    if report.get("records") != 232 or report.get("hypothesis_ready_view") is not None:
        raise ValueError("Trigger-event IMP-087 decision changed")
    for flag in (
        "threshold_selected",
        "filter_authorized",
        "candidate_selected",
        "validation_dataset_read",
        "test_dataset_read",
        "model_training_performed",
        "feature_schema_changed",
        "runtime_changed",
        "risk_changed",
        "runtime_change_request_authorized",
        "deployment_authorized",
    ):
        if report.get(flag) is not False:
            raise ValueError("Trigger-event IMP-087 protected state changed")
    if report.get("deployment_remains_no_go") is not True:
        raise ValueError("Trigger-event IMP-087 NO-GO lock changed")
    return actual


def write_requests(
    rows: list[dict[str, Any]],
    hashes: dict[str, str],
    imp087_hash: str,
    output_path: Path,
    manifest_path: Path,
) -> dict[str, Any]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REQUEST_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    manifest = {
        "trigger_event_request_manifest_schema_version": MANIFEST_SCHEMA_VERSION,
        "request_schema_version": REQUEST_SCHEMA_VERSION,
        "research_stage": "effective_train_past_only_m5_trigger_event_request",
        "source_hashes": {**hashes, "imp087_attribution_sha256": imp087_hash},
        "requests": len(rows),
        "first_observation": rows[0]["observation_time"],
        "last_observation": rows[-1]["observation_time"],
        "timeframe": "PERIOD_M5",
        "lookback_m5_bars": LOOKBACK_M5_BARS,
        "outcome_label_in_request": False,
        "validation_dataset_read": False,
        "test_dataset_read": False,
        "model_training_performed": False,
        "feature_schema_changed": False,
        "runtime_changed": False,
        "risk_changed": False,
        "deployment_authorized": False,
        "status": "TRIGGER_EVENT_REQUESTS_TRAIN_ONLY_NO_GO",
        "request_file_sha256": sha256(output_path),
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", required=True, type=Path)
    parser.add_argument("--expected-train-sha256", required=True)
    parser.add_argument("--effective-sample-audit", required=True, type=Path)
    parser.add_argument("--expected-audit-sha256", required=True)
    parser.add_argument("--pretrain-setup", required=True, type=Path)
    parser.add_argument("--expected-pretrain-setup-sha256", required=True)
    parser.add_argument("--main-setup", required=True, type=Path)
    parser.add_argument("--expected-main-setup-sha256", required=True)
    parser.add_argument("--past-only-target-manifest", required=True, type=Path)
    parser.add_argument("--expected-target-manifest-sha256", required=True)
    parser.add_argument("--imp086-attribution", required=True, type=Path)
    parser.add_argument("--expected-imp086-sha256", required=True)
    parser.add_argument("--imp087-attribution", required=True, type=Path)
    parser.add_argument("--expected-imp087-sha256", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    arguments = parser.parse_args()
    records, hashes = load_records(
        arguments.train,
        arguments.expected_train_sha256,
        arguments.effective_sample_audit,
        arguments.expected_audit_sha256,
        arguments.pretrain_setup,
        arguments.expected_pretrain_setup_sha256,
        arguments.main_setup,
        arguments.expected_main_setup_sha256,
        arguments.past_only_target_manifest,
        arguments.expected_target_manifest_sha256,
        arguments.imp086_attribution,
        arguments.expected_imp086_sha256,
    )
    imp087_hash = verify_imp087(
        arguments.imp087_attribution, arguments.expected_imp087_sha256
    )
    rows = build_request_rows(records)
    manifest = write_requests(
        rows, hashes, imp087_hash, arguments.output, arguments.manifest
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
