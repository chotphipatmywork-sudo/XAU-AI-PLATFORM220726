"""XAU AI PLATFORM | Offline Research | Version 1.0.0.

File: diagnose_setup_v2_hypotheses.py
Purpose: Evaluate preregistered CR-014 Setup V2 associations inside Train only.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from analyze_shadow_run import FEATURE_COLUMNS
from build_setup_outcome_dataset import (
    FEATURE_SCHEMA_VERSION,
    OUTCOME_AUDIT_COLUMNS,
    SETUP_OUTCOME_SCHEMA_VERSION,
    TRAINABLE_OUTCOMES,
    as_bool,
    parse_time,
)
from setup_quality_walk_forward import build_time_purged_folds, readiness


DIAGNOSTIC_SCHEMA_VERSION = "1.0.0"
DIAGNOSTIC_STATUS = "SETUP_V2_TRAIN_ONLY_DIAGNOSTIC_NO_GO"
EXPECTED_POSITIVE = "positive"
EXPECTED_NEGATIVE = "negative"
EXPECTED_EXPLORATORY = "exploratory"
MINIMUM_FOLD_MATCHES = 3
MINIMUM_TOTAL_MATCHES = 20
MINIMUM_ABSOLUTE_LIFT = 0.05


@dataclass(frozen=True)
class Hypothesis:
    name: str
    question: str
    rule: str
    expected_effect: str
    predicate: Callable[[dict[str, float]], bool]


def directional(value: float, direction: str) -> float:
    """Project a bullish 0..100 score into plan-direction strength."""
    if direction == "TRADE_SETUP_BUY":
        return value
    if direction == "TRADE_SETUP_SELL":
        return 100.0 - value
    raise ValueError(f"Unsupported Setup direction: {direction}")


def derived_values(sample: dict[str, Any]) -> dict[str, float]:
    features = sample["feature_map"]
    direction = str(sample["direction"])
    trend = [
        directional(float(features[column]), direction)
        for column in ("trend_regime", "trend_momentum", "trend_slope")
    ]
    sweep_alignment = directional(
        float(features["liquidity_sweep_direction"]), direction
    )
    range_position = float(features["liquidity_range_position"])
    # BUY support is lower in the range; SELL resistance is higher in the range.
    favorable_range_location = (
        100.0 - range_position
        if direction == "TRADE_SETUP_BUY"
        else range_position
    )
    return {
        "trend_minimum": min(trend),
        "trend_mean": sum(trend) / len(trend),
        "trend_spread": max(trend) - min(trend),
        "sweep_alignment": sweep_alignment,
        "favorable_range_location": favorable_range_location,
        "liquidity_activity": float(features["liquidity_activity"]),
        "volatility_regime": float(features["volatility_regime"]),
        "volatility_change": float(features["volatility_change"]),
        "session_asia": float(features["session_asia"]),
        "session_london": float(features["session_london"]),
        "session_new_york": float(features["session_new_york"]),
        "session_progress": float(features["session_progress"]),
    }


def registered_hypotheses() -> tuple[Hypothesis, ...]:
    """Return fixed, explainable questions; no threshold is fitted from outcomes."""
    return (
        Hypothesis(
            "continuation_trend_coherent",
            "Are all directional Trend components strong and mutually coherent?",
            "trend_minimum >= 70 and trend_spread <= 20",
            EXPECTED_POSITIVE,
            lambda value: value["trend_minimum"] >= 70.0
            and value["trend_spread"] <= 20.0,
        ),
        Hypothesis(
            "continuation_trend_minimum_60",
            "Does every directional Trend component clear a stronger 60 threshold?",
            "trend_minimum >= 60",
            EXPECTED_POSITIVE,
            lambda value: value["trend_minimum"] >= 60.0,
        ),
        Hypothesis(
            "trend_component_disagreement",
            "Does disagreement among Trend components identify fragile plans?",
            "trend_spread >= 20",
            EXPECTED_NEGATIVE,
            lambda value: value["trend_spread"] >= 20.0,
        ),
        Hypothesis(
            "liquidity_sweep_aligned",
            "Does the completed M15 Liquidity sweep align with plan direction?",
            "sweep_alignment >= 75",
            EXPECTED_POSITIVE,
            lambda value: value["sweep_alignment"] >= 75.0,
        ),
        Hypothesis(
            "liquidity_sweep_opposed",
            "Does an opposing completed M15 Liquidity sweep identify fragile plans?",
            "sweep_alignment <= 25",
            EXPECTED_NEGATIVE,
            lambda value: value["sweep_alignment"] <= 25.0,
        ),
        Hypothesis(
            "favorable_liquidity_range_location",
            "Is the plan located near directional support or resistance?",
            "favorable_range_location >= 60",
            EXPECTED_POSITIVE,
            lambda value: value["favorable_range_location"] >= 60.0,
        ),
        Hypothesis(
            "unfavorable_liquidity_range_location",
            "Is the plan entering from an unfavorable side of the Liquidity range?",
            "favorable_range_location <= 40",
            EXPECTED_NEGATIVE,
            lambda value: value["favorable_range_location"] <= 40.0,
        ),
        Hypothesis(
            "high_liquidity_activity",
            "Does high completed-bar Liquidity activity change setup quality?",
            "liquidity_activity >= 60",
            EXPECTED_EXPLORATORY,
            lambda value: value["liquidity_activity"] >= 60.0,
        ),
        Hypothesis(
            "high_volatility_regime",
            "Does a high completed-bar Volatility regime change setup quality?",
            "volatility_regime >= 60",
            EXPECTED_EXPLORATORY,
            lambda value: value["volatility_regime"] >= 60.0,
        ),
        Hypothesis(
            "volatility_expanding",
            "Does expanding completed-bar Volatility change setup quality?",
            "volatility_change >= 55",
            EXPECTED_EXPLORATORY,
            lambda value: value["volatility_change"] >= 55.0,
        ),
        Hypothesis(
            "session_asia",
            "Does the Asia Session identify a distinct setup-quality regime?",
            "session_asia >= 50",
            EXPECTED_EXPLORATORY,
            lambda value: value["session_asia"] >= 50.0,
        ),
        Hypothesis(
            "session_london",
            "Does the London Session identify a distinct setup-quality regime?",
            "session_london >= 50",
            EXPECTED_EXPLORATORY,
            lambda value: value["session_london"] >= 50.0,
        ),
        Hypothesis(
            "session_new_york",
            "Does the New York Session identify a distinct setup-quality regime?",
            "session_new_york >= 50",
            EXPECTED_EXPLORATORY,
            lambda value: value["session_new_york"] >= 50.0,
        ),
        Hypothesis(
            "session_early_phase",
            "Does the first third of a Session identify a distinct quality regime?",
            "session_progress < 33.333333",
            EXPECTED_EXPLORATORY,
            lambda value: value["session_progress"] < (100.0 / 3.0),
        ),
        Hypothesis(
            "session_late_phase",
            "Does the final third of a Session identify a distinct quality regime?",
            "session_progress >= 66.666667",
            EXPECTED_EXPLORATORY,
            lambda value: value["session_progress"] >= (200.0 / 3.0),
        ),
    )


def read_train_samples(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"CR-014 Train partition not found: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or tuple(reader.fieldnames) != OUTCOME_AUDIT_COLUMNS:
            raise ValueError(f"Unexpected CR-014 Train schema in {path}")
        rows = list(reader)
    if not rows:
        raise ValueError("CR-014 Train partition is empty")

    samples: list[dict[str, Any]] = []
    seen: set[datetime] = set()
    previous: datetime | None = None
    for row in rows:
        if row["setup_outcome_schema_version"] != SETUP_OUTCOME_SCHEMA_VERSION:
            raise ValueError("CR-014 Setup Outcome Schema version mismatch")
        if row["feature_schema_version"] != FEATURE_SCHEMA_VERSION:
            raise ValueError("CR-014 Feature Schema version mismatch")
        if not as_bool(row["trainable"]) or row["outcome"] not in TRAINABLE_OUTCOMES:
            raise ValueError("CR-014 Train contains a quarantined outcome")
        observation = parse_time(row["observation_time"])
        known_at = parse_time(row["outcome_known_at"])
        if observation in seen or (previous is not None and observation <= previous):
            raise ValueError("CR-014 Train observations are not unique and chronological")
        if known_at <= observation:
            raise ValueError("CR-014 outcome is not future-matured")
        direction = row["direction"]
        if direction not in {"TRADE_SETUP_BUY", "TRADE_SETUP_SELL"}:
            raise ValueError(f"Unsupported CR-014 Setup direction: {direction}")
        feature_map = {column: float(row[column]) for column in FEATURE_COLUMNS}
        if any(
            not math.isfinite(value) or value < 0.0 or value > 100.0
            for value in feature_map.values()
        ):
            raise ValueError("CR-014 Train feature is outside [0,100]")
        samples.append({
            "observation": observation,
            "known_at": known_at,
            "direction": direction,
            "feature_map": feature_map,
            "features": [feature_map[column] for column in FEATURE_COLUMNS],
            "label": 1 if row["outcome"] == "TARGET_FIRST" else 0,
        })
        seen.add(observation)
        previous = observation
    return samples


def subgroup_metrics(samples: list[dict[str, Any]], indices: list[int],
                     hypothesis: Hypothesis) -> dict[str, Any]:
    labels = [int(samples[index]["label"]) for index in indices]
    matches = [
        index for index in indices
        if hypothesis.predicate(derived_values(samples[index]))
    ]
    matched_labels = [int(samples[index]["label"]) for index in matches]
    matched_index_set = set(matches)
    complement_labels = [
        int(samples[index]["label"])
        for index in indices
        if index not in matched_index_set
    ]
    base_rate = sum(labels) / len(labels)
    match_rate = sum(matched_labels) / len(matched_labels) if matched_labels else None
    complement_rate = (
        sum(complement_labels) / len(complement_labels) if complement_labels else None
    )
    return {
        "evaluation_records": len(indices),
        "base_target_count": sum(labels),
        "base_target_rate": base_rate,
        "matched_records": len(matches),
        "matched_target_count": sum(matched_labels),
        "matched_target_rate": match_rate,
        "complement_records": len(complement_labels),
        "complement_target_rate": complement_rate,
        "target_rate_lift_vs_fold": (
            match_rate - base_rate if match_rate is not None else None
        ),
    }


def evaluate_hypothesis(samples: list[dict[str, Any]],
                        folds: list[tuple[list[int], list[int]]],
                        hypothesis: Hypothesis) -> dict[str, Any]:
    fold_reports: list[dict[str, Any]] = []
    aggregate_indices: list[int] = []
    for fold_number, (_, evaluation_indices) in enumerate(folds, start=1):
        metrics = subgroup_metrics(samples, evaluation_indices, hypothesis)
        metrics.update({
            "fold": fold_number,
            "evaluation_start": samples[evaluation_indices[0]]["observation"].strftime(
                "%Y.%m.%d %H:%M"
            ),
            "minimum_support_met": metrics["matched_records"] >= MINIMUM_FOLD_MATCHES,
        })
        fold_reports.append(metrics)
        aggregate_indices.extend(evaluation_indices)

    aggregate = subgroup_metrics(samples, aggregate_indices, hypothesis)
    lifts = [report["target_rate_lift_vs_fold"] for report in fold_reports]
    all_supported = all(report["minimum_support_met"] for report in fold_reports)
    total_supported = aggregate["matched_records"] >= MINIMUM_TOTAL_MATCHES
    positive_all = all(lift is not None and lift > 0.0 for lift in lifts)
    negative_all = all(lift is not None and lift < 0.0 for lift in lifts)
    same_sign_all = positive_all or negative_all
    aggregate_lift = aggregate["target_rate_lift_vs_fold"]
    effect_size_met = (
        aggregate_lift is not None
        and abs(float(aggregate_lift)) >= MINIMUM_ABSOLUTE_LIFT
    )
    expected_confirmed = (
        hypothesis.expected_effect == EXPECTED_POSITIVE and positive_all
    ) or (
        hypothesis.expected_effect == EXPECTED_NEGATIVE and negative_all
    )
    stable_association = all_supported and total_supported and same_sign_all and effect_size_met
    stage_2_eligible = (
        stable_association
        and expected_confirmed
        and hypothesis.expected_effect != EXPECTED_EXPLORATORY
    )
    return {
        "name": hypothesis.name,
        "question": hypothesis.question,
        "fixed_rule": hypothesis.rule,
        "preregistered_expected_effect": hypothesis.expected_effect,
        "aggregate": aggregate,
        "folds": fold_reports,
        "all_four_folds_supported": all_supported,
        "minimum_total_support_met": total_supported,
        "same_nonzero_effect_sign_all_four_folds": same_sign_all,
        "aggregate_effect_size_met": effect_size_met,
        "preregistered_effect_confirmed_all_four_folds": expected_confirmed,
        "stable_train_only_association": stable_association,
        "eligible_to_request_stage_2_contract": stage_2_eligible,
    }


def run_diagnostic(samples: list[dict[str, Any]]) -> dict[str, Any]:
    state = readiness(samples)
    report: dict[str, Any] = {
        "diagnostic_schema_version": DIAGNOSTIC_SCHEMA_VERSION,
        "diagnostic_stage": "cr_014_stage_1_train_only_preregistered_hypotheses",
        "diagnostic_status": DIAGNOSTIC_STATUS,
        "setup_outcome_schema_version": SETUP_OUTCOME_SCHEMA_VERSION,
        "feature_schema_version": FEATURE_SCHEMA_VERSION,
        "canonical_feature_groups_unchanged": True,
        "validation_dataset_used": False,
        "test_dataset_used": False,
        "model_training_performed": False,
        "runtime_integration_authorized": False,
        "deployment_authorized": False,
        "readiness": state,
        "gate": {
            "required_fold_count": 4,
            "minimum_matches_per_fold": MINIMUM_FOLD_MATCHES,
            "minimum_total_matches": MINIMUM_TOTAL_MATCHES,
            "minimum_absolute_target_rate_lift": MINIMUM_ABSOLUTE_LIFT,
            "requires_same_nonzero_effect_sign_all_folds": True,
        },
        "hypotheses": [],
        "stable_train_only_associations": [],
        "stable_exploratory_associations": [],
        "stage_2_request_eligible_hypotheses": [],
        "stage_2_contract_authorized": False,
    }
    if not state["ready"]:
        report["refusal_reason"] = "Stage D Train readiness gate is not met."
        return report

    folds = build_time_purged_folds(samples)
    results = [
        evaluate_hypothesis(samples, folds, hypothesis)
        for hypothesis in registered_hypotheses()
    ]
    report["fold_count"] = len(folds)
    report["hypotheses"] = results
    report["stable_train_only_associations"] = [
        result["name"]
        for result in results
        if result["stable_train_only_association"]
    ]
    report["stable_exploratory_associations"] = [
        result["name"]
        for result in results
        if result["stable_train_only_association"]
        and result["preregistered_expected_effect"] == EXPECTED_EXPLORATORY
    ]
    report["stage_2_request_eligible_hypotheses"] = [
        result["name"]
        for result in results
        if result["eligible_to_request_stage_2_contract"]
    ]
    report["limitations"] = [
        "Only the Stage D Train partition is accepted; Validation and Test are not CLI inputs.",
        "Fixed subgroup associations are descriptive and do not prove causal trading value.",
        "M15 Liquidity features do not constitute an independently valid M5 reversal plan.",
        "No result authorizes Runtime changes, model deployment, or broker trading.",
    ]
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    arguments = parser.parse_args()
    report = run_diagnostic(read_train_samples(arguments.train))
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({
        "diagnostic_stage": report["diagnostic_stage"],
        "readiness": report["readiness"],
        "hypothesis_count": len(report["hypotheses"]),
        "stable_train_only_associations": report[
            "stable_train_only_associations"
        ],
        "stable_exploratory_associations": report[
            "stable_exploratory_associations"
        ],
        "stage_2_request_eligible_hypotheses": report[
            "stage_2_request_eligible_hypotheses"
        ],
        "stage_2_contract_authorized": False,
        "runtime_integration_authorized": False,
        "deployment_authorized": False,
        "diagnostic_file": str(arguments.output),
    }, indent=2))


if __name__ == "__main__":
    main()
