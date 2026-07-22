"""XAU AI PLATFORM | Offline Research | Version 1.0.0.

File: diagnose_objective_setup_failures.py
Purpose: Diagnose frozen Objective Setup geometry inside Stage D Train only.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from build_setup_outcome_dataset import (
    FEATURE_SCHEMA_VERSION,
    OUTCOME_AUDIT_COLUMNS,
    SETUP_AUDIT_COLUMNS,
    SETUP_OUTCOME_SCHEMA_VERSION,
    TRAINABLE_OUTCOMES,
    as_bool,
    finite_float,
    parse_time,
)
from setup_quality_walk_forward import build_time_purged_folds, readiness


DIAGNOSTIC_SCHEMA_VERSION = "1.0.0"
DIAGNOSTIC_STATUS = "OBJECTIVE_SETUP_FAILURE_DIAGNOSTIC_NO_GO"
FROZEN_TRAIN_SHA256 = "DDBCECB29B2B53F848447006618CACF6032649AEC4EC46B60F3CAB4C6643BF84"
FROZEN_SETUP_AUDIT_SHA256 = "FCBBD1B4866D579F662E6D3D97EBFDA455D8220B44F2769A5DD7799428714CEC"
EXPECTED_POSITIVE = "positive"
EXPECTED_NEGATIVE = "negative"
EXPECTED_EXPLORATORY = "exploratory"
MINIMUM_FOLD_MATCHES = 3
MINIMUM_TOTAL_MATCHES = 20
MINIMUM_TARGET_RATE_LIFT = 0.05
MINIMUM_EXPECTANCY_LIFT_R = 0.10


@dataclass(frozen=True)
class GeometryHypothesis:
    name: str
    question: str
    rule: str
    expected_effect: str
    predicate: Callable[[dict[str, float]], bool]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def verify_frozen_sources(train_path: Path, setup_path: Path) -> dict[str, str]:
    train_hash = sha256(train_path)
    setup_hash = sha256(setup_path)
    if train_hash != FROZEN_TRAIN_SHA256:
        raise ValueError("Objective failure diagnostic Train hash mismatch")
    if setup_hash != FROZEN_SETUP_AUDIT_SHA256:
        raise ValueError("Objective failure diagnostic Setup Audit hash mismatch")
    return {"train_sha256": train_hash, "setup_audit_sha256": setup_hash}


def registered_hypotheses() -> tuple[GeometryHypothesis, ...]:
    return (
        GeometryHypothesis(
            "deep_sweep",
            "Does penetration of at least 0.10 ATR support plan quality?",
            "sweep_penetration_atr >= 0.10",
            EXPECTED_POSITIVE,
            lambda value: value["sweep_penetration_atr"] >= 0.10,
        ),
        GeometryHypothesis(
            "marginal_sweep",
            "Does penetration below 0.05 ATR identify fragile triggers?",
            "sweep_penetration_atr < 0.05",
            EXPECTED_NEGATIVE,
            lambda value: value["sweep_penetration_atr"] < 0.05,
        ),
        GeometryHypothesis(
            "strong_reclaim",
            "Does a reclaim of at least 0.10 ATR support plan quality?",
            "reclaim_distance_atr >= 0.10",
            EXPECTED_POSITIVE,
            lambda value: value["reclaim_distance_atr"] >= 0.10,
        ),
        GeometryHypothesis(
            "weak_reclaim",
            "Does a reclaim below 0.05 ATR identify fragile triggers?",
            "reclaim_distance_atr < 0.05",
            EXPECTED_NEGATIVE,
            lambda value: value["reclaim_distance_atr"] < 0.05,
        ),
        GeometryHypothesis(
            "reclaim_dominates_sweep",
            "Does reclaim distance at least equal sweep penetration?",
            "reclaim_to_sweep_ratio >= 1.0",
            EXPECTED_POSITIVE,
            lambda value: value["reclaim_to_sweep_ratio"] >= 1.0,
        ),
        GeometryHypothesis(
            "reclaim_less_than_half_sweep",
            "Does reclaim below half the sweep identify fragile triggers?",
            "reclaim_to_sweep_ratio < 0.50",
            EXPECTED_NEGATIVE,
            lambda value: value["reclaim_to_sweep_ratio"] < 0.50,
        ),
        GeometryHypothesis(
            "large_trigger_excursion",
            "Does combined sweep and reclaim of at least 0.20 ATR support quality?",
            "trigger_excursion_atr >= 0.20",
            EXPECTED_POSITIVE,
            lambda value: value["trigger_excursion_atr"] >= 0.20,
        ),
        GeometryHypothesis(
            "high_cost_burden",
            "Does estimated cost at least 20% of effective risk identify fragility?",
            "cost_to_effective_risk >= 0.20",
            EXPECTED_NEGATIVE,
            lambda value: value["cost_to_effective_risk"] >= 0.20,
        ),
        GeometryHypothesis(
            "low_cost_burden",
            "Does estimated cost at most 10% of effective risk support quality?",
            "cost_to_effective_risk <= 0.10",
            EXPECTED_POSITIVE,
            lambda value: value["cost_to_effective_risk"] <= 0.10,
        ),
        GeometryHypothesis(
            "rr_near_minimum",
            "Does a cost-adjusted RR below 2.50 change plan quality?",
            "plan_rr < 2.50",
            EXPECTED_EXPLORATORY,
            lambda value: value["plan_rr"] < 2.50,
        ),
        GeometryHypothesis(
            "rr_at_least_three",
            "Does a cost-adjusted RR of at least 3.0 change plan quality?",
            "plan_rr >= 3.0",
            EXPECTED_EXPLORATORY,
            lambda value: value["plan_rr"] >= 3.0,
        ),
    )


def read_train(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or tuple(reader.fieldnames) != OUTCOME_AUDIT_COLUMNS:
            raise ValueError("Unexpected Objective failure Train schema")
        rows = list(reader)
    samples: list[dict[str, Any]] = []
    previous: datetime | None = None
    for row in rows:
        if row["setup_outcome_schema_version"] != SETUP_OUTCOME_SCHEMA_VERSION:
            raise ValueError("Objective failure Setup Outcome Schema mismatch")
        if row["feature_schema_version"] != FEATURE_SCHEMA_VERSION:
            raise ValueError("Objective failure Feature Schema mismatch")
        if not as_bool(row["trainable"]) or row["outcome"] not in TRAINABLE_OUTCOMES:
            raise ValueError("Objective failure Train contains quarantined evidence")
        observation = parse_time(row["observation_time"])
        known_at = parse_time(row["outcome_known_at"])
        if previous is not None and observation <= previous:
            raise ValueError("Objective failure Train is not chronological")
        direction = row["direction"]
        if direction not in {"TRADE_SETUP_BUY", "TRADE_SETUP_SELL"}:
            raise ValueError("Objective failure Train direction is invalid")
        plan_entry = finite_float(row["plan_entry"], "plan_entry")
        plan_stop = finite_float(row["plan_stop"], "plan_stop")
        plan_target = finite_float(row["plan_target"], "plan_target")
        plan_rr = finite_float(row["plan_rr"], "plan_rr")
        point_size = finite_float(row["point_size"], "point_size")
        risk_points = finite_float(row["risk_points"], "risk_points")
        cost_points = finite_float(row["estimated_cost_points"], "estimated_cost_points")
        if point_size <= 0.0 or risk_points <= 0.0 or cost_points < 0.0:
            raise ValueError("Objective failure Train planning values are invalid")
        net_outcome_r = (
            plan_rr if row["outcome"] == "TARGET_FIRST"
            else -1.0 if row["outcome"] == "STOP_FIRST"
            else 0.0
        )
        samples.append({
            "observation": observation,
            "known_at": known_at,
            "direction": direction,
            "plan_entry": plan_entry,
            "plan_stop": plan_stop,
            "plan_target": plan_target,
            "plan_rr": plan_rr,
            "minimum_rr": finite_float(row["minimum_rr"], "minimum_rr"),
            "point_size": point_size,
            "risk_points": risk_points,
            "estimated_cost_points": cost_points,
            "label": 1 if row["outcome"] == "TARGET_FIRST" else 0,
            "outcome": row["outcome"],
            "net_outcome_r": net_outcome_r,
        })
        previous = observation
    if not samples:
        raise ValueError("Objective failure Train is empty")
    return samples


def close_enough(left: float, right: float) -> bool:
    return math.isclose(left, right, rel_tol=1e-9, abs_tol=1e-6)


def join_setup_geometry(samples: list[dict[str, Any]], setup_path: Path) -> None:
    sample_by_time = {sample["observation"]: sample for sample in samples}
    matched: set[datetime] = set()
    with setup_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or tuple(reader.fieldnames) != SETUP_AUDIT_COLUMNS:
            raise ValueError("Unexpected frozen Objective Setup Audit schema")
        for row in reader:
            observation = parse_time(row["observation_time"])
            sample = sample_by_time.get(observation)
            if sample is None:
                continue
            if observation in matched or not as_bool(row["plan_available"]):
                raise ValueError("Objective failure Setup join is duplicate or unavailable")
            if row["direction"] != sample["direction"]:
                raise ValueError("Objective failure Setup direction join mismatch")
            comparisons = (
                ("plan_entry", sample["plan_entry"]),
                ("plan_stop", sample["plan_stop"]),
                ("plan_target", sample["plan_target"]),
                ("plan_rr", sample["plan_rr"]),
                ("minimum_rr", sample["minimum_rr"]),
                ("estimated_cost_points", sample["estimated_cost_points"]),
            )
            if any(
                not close_enough(finite_float(row[name], name), float(expected))
                for name, expected in comparisons
            ):
                raise ValueError("Objective failure Setup planning join mismatch")
            sweep = finite_float(row["sweep_penetration_atr"], "sweep_penetration_atr")
            reclaim = finite_float(row["reclaim_distance_atr"], "reclaim_distance_atr")
            if sweep <= 0.0 or reclaim < 0.0:
                raise ValueError("Objective failure Setup trigger geometry is invalid")
            gross_risk = float(sample["risk_points"])
            cost = float(sample["estimated_cost_points"])
            geometry = {
                "sweep_penetration_atr": sweep,
                "reclaim_distance_atr": reclaim,
                "reclaim_to_sweep_ratio": reclaim / sweep,
                "trigger_excursion_atr": sweep + reclaim,
                "cost_to_effective_risk": cost / (gross_risk + cost),
                "plan_rr": float(sample["plan_rr"]),
                "rr_headroom": float(sample["plan_rr"]) - float(sample["minimum_rr"]),
                "gross_reward_to_risk": (
                    abs(float(sample["plan_target"]) - float(sample["plan_entry"]))
                    / abs(float(sample["plan_entry"]) - float(sample["plan_stop"]))
                ),
            }
            if any(not math.isfinite(value) for value in geometry.values()):
                raise ValueError("Objective failure derived geometry is non-finite")
            sample["geometry"] = geometry
            matched.add(observation)
    if len(matched) != len(samples):
        raise ValueError(
            f"Objective failure Setup join missing {len(samples) - len(matched)} Train plans"
        )


def subgroup_metrics(
    samples: list[dict[str, Any]], indices: list[int], hypothesis: GeometryHypothesis
) -> dict[str, Any]:
    matches = [
        index for index in indices
        if hypothesis.predicate(samples[index]["geometry"])
    ]
    matched_set = set(matches)
    complement = [index for index in indices if index not in matched_set]
    base_labels = [int(samples[index]["label"]) for index in indices]
    matched_labels = [int(samples[index]["label"]) for index in matches]
    base_returns = [float(samples[index]["net_outcome_r"]) for index in indices]
    matched_returns = [float(samples[index]["net_outcome_r"]) for index in matches]
    complement_labels = [int(samples[index]["label"]) for index in complement]
    complement_returns = [
        float(samples[index]["net_outcome_r"]) for index in complement
    ]
    base_rate = sum(base_labels) / len(base_labels)
    base_expectancy = sum(base_returns) / len(base_returns)
    matched_rate = sum(matched_labels) / len(matched_labels) if matches else None
    matched_expectancy = sum(matched_returns) / len(matched_returns) if matches else None
    return {
        "evaluation_records": len(indices),
        "base_target_rate": base_rate,
        "base_expectancy_r": base_expectancy,
        "matched_records": len(matches),
        "matched_target_count": sum(matched_labels),
        "matched_target_rate": matched_rate,
        "matched_expectancy_r": matched_expectancy,
        "complement_records": len(complement),
        "complement_target_count": sum(complement_labels),
        "complement_target_rate": (
            sum(complement_labels) / len(complement) if complement else None
        ),
        "complement_expectancy_r": (
            sum(complement_returns) / len(complement) if complement else None
        ),
        "target_rate_lift": matched_rate - base_rate if matched_rate is not None else None,
        "expectancy_lift_r": (
            matched_expectancy - base_expectancy
            if matched_expectancy is not None else None
        ),
    }


def evaluate_hypothesis(
    samples: list[dict[str, Any]], folds: list[tuple[list[int], list[int]]],
    hypothesis: GeometryHypothesis
) -> dict[str, Any]:
    fold_reports: list[dict[str, Any]] = []
    aggregate_indices: list[int] = []
    for fold_number, (_, evaluation_indices) in enumerate(folds, start=1):
        metrics = subgroup_metrics(samples, evaluation_indices, hypothesis)
        metrics.update({
            "fold": fold_number,
            "minimum_support_met": metrics["matched_records"] >= MINIMUM_FOLD_MATCHES,
        })
        fold_reports.append(metrics)
        aggregate_indices.extend(evaluation_indices)
    aggregate = subgroup_metrics(samples, aggregate_indices, hypothesis)
    target_lifts = [report["target_rate_lift"] for report in fold_reports]
    expectancy_lifts = [report["expectancy_lift_r"] for report in fold_reports]
    support_met = (
        all(report["minimum_support_met"] for report in fold_reports)
        and aggregate["matched_records"] >= MINIMUM_TOTAL_MATCHES
    )
    positive_all = all(
        target is not None and target > 0.0 and expectancy is not None and expectancy > 0.0
        for target, expectancy in zip(target_lifts, expectancy_lifts)
    )
    negative_all = all(
        target is not None and target < 0.0 and expectancy is not None and expectancy < 0.0
        for target, expectancy in zip(target_lifts, expectancy_lifts)
    )
    expected_sign_met = (
        hypothesis.expected_effect == EXPECTED_POSITIVE and positive_all
    ) or (
        hypothesis.expected_effect == EXPECTED_NEGATIVE and negative_all
    )
    target_effect_met = (
        aggregate["target_rate_lift"] is not None
        and abs(float(aggregate["target_rate_lift"])) >= MINIMUM_TARGET_RATE_LIFT
    )
    expectancy_effect_met = (
        aggregate["expectancy_lift_r"] is not None
        and abs(float(aggregate["expectancy_lift_r"])) >= MINIMUM_EXPECTANCY_LIFT_R
    )
    stable = support_met and expected_sign_met and target_effect_met and expectancy_effect_met
    return {
        "name": hypothesis.name,
        "question": hypothesis.question,
        "fixed_rule": hypothesis.rule,
        "preregistered_expected_effect": hypothesis.expected_effect,
        "aggregate": aggregate,
        "folds": fold_reports,
        "support_gate_met": support_met,
        "expected_target_and_expectancy_sign_met_all_four_folds": expected_sign_met,
        "aggregate_target_effect_met": target_effect_met,
        "aggregate_expectancy_effect_met": expectancy_effect_met,
        "stable_failure_diagnostic_gate_met": stable,
    }


def run_diagnostic(
    samples: list[dict[str, Any]], source_audit: dict[str, str] | None = None
) -> dict[str, Any]:
    state = readiness(samples)
    report: dict[str, Any] = {
        "diagnostic_schema_version": DIAGNOSTIC_SCHEMA_VERSION,
        "diagnostic_stage": "objective_setup_train_only_failure_geometry",
        "diagnostic_status": DIAGNOSTIC_STATUS,
        "setup_outcome_schema_version": SETUP_OUTCOME_SCHEMA_VERSION,
        "feature_schema_version": FEATURE_SCHEMA_VERSION,
        "source_audit": source_audit or {},
        "validation_dataset_used": False,
        "test_dataset_used": False,
        "model_training_performed": False,
        "runtime_integration_authorized": False,
        "deployment_authorized": False,
        "readiness": state,
        "predicate_fields": [
            "sweep_penetration_atr", "reclaim_distance_atr",
            "reclaim_to_sweep_ratio", "trigger_excursion_atr",
            "cost_to_effective_risk", "plan_rr", "rr_headroom",
            "gross_reward_to_risk",
        ],
        "forbidden_predicate_fields": [
            "outcome", "bars_observed", "mfe_points", "mae_points",
            "mfe_r", "mae_r", "realized_r",
        ],
        "hypotheses": [],
        "stable_preregistered_findings": [],
        "eligible_to_request_setup_contract_change": False,
        "setup_contract_change_authorized": False,
    }
    if not state["ready"]:
        report["refusal_reason"] = "Stage D Train readiness gate is not met."
        return report
    if any("geometry" not in sample for sample in samples):
        raise ValueError("Objective failure Train is missing frozen Setup geometry")
    folds = build_time_purged_folds(samples)
    results = [
        evaluate_hypothesis(samples, folds, hypothesis)
        for hypothesis in registered_hypotheses()
    ]
    stable = [
        result["name"]
        for result in results
        if result["stable_failure_diagnostic_gate_met"]
    ]
    report["fold_count"] = len(folds)
    report["hypotheses"] = results
    report["stable_preregistered_findings"] = stable
    report["eligible_to_request_setup_contract_change"] = bool(stable)
    report["limitations"] = [
        "Only the frozen Stage D Train and matching frozen Setup Audit are read.",
        "Plan/outcome fields remain outside the canonical AI Feature Schema.",
        "Entry ATR is absent, so Stop/Target volatility normalization is not inferred.",
        "A stable finding requests review and never changes Runtime automatically.",
    ]
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", required=True, type=Path)
    parser.add_argument("--setup-audit", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    arguments = parser.parse_args()
    source_audit = verify_frozen_sources(arguments.train, arguments.setup_audit)
    samples = read_train(arguments.train)
    join_setup_geometry(samples, arguments.setup_audit)
    report = run_diagnostic(samples, source_audit)
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({
        "diagnostic_stage": report["diagnostic_stage"],
        "readiness": report["readiness"],
        "hypothesis_count": len(report["hypotheses"]),
        "stable_preregistered_findings": report["stable_preregistered_findings"],
        "eligible_to_request_setup_contract_change": report[
            "eligible_to_request_setup_contract_change"
        ],
        "setup_contract_change_authorized": False,
        "runtime_integration_authorized": False,
        "deployment_authorized": False,
        "diagnostic_file": str(arguments.output),
    }, indent=2))


if __name__ == "__main__":
    main()
