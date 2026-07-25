"""XAU AI PLATFORM | Offline Research | Version 1.0.0.

Diagnose Train-only Objective Entry/Stop/Target reachability without changing
Runtime, Risk, minimum RR, or sealed Validation/Test evidence.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from analyze_shadow_run import DECISION_COLUMNS, FEATURE_COLUMNS
from build_setup_outcome_dataset import (
    FEATURE_SCHEMA_VERSION,
    OBJECTIVE_MODEL_STATUS,
    OBJECTIVE_PROVIDER,
    OUTCOME_AUDIT_COLUMNS,
    SETUP_AUDIT_COLUMNS_V1,
    SETUP_OUTCOME_SCHEMA_VERSION,
    as_bool,
    finite_float,
    parse_time,
)


DIAGNOSTIC_SCHEMA_VERSION = "1.0.0"
DIAGNOSTIC_STATUS = "STRUCTURAL_OPPORTUNITY_TRAIN_ONLY_NO_GO"
TRAIN_END_EXCLUSIVE = datetime(2025, 7, 16, 3, 0)
POINT_SIZE = 0.01
MINIMUM_RR = 2.0
QUALITY_EXCLUSION_SCHEMA_VERSION = "1.0.0"

FROZEN_HASHES = {
    "pretrain_setup": "A406B7EDADA6CACB5691487341294E5F950FF262D1CE8AE26EF958843338B8B8",
    "pretrain_decisions": "E27DE54D7ED276E10D04483083CD638BE2185E6458741B368E827504DF698FEE",
    "main_setup": "A8463D7F118CB52A7B514099FF8B8839F3C2401ECA5A66F50376C4D87C1C9F7A",
    "main_decisions": "AD388204969B9D5EB032D807342132A8AFBDD3FFD6EDC1181512EFCE1FB955E4",
    "augmented_train": "F31E6DED4E0AC3B20FDD7964D3E634902736C8AD3316AA15A4E63D5C3C7E9A7E",
    "pretrain_exclusions": "912BEDFF33A1CB0ECF8D89406422B8978B752AEC74496D44C35F29DD97603AB7",
    "main_exclusions": "346C26E5C9A3DF62CB2CB2A7C87A669F88CFC8B38C5B89428EC6DEFF0A3C80CE",
    "split_summary": "34A416B245DB97D8572292C050499221B520938CADA41EB7E6A7F2921E901A30",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def verify_frozen_hashes(paths: dict[str, Path]) -> dict[str, str]:
    if set(paths) != set(FROZEN_HASHES):
        raise ValueError("Structural opportunity frozen source set is incomplete")
    actual: dict[str, str] = {}
    for name, path in paths.items():
        if not path.exists():
            raise FileNotFoundError(f"Structural opportunity source missing: {path}")
        actual[name] = sha256(path)
        if actual[name] != FROZEN_HASHES[name]:
            raise ValueError(f"Structural opportunity frozen hash mismatch: {name}")
    return actual


def validate_split_summary(path: Path) -> datetime:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if payload.get("validation_dataset_used_for_selection") is not False:
        raise ValueError("Frozen split summary does not seal Validation selection")
    if payload.get("test_dataset_used_for_selection") is not False:
        raise ValueError("Frozen split summary does not seal Test selection")
    cutoff = parse_time(str(payload.get("validation_start", "")))
    if cutoff != TRAIN_END_EXCLUSIVE:
        raise ValueError("Structural opportunity Train cutoff changed")
    return cutoff


def load_excluded_dates(path: Path) -> frozenset[date]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if payload.get("quality_exclusion_schema_version") != (
        QUALITY_EXCLUSION_SCHEMA_VERSION
    ):
        raise ValueError("Structural opportunity quality schema mismatch")
    entries = payload.get("excluded_dates")
    if not isinstance(entries, list) or not entries:
        raise ValueError("Structural opportunity quality exclusions are empty")
    values: list[date] = []
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("date"), str):
            raise ValueError("Structural opportunity quality exclusion is invalid")
        values.append(date.fromisoformat(entry["date"]))
    if len(values) != len(set(values)):
        raise ValueError("Structural opportunity quality exclusions are duplicated")
    return frozenset(values)


def session_bucket(progress: float) -> str:
    if progress <= 25.0:
        return "early_0_25"
    if progress >= 75.0:
        return "late_75_100"
    return "middle_25_75"


def read_decision_context(
    path: Path,
    cutoff: datetime,
    excluded_dates: frozenset[date],
    require_cutoff: bool,
) -> tuple[dict[datetime, dict[str, Any]], dict[str, Any]]:
    contexts: dict[datetime, dict[str, Any]] = {}
    previous: datetime | None = None
    cutoff_reached = False
    excluded = 0
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or tuple(reader.fieldnames) != DECISION_COLUMNS:
            raise ValueError("Unexpected structural opportunity Decision schema")
        for row in reader:
            closed_bar = parse_time(row["closed_bar"])
            observation = closed_bar + timedelta(minutes=15)
            if previous is not None and observation <= previous:
                raise ValueError("Structural opportunity Decisions are not chronological")
            previous = observation
            if observation >= cutoff:
                cutoff_reached = True
                break
            if observation.date() in excluded_dates:
                excluded += 1
                continue
            if row["timeframe"] != "PERIOD_M15":
                raise ValueError("Structural opportunity accepts M15 Decisions only")
            if row["feature_schema_version"] != FEATURE_SCHEMA_VERSION:
                raise ValueError("Structural opportunity requires Feature Schema 4.0")
            if row["inference_provider"] != OBJECTIVE_PROVIDER:
                raise ValueError("Structural opportunity Decision provider changed")
            if row["model_status"] != OBJECTIVE_MODEL_STATUS:
                raise ValueError("Structural opportunity Decision NO-GO status changed")
            if as_bool(row["model_deployment_authorized"]):
                raise ValueError("Deployable Decision evidence is forbidden")
            progress = finite_float(row["session_progress"], "session_progress")
            if not 0.0 <= progress <= 100.0:
                raise ValueError("Structural opportunity Session Progress is invalid")
            contexts[observation] = {
                "session_progress": progress,
                "session_bucket": session_bucket(progress),
                "trend_regime": finite_float(row["trend_regime"], "trend_regime"),
                "trend_momentum": finite_float(
                    row["trend_momentum"], "trend_momentum"
                ),
                "trend_slope": finite_float(row["trend_slope"], "trend_slope"),
            }
    if require_cutoff and not cutoff_reached:
        raise ValueError("Structural opportunity main Decisions did not reach cutoff")
    if not contexts:
        raise ValueError("Structural opportunity Decision context is empty")
    return contexts, {
        "retained_decision_rows": len(contexts),
        "quality_excluded_decision_rows": excluded,
        "cutoff_reached": cutoff_reached,
    }


def close_enough(left: float, right: float) -> bool:
    return math.isclose(left, right, rel_tol=1e-9, abs_tol=1e-6)


def calculable_geometry(row: dict[str, str]) -> dict[str, float]:
    entry = finite_float(row["plan_entry"], "plan_entry")
    stop = finite_float(row["plan_stop"], "plan_stop")
    target = finite_float(row["plan_target"], "plan_target")
    plan_rr = finite_float(row["plan_rr"], "plan_rr")
    minimum_rr = finite_float(row["minimum_rr"], "minimum_rr")
    cost_points = finite_float(row["estimated_cost_points"], "estimated_cost_points")
    direction = row["direction"]
    if direction == "TRADE_SETUP_BUY":
        valid_geometry = stop < entry < target
    elif direction == "TRADE_SETUP_SELL":
        valid_geometry = target < entry < stop
    else:
        raise ValueError("Structural opportunity trigger direction is invalid")
    if not valid_geometry or minimum_rr < MINIMUM_RR or cost_points < 0.0:
        raise ValueError("Structural opportunity calculable plan geometry is invalid")
    cost_price = cost_points * POINT_SIZE
    gross_risk = abs(entry - stop)
    gross_target = abs(target - entry)
    effective_risk = gross_risk + cost_price
    net_reward = gross_target - cost_price
    calculated_rr = net_reward / effective_risk
    if net_reward <= 0.0 or not close_enough(calculated_rr, plan_rr):
        raise ValueError("Structural opportunity plan RR is inconsistent")
    required_gross_target = minimum_rr * effective_risk + cost_price
    return {
        "plan_rr": plan_rr,
        "minimum_rr": minimum_rr,
        "gross_risk_points": gross_risk / POINT_SIZE,
        "gross_target_points": gross_target / POINT_SIZE,
        "estimated_cost_points": cost_points,
        "required_target_multiplier": required_gross_target / gross_target,
        "target_shortfall_points": max(
            0.0, (required_gross_target - gross_target) / POINT_SIZE
        ),
    }


def read_trigger_samples(
    path: Path,
    decisions: dict[datetime, dict[str, Any]],
    cutoff: datetime,
    excluded_dates: frozenset[date],
    source_name: str,
    require_cutoff: bool,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    samples: list[dict[str, Any]] = []
    previous: datetime | None = None
    cutoff_reached = False
    counts: Counter[str] = Counter()
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or tuple(reader.fieldnames) != (
            SETUP_AUDIT_COLUMNS_V1
        ):
            raise ValueError("Unexpected structural opportunity Setup Audit schema")
        for row in reader:
            observation = parse_time(row["observation_time"])
            if previous is not None and observation <= previous:
                raise ValueError("Structural opportunity Setup Audit is not chronological")
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
            direction = row["direction"]
            if direction in {"TRADE_SETUP_BUY", "TRADE_SETUP_SELL"}:
                counts["direction_aligned_rows"] += 1
            if as_bool(row["poi_confirmed"]):
                counts["poi_confirmed_rows"] += 1
            if not trigger:
                continue
            counts["trigger_rows"] += 1
            context = decisions.get(observation)
            if context is None:
                raise ValueError("Structural opportunity trigger has no Train Decision")
            if direction not in {"TRADE_SETUP_BUY", "TRADE_SETUP_SELL"}:
                raise ValueError("Structural opportunity trigger has invalid direction")
            reason = row["setup_reason"]
            plan_available = as_bool(row["plan_available"])
            geometry: dict[str, float] | None = None
            if plan_available:
                disposition = "accepted_plan"
                geometry = calculable_geometry(row)
                if geometry["plan_rr"] + 1e-9 < geometry["minimum_rr"]:
                    raise ValueError("Accepted structural plan is below minimum RR")
            elif "below minimum RR" in reason:
                disposition = "below_minimum_rr"
                geometry = calculable_geometry(row)
                if geometry["plan_rr"] + 1e-9 >= geometry["minimum_rr"]:
                    raise ValueError("Below-minimum disposition satisfies minimum RR")
            elif "geometry is invalid" in reason:
                disposition = "invalid_geometry"
            else:
                disposition = "other_fail_closed"
            counts[disposition] += 1
            samples.append({
                "observation": observation,
                "source": source_name,
                "direction": direction,
                "session_progress": context["session_progress"],
                "session_bucket": context["session_bucket"],
                "disposition": disposition,
                "sweep_penetration_atr": finite_float(
                    row["sweep_penetration_atr"], "sweep_penetration_atr"
                ),
                "reclaim_distance_atr": finite_float(
                    row["reclaim_distance_atr"], "reclaim_distance_atr"
                ),
                "geometry": geometry,
            })
    if require_cutoff and not cutoff_reached:
        raise ValueError("Structural opportunity main Setup Audit did not reach cutoff")
    if not samples:
        raise ValueError("Structural opportunity trigger evidence is empty")
    return samples, {**counts, "cutoff_reached": cutoff_reached}


def quantile(values: list[float], fraction: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = fraction * (len(ordered) - 1)
    lower = int(math.floor(position))
    upper = int(math.ceil(position))
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def distribution(values: list[float]) -> dict[str, float | int | None]:
    return {
        "records": len(values),
        "minimum": min(values) if values else None,
        "p25": quantile(values, 0.25),
        "median": quantile(values, 0.50),
        "p75": quantile(values, 0.75),
        "maximum": max(values) if values else None,
    }


def summarize_samples(samples: list[dict[str, Any]]) -> dict[str, Any]:
    dispositions = Counter(sample["disposition"] for sample in samples)
    calculable = [sample for sample in samples if sample["geometry"] is not None]
    rr_values = [float(sample["geometry"]["plan_rr"]) for sample in calculable]
    below_minimum = [
        sample for sample in samples
        if sample["disposition"] == "below_minimum_rr"
    ]
    multipliers = [
        float(sample["geometry"]["required_target_multiplier"])
        for sample in below_minimum
    ]
    shortfalls = [
        float(sample["geometry"]["target_shortfall_points"])
        for sample in below_minimum
    ]
    total = len(samples)
    accepted = dispositions.get("accepted_plan", 0)
    return {
        "triggers": total,
        "dispositions": dict(sorted(dispositions.items())),
        "plan_reachability_rate": accepted / total if total else None,
        "structural_failure_rate": (
            dispositions.get("below_minimum_rr", 0)
            + dispositions.get("invalid_geometry", 0)
            + dispositions.get("other_fail_closed", 0)
        ) / total if total else None,
        "calculable_rr": distribution(rr_values),
        "rr_bands": {
            "below_1r": sum(value < 1.0 for value in rr_values),
            "from_1r_to_below_2r": sum(1.0 <= value < 2.0 for value in rr_values),
            "at_least_2r": sum(value >= 2.0 for value in rr_values),
            "not_calculable": total - len(rr_values),
        },
        "below_minimum_required_target_multiplier": distribution(multipliers),
        "below_minimum_target_shortfall_points": distribution(shortfalls),
    }


def grouped_report(
    samples: list[dict[str, Any]], key: str
) -> dict[str, dict[str, Any]]:
    values = sorted({str(sample[key]) for sample in samples})
    return {
        value: summarize_samples([
            sample for sample in samples if str(sample[key]) == value
        ])
        for value in values
    }


def chronological_blocks(samples: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ordered = sorted(samples, key=lambda sample: sample["observation"])
    reports: list[dict[str, Any]] = []
    for index in range(4):
        start = index * len(ordered) // 4
        end = (index + 1) * len(ordered) // 4
        block = ordered[start:end]
        if not block:
            raise ValueError("Structural opportunity chronological block is empty")
        reports.append({
            "block": index + 1,
            "first_observation": block[0]["observation"].strftime("%Y.%m.%d %H:%M"),
            "last_observation": block[-1]["observation"].strftime("%Y.%m.%d %H:%M"),
            "metrics": summarize_samples(block),
        })
    return reports


def read_augmented_train(path: Path) -> dict[str, Any]:
    upper_name = path.name.upper()
    if "AUGMENTED_TRAIN" not in upper_name or "VALIDATION" in upper_name or (
        "TEST" in upper_name
    ):
        raise ValueError("Structural opportunity accepts augmented Train only")
    samples: list[dict[str, Any]] = []
    previous: datetime | None = None
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or tuple(reader.fieldnames) != OUTCOME_AUDIT_COLUMNS:
            raise ValueError("Unexpected structural opportunity augmented Train schema")
        for row in reader:
            if row["setup_outcome_schema_version"] != SETUP_OUTCOME_SCHEMA_VERSION:
                raise ValueError("Structural opportunity outcome schema changed")
            if row["feature_schema_version"] != FEATURE_SCHEMA_VERSION:
                raise ValueError("Structural opportunity feature schema changed")
            if not as_bool(row["trainable"]):
                raise ValueError("Structural opportunity Train contains quarantined outcome")
            observation = parse_time(row["observation_time"])
            if observation >= TRAIN_END_EXCLUSIVE:
                raise ValueError("Structural opportunity Train crossed Validation cutoff")
            if previous is not None and observation <= previous:
                raise ValueError("Structural opportunity augmented Train is not chronological")
            previous = observation
            outcome = row["outcome"]
            plan_rr = finite_float(row["plan_rr"], "plan_rr")
            if outcome == "TARGET_FIRST":
                return_r = plan_rr
            elif outcome == "STOP_FIRST":
                return_r = -1.0
            elif outcome == "TIMEOUT":
                return_r = 0.0
            else:
                raise ValueError("Structural opportunity Train outcome is invalid")
            progress = finite_float(row["session_progress"], "session_progress")
            samples.append({
                "observation": observation,
                "direction": row["direction"],
                "session_bucket": session_bucket(progress),
                "outcome": outcome,
                "return_r": return_r,
            })
    if not samples:
        raise ValueError("Structural opportunity augmented Train is empty")

    def outcome_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
        outcomes = Counter(row["outcome"] for row in rows)
        return {
            "records": len(rows),
            "outcomes": dict(sorted(outcomes.items())),
            "target_rate": outcomes.get("TARGET_FIRST", 0) / len(rows),
            "mean_cost_aware_r": sum(float(row["return_r"]) for row in rows) / len(rows),
        }

    return {
        "overall": outcome_metrics(samples),
        "by_direction": {
            value: outcome_metrics([row for row in samples if row["direction"] == value])
            for value in sorted({row["direction"] for row in samples})
        },
        "by_session_bucket": {
            value: outcome_metrics([
                row for row in samples if row["session_bucket"] == value
            ])
            for value in sorted({row["session_bucket"] for row in samples})
        },
        "first_observation": samples[0]["observation"].strftime("%Y.%m.%d %H:%M"),
        "last_observation": samples[-1]["observation"].strftime("%Y.%m.%d %H:%M"),
    }


def build_report(
    samples: list[dict[str, Any]],
    source_audits: dict[str, Any],
    decision_audits: dict[str, Any],
    outcome_baseline: dict[str, Any],
    source_hashes: dict[str, str],
) -> dict[str, Any]:
    combined = summarize_samples(samples)
    dispositions = combined["dispositions"]
    geometry_failures = int(dispositions.get("below_minimum_rr", 0)) + int(
        dispositions.get("invalid_geometry", 0)
    )
    return {
        "diagnostic_schema_version": DIAGNOSTIC_SCHEMA_VERSION,
        "diagnostic_status": DIAGNOSTIC_STATUS,
        "train_end_exclusive": TRAIN_END_EXCLUSIVE.strftime("%Y.%m.%d %H:%M"),
        "validation_dataset_used": False,
        "test_dataset_used": False,
        "model_training_performed": False,
        "runtime_changed": False,
        "risk_changed": False,
        "minimum_rr_changed": False,
        "deployment_authorized": False,
        "source_hashes": source_hashes,
        "source_audits": source_audits,
        "decision_audits": decision_audits,
        "combined_trigger_geometry": combined,
        "by_source": grouped_report(samples, "source"),
        "by_direction": grouped_report(samples, "direction"),
        "by_session_bucket": grouped_report(samples, "session_bucket"),
        "chronological_blocks": chronological_blocks(samples),
        "accepted_plan_outcome_baseline": outcome_baseline,
        "geometry_failure_share": geometry_failures / len(samples),
        "structural_target_bottleneck_observed": geometry_failures > 0,
        "runtime_candidate_ready": False,
        "next_artifact_required": "past_only_multilevel_structural_target_export_or_replay",
        "limitations": [
            "Setup Audit V1 does not retain trigger Entry for invalid-geometry rows.",
            "Setup Audit V1 does not retain alternative confirmed Target levels.",
            "Rejected triggers have no counterfactual outcome label.",
            "This descriptive Train-only diagnostic cannot select a Runtime contract.",
        ],
    }


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
    pretrain_samples, pretrain_source_audit = read_trigger_samples(
        arguments.pretrain_setup, pretrain_decisions, cutoff,
        pretrain_exclusions, "pretrain_202001_202106", False,
    )
    main_samples, main_source_audit = read_trigger_samples(
        arguments.main_setup, main_decisions, cutoff,
        main_exclusions, "train_202107_202507", True,
    )
    samples = sorted(
        [*pretrain_samples, *main_samples], key=lambda sample: sample["observation"]
    )
    if any(
        samples[index]["observation"] >= samples[index + 1]["observation"]
        for index in range(len(samples) - 1)
    ):
        raise ValueError("Structural opportunity combined triggers overlap")

    report = build_report(
        samples,
        {
            "pretrain": pretrain_source_audit,
            "main_train_before_cutoff": main_source_audit,
        },
        {
            "pretrain": pretrain_decision_audit,
            "main_train_before_cutoff": main_decision_audit,
        },
        read_augmented_train(arguments.augmented_train),
        source_hashes,
    )
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
