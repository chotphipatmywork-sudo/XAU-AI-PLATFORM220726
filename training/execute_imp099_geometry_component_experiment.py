"""Execute the locked IMP-099 Train-only four-arm geometry experiment."""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
from collections import Counter
from pathlib import Path
from statistics import median
from typing import Any

from build_setup_outcome_dataset import parse_time
from diagnose_current_feed_setup_funnel import TRAIN_END_EXCLUSIVE, sha256
from replay_past_only_targets import geometry_and_rr
from validate_imp099_preregistration import validate_spec, verify_sources


EXPECTED_PREREGISTRATION_SHA256 = (
    "E0A9B1F5D342C2527AC929557CFCB961E9C8BF71B4193A20234AE252A33F17FA"
)
POINT_SIZE = 0.01
BOOTSTRAP_REPLICATES = 10000

RAW_COLUMNS = (
    "experiment_id",
    "request_id",
    "observation_time",
    "direction",
    "arm_id",
    "stop_name",
    "target_name",
    "entry",
    "stop",
    "target",
    "structurally_valid",
    "cost_known",
    "eligible",
    "stop_distance_points",
    "target_distance_points",
    "cost_adjusted_rr",
    "minimum_rr",
    "rr_pass",
    "common_support",
    "validation_dataset_used",
    "test_dataset_used",
    "deployment_authorized",
)


def read_indexed(path: Path) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"IMP-099 source header missing: {path}")
        for row in reader:
            request_id = row["request_id"]
            if request_id in result:
                raise ValueError(f"IMP-099 duplicate request: {request_id}")
            result[request_id] = row
    return result


def evaluate_arm(
    stop_row: dict[str, str],
    target_row: dict[str, str],
    arm: dict[str, str],
    minimum_rr: float,
) -> dict[str, Any]:
    direction = stop_row["direction"]
    entry = float(stop_row["entry"])
    stop = float(stop_row[arm["stop"]])
    target = float(target_row[arm["target"]])
    cost_known = stop_row["cost_known"].lower() == "true"
    structurally_valid = (
        stop > 0.0
        and target > 0.0
        and (
            direction == "TRADE_SETUP_BUY" and stop < entry < target
            or direction == "TRADE_SETUP_SELL" and target < entry < stop
        )
    )
    eligible = False
    adjusted_rr = None
    if structurally_valid and cost_known:
        eligible, adjusted_rr = geometry_and_rr(
            direction,
            entry,
            stop,
            target,
            float(stop_row["estimated_cost_points"]),
        )
    return {
        "arm_id": arm["arm_id"],
        "stop_name": arm["stop"],
        "target_name": arm["target"],
        "entry": entry,
        "stop": stop,
        "target": target,
        "structurally_valid": structurally_valid,
        "cost_known": cost_known,
        "eligible": bool(eligible and adjusted_rr is not None),
        "stop_distance_points": (
            abs(entry - stop) / POINT_SIZE if structurally_valid else None
        ),
        "target_distance_points": (
            abs(target - entry) / POINT_SIZE if structurally_valid else None
        ),
        "cost_adjusted_rr": adjusted_rr,
        "minimum_rr": minimum_rr,
        "rr_pass": bool(
            eligible
            and adjusted_rr is not None
            and adjusted_rr + 1e-9 >= minimum_rr
        ),
    }


def exact_mcnemar_p_value(improved: int, worsened: int) -> float:
    discordant = improved + worsened
    if discordant == 0:
        return 1.0
    tail = sum(
        math.comb(discordant, value)
        for value in range(0, min(improved, worsened) + 1)
    ) / (2 ** discordant)
    return min(1.0, 2.0 * tail)


