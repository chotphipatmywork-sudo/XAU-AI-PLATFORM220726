"""XAU AI PLATFORM | Offline Evidence Validation | Version 1.0.0."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any

from augment_pretrain_history import sha256
from build_setup_outcome_dataset import as_bool, finite_float
from build_trigger_event_requests import REQUEST_COLUMNS, REQUEST_SCHEMA_VERSION


EXPORT_SCHEMA_VERSION = "1.1.0"
EXPORT_COLUMNS = (
    "export_schema_version", "request_id", "observation_time", "symbol",
    "data_symbol", "direction", "entry_bar_open", "context_bar_open", "entry_atr",
    "trigger_open", "trigger_high", "trigger_low", "trigger_close",
    "context_open", "context_high", "context_low", "context_close",
    "trigger_range_atr", "trigger_body_atr",
    "directional_trigger_body_atr", "upper_wick_atr", "lower_wick_atr",
    "trigger_close_location", "context_body_atr",
    "directional_context_body_atr", "context_close_location",
    "trigger_followthrough_atr", "sweep_penetration_atr",
    "reclaim_distance_atr", "entry_drift_atr", "poi_level_age_bars",
    "target_level_age_bars", "prior_poi_touch_age_bars",
    "prior_poi_touch_count_64", "entry_parity_valid",
    "structure_parity_valid", "trigger_parity_valid",
    "history_known_at_valid", "deployment_authorized",
)


def close(left: float, right: float) -> bool:
    return math.isclose(left, right, rel_tol=1e-8, abs_tol=1e-8)


def read_requests(path: Path, manifest_path: Path) -> tuple[list[dict[str, str]], str]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    request_hash = sha256(path)
    if manifest.get("trigger_event_request_manifest_schema_version") != "1.0.0" or (
        manifest.get("request_schema_version") != REQUEST_SCHEMA_VERSION
    ) or manifest.get("request_file_sha256") != request_hash or (
        manifest.get("outcome_label_in_request") is not False
    ) or manifest.get("deployment_authorized") is not False:
        raise ValueError("Trigger-event request manifest contract changed")
    for flag in (
        "validation_dataset_read", "test_dataset_read", "model_training_performed",
        "feature_schema_changed", "runtime_changed", "risk_changed",
    ):
        if manifest.get(flag) is not False:
            raise ValueError("Trigger-event request manifest safety changed")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or tuple(reader.fieldnames) != REQUEST_COLUMNS:
            raise ValueError("Trigger-event request schema changed")
        rows = list(reader)
    if len(rows) != 232 or manifest.get("requests") != len(rows):
        raise ValueError("Trigger-event request count changed")
    if any("outcome" in key.lower() for key in reader.fieldnames):
        raise ValueError("Trigger-event request contains outcome leakage")
    return rows, request_hash


def valid_bar(row: dict[str, str], prefix: str) -> tuple[float, float, float, float]:
    open_value = finite_float(row[f"{prefix}_open"], f"{prefix}_open")
    high = finite_float(row[f"{prefix}_high"], f"{prefix}_high")
    low = finite_float(row[f"{prefix}_low"], f"{prefix}_low")
    close_value = finite_float(row[f"{prefix}_close"], f"{prefix}_close")
    if min(open_value, high, low, close_value) <= 0.0 or high <= low or (
        high < max(open_value, close_value) or low > min(open_value, close_value)
    ):
        raise ValueError(f"Trigger-event {prefix} bar is invalid")
    return open_value, high, low, close_value


def validate_row(row: dict[str, str], request: dict[str, str]) -> None:
    for field in (
        "request_id", "observation_time", "symbol", "direction",
        "entry_bar_open", "context_bar_open",
    ):
        if row[field] != request[field]:
            raise ValueError(f"Trigger-event export {field} parity failed")
    if row["export_schema_version"] != EXPORT_SCHEMA_VERSION or (
        row["direction"] not in {"TRADE_SETUP_BUY", "TRADE_SETUP_SELL"}
    ):
        raise ValueError("Trigger-event export identity is invalid")
    if not row["data_symbol"].startswith(request["symbol"]):
        raise ValueError("Trigger-event broker data symbol is incompatible")
    for flag in (
        "entry_parity_valid", "structure_parity_valid", "trigger_parity_valid",
        "history_known_at_valid",
    ):
        if not as_bool(row[flag]):
            raise ValueError(f"Trigger-event export {flag} is false")
    if as_bool(row["deployment_authorized"]):
        raise ValueError("Trigger-event export authorized Deployment")

    atr = finite_float(row["entry_atr"], "entry_atr")
    if atr <= 0.0:
        raise ValueError("Trigger-event ATR is invalid")
    trigger_open, trigger_high, trigger_low, trigger_close = valid_bar(row, "trigger")
    context_open, context_high, context_low, context_close = valid_bar(row, "context")
    direction = row["direction"]
    buy = direction == "TRADE_SETUP_BUY"
    expected_entry = finite_float(request["expected_entry"], "expected_entry")
    point = finite_float(request["point_size"], "point_size")
    poi = finite_float(request["reference_poi"], "reference_poi")
    if point <= 0.0 or abs(trigger_close - expected_entry) > point * 0.5 + 1e-9:
        raise ValueError("Trigger-event Entry parity failed")

    expected_shape = {
        "trigger_range_atr": (trigger_high - trigger_low) / atr,
        "trigger_body_atr": abs(trigger_close - trigger_open) / atr,
        "directional_trigger_body_atr": (
            (trigger_close - trigger_open) if buy else (trigger_open - trigger_close)
        ) / atr,
        "upper_wick_atr": (
            trigger_high - max(trigger_open, trigger_close)
        ) / atr,
        "lower_wick_atr": (
            min(trigger_open, trigger_close) - trigger_low
        ) / atr,
        "trigger_close_location": (
            (trigger_close - trigger_low) / (trigger_high - trigger_low)
        ),
        "context_body_atr": abs(context_close - context_open) / atr,
        "directional_context_body_atr": (
            (context_close - context_open) if buy else (context_open - context_close)
        ) / atr,
        "context_close_location": (
            (context_close - context_low) / (context_high - context_low)
        ),
        "trigger_followthrough_atr": (
            (trigger_close - context_close) if buy else (context_close - trigger_close)
        ) / atr,
        "entry_drift_atr": abs(expected_entry - trigger_close) / atr,
    }
    for name, expected in expected_shape.items():
        actual = finite_float(row[name], name)
        if not close(actual, expected):
            raise ValueError(f"Trigger-event derived {name} changed")
    if expected_shape["directional_trigger_body_atr"] <= 0.0:
        raise ValueError("Trigger-event trigger direction is invalid")

    sweep = (
        max(0.0, (poi - trigger_low) / atr) if buy
        else max(0.0, (trigger_high - poi) / atr)
    )
    reclaim = (
        max(0.0, (trigger_close - poi) / atr) if buy
        else max(0.0, (poi - trigger_close) / atr)
    )
    for name, actual, expected in (
        ("sweep", row["sweep_penetration_atr"], sweep),
        ("reclaim", row["reclaim_distance_atr"], reclaim),
        ("request sweep", request["expected_sweep_penetration_atr"], sweep),
        ("request reclaim", request["expected_reclaim_distance_atr"], reclaim),
    ):
        if not close(finite_float(actual, name), expected):
            raise ValueError(f"Trigger-event {name} parity failed")

    for name in (
        "poi_level_age_bars", "target_level_age_bars",
        "prior_poi_touch_age_bars", "prior_poi_touch_count_64",
    ):
        value = int(finite_float(row[name], name))
        minimum = 2 if name in {"poi_level_age_bars", "target_level_age_bars"} else 1
        if value < minimum or value > 64:
            raise ValueError(f"Trigger-event {name} is invalid")


def validate_export(
    request_path: Path, manifest_path: Path, export_path: Path
) -> dict[str, Any]:
    requests, request_hash = read_requests(request_path, manifest_path)
    with export_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or tuple(reader.fieldnames) != EXPORT_COLUMNS:
            raise ValueError("Trigger-event export schema changed")
        rows = list(reader)
    if len(rows) != len(requests):
        raise ValueError("Trigger-event export request coverage changed")
    if [row["request_id"] for row in rows] != [
        row["request_id"] for row in requests
    ]:
        raise ValueError("Trigger-event export order/key parity failed")
    for row, request in zip(rows, requests):
        validate_row(row, request)
    return {
        "trigger_event_collection_schema_version": "1.0.0",
        "status": "TRIGGER_EVENT_EVIDENCE_COLLECTED_TRAIN_ONLY_NO_GO",
        "request_file_sha256": request_hash,
        "request_manifest_sha256": sha256(manifest_path),
        "trigger_event_export_sha256": sha256(export_path),
        "data_symbols": sorted({row["data_symbol"] for row in rows}),
        "requests": len(requests),
        "export_records": len(rows),
        "complete_coverage": True,
        "outcome_label_in_export": False,
        "validation_dataset_read": False,
        "test_dataset_read": False,
        "model_training_performed": False,
        "feature_schema_changed": False,
        "runtime_changed": False,
        "risk_changed": False,
        "deployment_authorized": False,
        "deployment_remains_no_go": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", required=True, type=Path)
    parser.add_argument("--request-manifest", required=True, type=Path)
    parser.add_argument("--trigger-event-export", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    arguments = parser.parse_args()
    report = validate_export(
        arguments.request, arguments.request_manifest, arguments.trigger_event_export
    )
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
