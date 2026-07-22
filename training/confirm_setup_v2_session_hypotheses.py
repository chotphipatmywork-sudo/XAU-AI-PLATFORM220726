"""XAU AI PLATFORM | Offline Confirmation | Version 1.0.0.

File: confirm_setup_v2_session_hypotheses.py
Purpose: Confirm frozen CR-014 Session hypotheses on one fresh period only.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

from analyze_shadow_run import FEATURE_COLUMNS
from build_setup_outcome_dataset import (
    FEATURE_SCHEMA_VERSION,
    OUTCOME_AUDIT_COLUMNS,
    SETUP_OUTCOME_SCHEMA_VERSION,
    TRAINABLE_OUTCOMES,
    as_bool,
    parse_time,
)
from diagnose_setup_v2_hypotheses import (
    EXPECTED_NEGATIVE,
    EXPECTED_POSITIVE,
    Hypothesis,
    derived_values,
    subgroup_metrics,
)


CONFIRMATION_SCHEMA_VERSION = "1.0.0"
CONFIRMATION_STATUS = "SETUP_V2_SESSION_CONFIRMATION_NO_GO"
CONFIRMATION_FILENAME = "XAU_AI_SETUP_OUTCOME_CONFIRMATION.csv"
FRESH_PERIOD_AFTER = datetime(2026, 6, 26, 21, 30)
FOLD_COUNT = 4
MINIMUM_RECORDS = 80
MINIMUM_TARGET_RECORDS = 15
MINIMUM_NON_TARGET_RECORDS = 40
MINIMUM_FOLD_MATCHES = 3
MINIMUM_TOTAL_MATCHES = 20
MINIMUM_ABSOLUTE_LIFT = 0.05


def confirmation_hypotheses() -> tuple[Hypothesis, ...]:
    return (
        Hypothesis(
            "session_early_phase_positive",
            "Does the first third of a Session retain higher Setup quality?",
            "session_progress < 33.333333",
            EXPECTED_POSITIVE,
            lambda value: value["session_progress"] < (100.0 / 3.0),
        ),
        Hypothesis(
            "session_late_phase_negative",
            "Does the final third of a Session retain lower Setup quality?",
            "session_progress >= 66.666667",
            EXPECTED_NEGATIVE,
            lambda value: value["session_progress"] >= (200.0 / 3.0),
        ),
    )


def validate_confirmation_filename(path: Path) -> None:
    if path.name != CONFIRMATION_FILENAME:
        raise ValueError(
            "CR-014 confirmation accepts only "
            f"{CONFIRMATION_FILENAME}; Train/Validation/Test files are forbidden"
        )


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def validate_fresh_samples(samples: list[dict[str, Any]]) -> None:
    previous: datetime | None = None
    for sample in samples:
        observation = sample["observation"]
        known_at = sample["known_at"]
        if observation <= FRESH_PERIOD_AFTER:
            raise ValueError(
                "CR-014 confirmation contains evidence at or before the frozen cutoff"
            )
        if previous is not None and observation <= previous:
            raise ValueError("CR-014 confirmation observations are not chronological")
        if known_at <= observation:
            raise ValueError("CR-014 confirmation outcome is not future-matured")
        previous = observation


def read_confirmation_samples(path: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    validate_confirmation_filename(path)
    if not path.exists():
        raise FileNotFoundError(f"CR-014 confirmation Dataset not found: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or tuple(reader.fieldnames) != OUTCOME_AUDIT_COLUMNS:
            raise ValueError(f"Unexpected CR-014 confirmation schema in {path}")
        rows = list(reader)
    if not rows:
        raise ValueError("CR-014 confirmation Dataset is empty")

    samples: list[dict[str, Any]] = []
    seen: set[datetime] = set()
    previous: datetime | None = None
    quarantined = 0
    first_observation: datetime | None = None
    last_observation: datetime | None = None
    for row in rows:
        if row["setup_outcome_schema_version"] != SETUP_OUTCOME_SCHEMA_VERSION:
            raise ValueError("CR-014 confirmation Setup Outcome Schema mismatch")
        if row["feature_schema_version"] != FEATURE_SCHEMA_VERSION:
            raise ValueError("CR-014 confirmation Feature Schema mismatch")
        if row["timeframe"] != "PERIOD_M15":
            raise ValueError("CR-014 confirmation accepts only PERIOD_M15")
        observation = parse_time(row["observation_time"])
        if observation <= FRESH_PERIOD_AFTER:
            raise ValueError(
                "CR-014 confirmation contains evidence at or before the frozen cutoff"
            )
        if observation in seen or (previous is not None and observation <= previous):
            raise ValueError("CR-014 confirmation observations are not unique and chronological")
        direction = row["direction"]
        if direction not in {"TRADE_SETUP_BUY", "TRADE_SETUP_SELL"}:
            raise ValueError(f"Unsupported CR-014 Setup direction: {direction}")
        feature_map = {column: float(row[column]) for column in FEATURE_COLUMNS}
        if any(
            not math.isfinite(value) or value < 0.0 or value > 100.0
            for value in feature_map.values()
        ):
            raise ValueError("CR-014 confirmation feature is outside [0,100]")

        trainable = as_bool(row["trainable"])
        if not trainable:
            if row["outcome"] in TRAINABLE_OUTCOMES:
                raise ValueError("CR-014 confirmation quarantined a trainable outcome")
            quarantined += 1
        else:
            if row["outcome"] not in TRAINABLE_OUTCOMES:
                raise ValueError("CR-014 confirmation marked an invalid outcome trainable")
            known_at = parse_time(row["outcome_known_at"])
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
        first_observation = observation if first_observation is None else first_observation
        last_observation = observation

    if not samples:
        raise ValueError("CR-014 confirmation has no mature trainable outcomes")
    validate_fresh_samples(samples)
    return samples, {
        "source_rows": len(rows),
        "mature_trainable_rows": len(samples),
        "quarantined_rows": quarantined,
        "first_observation": first_observation.strftime("%Y.%m.%d %H:%M"),
        "last_observation": last_observation.strftime("%Y.%m.%d %H:%M"),
        "source_sha256": file_sha256(path),
    }


def confirmation_readiness(samples: list[dict[str, Any]]) -> dict[str, Any]:
    labels = Counter(int(sample["label"]) for sample in samples)
    target_count = labels.get(1, 0)
    non_target_count = labels.get(0, 0)
    return {
        "records": len(samples),
        "target_records": target_count,
        "non_target_records": non_target_count,
        "minimum_records": MINIMUM_RECORDS,
        "minimum_target_records": MINIMUM_TARGET_RECORDS,
        "minimum_non_target_records": MINIMUM_NON_TARGET_RECORDS,
        "sample_size_requirement_met": len(samples) >= MINIMUM_RECORDS,
        "target_coverage_met": target_count >= MINIMUM_TARGET_RECORDS,
        "non_target_coverage_met": non_target_count >= MINIMUM_NON_TARGET_RECORDS,
        "ready": (
            len(samples) >= MINIMUM_RECORDS
            and target_count >= MINIMUM_TARGET_RECORDS
            and non_target_count >= MINIMUM_NON_TARGET_RECORDS
        ),
    }


def chronological_blocks(samples: list[dict[str, Any]]) -> list[list[int]]:
    if len(samples) < MINIMUM_RECORDS:
        raise ValueError("CR-014 confirmation does not meet minimum sample size")
    base_size = len(samples) // FOLD_COUNT
    blocks: list[list[int]] = []
    start = 0
    for fold_index in range(FOLD_COUNT):
        end = len(samples) if fold_index == FOLD_COUNT - 1 else start + base_size
        blocks.append(list(range(start, end)))
        start = end
    return blocks


def evaluate_confirmation_hypothesis(
    samples: list[dict[str, Any]], blocks: list[list[int]], hypothesis: Hypothesis
) -> dict[str, Any]:
    fold_reports: list[dict[str, Any]] = []
    aggregate_indices: list[int] = []
    for fold_number, indices in enumerate(blocks, start=1):
        metrics = subgroup_metrics(samples, indices, hypothesis)
        metrics.update({
            "fold": fold_number,
            "evaluation_start": samples[indices[0]]["observation"].strftime(
                "%Y.%m.%d %H:%M"
            ),
            "minimum_support_met": metrics["matched_records"] >= MINIMUM_FOLD_MATCHES,
        })
        fold_reports.append(metrics)
        aggregate_indices.extend(indices)

    aggregate = subgroup_metrics(samples, aggregate_indices, hypothesis)
    lifts = [report["target_rate_lift_vs_fold"] for report in fold_reports]
    support_met = (
        all(report["minimum_support_met"] for report in fold_reports)
        and aggregate["matched_records"] >= MINIMUM_TOTAL_MATCHES
    )
    expected_sign_met = (
        hypothesis.expected_effect == EXPECTED_POSITIVE
        and all(lift is not None and lift > 0.0 for lift in lifts)
    ) or (
        hypothesis.expected_effect == EXPECTED_NEGATIVE
        and all(lift is not None and lift < 0.0 for lift in lifts)
    )
    aggregate_lift = aggregate["target_rate_lift_vs_fold"]
    effect_size_met = (
        aggregate_lift is not None
        and abs(float(aggregate_lift)) >= MINIMUM_ABSOLUTE_LIFT
    )
    confirmed = support_met and expected_sign_met and effect_size_met
    return {
        "name": hypothesis.name,
        "question": hypothesis.question,
        "frozen_rule": hypothesis.rule,
        "frozen_expected_effect": hypothesis.expected_effect,
        "aggregate": aggregate,
        "folds": fold_reports,
        "support_gate_met": support_met,
        "expected_effect_sign_met_all_four_folds": expected_sign_met,
        "aggregate_effect_size_met": effect_size_met,
        "fresh_period_confirmation_met": confirmed,
    }


def run_confirmation(
    samples: list[dict[str, Any]], source_audit: dict[str, Any] | None = None
) -> dict[str, Any]:
    validate_fresh_samples(samples)
    state = confirmation_readiness(samples)
    report: dict[str, Any] = {
        "confirmation_schema_version": CONFIRMATION_SCHEMA_VERSION,
        "confirmation_stage": "cr_014_stage_1b_fresh_session_confirmation",
        "confirmation_status": CONFIRMATION_STATUS,
        "frozen_cutoff_exclusive": FRESH_PERIOD_AFTER.strftime("%Y.%m.%d %H:%M"),
        "setup_outcome_schema_version": SETUP_OUTCOME_SCHEMA_VERSION,
        "feature_schema_version": FEATURE_SCHEMA_VERSION,
        "validation_dataset_used": False,
        "test_dataset_used": False,
        "model_training_performed": False,
        "runtime_integration_authorized": False,
        "deployment_authorized": False,
        "source_audit": source_audit or {},
        "readiness": state,
        "gate": {
            "required_chronological_blocks": FOLD_COUNT,
            "minimum_matches_per_block": MINIMUM_FOLD_MATCHES,
            "minimum_total_matches": MINIMUM_TOTAL_MATCHES,
            "minimum_absolute_target_rate_lift": MINIMUM_ABSOLUTE_LIFT,
            "requires_frozen_effect_sign_all_blocks": True,
        },
        "hypotheses": [],
        "confirmed_hypotheses": [],
        "confirmation_gate_met": False,
        "eligible_to_request_stage_2_review": False,
        "stage_2_contract_authorized": False,
    }
    if not state["ready"]:
        report["refusal_reason"] = "Fresh confirmation readiness gate is not met."
        return report

    blocks = chronological_blocks(samples)
    results = [
        evaluate_confirmation_hypothesis(samples, blocks, hypothesis)
        for hypothesis in confirmation_hypotheses()
    ]
    confirmed = [
        result["name"] for result in results if result["fresh_period_confirmation_met"]
    ]
    report["hypotheses"] = results
    report["confirmed_hypotheses"] = confirmed
    report["confirmation_gate_met"] = len(confirmed) == len(results)
    report["eligible_to_request_stage_2_review"] = report["confirmation_gate_met"]
    report["limitations"] = [
        "This one-shot confirmation accepts no Train, Validation, or Test file.",
        "A confirmed association is not an independent reversal Trade Plan.",
        "Eligibility requests human review and never authorizes Stage 2 automatically.",
        "Runtime, deployment, and broker trading remain forbidden.",
    ]
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--confirmation", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    arguments = parser.parse_args()
    if arguments.output.exists():
        raise FileExistsError(
            "CR-014 confirmation output already exists; the period is no longer untouched"
        )
    samples, source_audit = read_confirmation_samples(arguments.confirmation)
    report = run_confirmation(samples, source_audit)
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({
        "confirmation_stage": report["confirmation_stage"],
        "source_audit": report["source_audit"],
        "readiness": report["readiness"],
        "confirmed_hypotheses": report["confirmed_hypotheses"],
        "confirmation_gate_met": report["confirmation_gate_met"],
        "eligible_to_request_stage_2_review": report[
            "eligible_to_request_stage_2_review"
        ],
        "stage_2_contract_authorized": False,
        "runtime_integration_authorized": False,
        "deployment_authorized": False,
        "confirmation_file": str(arguments.output),
    }, indent=2))


if __name__ == "__main__":
    main()