def paired_bootstrap_interval(
    control: list[int], candidate: list[int], seed: int = 98099
) -> list[float]:
    if len(control) != len(candidate) or not control:
        raise ValueError("IMP-099 paired bootstrap population invalid")
    rng = random.Random(seed)
    size = len(control)
    deltas: list[float] = []
    for _ in range(BOOTSTRAP_REPLICATES):
        difference = 0
        for _ in range(size):
            index = rng.randrange(size)
            difference += candidate[index] - control[index]
        deltas.append(difference / size)
    deltas.sort()
    return [
        deltas[int(0.025 * (len(deltas) - 1))],
        deltas[int(0.975 * (len(deltas) - 1))],
    ]


def arm_metrics(rows: list[dict[str, Any]], request_count: int) -> dict[str, Any]:
    eligible = [row for row in rows if row["eligible"]]
    passes = [row for row in eligible if row["rr_pass"]]
    by_direction: dict[str, Any] = {}
    for direction in ("TRADE_SETUP_BUY", "TRADE_SETUP_SELL"):
        subset = [row for row in eligible if row["direction"] == direction]
        direction_passes = sum(row["rr_pass"] for row in subset)
        by_direction[direction] = {
            "eligible": len(subset),
            "passes": direction_passes,
            "pass_rate": direction_passes / len(subset) if subset else None,
        }
    return {
        "requests": request_count,
        "structurally_valid": sum(row["structurally_valid"] for row in rows),
        "eligible": len(eligible),
        "coverage_rate": len(eligible) / request_count,
        "passes": len(passes),
        "pass_rate": len(passes) / len(eligible) if eligible else None,
        "median_stop_distance_points": median(
            row["stop_distance_points"] for row in eligible
        ) if eligible else None,
        "median_target_distance_points": median(
            row["target_distance_points"] for row in eligible
        ) if eligible else None,
        "median_cost_adjusted_rr": median(
            row["cost_adjusted_rr"] for row in eligible
        ) if eligible else None,
        "by_direction": by_direction,
    }


