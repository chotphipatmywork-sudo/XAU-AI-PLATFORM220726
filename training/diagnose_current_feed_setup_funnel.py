"""XAU AI PLATFORM | Offline Research | Version 1.0.0.

Diagnose the frozen current-feed Objective Setup funnel before a preregistered
Train cutoff without reading later evidence or changing Runtime/Risk.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Iterable

from build_setup_outcome_dataset import (
    SETUP_AUDIT_COLUMNS_V3,
    as_bool,
    finite_float,
    parse_time,
)


DIAGNOSTIC_SCHEMA_VERSION = "1.0.0"
TRAIN_END_EXCLUSIVE = datetime(2024, 7, 1)
EXPECTED_SETUP_SHA256 = (
    "B6122AEA49F764055347B0459104DA53AD37EA815D2CC6568E4B0BC6885490F1"
)
MINIMUM_RR = 2.0


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def bucket_reason(reason: str) -> str:
    text = reason.strip().lower()
    if "poi" in text:
        return "poi"
    if "trigger" in text or "sweep" in text or "reclaim" in text:
        return "trigger"
    if "reversal" in text or "context" in text:
        return "reversal_context"
    if "minimum rr" in text:
        return "minimum_rr"
    if "geometry" in text or "target" in text or "stop" in text:
        return "geometry"
    if "plan" in text:
        return "plan"
    return "other"


def quantile(values: list[float], fraction: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = fraction * (len(ordered) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def summarize_rows(
    rows: Iterable[dict[str, str]], cutoff: datetime = TRAIN_END_EXCLUSIVE
) -> dict[str, object]:
    counts: Counter[str] = Counter()
    reasons: Counter[str] = Counter()
    reason_buckets: Counter[str] = Counter()
    trigger_rr: list[float] = []
    previous: datetime | None = None
    cutoff_reached = False
    first_observation: datetime | None = None
    last_observation: datetime | None = None

    for row in rows:
        observation = parse_time(row["observation_time"])
        if previous is not None and observation <= previous:
            raise ValueError("Current-feed Setup Audit is not chronological")
        previous = observation
        if observation >= cutoff:
            cutoff_reached = True
            break
        if first_observation is None:
            first_observation = observation
        last_observation = observation
        counts["observations"] += 1

        poi = as_bool(row["poi_confirmed"])
        trigger = as_bool(row["trigger_confirmed"])
        context = as_bool(row["reversal_context_confirmed"])
        plan = as_bool(row["plan_available"])
        if trigger and not poi:
            raise ValueError("Trigger bypassed POI")
        if context and not trigger:
            raise ValueError("Reversal context bypassed trigger")
        if plan and not context:
            raise ValueError("Plan bypassed reversal context")

        if poi:
            counts["poi_confirmed"] += 1
        if trigger:
            counts["trigger_confirmed"] += 1
            rr = finite_float(row["plan_rr"], "plan_rr")
            if rr >= 0.0:
                trigger_rr.append(rr)
        if context:
            counts["reversal_context_confirmed"] += 1
        if plan:
            counts["plan_available"] += 1
            if finite_float(row["plan_rr"], "plan_rr") + 1e-9 < MINIMUM_RR:
                raise ValueError("Accepted plan is below frozen minimum RR")

        reason = row["setup_reason"].strip()
        reasons[reason] += 1
        if not plan:
            reason_buckets[bucket_reason(reason)] += 1

        if as_bool(row["execution_success"]):
            counts["execution_success"] += 1
        if as_bool(row["risk_allowed"]):
            counts["risk_allowed"] += 1

    if not cutoff_reached:
        raise ValueError("Current-feed Setup Audit did not reach Train cutoff")
    if not counts["observations"]:
        raise ValueError("Current-feed Train evidence is empty")

    def conversion(numerator: str, denominator: str) -> float:
        base = counts[denominator]
        return counts[numerator] / base if base else 0.0

    return {
        "diagnostic_schema_version": DIAGNOSTIC_SCHEMA_VERSION,
        "diagnostic_status": "CURRENT_FEED_SETUP_FUNNEL_TRAIN_ONLY_NO_GO",
        "train_end_exclusive": cutoff.strftime("%Y.%m.%d %H:%M"),
        "first_observation": first_observation.strftime("%Y.%m.%d %H:%M"),
        "last_observation": last_observation.strftime("%Y.%m.%d %H:%M"),
        "funnel": dict(counts),
        "conversion": {
            "poi_per_observation": conversion("poi_confirmed", "observations"),
            "trigger_per_poi": conversion("trigger_confirmed", "poi_confirmed"),
            "context_per_trigger": conversion(
                "reversal_context_confirmed", "trigger_confirmed"
            ),
            "plan_per_context": conversion(
                "plan_available", "reversal_context_confirmed"
            ),
        },
        "non_plan_reason_buckets": dict(reason_buckets.most_common()),
        "setup_reasons": dict(reasons.most_common()),
        "trigger_plan_rr": {
            "records": len(trigger_rr),
            "minimum": min(trigger_rr) if trigger_rr else None,
            "median": quantile(trigger_rr, 0.5),
            "p75": quantile(trigger_rr, 0.75),
            "maximum": max(trigger_rr) if trigger_rr else None,
            "at_least_2r": sum(value >= MINIMUM_RR for value in trigger_rr),
        },
        "minimum_rr_changed": False,
        "validation_dataset_used_for_selection": False,
        "test_dataset_used_for_selection": False,
        "training_performed": False,
        "deployment_authorized": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--setup-audit", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    arguments = parser.parse_args()
    actual_hash = sha256(arguments.setup_audit)
    if actual_hash != EXPECTED_SETUP_SHA256:
        raise ValueError("Current-feed Setup Audit SHA-256 mismatch")
    with arguments.setup_audit.open(
        "r", encoding="utf-8-sig", newline=""
    ) as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or tuple(reader.fieldnames) != (
            SETUP_AUDIT_COLUMNS_V3
        ):
            raise ValueError("Current-feed Setup Audit Schema 3.0 mismatch")
        report = summarize_rows(reader)
    report["setup_audit_sha256"] = actual_hash
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
