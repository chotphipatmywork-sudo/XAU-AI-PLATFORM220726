"""IMP-098 Train-only structural Stop-to-Target imbalance diagnostics."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from statistics import mean, median
from typing import Any, Iterable

from analyze_current_feed_rr_rejections import (
    factor_analysis,
    fixed_regime,
    session_label,
    time_of_day,
    trend_alignment,
)
from build_setup_outcome_dataset import parse_time
from diagnose_current_feed_setup_funnel import TRAIN_END_EXCLUSIVE, sha256


POINT_SIZE = 0.01
EXPECTED_DETAIL_SHA256 = (
    "AB32EC7B6212DBD78169DB9339B666CA3A6076381B2152D827E272AF1805B83D"
)
EXPECTED_STOP_SHA256 = (
    "FB6E0073BDF0FD89E4B09324B6C092F0812DBA7D243608063B61E4F167627C75"
)
EXPECTED_TARGET_SHA256 = (
    "E930FFEEB5AF464DBCFD7FFD531D264AA9ED7D326CDAAD07ED2487CC72E7E2FA"
)
EXPECTED_DECISIONS_SHA256 = (
    "A20A7B5F1399541C271D46999433B8C69B650D27F48DC3480B59E15E9C4022EC"
)
EXPECTED_ROOT_SHA256 = (
    "403AB570A756A9C6F708BDB7B62E4A56644D138AAC675ED72FCD10E73191000C"
)

DETAIL_COLUMNS = (
    "detail_schema_version",
    "request_id",
    "observation_time",
    "direction",
    "gate_result",
    "stop_distance_points",
    "target_distance_points",
    "stop_1_distance_points",
    "stop_2_distance_points",
    "stop_3_distance_points",
    "stop_1_to_2_increment_points",
    "selected_stop_depth",
    "nearest_target_distance_points",
    "selected_target_distance_points",
    "target_obstruction_gap_points",
    "intervening_target_barriers",
    "stop_to_target_ratio",
    "entry_position_fraction",
    "atr",
    "volatility_change",
    "session",
    "time_of_day",
    "volatility_regime",
    "trend_regime",
    "trend_alignment",
    "validation_dataset_used",
    "test_dataset_used",
    "deployment_authorized",
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"CSV header missing: {path}")
        return list(reader)


def load_extended_contexts(
    path: Path, observations: set[datetime]
) -> dict[datetime, dict[str, float]]:
    required = {
        "recorded_at", "atr", "trend_regime", "volatility_regime",
        "volatility_change", "session_asia", "session_london",
        "session_new_york",
    }
    contexts: dict[datetime, dict[str, float]] = {}
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or not required.issubset(reader.fieldnames):
            raise ValueError("IMP-098 Decision context schema changed")
        for row in reader:
            recorded_at = parse_time(row["recorded_at"]).replace(
                second=0, microsecond=0
            )
            if recorded_at not in observations:
                continue
            if recorded_at in contexts:
                raise ValueError("IMP-098 Decision context is duplicated")
            contexts[recorded_at] = {
                field: float(row[field])
                for field in required - {"recorded_at"}
            }
    if set(contexts) != observations:
        raise ValueError("IMP-098 Decision context coverage changed")
    return contexts


def numeric_summary(values: Iterable[float]) -> dict[str, float | int | None]:
    ordered = sorted(float(value) for value in values if math.isfinite(float(value)))
    if not ordered:
        return {"records": 0, "minimum": None, "median": None, "mean": None,
                "maximum": None}
    return {
        "records": len(ordered),
        "minimum": ordered[0],
        "median": median(ordered),
        "mean": mean(ordered),
        "maximum": ordered[-1],
    }


def cliffs_delta(left: list[float], right: list[float]) -> float | None:
    if not left or not right:
        return None
    greater = 0
    lower = 0
    for lhs in left:
        for rhs in right:
            if lhs > rhs:
                greater += 1
            elif lhs < rhs:
                lower += 1
    return (greater - lower) / (len(left) * len(right))


def distance(entry: float, level: float) -> float | None:
    if level <= 0.0:
        return None
    return abs(entry - level) / POINT_SIZE


def valid_directional_level(direction: str, entry: float, level: float,
                            side: str) -> bool:
    if level <= 0.0:
        return False
    if side == "stop":
        return (direction == "TRADE_SETUP_BUY" and level < entry) or (
            direction == "TRADE_SETUP_SELL" and level > entry
        )
    return (direction == "TRADE_SETUP_BUY" and level > entry) or (
        direction == "TRADE_SETUP_SELL" and level < entry
    )


def build_records(
    details: list[dict[str, str]],
    stops: dict[str, dict[str, str]],
    targets: dict[str, dict[str, str]],
    contexts: dict[datetime, dict[str, float]],
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for detail in details:
        request_id = detail["request_id"]
        if request_id not in stops or request_id not in targets:
            raise ValueError(f"IMP-098 ladder coverage missing: {request_id}")
        stop_row = stops[request_id]
        target_row = targets[request_id]
        observation = parse_time(detail["observation_time"])
        if observation >= TRAIN_END_EXCLUSIVE:
            raise ValueError("IMP-098 evidence escaped Train-only boundary")
        context = contexts[observation]
        direction = detail["direction"]
        entry = float(detail["entry"])
        stop_levels = [
            float(stop_row[f"m5_stop_{index}"]) for index in range(1, 4)
        ]
        target_levels = [
            float(target_row[f"m5_target_{index}"]) for index in range(1, 4)
        ]
        selected_target = float(target_row["m15_target_1"])
        stop_distances = [
            distance(entry, value)
            if valid_directional_level(direction, entry, value, "stop")
            else None
            for value in stop_levels
        ]
        target_distances = [
            distance(entry, value)
            if valid_directional_level(direction, entry, value, "target")
            else None
            for value in target_levels
        ]
        selected_target_distance = distance(entry, selected_target)
        if selected_target_distance is None:
            raise ValueError("IMP-098 selected target is unavailable")
        valid_targets = sorted(value for value in target_distances if value is not None)
        intervening_targets = [
            value for value in valid_targets
            if value + 1e-9 < selected_target_distance
        ]
        nearest_target = (
            intervening_targets[0]
            if intervening_targets else selected_target_distance
        )
        selected_stop_distance = float(detail["stop_distance_points"])
        stop_1 = stop_distances[0]
        stop_2 = stop_distances[1]
        stop_3 = stop_distances[2]
        if stop_2 is None or not math.isclose(
            stop_2, selected_stop_distance, rel_tol=0.0, abs_tol=1e-6
        ):
            raise ValueError("IMP-098 selected Stop parity changed")
        barrier_count = len(intervening_targets)
        span = selected_stop_distance + selected_target_distance
        records.append({
            "request_id": request_id,
            "observation": observation,
            "direction": direction,
            "gate_result": detail["gate_result"],
            "rejected": detail["gate_result"] == "REJECTED",
            "stop_distance_points": selected_stop_distance,
            "target_distance_points": selected_target_distance,
            "stop_1_distance_points": stop_1,
            "stop_2_distance_points": stop_2,
            "stop_3_distance_points": stop_3,
            "stop_1_to_2_increment_points": (
                stop_2 - stop_1 if stop_1 is not None else None
            ),
            "selected_stop_depth": 2,
            "nearest_target_distance_points": nearest_target,
            "selected_target_distance_points": selected_target_distance,
            "target_obstruction_gap_points": (
                selected_target_distance - nearest_target
            ),
            "intervening_target_barriers": barrier_count,
            "stop_to_target_ratio": (
                selected_stop_distance / selected_target_distance
            ),
            "entry_position_fraction": (
                selected_stop_distance / span if span > 0.0 else None
            ),
            "atr": context["atr"],
            "volatility_change": context["volatility_change"],
            "session": session_label(context),
            "time_of_day": time_of_day(observation),
            "volatility_regime": fixed_regime(context["volatility_regime"]),
            "trend_regime": fixed_regime(context["trend_regime"]),
            "trend_alignment": trend_alignment(
                direction, context["trend_regime"]
            ),
        })
    return records


def numeric_comparison(records: list[dict[str, Any]], field: str) -> dict[str, Any]:
    rejected = [
        float(row[field]) for row in records
        if row["rejected"] and row[field] is not None
    ]
    accepted = [
        float(row[field]) for row in records
        if not row["rejected"] and row[field] is not None
    ]
    return {
        "rejected": numeric_summary(rejected),
        "accepted": numeric_summary(accepted),
        "cliffs_delta_rejected_minus_accepted": cliffs_delta(rejected, accepted),
    }


def classify_imbalance(comparisons: dict[str, dict[str, Any]]) -> dict[str, Any]:
    stop = comparisons["stop_distance_points"]
    target = comparisons["target_distance_points"]
    stop_ratio = stop["rejected"]["median"] / stop["accepted"]["median"]
    target_ratio = target["rejected"]["median"] / target["accepted"]["median"]
    oversized_stop = stop_ratio > 1.25
    undersized_target = target_ratio < 0.80
    if oversized_stop and undersized_target:
        classification = "BOTH_OVERSIZED_STOP_AND_UNDERSIZED_TARGET"
    elif oversized_stop:
        classification = "PRIMARILY_OVERSIZED_STOP"
    elif undersized_target:
        classification = "PRIMARILY_UNDERSIZED_TARGET"
    else:
        classification = "NO_LARGE_MEDIAN_SHIFT"
    return {
        "classification": classification,
        "rejected_to_accepted_stop_median_ratio": stop_ratio,
        "rejected_to_accepted_target_median_ratio": target_ratio,
        "rule": "stop ratio > 1.25; target ratio < 0.80; fixed before analysis",
    }


def write_details(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=DETAIL_COLUMNS)
        writer.writeheader()
        for row in records:
            output = {
                key: (
                    row["observation"].strftime("%Y.%m.%d %H:%M")
                    if key == "observation_time"
                    else row.get(key, "")
                )
                for key in DETAIL_COLUMNS
            }
            output.update({
                "detail_schema_version": "1.0.0",
                "validation_dataset_used": "false",
                "test_dataset_used": "false",
                "deployment_authorized": "false",
            })
            writer.writerow(output)


def indexed(rows: list[dict[str, str]], name: str) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for row in rows:
        request_id = row["request_id"]
        if request_id in result:
            raise ValueError(f"IMP-098 duplicate {name}: {request_id}")
        result[request_id] = row
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--imp097-details", required=True, type=Path)
    parser.add_argument("--imp097-root", required=True, type=Path)
    parser.add_argument("--stop-export", required=True, type=Path)
    parser.add_argument("--target-export", required=True, type=Path)
    parser.add_argument("--decisions", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--details", required=True, type=Path)
    arguments = parser.parse_args()

    expected_hashes = {
        arguments.imp097_details: EXPECTED_DETAIL_SHA256,
        arguments.imp097_root: EXPECTED_ROOT_SHA256,
        arguments.stop_export: EXPECTED_STOP_SHA256,
        arguments.target_export: EXPECTED_TARGET_SHA256,
        arguments.decisions: EXPECTED_DECISIONS_SHA256,
    }
    for path, expected in expected_hashes.items():
        actual = sha256(path)
        if actual != expected:
            raise ValueError(
                f"IMP-098 frozen evidence hash changed: {path} {actual}"
            )

    details = read_csv(arguments.imp097_details)
    if len(details) != 459:
        raise ValueError("IMP-098 IMP-097 detail population changed")
    observations = {parse_time(row["observation_time"]) for row in details}
    contexts = load_extended_contexts(arguments.decisions, observations)
    records = build_records(
        details,
        indexed(read_csv(arguments.stop_export), "Stop ladder"),
        indexed(read_csv(arguments.target_export), "Target ladder"),
        contexts,
    )
    accounting = Counter(
        "rejected" if row["rejected"] else "accepted" for row in records
    )
    if accounting != Counter({"rejected": 383, "accepted": 76}):
        raise ValueError(f"IMP-098 IMP-097 accounting parity failed: {accounting}")

    numeric_fields = (
        "stop_distance_points",
        "target_distance_points",
        "stop_1_distance_points",
        "stop_1_to_2_increment_points",
        "nearest_target_distance_points",
        "target_obstruction_gap_points",
        "intervening_target_barriers",
        "entry_position_fraction",
        "atr",
        "volatility_change",
    )
    comparisons = {
        field: numeric_comparison(records, field) for field in numeric_fields
    }
    factor_fields = (
        "direction", "session", "time_of_day", "volatility_regime",
        "trend_regime", "trend_alignment",
    )
    factors, factor_tests = factor_analysis(records, factor_fields)
    significant = [
        item for item in factor_tests
        if item["statistically_significant"]
    ]
    imbalance = classify_imbalance(comparisons)

    observability = {
        "entry_location_inside_selected_stop_target_span": "OBSERVED_PROXY",
        "invalidation_distance": "OBSERVED",
        "originating_structure_width": "OBSERVED_PROXY_STOP_1_TO_2_INCREMENT",
        "nearby_target_obstruction": "OBSERVED_PROXY_TARGET_LADDER",
        "available_liquidity_distance": "OBSERVED_PROXY_TARGET_LADDER",
        "market_compression_expansion": "OBSERVED_PROXY_VOLATILITY",
        "trend_alignment": "OBSERVED",
        "buy_sell": "OBSERVED",
        "session": "OBSERVED",
        "volatility_regime": "OBSERVED",
        "market_regime": "OBSERVED_PROXY_TREND_AND_VOLATILITY",
        "structure_age": "UNOBSERVABLE_NO_STRUCTURE_TIMESTAMP",
        "structure_depth": "OBSERVED_LADDER_RANK",
        "intervening_barriers": "OBSERVED_TARGET_LADDER_COUNT",
        "late_entry_in_developed_move": "UNOBSERVABLE_NO_MOVE_ORIGIN_TIMESTAMP",
    }
    root_causes = [
        {
            "cause": "OVERSIZED_SELECTED_STOP",
            "evidence": comparisons["stop_distance_points"],
            "causal_status": "PLAUSIBLE_MECHANICAL_COMPONENT",
        },
        {
            "cause": "UNDERSIZED_AVAILABLE_TARGET",
            "evidence": comparisons["target_distance_points"],
            "causal_status": "PLAUSIBLE_MECHANICAL_COMPONENT",
        },
        {
            "cause": "STOP_DEPTH_INCREMENT",
            "evidence": comparisons["stop_1_to_2_increment_points"],
            "causal_status": "PLAUSIBLE_STOP_CONSTRUCTION_COMPONENT",
        },
        {
            "cause": "TARGET_LADDER_OBSTRUCTION",
            "evidence": comparisons["intervening_target_barriers"],
            "causal_status": "ASSOCIATION_ONLY_PROXY",
        },
    ]
    next_decision = (
        "GO_TRAIN_ONLY_EXPERIMENT"
        if imbalance["classification"]
        == "BOTH_OVERSIZED_STOP_AND_UNDERSIZED_TARGET"
        and any(
            abs(item["evidence"]["cliffs_delta_rejected_minus_accepted"] or 0.0)
            >= 0.33
            for item in root_causes[:3]
        )
        else "CONTINUE_DIAGNOSTIC_RESEARCH"
    )
    report = {
        "report_schema_version": "1.0.0",
        "status": "IMP098_STRUCTURAL_IMBALANCE_DIAGNOSTIC_NO_RUNTIME_GO",
        "architecture_baseline": "ABR-1.0_FROZEN",
        "frozen_baseline": "IMP-097",
        "methodology": {
            "scope": "TRAIN_ONLY_DIAGNOSTIC",
            "population": len(records),
            "minimum_rr_changed": False,
            "geometry_changed": False,
            "fixed_imbalance_rule": imbalance["rule"],
            "numeric_effect": "Cliffs delta, rejected minus accepted",
            "categorical_tests": "Two-proportion tests with Bonferroni correction",
        },
        "source_hashes": {
            path.name: sha256(path) for path in expected_hashes
        },
        "baseline_parity": {
            "rr_evaluable_geometry": len(records) == 459,
            "rejected": accounting["rejected"] == 383,
            "accepted": accounting["accepted"] == 76,
            "train_only": all(
                row["observation"] < TRAIN_END_EXCLUSIVE for row in records
            ),
        },
        "accounting": dict(accounting),
        "observability": observability,
        "stop_vs_target_diagnosis": imbalance,
        "numeric_component_analysis": comparisons,
        "factor_analysis": factors,
        "significant_associations_after_correction": significant,
        "root_cause_summary": root_causes,
        "research_questions": {
            "oversized_stop_or_undersized_target": imbalance["classification"],
            "stop_components": "Selected Stop-2 distance and Stop-1-to-2 increment",
            "target_constraints": "Selected/nearest target distances and intervening ladder barriers",
            "entry_placement": "Measured only as selected Stop/Target span proxy",
            "late_entry": "UNANSWERED_WITH_CURRENT_PROVENANCE",
            "nearby_opposing_structures": "Measured only through target-ladder proxies",
            "buy_sell_session_regime": "Reported as corrected associations, not causation",
            "causal_interpretation": "Geometry distances are mechanical; context factors are correlational",
            "future_experiment_evidence": next_decision,
        },
        "gate_decision": {
            "decision": next_decision,
            "runtime_candidate_created": False,
            "minimum_rr_changed": False,
            "parameters_optimized": False,
            "validation_dataset_used": False,
            "test_dataset_used": False,
            "model_training_performed": False,
            "runtime_changed": False,
            "protected_modules_changed": False,
            "deployment_authorized": False,
        },
        "limitations": [
            "Structure age and late-entry timing are not present in frozen evidence.",
            "Target ladder counts are obstruction proxies, not identified causal structures.",
            "No association is converted into a Runtime filter or production threshold.",
            "The fixed median-ratio classification is diagnostic, not optimization.",
        ],
    }
    if not all(report["baseline_parity"].values()):
        raise ValueError("IMP-098 baseline parity failed")
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(
        json.dumps(report, indent=2, sort_keys=True), encoding="utf-8"
    )
    write_details(arguments.details, records)
    print(json.dumps({
        "status": report["status"],
        "accounting": report["accounting"],
        "diagnosis": imbalance,
        "significant_associations": significant,
        "gate_decision": report["gate_decision"],
    }, indent=2))


if __name__ == "__main__":
    main()
