"""Compare Objective Setup/Feature generation across Strategy Tester models."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

from analyze_shadow_run import DECISION_COLUMNS, FEATURE_COLUMNS
from build_setup_outcome_dataset import SETUP_AUDIT_COLUMNS, read_exact_csv


DECISION_STRING_COLUMNS = (
    "recorded_at", "closed_bar", "symbol", "timeframe",
    "feature_schema_version", "inference_provider", "model_status",
    "model_deployment_authorized",
)
DECISION_NUMERIC_COLUMNS = (
    "bar_open", "bar_high", "bar_low", "bar_close", "atr", *FEATURE_COLUMNS,
)
SETUP_STRING_COLUMNS = (
    "observation_time", "symbol", "higher_bar_open", "entry_bar_open",
    "direction", "poi_confirmed", "trigger_confirmed", "plan_available",
    "setup_reason", "ai_action",
)
SETUP_NUMERIC_COLUMNS = (
    "reference_poi", "nearest_target", "structural_stop",
    "sweep_penetration_atr", "reclaim_distance_atr", "plan_entry",
    "plan_stop", "plan_target", "plan_rr", "minimum_rr",
    "estimated_cost_points", "ai_confidence",
)


def compare_rows(
    reference: list[dict[str, str]],
    candidate: list[dict[str, str]],
    key: str,
    string_columns: tuple[str, ...],
    numeric_columns: tuple[str, ...],
) -> dict[str, Any]:
    mismatches: list[str] = []
    reference_index = {row[key]: row for row in reference}
    candidate_index = {row[key]: row for row in candidate}
    if len(reference_index) != len(reference):
        mismatches.append(f"reference duplicate {key}")
    if len(candidate_index) != len(candidate):
        mismatches.append(f"candidate duplicate {key}")
    reference_keys = set(reference_index)
    candidate_keys = set(candidate_index)
    missing = sorted(reference_keys - candidate_keys)
    extra = sorted(candidate_keys - reference_keys)
    if missing:
        mismatches.append(f"missing keys: {missing[:5]}")
    if extra:
        mismatches.append(f"extra keys: {extra[:5]}")

    compared = 0
    for value in sorted(reference_keys & candidate_keys):
        compared += 1
        left = reference_index[value]
        right = candidate_index[value]
        for column in string_columns:
            if left[column] != right[column]:
                mismatches.append(
                    f"{key}={value} {column}: {left[column]} != {right[column]}"
                )
        for column in numeric_columns:
            left_value = float(left[column])
            right_value = float(right[column])
            if not (
                math.isfinite(left_value)
                and math.isfinite(right_value)
                and math.isclose(left_value, right_value, rel_tol=1e-9, abs_tol=1e-7)
            ):
                mismatches.append(
                    f"{key}={value} {column}: {left_value} != {right_value}"
                )
        if len(mismatches) >= 50:
            break
    return {
        "reference_rows": len(reference),
        "candidate_rows": len(candidate),
        "compared_rows": compared,
        "missing_keys": len(missing),
        "extra_keys": len(extra),
        "mismatch_count_capped": len(mismatches),
        "mismatch_examples": mismatches[:20],
        "parity_valid": not mismatches,
    }


def compare(
    reference_setup_path: Path,
    reference_decisions_path: Path,
    candidate_setup_path: Path,
    candidate_decisions_path: Path,
) -> dict[str, Any]:
    reference_setup = read_exact_csv(reference_setup_path, SETUP_AUDIT_COLUMNS)
    candidate_setup = read_exact_csv(candidate_setup_path, SETUP_AUDIT_COLUMNS)
    reference_decisions = read_exact_csv(reference_decisions_path, DECISION_COLUMNS)
    candidate_decisions = read_exact_csv(candidate_decisions_path, DECISION_COLUMNS)
    decisions = compare_rows(
        reference_decisions,
        candidate_decisions,
        "recorded_at",
        DECISION_STRING_COLUMNS,
        DECISION_NUMERIC_COLUMNS,
    )
    setups = compare_rows(
        reference_setup,
        candidate_setup,
        "observation_time",
        SETUP_STRING_COLUMNS,
        SETUP_NUMERIC_COLUMNS,
    )
    return {
        "comparison_stage": "stage_d_generation_model_parity_only",
        "training_performed": False,
        "deployment_authorized": False,
        "ignored_by_design": [
            "Risk messages and approvals",
            "Execution results and synthetic tickets",
            "Telemetry and paper lifecycle",
        ],
        "decisions": decisions,
        "setups": setups,
        "generation_parity_valid": (
            bool(decisions["parity_valid"]) and bool(setups["parity_valid"])
        ),
        "limitations": [
            "Parity authorizes faster offline Dataset generation only.",
            "Final strategy-quality evidence still requires real ticks.",
            "This comparison cannot train or authorize Runtime deployment.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-setup", required=True, type=Path)
    parser.add_argument("--reference-decisions", required=True, type=Path)
    parser.add_argument("--candidate-setup", required=True, type=Path)
    parser.add_argument("--candidate-decisions", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    arguments = parser.parse_args()
    result = compare(
        arguments.reference_setup,
        arguments.reference_decisions,
        arguments.candidate_setup,
        arguments.candidate_decisions,
    )
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