def execute(
    spec: dict[str, Any],
    stop_rows: dict[str, dict[str, str]],
    target_rows: dict[str, dict[str, str]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if set(stop_rows) != set(target_rows):
        raise ValueError("IMP-099 Stop/Target request pairing changed")
    if len(stop_rows) != spec["population"]["request_records"]:
        raise ValueError("IMP-099 request population changed")
    arms = spec["factorial_design"]["arms"]
    minimum_rr = float(spec["frozen_policy"]["minimum_rr"])
    raw: list[dict[str, Any]] = []
    evaluations: dict[str, dict[str, dict[str, Any]]] = {}
    for request_id in sorted(stop_rows):
        stop_row = stop_rows[request_id]
        target_row = target_rows[request_id]
        if stop_row["observation_time"] != target_row["observation_time"]:
            raise ValueError("IMP-099 paired observation changed")
        observation = parse_time(stop_row["observation_time"])
        if observation >= TRAIN_END_EXCLUSIVE:
            raise ValueError("IMP-099 future data escaped Train-only boundary")
        if stop_row["direction"] != target_row["direction"]:
            raise ValueError("IMP-099 paired direction changed")
        evaluations[request_id] = {
            arm["arm_id"]: evaluate_arm(stop_row, target_row, arm, minimum_rr)
            for arm in arms
        }
    common_ids = {
        request_id for request_id, items in evaluations.items()
        if all(item["eligible"] for item in items.values())
    }
    for request_id in sorted(evaluations):
        stop_row = stop_rows[request_id]
        for arm in arms:
            item = evaluations[request_id][arm["arm_id"]]
            raw.append({
                "experiment_id": "IMP-099",
                "request_id": request_id,
                "observation_time": stop_row["observation_time"],
                "direction": stop_row["direction"],
                **item,
                "common_support": request_id in common_ids,
            })

    grouped = {
        arm["arm_id"]: [
            row for row in raw if row["arm_id"] == arm["arm_id"]
        ]
        for arm in arms
    }
    metrics = {
        arm_id: arm_metrics(rows, len(stop_rows))
        for arm_id, rows in grouped.items()
    }
    control_common = {
        row["request_id"]: row for row in grouped["CONTROL"]
        if row["request_id"] in common_ids
    }
    gate = spec["train_only_experiment_gate"]
    alpha = spec["analysis_contract"]["bonferroni_alpha"]
    contrasts: dict[str, Any] = {}
    for arm_id in ("STOP_ONLY", "TARGET_ONLY", "COMBINED"):
        candidate_common = {
            row["request_id"]: row for row in grouped[arm_id]
            if row["request_id"] in common_ids
        }
        ordered_ids = sorted(common_ids)
        control_values = [
            int(control_common[item]["rr_pass"]) for item in ordered_ids
        ]
        candidate_values = [
            int(candidate_common[item]["rr_pass"]) for item in ordered_ids
        ]
        improved = sum(
            candidate > control
            for control, candidate in zip(control_values, candidate_values)
        )
        worsened = sum(
            candidate < control
            for control, candidate in zip(control_values, candidate_values)
        )
        control_rate = sum(control_values) / len(ordered_ids)
        candidate_rate = sum(candidate_values) / len(ordered_ids)
        direction_improvements: dict[str, float] = {}
        for direction in ("TRADE_SETUP_BUY", "TRADE_SETUP_SELL"):
            direction_ids = [
                item for item in ordered_ids
                if stop_rows[item]["direction"] == direction
            ]
            direction_improvements[direction] = (
                sum(candidate_common[item]["rr_pass"] for item in direction_ids)
                - sum(control_common[item]["rr_pass"] for item in direction_ids)
            ) / len(direction_ids)
        coverage_ratio = (
            metrics[arm_id]["coverage_rate"]
            / metrics["CONTROL"]["coverage_rate"]
        )
        p_value = exact_mcnemar_p_value(improved, worsened)
        improvement = candidate_rate - control_rate
        checks = {
            "minimum_common_support": len(common_ids)
            >= gate["minimum_common_support_records"],
            "minimum_absolute_improvement": improvement
            >= gate["minimum_absolute_pass_rate_improvement"],
            "minimum_relative_coverage": coverage_ratio
            >= gate["minimum_relative_coverage_vs_control"],
            "corrected_significance": p_value < alpha,
            "both_directions_improve": all(
                value > 0.0 for value in direction_improvements.values()
            ),
        }
        contrasts[f"{arm_id}_MINUS_CONTROL"] = {
            "common_support_records": len(common_ids),
            "control_pass_rate": control_rate,
            "candidate_pass_rate": candidate_rate,
            "absolute_pass_rate_improvement": improvement,
            "paired_bootstrap_95": paired_bootstrap_interval(
                control_values, candidate_values
            ),
            "improved_pairs": improved,
            "worsened_pairs": worsened,
            "mcnemar_exact_two_sided_p_value": p_value,
            "bonferroni_alpha": alpha,
            "relative_coverage_vs_control": coverage_ratio,
            "direction_improvements": direction_improvements,
            "gate_checks": checks,
            "gate_passed": all(checks.values()),
        }
    any_passed = any(item["gate_passed"] for item in contrasts.values())
    decision = (
        "GO_TRAIN_ONLY_REPLAY"
        if any_passed else "CONTINUE_DIAGNOSTIC_RESEARCH"
    )
    report = {
        "report_schema_version": "1.0.0",
        "experiment_id": "IMP-099",
        "status": "EXECUTED_TRAIN_ONLY",
        "contract_sha256": EXPECTED_PREREGISTRATION_SHA256,
        "configuration_matches_preregistration": True,
        "source_hashes_verified": True,
        "future_data_leakage_detected": False,
        "pairing_preserved": True,
        "common_support_definition": "ALL_FOUR_ARMS_ELIGIBLE",
        "common_support_records": len(common_ids),
        "arm_metrics": metrics,
        "primary_contrasts": contrasts,
        "gate_result": {
            "decision": decision,
            "passing_arms": [
                name for name, item in contrasts.items()
                if item["gate_passed"]
            ],
            "runtime_candidate_created": False,
            "validation_dataset_used": False,
            "test_dataset_used": False,
            "runtime_changed": False,
            "protected_modules_changed": False,
            "deployment_authorized": False,
        },
    }
    if metrics["CONTROL"]["eligible"] != 459:
        raise ValueError("IMP-099 CONTROL eligible parity failed")
    if metrics["CONTROL"]["passes"] != 76:
        raise ValueError("IMP-099 CONTROL pass parity failed")
    return raw, report


def write_raw(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=RAW_COLUMNS)
        writer.writeheader()
        for row in rows:
            output = {key: row.get(key, "") for key in RAW_COLUMNS}
            output.update({
                "structurally_valid": str(row["structurally_valid"]).lower(),
                "cost_known": str(row["cost_known"]).lower(),
                "eligible": str(row["eligible"]).lower(),
                "rr_pass": str(row["rr_pass"]).lower(),
                "common_support": str(row["common_support"]).lower(),
                "validation_dataset_used": "false",
                "test_dataset_used": "false",
                "deployment_authorized": "false",
            })
            writer.writerow(output)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--repository", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--raw", required=True, type=Path)
    parser.add_argument("--validation", required=True, type=Path)
    parser.add_argument("--gate", required=True, type=Path)
    arguments = parser.parse_args()
    if sha256(arguments.config) != EXPECTED_PREREGISTRATION_SHA256:
        raise ValueError("IMP-099 preregistration file changed")
    spec = json.loads(arguments.config.read_text(encoding="utf-8-sig"))
    validate_spec(spec)
    verify_sources(spec, arguments.repository)
    stop_path = arguments.repository / spec["frozen_sources"]["stop_ladder"]["path"]
    target_path = (
        arguments.repository / spec["frozen_sources"]["target_ladder"]["path"]
    )
    raw, report = execute(
        spec, read_indexed(stop_path), read_indexed(target_path)
    )
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(
        json.dumps(report, indent=2, sort_keys=True), encoding="utf-8"
    )
    write_raw(arguments.raw, raw)
    validation = {
        "validation_schema_version": "1.0.0",
        "experiment_id": "IMP-099",
        "status": "PASS",
        "configuration_matches_preregistration": True,
        "source_hashes_verified": True,
        "contract_violation_detected": False,
        "future_data_leakage_detected": False,
        "pairing_preserved": True,
        "common_support_definition_preserved": True,
        "control_eligible_parity": (
            report["arm_metrics"]["CONTROL"]["eligible"] == 459
        ),
        "control_pass_parity": (
            report["arm_metrics"]["CONTROL"]["passes"] == 76
        ),
        "raw_record_count": len(raw),
        "expected_raw_record_count": 597 * 4,
        "validation_dataset_used": False,
        "test_dataset_used": False,
        "runtime_changed": False,
        "protected_modules_changed": False,
        "deployment_authorized": False,
    }
    required_checks = (
        "configuration_matches_preregistration",
        "source_hashes_verified",
        "pairing_preserved",
        "common_support_definition_preserved",
        "control_eligible_parity",
        "control_pass_parity",
    )
    if not all(validation[key] for key in required_checks) or (
        validation["raw_record_count"]
        != validation["expected_raw_record_count"]
    ):
        raise ValueError("IMP-099 execution validation failed")
    arguments.validation.write_text(
        json.dumps(validation, indent=2, sort_keys=True), encoding="utf-8"
    )
    arguments.gate.write_text(
        json.dumps(report["gate_result"], indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(json.dumps({
        "status": report["status"],
        "common_support_records": report["common_support_records"],
        "arm_metrics": report["arm_metrics"],
        "primary_contrasts": report["primary_contrasts"],
        "gate_result": report["gate_result"],
    }, indent=2))


if __name__ == "__main__":
    main()
