"""XAU AI PLATFORM | Offline Test | Version 1.0.0.

File: test_objective_setup_failure_diagnostic.py
Purpose: Verify the Train-only Objective geometry failure diagnostic gates.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from diagnose_objective_setup_failures import run_diagnostic


def samples(count: int = 300) -> list[dict[str, object]]:
    start = datetime(2025, 1, 1)
    rows: list[dict[str, object]] = []
    for index in range(count):
        observation = start + timedelta(hours=6 * index)
        target = index % 3 == 0
        plan_rr = 3.0
        rows.append({
            "observation": observation,
            "known_at": observation + timedelta(hours=1),
            "label": 1 if target else 0,
            "outcome": "TARGET_FIRST" if target else "STOP_FIRST",
            "net_outcome_r": plan_rr if target else -1.0,
            "features": [50.0] * 12,
            "geometry": {
                "sweep_penetration_atr": 0.15 if target else 0.03,
                "reclaim_distance_atr": 0.20 if target else 0.01,
                "reclaim_to_sweep_ratio": 1.25 if target else 0.25,
                "trigger_excursion_atr": 0.35 if target else 0.04,
                "cost_to_effective_risk": 0.05 if target else 0.25,
                "plan_rr": plan_rr,
                "rr_headroom": 1.0,
                "gross_reward_to_risk": 3.5,
            },
        })
    return rows


def main() -> None:
    insufficient = run_diagnostic(samples(60))
    if insufficient["readiness"]["ready"] or insufficient["hypotheses"]:
        raise AssertionError("Objective failure diagnostic bypassed readiness")

    report = run_diagnostic(samples())
    stable = set(report["stable_preregistered_findings"])
    expected = {"deep_sweep", "marginal_sweep", "strong_reclaim", "weak_reclaim"}
    if not expected.issubset(stable):
        raise AssertionError(f"Synthetic Objective geometry signals failed: {stable}")
    forbidden = set(report["forbidden_predicate_fields"])
    if forbidden.intersection(report["predicate_fields"]):
        raise AssertionError("Post-outcome field entered Objective geometry predicates")
    if report["validation_dataset_used"] or report["test_dataset_used"]:
        raise AssertionError("Objective failure diagnostic opened a sealed partition")
    if report["model_training_performed"]:
        raise AssertionError("Objective failure diagnostic trained a model")
    if report["setup_contract_change_authorized"]:
        raise AssertionError("Objective failure diagnostic changed the Setup contract")
    if report["runtime_integration_authorized"] or report["deployment_authorized"]:
        raise AssertionError("Objective failure diagnostic authorized Runtime or deployment")
    print("Objective Setup failure diagnostic test passed")


if __name__ == "__main__":
    main()
