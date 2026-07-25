"""XAU AI PLATFORM | Offline Research | Version 1.0.0.

Build outcome-blind past-only Target-ladder requests from current-feed
reversal contexts before the preregistered Train cutoff.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

from build_past_only_target_requests import (
    MINIMUM_RR,
    REQUEST_COLUMNS,
    REQUEST_SCHEMA_VERSION,
    format_time,
    write_requests,
)
from build_setup_outcome_dataset import (
    SETUP_AUDIT_COLUMNS_V3,
    as_bool,
    finite_float,
    parse_time,
)
from diagnose_current_feed_setup_funnel import (
    EXPECTED_SETUP_SHA256,
    TRAIN_END_EXCLUSIVE,
    sha256,
)


REQUEST_STATUS = "CURRENT_FEED_PAST_ONLY_TARGET_REQUESTS_TRAIN_ONLY_NO_GO"


def build_requests(
    rows: list[dict[str, str]],
    cutoff: datetime = TRAIN_END_EXCLUSIVE,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    requests: list[dict[str, object]] = []
    counts: Counter[str] = Counter()
    previous: datetime | None = None
    cutoff_reached = False
    for row in rows:
        observation = parse_time(row["observation_time"])
        if previous is not None and observation <= previous:
            raise ValueError("Current-feed Target source is not chronological")
        previous = observation
        if observation >= cutoff:
            cutoff_reached = True
            break
        counts["source_rows"] += 1
        if not as_bool(row["reversal_context_confirmed"]):
            continue
        if not as_bool(row["poi_confirmed"]) or not as_bool(
            row["trigger_confirmed"]
        ):
            raise ValueError("Current-feed Target context bypassed causal gates")
        counts["reversal_context_rows"] += 1
        direction = row["direction"]
        if direction not in {"TRADE_SETUP_BUY", "TRADE_SETUP_SELL"}:
            raise ValueError("Current-feed Target direction is invalid")
        entry_bar_open = parse_time(row["entry_bar_open"])
        if entry_bar_open + timedelta(minutes=5) != observation:
            raise ValueError("Current-feed Target trigger timing changed")
        stop = finite_float(row["structural_stop"], "structural_stop")
        target = finite_float(row["nearest_target"], "nearest_target")
        if stop <= 0.0 or target <= 0.0:
            raise ValueError("Current-feed Target structural level is invalid")

        entry = finite_float(row["plan_entry"], "plan_entry")
        cost = finite_float(row["estimated_cost_points"], "estimated_cost_points")
        minimum_rr = finite_float(row["minimum_rr"], "minimum_rr")
        entry_known = entry > 0.0
        if entry_known:
            if cost < 0.0 or minimum_rr < MINIMUM_RR:
                raise ValueError("Current-feed known Entry evidence is invalid")
            counts["known_entry_rows"] += 1
        else:
            if entry != 0.0 or cost != 0.0 or minimum_rr != 0.0:
                raise ValueError("Current-feed unknown Entry evidence is inconsistent")
            cost = 0.0
            counts["unknown_entry_rows"] += 1

        request_id = f"current_feed_{observation.strftime('%Y%m%d_%H%M')}"
        requests.append({
            "request_schema_version": REQUEST_SCHEMA_VERSION,
            "request_id": request_id,
            "source": "current_feed_train_context",
            "observation_time": format_time(observation),
            "symbol": row["symbol"],
            "direction": direction,
            "entry_bar_open": format_time(entry_bar_open),
            "expected_entry": entry if entry_known else 0.0,
            "entry_known": str(entry_known).lower(),
            "structural_stop": stop,
            "current_target": target,
            "estimated_cost_points": cost,
            "cost_known": str(entry_known).lower(),
            "minimum_rr": MINIMUM_RR,
        })
    if not cutoff_reached:
        raise ValueError("Current-feed Target source did not reach Train cutoff")
    if not requests:
        raise ValueError("Current-feed Target request set is empty")
    if len({row["request_id"] for row in requests}) != len(requests):
        raise ValueError("Current-feed Target request IDs are duplicated")
    return requests, {**counts, "cutoff_reached": cutoff_reached}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--setup-audit", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    arguments = parser.parse_args()
    source_hash = sha256(arguments.setup_audit)
    if source_hash != EXPECTED_SETUP_SHA256:
        raise ValueError("Current-feed Target Setup Audit SHA-256 mismatch")
    with arguments.setup_audit.open(
        "r", encoding="utf-8-sig", newline=""
    ) as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or tuple(reader.fieldnames) != (
            SETUP_AUDIT_COLUMNS_V3
        ):
            raise ValueError("Current-feed Target Setup Audit schema mismatch")
        requests, audit = build_requests(list(reader))
    request_hash = write_requests(arguments.output, requests)
    manifest = {
        "request_schema_version": REQUEST_SCHEMA_VERSION,
        "status": REQUEST_STATUS,
        "train_end_exclusive": format_time(TRAIN_END_EXCLUSIVE),
        "validation_dataset_used": False,
        "test_dataset_used": False,
        "outcome_label_in_request": False,
        "runtime_changed": False,
        "minimum_rr_changed": False,
        "deployment_authorized": False,
        "setup_audit_sha256": source_hash,
        "source_audit": audit,
        "requests": len(requests),
        "request_file_sha256": request_hash,
    }
    arguments.manifest.parent.mkdir(parents=True, exist_ok=True)
    arguments.manifest.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
