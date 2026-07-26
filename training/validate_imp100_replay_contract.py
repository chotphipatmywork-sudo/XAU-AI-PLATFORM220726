"""Validate the frozen IMP-100 Train-only causal replay contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from diagnose_current_feed_setup_funnel import sha256


EXPECTED_CONTRACT_SHA256 = (
    "9D0142D1671E80C1263D93A61E1CB53316EC8E816040B251F477F974540494A9"
)
EXPECTED_ARMS = {
    ("CONTROL", "m5_stop_2", "m15_target_1", 76),
    ("STOP_ONLY", "m5_stop_1", "m15_target_1", 195),
    ("TARGET_ONLY", "m5_stop_2", "m15_target_2", 146),
    ("COMBINED", "m5_stop_1", "m15_target_2", 268),
}
EXPECTED_GATES = {
    "minimum_effective_paths": 200,
    "mean_realized_r_positive": True,
    "moving_block_ci95_lower_positive": True,
    "all_four_chronological_blocks_positive": True,
    "both_directions_positive": True,
    "profit_factor_minimum": 1.1,
    "maximum_drawdown_r_maximum": 25.0,
    "longest_loss_sequence_maximum": 10,
    "cost_multipliers": [1.0, 1.25, 1.5],
    "all_cost_stress_intervals_positive": True,
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def verify_hash(path: Path, expected: str, label: str) -> None:
    require(path.is_file(), f"IMP-100 source missing: {label}")
    require(sha256(path) == expected, f"IMP-100 source hash changed: {label}")


def validate_contract(contract: dict[str, Any]) -> None:
    require(contract["experiment_id"] == "IMP-100", "experiment changed")
    require(
        contract["phase"] == "CONTRACT_AND_REQUEST_PREPARATION",
        "phase changed",
    )
    require(
        contract["baseline_commit"]
        == "32e044c86691b9e84f8fa54d21e3d20448f27eeb",
        "baseline commit changed",
    )
    require(
        contract["architecture_baseline"] == "ABR-1.0_FROZEN",
        "architecture baseline changed",
    )
    require(contract["dataset_partition"] == "TRAIN_ONLY", "partition changed")
    accounting = contract["verified_imp099_accounting"]
    require(accounting["base_opportunities"] == 597, "request count changed")
    require(accounting["arm_records"] == 2388, "arm record count changed")
    require(
        accounting["common_support_opportunities"] == 362,
        "common support changed",
    )
    require(accounting["control_eligible"] == 459, "Control eligible changed")
    require(accounting["control_rr_passes"] == 76, "Control passes changed")
    require(
        accounting["final_gate"] == "GO_TRAIN_ONLY_REPLAY",
        "IMP-099 gate changed",
    )
    arms = {
        (
            arm["arm_id"],
            arm["stop_identity"],
            arm["target_identity"],
            arm["rr_passing_requests"],
        )
        for arm in contract["arms"]
    }
    require(arms == EXPECTED_ARMS, "exact four-arm contract changed")
    rules = contract["replay_rules"]
    require(rules["minimum_rr"] == 2.0, "Minimum RR changed")
    require(rules["primary_population"] == "COMMON_SUPPORT_362",
            "primary population changed")
    require(rules["secondary_population"] == "ALL_597_BASE_OPPORTUNITIES",
            "secondary population changed")
    require(rules["comparison"] == "PAIRED_REQUEST_LEVEL",
            "pairing changed")
    require(rules["path_timing"] == "CAUSAL_CLOSED_M5_ONLY",
            "path timing changed")
    require(not rules["outcome_imputation_allowed"], "outcome imputation enabled")
    require(not rules["missing_geometry_imputation_allowed"],
            "geometry imputation enabled")
    require(not rules["validation_dataset_used"], "Validation enabled")
    require(not rules["test_dataset_used"], "Test enabled")
    outputs = contract["request_outputs"]
    require(outputs["active_requests_expected"] == 685,
            "active request count changed")
    require(outputs["opportunity_ledger_records_expected"] == 2388,
            "ledger count changed")
    require(not outputs["replay_outcome_fields_allowed"],
            "outcome fields enabled")
    require(contract["strategy_gates"] == EXPECTED_GATES,
            "approved strategy gates changed")
    require(all(contract["prohibitions"].values()),
            "a prohibited activity was enabled")


def verify_frozen_inputs(contract: dict[str, Any], repository: Path) -> None:
    for label, source in contract["frozen_inputs"].items():
        verify_hash(repository / source["path"], source["sha256"], label)


def load_and_validate(contract_path: Path, repository: Path) -> dict[str, Any]:
    verify_hash(contract_path, EXPECTED_CONTRACT_SHA256, "IMP-100 contract")
    contract = json.loads(contract_path.read_text(encoding="utf-8-sig"))
    validate_contract(contract)
    verify_frozen_inputs(contract, repository)
    return contract


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--repository", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    arguments = parser.parse_args()
    contract = load_and_validate(arguments.contract, arguments.repository)
    result = {
        "validation_schema_version": "1.0.0",
        "experiment_id": "IMP-100",
        "phase": "CONTRACT_AND_REQUEST_PREPARATION",
        "status": "PASS",
        "contract_sha256": EXPECTED_CONTRACT_SHA256,
        "frozen_input_hashes_verified": True,
        "exact_four_arms": True,
        "minimum_rr": contract["replay_rules"]["minimum_rr"],
        "common_support_opportunities": 362,
        "base_opportunities": 597,
        "validation_dataset_used": False,
        "test_dataset_used": False,
        "replay_executed": False,
        "runtime_changed": False,
        "protected_modules_changed": False,
        "deployment_authorized": False,
    }
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
