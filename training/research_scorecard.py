"""XAU AI PLATFORM | Research Governance | Version 1.0.0.

Calculate the frozen Research Quality, Strategy Evidence, Operational Safety,
and hard-gated Overall Readiness scores for one experiment candidate.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


INPUT_SCHEMA_VERSION = "1.0.0"
OUTPUT_SCHEMA_VERSION = "1.0.0"
MINIMUM_EFFECTIVE_SAMPLE = 200

TOP_LEVEL_KEYS = {
    "scorecard_input_schema_version",
    "experiment_id",
    "candidate_id",
    "candidate_role",
    "evidence_date",
    "evidence_hashes",
    "research_quality",
    "strategy_evidence",
    "operational_safety",
    "notes",
}
RESEARCH_KEYS = {
    "hypothesis_preregistered",
    "artifact_hashes_verified",
    "past_only_enforced",
    "validation_sealed",
    "test_sealed",
    "data_quality_coverage_rate",
    "replay_parity_passed",
    "regression_passed",
    "compile_clean",
    "effective_sample_audited",
    "safety_governance_passed",
}
STRATEGY_KEYS = {
    "mature_records",
    "effective_sample_records",
    "minimum_effective_sample",
    "mean_cost_aware_r",
    "mean_r_ci95_lower",
    "drawdown_gate_passed",
    "positive_chronological_blocks",
    "chronological_blocks_tested",
    "positive_directions",
    "directions_tested",
    "cost_stress_passed",
    "ranker_required",
    "ranker_passing_folds",
    "ranker_total_folds",
    "locked_validation_passed",
    "forward_shadow_passed",
}
OPERATIONAL_KEYS = {
    "focused_tests_passed",
    "runtime_compile_clean",
    "regression_passed",
    "safety_locks_valid",
    "broker_state_unchanged",
    "artifact_set_complete",
    "deployment_authorized",
}


def finite_number(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"Scorecard {name} must be numeric")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"Scorecard {name} must be finite")
    return result


def exact_keys(payload: dict[str, Any], expected: set[str], name: str) -> None:
    if set(payload) != expected:
        missing = sorted(expected - set(payload))
        extra = sorted(set(payload) - expected)
        raise ValueError(f"Scorecard {name} keys changed: missing={missing} extra={extra}")


def require_bool(payload: dict[str, Any], key: str) -> bool:
    value = payload[key]
    if not isinstance(value, bool):
        raise ValueError(f"Scorecard {key} must be Boolean")
    return value


def require_count(payload: dict[str, Any], key: str) -> int:
    value = payload[key]
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"Scorecard {key} must be a non-negative integer")
    return value


def validate_input(payload: dict[str, Any]) -> None:
    exact_keys(payload, TOP_LEVEL_KEYS, "top-level")
    if payload["scorecard_input_schema_version"] != INPUT_SCHEMA_VERSION:
        raise ValueError("Scorecard input schema changed")
    if payload["candidate_role"] not in {"BASELINE", "CANDIDATE"}:
        raise ValueError("Scorecard candidate role is invalid")
    for key in ("experiment_id", "candidate_id", "evidence_date"):
        if not isinstance(payload[key], str) or not payload[key].strip():
            raise ValueError(f"Scorecard {key} is empty")
    hashes = payload["evidence_hashes"]
    if not isinstance(hashes, dict) or not hashes:
        raise ValueError("Scorecard evidence hashes are empty")
    for name, value in hashes.items():
        if not isinstance(name, str) or not isinstance(value, str) or (
            len(value) != 64 or any(character not in "0123456789ABCDEF" for character in value)
        ):
            raise ValueError("Scorecard evidence hash is invalid")
    if not isinstance(payload["notes"], list) or not all(
        isinstance(note, str) and note.strip() for note in payload["notes"]
    ):
        raise ValueError("Scorecard notes are invalid")

    research = payload["research_quality"]
    strategy = payload["strategy_evidence"]
    operational = payload["operational_safety"]
    if not all(isinstance(section, dict) for section in (research, strategy, operational)):
        raise ValueError("Scorecard section must be an object")
    exact_keys(research, RESEARCH_KEYS, "research")
    exact_keys(strategy, STRATEGY_KEYS, "strategy")
    exact_keys(operational, OPERATIONAL_KEYS, "operational")

    for key in RESEARCH_KEYS - {"data_quality_coverage_rate"}:
        require_bool(research, key)
    quality_rate = finite_number(
        research["data_quality_coverage_rate"], "data_quality_coverage_rate"
    )
    if not 0.0 <= quality_rate <= 1.0:
        raise ValueError("Scorecard data quality coverage must be in [0,1]")

    for key in (
        "mature_records", "minimum_effective_sample",
        "positive_chronological_blocks", "chronological_blocks_tested",
        "positive_directions", "directions_tested", "ranker_passing_folds",
        "ranker_total_folds",
    ):
        require_count(strategy, key)
    effective = strategy["effective_sample_records"]
    if effective is not None and (
        isinstance(effective, bool) or not isinstance(effective, int) or effective < 0
    ):
        raise ValueError("Scorecard effective sample is invalid")
    if strategy["minimum_effective_sample"] != MINIMUM_EFFECTIVE_SAMPLE:
        raise ValueError("Scorecard minimum effective sample changed")
    finite_number(strategy["mean_cost_aware_r"], "mean_cost_aware_r")
    if strategy["mean_r_ci95_lower"] is not None:
        finite_number(strategy["mean_r_ci95_lower"], "mean_r_ci95_lower")
    for key in (
        "drawdown_gate_passed", "cost_stress_passed", "ranker_required",
        "locked_validation_passed", "forward_shadow_passed",
    ):
        require_bool(strategy, key)
    if strategy["positive_chronological_blocks"] > strategy["chronological_blocks_tested"]:
        raise ValueError("Scorecard positive blocks exceed tested blocks")
    if strategy["positive_directions"] > strategy["directions_tested"]:
        raise ValueError("Scorecard positive directions exceed tested directions")
    if strategy["ranker_passing_folds"] > strategy["ranker_total_folds"]:
        raise ValueError("Scorecard passing folds exceed total folds")
    if strategy["chronological_blocks_tested"] == 0 or strategy["directions_tested"] == 0:
        raise ValueError("Scorecard stability denominators must be positive")
    if strategy["ranker_required"] and strategy["ranker_total_folds"] == 0:
        raise ValueError("Scorecard required ranker has no folds")
    if not strategy["ranker_required"] and (
        strategy["ranker_passing_folds"] != 0 or strategy["ranker_total_folds"] != 0
    ):
        raise ValueError("Scorecard optional ranker must not carry fold evidence")

    for key in OPERATIONAL_KEYS:
        require_bool(operational, key)


def score_research(research: dict[str, Any]) -> tuple[float, dict[str, float]]:
    components = {
        "hypothesis_preregistered": 10.0 if research["hypothesis_preregistered"] else 0.0,
        "artifact_integrity": 15.0 if research["artifact_hashes_verified"] else 0.0,
        "past_only_causality": 15.0 if research["past_only_enforced"] else 0.0,
        "sealed_validation_test": 2.5 * int(research["validation_sealed"])
        + 2.5 * int(research["test_sealed"]),
        "data_quality": 15.0 * float(research["data_quality_coverage_rate"]),
        "replay_parity": 15.0 if research["replay_parity_passed"] else 0.0,
        "regression": 5.0 if research["regression_passed"] else 0.0,
        "compile": 5.0 if research["compile_clean"] else 0.0,
        "effective_sample_audit": 10.0 if research["effective_sample_audited"] else 0.0,
        "safety_governance": 5.0 if research["safety_governance_passed"] else 0.0,
    }
    return sum(components.values()), components


def score_strategy(strategy: dict[str, Any]) -> tuple[float, dict[str, float]]:
    effective = strategy["effective_sample_records"]
    if effective is None:
        sample_score = min(
            7.5,
            7.5 * strategy["mature_records"] / MINIMUM_EFFECTIVE_SAMPLE,
        )
    else:
        sample_score = min(15.0, 15.0 * effective / MINIMUM_EFFECTIVE_SAMPLE)
    mean_r = float(strategy["mean_cost_aware_r"])
    ci_lower = strategy["mean_r_ci95_lower"]
    if mean_r <= 0.0:
        expectancy_score = 0.0
    elif ci_lower is not None and float(ci_lower) > 0.0:
        expectancy_score = 25.0
    else:
        expectancy_score = 12.5
    ranker_score = 5.0
    if strategy["ranker_required"]:
        ranker_score = 5.0 * (
            strategy["ranker_passing_folds"] / strategy["ranker_total_folds"]
        )
    components = {
        "effective_sample": sample_score,
        "positive_expectancy": expectancy_score,
        "drawdown_tail": 10.0 if strategy["drawdown_gate_passed"] else 0.0,
        "chronological_stability": 15.0 * (
            strategy["positive_chronological_blocks"]
            / strategy["chronological_blocks_tested"]
        ),
        "direction_robustness": 10.0 * (
            strategy["positive_directions"] / strategy["directions_tested"]
        ),
        "cost_stress": 10.0 if strategy["cost_stress_passed"] else 0.0,
        "ranker_stability": ranker_score,
        "locked_validation": 5.0 if strategy["locked_validation_passed"] else 0.0,
        "forward_shadow": 5.0 if strategy["forward_shadow_passed"] else 0.0,
    }
    return sum(components.values()), components


def score_operational(operational: dict[str, Any]) -> tuple[float, dict[str, float]]:
    components = {
        "focused_tests": 20.0 if operational["focused_tests_passed"] else 0.0,
        "runtime_compile": 20.0 if operational["runtime_compile_clean"] else 0.0,
        "regression": 20.0 if operational["regression_passed"] else 0.0,
        "safety_locks": 20.0 if operational["safety_locks_valid"] else 0.0,
        "broker_and_artifacts": 10.0 * int(operational["broker_state_unchanged"])
        + 10.0 * int(operational["artifact_set_complete"]),
    }
    return sum(components.values()), components


def evaluate_gates(payload: dict[str, Any]) -> tuple[dict[str, bool], str, float]:
    research = payload["research_quality"]
    strategy = payload["strategy_evidence"]
    operational = payload["operational_safety"]
    effective = strategy["effective_sample_records"]
    ranker_passed = (
        not strategy["ranker_required"]
        or strategy["ranker_passing_folds"] == strategy["ranker_total_folds"]
    )
    gates = {
        "G0_integrity_safety": all((
            research["hypothesis_preregistered"],
            research["artifact_hashes_verified"],
            research["past_only_enforced"],
            research["validation_sealed"],
            research["test_sealed"],
            research["data_quality_coverage_rate"] == 1.0,
            research["replay_parity_passed"],
            research["regression_passed"],
            research["compile_clean"],
            research["safety_governance_passed"],
            operational["safety_locks_valid"],
        )),
        "G1_effective_sample": (
            research["effective_sample_audited"]
            and effective is not None
            and effective >= MINIMUM_EFFECTIVE_SAMPLE
        ),
        "G2_positive_expectancy": (
            strategy["mean_cost_aware_r"] > 0.0
            and strategy["mean_r_ci95_lower"] is not None
            and strategy["mean_r_ci95_lower"] > 0.0
        ),
        "G3_temporal_stability": (
            strategy["positive_chronological_blocks"]
            == strategy["chronological_blocks_tested"]
        ),
        "G4_direction_robustness": (
            strategy["positive_directions"] == strategy["directions_tested"]
        ),
        "G5_drawdown_cost": (
            strategy["drawdown_gate_passed"] and strategy["cost_stress_passed"]
        ),
        "G6_ranker_stability": ranker_passed,
        "G7_locked_validation": strategy["locked_validation_passed"],
        "G8_forward_shadow": strategy["forward_shadow_passed"],
    }
    if not gates["G0_integrity_safety"]:
        return gates, "INVALID_EVIDENCE", 0.0
    train_gates = [gates[f"G{index}_{name}"] for index, name in (
        (1, "effective_sample"), (2, "positive_expectancy"),
        (3, "temporal_stability"), (4, "direction_robustness"),
        (5, "drawdown_cost"), (6, "ranker_stability"),
    )]
    if not all(train_gates):
        return gates, "NO_GO_TRAIN", 49.0
    if not gates["G7_locked_validation"]:
        return gates, "NO_GO_VALIDATION", 69.0
    if not gates["G8_forward_shadow"]:
        return gates, "NO_GO_FORWARD", 84.0
    if not operational["deployment_authorized"]:
        return gates, "READY_FOR_DEPLOYMENT_REVIEW", 94.0
    return gates, "GO_AUTHORIZED", 100.0


def build_scorecard(payload: dict[str, Any]) -> dict[str, Any]:
    validate_input(payload)
    research_score, research_components = score_research(payload["research_quality"])
    strategy_score, strategy_components = score_strategy(payload["strategy_evidence"])
    operational_score, operational_components = score_operational(
        payload["operational_safety"]
    )
    gates, status, cap = evaluate_gates(payload)
    raw_overall = 0.30 * research_score + 0.50 * strategy_score + 0.20 * operational_score
    overall = min(raw_overall, cap)
    return {
        "scorecard_schema_version": OUTPUT_SCHEMA_VERSION,
        "experiment_id": payload["experiment_id"],
        "candidate_id": payload["candidate_id"],
        "candidate_role": payload["candidate_role"],
        "evidence_date": payload["evidence_date"],
        "evidence_hashes": payload["evidence_hashes"],
        "scores": {
            "research_quality": round(research_score, 2),
            "strategy_evidence": round(strategy_score, 2),
            "operational_safety": round(operational_score, 2),
            "raw_overall": round(raw_overall, 2),
            "hard_gate_cap": round(cap, 2),
            "overall_readiness": round(overall, 2),
        },
        "components": {
            "research_quality": {
                key: round(value, 2) for key, value in research_components.items()
            },
            "strategy_evidence": {
                key: round(value, 2) for key, value in strategy_components.items()
            },
            "operational_safety": {
                key: round(value, 2) for key, value in operational_components.items()
            },
        },
        "gates": gates,
        "status": status,
        "baseline_promotion_allowed": status in {
            "READY_FOR_DEPLOYMENT_REVIEW", "GO_AUTHORIZED"
        },
        "deployment_authorized": payload["operational_safety"]["deployment_authorized"],
        "notes": payload["notes"],
    }


def add_reference_delta(
    scorecard: dict[str, Any], reference: dict[str, Any]
) -> None:
    if reference.get("scorecard_schema_version") != OUTPUT_SCHEMA_VERSION:
        raise ValueError("Reference scorecard schema changed")
    scorecard["reference"] = {
        "experiment_id": reference["experiment_id"],
        "candidate_id": reference["candidate_id"],
    }
    scorecard["score_deltas"] = {
        key: round(scorecard["scores"][key] - reference["scores"][key], 2)
        for key in (
            "research_quality", "strategy_evidence", "operational_safety",
            "raw_overall", "overall_readiness",
        )
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--reference", type=Path)
    arguments = parser.parse_args()
    payload = json.loads(arguments.input.read_text(encoding="utf-8-sig"))
    scorecard = build_scorecard(payload)
    if arguments.reference is not None:
        reference = json.loads(arguments.reference.read_text(encoding="utf-8-sig"))
        add_reference_delta(scorecard, reference)
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
    print(json.dumps(scorecard, indent=2))


if __name__ == "__main__":
    main()
