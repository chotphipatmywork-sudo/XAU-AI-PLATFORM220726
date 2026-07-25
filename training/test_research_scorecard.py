"""Focused checks for Research Scorecard Standard 1.0."""

from __future__ import annotations

from copy import deepcopy

from research_scorecard import add_reference_delta, build_scorecard


def valid_input() -> dict:
    return {
        "scorecard_input_schema_version": "1.0.0",
        "experiment_id": "IMP-080",
        "candidate_id": "current_target",
        "candidate_role": "BASELINE",
        "evidence_date": "2026-07-22",
        "evidence_hashes": {"report": "A" * 64},
        "research_quality": {
            "hypothesis_preregistered": True,
            "artifact_hashes_verified": True,
            "past_only_enforced": True,
            "validation_sealed": True,
            "test_sealed": True,
            "data_quality_coverage_rate": 1.0,
            "replay_parity_passed": True,
            "regression_passed": True,
            "compile_clean": True,
            "effective_sample_audited": False,
            "safety_governance_passed": True,
        },
        "strategy_evidence": {
            "mature_records": 233,
            "effective_sample_records": None,
            "minimum_effective_sample": 200,
            "mean_cost_aware_r": -0.078,
            "mean_r_ci95_lower": None,
            "drawdown_gate_passed": False,
            "positive_chronological_blocks": 1,
            "chronological_blocks_tested": 4,
            "positive_directions": 0,
            "directions_tested": 2,
            "cost_stress_passed": False,
            "ranker_required": True,
            "ranker_passing_folds": 1,
            "ranker_total_folds": 4,
            "locked_validation_passed": False,
            "forward_shadow_passed": False,
        },
        "operational_safety": {
            "focused_tests_passed": True,
            "runtime_compile_clean": True,
            "regression_passed": True,
            "safety_locks_valid": True,
            "broker_state_unchanged": True,
            "artifact_set_complete": True,
            "deployment_authorized": False,
        },
        "notes": ["Synthetic current baseline."],
    }


def expect_value_error(action, message: str) -> None:
    try:
        action()
    except ValueError:
        return
    raise AssertionError(message)


def main() -> None:
    current = build_scorecard(valid_input())
    if current["scores"] != {
        "research_quality": 90.0,
        "strategy_evidence": 12.5,
        "operational_safety": 100.0,
        "raw_overall": 53.25,
        "hard_gate_cap": 49.0,
        "overall_readiness": 49.0,
    }:
        raise AssertionError("Current Research Scorecard calculation changed")
    if current["status"] != "NO_GO_TRAIN" or current["baseline_promotion_allowed"]:
        raise AssertionError("Negative baseline escaped Train NO-GO")

    perfect_input = valid_input()
    research = perfect_input["research_quality"]
    strategy = perfect_input["strategy_evidence"]
    research["effective_sample_audited"] = True
    strategy.update({
        "effective_sample_records": 250,
        "mean_cost_aware_r": 0.25,
        "mean_r_ci95_lower": 0.05,
        "drawdown_gate_passed": True,
        "positive_chronological_blocks": 4,
        "positive_directions": 2,
        "cost_stress_passed": True,
        "ranker_passing_folds": 4,
        "locked_validation_passed": True,
        "forward_shadow_passed": True,
    })
    perfect = build_scorecard(perfect_input)
    if perfect["scores"]["raw_overall"] != 100.0:
        raise AssertionError("Perfect Research Scorecard did not reach raw 100")
    if perfect["scores"]["overall_readiness"] != 94.0:
        raise AssertionError("Unauthorized deployment review cap changed")
    if perfect["status"] != "READY_FOR_DEPLOYMENT_REVIEW":
        raise AssertionError("Perfect evidence bypassed deployment review")

    invalid = valid_input()
    invalid["research_quality"]["past_only_enforced"] = False
    invalid_score = build_scorecard(invalid)
    if invalid_score["status"] != "INVALID_EVIDENCE" or (
        invalid_score["scores"]["overall_readiness"] != 0.0
    ):
        raise AssertionError("Invalid evidence escaped the zero hard cap")

    positive_uncertain = valid_input()
    positive_uncertain["strategy_evidence"]["mean_cost_aware_r"] = 0.1
    uncertain = build_scorecard(positive_uncertain)
    if uncertain["components"]["strategy_evidence"]["positive_expectancy"] != 12.5:
        raise AssertionError("Uncertain positive expectancy received full credit")

    changed = deepcopy(current)
    changed["scores"]["research_quality"] += 5.0
    add_reference_delta(changed, current)
    if changed["score_deltas"]["research_quality"] != 5.0:
        raise AssertionError("Research Scorecard reference delta changed")

    malformed = valid_input()
    malformed["unexpected"] = True
    expect_value_error(
        lambda: build_scorecard(malformed),
        "Research Scorecard accepted an unexpected field",
    )

    print("Research Scorecard Standard test passed")


if __name__ == "__main__":
    main()

