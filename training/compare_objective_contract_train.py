"""XAU AI PLATFORM | Offline Comparison | Version 1.0.0.

Compare two Objective contracts using Train partitions only.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

from build_setup_outcome_dataset import OUTCOME_AUDIT_COLUMNS


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def read_train(path: Path) -> list[dict[str, str]]:
    upper = path.name.upper()
    if "VALIDATION" in upper or "TEST" in upper or "TRAIN" not in upper:
        raise ValueError("Objective contract comparison accepts Train files only")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or tuple(reader.fieldnames) != OUTCOME_AUDIT_COLUMNS:
            raise ValueError("Unexpected Objective Train schema")
        rows = list(reader)
    if not rows:
        raise ValueError("Objective Train comparison source is empty")
    return rows


def metrics(rows: list[dict[str, str]]) -> dict[str, float | int]:
    targets = sum(row["outcome"] == "TARGET_FIRST" for row in rows)
    stops = sum(row["outcome"] == "STOP_FIRST" for row in rows)
    returns = [
        float(row["plan_rr"]) if row["outcome"] == "TARGET_FIRST" else
        -1.0 if row["outcome"] == "STOP_FIRST" else 0.0
        for row in rows
    ]
    return {
        "records": len(rows),
        "target_first": targets,
        "stop_first": stops,
        "target_rate": targets / len(rows),
        "mean_cost_aware_r": sum(returns) / len(returns),
    }


def compare(reference_path: Path, candidate_path: Path) -> dict[str, object]:
    reference = metrics(read_train(reference_path))
    candidate = metrics(read_train(candidate_path))
    return {
        "comparison_stage": "objective_contract_train_only_descriptive",
        "validation_dataset_used": False,
        "test_dataset_used": False,
        "model_training_performed": False,
        "reference_train_sha256": sha256(reference_path),
        "candidate_train_sha256": sha256(candidate_path),
        "reference": reference,
        "candidate": candidate,
        "target_rate_change": (
            float(candidate["target_rate"]) - float(reference["target_rate"])
        ),
        "mean_cost_aware_r_change": (
            float(candidate["mean_cost_aware_r"])
            - float(reference["mean_cost_aware_r"])
        ),
        "candidate_sample_gate_met": int(candidate["records"]) >= 200,
        "contract_promotion_authorized": False,
        "runtime_integration_authorized": False,
        "deployment_authorized": False,
        "limitations": [
            "Partitions may have different chronological boundaries.",
            "This is descriptive Train-only evidence, not a paired test.",
            "Validation and Test remain forbidden selection inputs.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-train", required=True, type=Path)
    parser.add_argument("--candidate-train", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    arguments = parser.parse_args()
    report = compare(arguments.reference_train, arguments.candidate_train)
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
