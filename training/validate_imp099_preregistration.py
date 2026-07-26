"""Validate the frozen IMP-099 Train-only experiment preregistration."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from diagnose_current_feed_setup_funnel import sha256


EXPECTED_ARMS = {
    ("CONTROL", "m5_stop_2", "m15_target_1"),
    ("STOP_ONLY", "m5_stop_1", "m15_target_1"),
    ("TARGET_ONLY", "m5_stop_2", "m15_target_2"),
    ("COMBINED", "m5_stop_1", "m15_target_2"),
}
EXPECTED_DECISIONS = {
    "NO_GO", "CONTINUE_DIAGNOSTIC_RESEARCH", "GO_TRAIN_ONLY_REPLAY"
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate_spec(spec: dict[str, Any]) -> None:
    require(spec["experiment_id"] == "IMP-099", "experiment identity changed")
    require(spec["scope"] == "DESIGN_ONLY_NOT_EXECUTED", "design-only lock changed")
    require(
        spec["architecture_baseline"] == "ABR-1.0_FROZEN",
        "architecture baseline changed",
    )
    population = spec["population"]
    require(population["partition"] == "TRAIN_ONLY", "partition is not Train-only")
    require(population["request_records"] == 597, "request population changed")
    require(not population["validation_dataset_used"], "Validation was authorized")
    require(not population["test_dataset_used"], "Test was authorized")

    policy = spec["frozen_policy"]
    require(policy["minimum_rr"] == 2.0, "Minimum RR changed")
    require(not policy["parameter_optimization_allowed"], "optimization authorized")
    require(not policy["session_filter_allowed"], "session filter authorized")

    arms = {
        (item["arm_id"], item["stop"], item["target"])
        for item in spec["factorial_design"]["arms"]
    }
    require(arms == EXPECTED_ARMS, "fixed 2x2 geometry arms changed")
    require(len(spec["hypotheses"]) == 3, "hypothesis family changed")

    analysis = spec["analysis_contract"]
    require(
        analysis["primary_population"] == "COMMON_SUPPORT_ALL_FOUR_ARMS",
        "primary population changed",
    )
    require(analysis["planned_primary_contrasts"] == 3, "contrast count changed")
    require(
        abs(analysis["bonferroni_alpha"] - 0.05 / 3.0) < 1e-15,
        "multiple-testing correction changed",
    )
    require(
        analysis["missing_geometry"] == "REPORT_SEPARATELY_NEVER_IMPUTE",
        "missing-geometry policy changed",
    )

    gate = spec["train_only_experiment_gate"]
    require(gate["minimum_common_support_records"] == 200, "sample gate changed")
    require(gate["minimum_absolute_pass_rate_improvement"] == 0.05,
            "effect gate changed")
    require(gate["minimum_relative_coverage_vs_control"] == 0.8,
            "coverage gate changed")
    require(not gate["runtime_candidate_creation_allowed"],
            "Runtime candidate authorized")
    require(not gate["deployment_authorized"], "deployment authorized")
    require(set(spec["permitted_next_decisions"]) == EXPECTED_DECISIONS,
            "next-decision set changed")
    require(not any(spec["safety"].values()), "a safety lock was enabled")


def verify_sources(spec: dict[str, Any], repository: Path) -> None:
    for source_id, source in spec["frozen_sources"].items():
        path = repository / source["path"]
        require(path.is_file(), f"missing frozen source: {source_id}")
        require(sha256(path) == source["sha256"],
                f"frozen source hash changed: {source_id}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--repository", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    arguments = parser.parse_args()
    spec = json.loads(arguments.config.read_text(encoding="utf-8-sig"))
    validate_spec(spec)
    verify_sources(spec, arguments.repository)
    result = {
        "validation_schema_version": "1.0.0",
        "experiment_id": "IMP-099",
        "status": "PREREGISTRATION_VALID_READY_TO_RUN_TRAIN_ONLY",
        "source_hashes_verified": True,
        "arm_count": 4,
        "primary_contrast_count": 3,
        "validation_dataset_used": False,
        "test_dataset_used": False,
        "experiment_executed": False,
        "runtime_changed": False,
        "protected_modules_changed": False,
        "deployment_authorized": False,
        "gate_decision": "READY_TO_RUN_TRAIN_ONLY_EXPERIMENT",
    }
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
