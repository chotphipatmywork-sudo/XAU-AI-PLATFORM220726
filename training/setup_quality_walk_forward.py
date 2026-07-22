"""Evaluate an isolated Stage D Setup-quality ranker inside Train only."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from analyze_shadow_run import FEATURE_COLUMNS
from build_setup_outcome_dataset import (
    FEATURE_SCHEMA_VERSION,
    MINIMUM_NON_TARGET_ROWS,
    MINIMUM_TARGET_ROWS,
    MINIMUM_TRAINABLE_ROWS,
    OUTCOME_AUDIT_COLUMNS,
    SETUP_OUTCOME_SCHEMA_VERSION,
    TRAINABLE_OUTCOMES,
    as_bool,
    parse_time,
)


QUALITY_MODEL_STATUS = "SETUP_QUALITY_RESEARCH_NO_GO"
FOLD_COUNT = 4


def read_train_samples(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Stage D Train partition not found: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or tuple(reader.fieldnames) != OUTCOME_AUDIT_COLUMNS:
            raise ValueError(f"Unexpected Stage D Train schema in {path}")
        rows = list(reader)
    if not rows:
        raise ValueError("Stage D Train partition is empty")

    samples: list[dict[str, Any]] = []
    seen: set[datetime] = set()
    previous: datetime | None = None
    for row in rows:
        if row["setup_outcome_schema_version"] != SETUP_OUTCOME_SCHEMA_VERSION:
            raise ValueError("Setup Outcome Schema version mismatch")
        if row["feature_schema_version"] != FEATURE_SCHEMA_VERSION:
            raise ValueError("Feature Schema version mismatch")
        if not as_bool(row["trainable"]) or row["outcome"] not in TRAINABLE_OUTCOMES:
            raise ValueError("Stage D Train contains a quarantined outcome")
        observation = parse_time(row["observation_time"])
        known_at = parse_time(row["outcome_known_at"])
        if observation in seen:
            raise ValueError(f"Duplicate Stage D Train observation: {row['observation_time']}")
        if previous is not None and observation <= previous:
            raise ValueError("Stage D Train rows are not strictly chronological")
        if known_at <= observation:
            raise ValueError("Stage D Train outcome is not future-matured")
        features = [float(row[column]) for column in FEATURE_COLUMNS]
        if any(value < 0.0 or value > 100.0 for value in features):
            raise ValueError("Stage D Train feature is outside [0,100]")
        samples.append({
            "observation": observation,
            "known_at": known_at,
            "features": features,
            "label": 1 if row["outcome"] == "TARGET_FIRST" else 0,
            "outcome": row["outcome"],
        })
        seen.add(observation)
        previous = observation
    return samples


def readiness(samples: list[dict[str, Any]]) -> dict[str, Any]:
    labels = Counter(int(sample["label"]) for sample in samples)
    target_count = labels.get(1, 0)
    non_target_count = labels.get(0, 0)
    return {
        "train_records": len(samples),
        "target_records": target_count,
        "non_target_records": non_target_count,
        "minimum_train_records": MINIMUM_TRAINABLE_ROWS,
        "minimum_target_records": MINIMUM_TARGET_ROWS,
        "minimum_non_target_records": MINIMUM_NON_TARGET_ROWS,
        "sample_size_requirement_met": len(samples) >= MINIMUM_TRAINABLE_ROWS,
        "target_coverage_met": target_count >= MINIMUM_TARGET_ROWS,
        "non_target_coverage_met": non_target_count >= MINIMUM_NON_TARGET_ROWS,
        "ready": (
            len(samples) >= MINIMUM_TRAINABLE_ROWS
            and target_count >= MINIMUM_TARGET_ROWS
            and non_target_count >= MINIMUM_NON_TARGET_ROWS
        ),
    }


def build_time_purged_folds(
    samples: list[dict[str, Any]], fold_count: int = FOLD_COUNT
) -> list[tuple[list[int], list[int]]]:
    state = readiness(samples)
    if not state["ready"]:
        raise ValueError("Stage D Train readiness gate is not met")
    if fold_count != FOLD_COUNT:
        raise ValueError("Setup Quality V1 fixes four expanding folds")
    initial_train = len(samples) // 2
    remaining = len(samples) - initial_train
    base_size = remaining // fold_count
    if base_size < 10:
        raise ValueError("Stage D Train has insufficient evaluation rows per fold")

    folds: list[tuple[list[int], list[int]]] = []
    evaluation_start = initial_train
    for fold_index in range(fold_count):
        evaluation_end = (
            len(samples)
            if fold_index == fold_count - 1
            else evaluation_start + base_size
        )
        evaluation_indices = list(range(evaluation_start, evaluation_end))
        evaluation_time = samples[evaluation_start]["observation"]
        train_indices = [
            index for index in range(evaluation_start)
            if samples[index]["known_at"] < evaluation_time
        ]
        train_labels = Counter(samples[index]["label"] for index in train_indices)
        evaluation_labels = Counter(
            samples[index]["label"] for index in evaluation_indices
        )
        if len(train_indices) < 30 or set(train_labels) != {0, 1}:
            raise ValueError("A Stage D fold lacks purged Train class coverage")
        if set(evaluation_labels) != {0, 1}:
            raise ValueError("A Stage D fold lacks both evaluation quality classes")
        if min(evaluation_labels.values()) < 5:
            raise ValueError("A Stage D fold has fewer than five rows in one class")
        if any(samples[index]["known_at"] >= evaluation_time for index in train_indices):
            raise AssertionError("Stage D time purge failed")
        folds.append((train_indices, evaluation_indices))
        evaluation_start = evaluation_end
    return folds


def quality_metrics(actual: list[int], predicted: list[int]) -> dict[str, float | int]:
    return {
        "sample_count": len(actual),
        "target_count": sum(actual),
        "accepted_count": sum(predicted),
        "accuracy": float(accuracy_score(actual, predicted)),
        "balanced_accuracy": float(balanced_accuracy_score(actual, predicted)),
        "macro_f1": float(f1_score(actual, predicted, average="macro", zero_division=0)),
        "target_precision": float(precision_score(actual, predicted, zero_division=0)),
        "target_recall": float(recall_score(actual, predicted, zero_division=0)),
    }


def fold_gate(metrics: dict[str, float | int]) -> bool:
    return (
        float(metrics["balanced_accuracy"]) >= 0.55
        and float(metrics["macro_f1"]) >= 0.55
        and float(metrics["target_precision"]) >= 0.50
        and float(metrics["target_recall"]) >= 0.25
    )


def candidate_factories() -> list[tuple[str, Callable[[], Any]]]:
    return [
        (
            "logistic_balanced",
            lambda: make_pipeline(
                StandardScaler(),
                LogisticRegression(
                    class_weight="balanced", max_iter=2000, random_state=42
                ),
            ),
        ),
        (
            "random_forest_depth_5_balanced",
            lambda: RandomForestClassifier(
                n_estimators=300,
                max_depth=5,
                min_samples_leaf=5,
                class_weight="balanced_subsample",
                random_state=42,
                n_jobs=-1,
            ),
        ),
    ]


def evaluate_candidate(
    samples: list[dict[str, Any]],
    folds: list[tuple[list[int], list[int]]],
    factory: Callable[[], Any],
) -> dict[str, Any]:
    all_actual: list[int] = []
    all_predicted: list[int] = []
    fold_reports: list[dict[str, Any]] = []
    for train_indices, evaluation_indices in folds:
        model = factory()
        train_features = [samples[index]["features"] for index in train_indices]
        train_labels = [samples[index]["label"] for index in train_indices]
        evaluation_features = [
            samples[index]["features"] for index in evaluation_indices
        ]
        actual = [samples[index]["label"] for index in evaluation_indices]
        model.fit(train_features, train_labels)
        predicted = [int(value) for value in model.predict(evaluation_features)]
        metrics = quality_metrics(actual, predicted)
        fold_reports.append({
            "train_records": len(train_indices),
            "evaluation_records": len(evaluation_indices),
            "purged_train_candidates": evaluation_indices[0] - len(train_indices),
            "evaluation_start": samples[evaluation_indices[0]][
                "observation"
            ].strftime("%Y.%m.%d %H:%M"),
            "metrics": metrics,
            "gate_met": fold_gate(metrics),
        })
        all_actual.extend(actual)
        all_predicted.extend(predicted)
    aggregate = quality_metrics(all_actual, all_predicted)
    folds_passing = sum(bool(report["gate_met"]) for report in fold_reports)
    return {
        "aggregate_metrics": aggregate,
        "aggregate_gate_met": fold_gate(aggregate),
        "folds_passing_gate": folds_passing,
        "stable_walk_forward_gate_met": (
            fold_gate(aggregate) and folds_passing == len(folds)
        ),
        "folds": fold_reports,
    }


def run_selection(samples: list[dict[str, Any]]) -> dict[str, Any]:
    state = readiness(samples)
    report: dict[str, Any] = {
        "selection_stage": "stage_d_train_only_time_purged_setup_quality",
        "setup_outcome_schema_version": SETUP_OUTCOME_SCHEMA_VERSION,
        "feature_schema_version": FEATURE_SCHEMA_VERSION,
        "model_feature_order": list(FEATURE_COLUMNS),
        "validation_dataset_used": False,
        "test_dataset_used": False,
        "runtime_integration_authorized": False,
        "deployment_authorized": False,
        "model_status": QUALITY_MODEL_STATUS,
        "readiness": state,
        "training_performed": False,
        "candidates": [],
        "selected": None,
    }
    if not state["ready"]:
        report["refusal_reason"] = "Stage D Train readiness gate is not met."
        return report

    folds = build_time_purged_folds(samples)
    actual = [samples[index]["label"] for _, evaluation in folds for index in evaluation]
    accept_all = quality_metrics(actual, [1] * len(actual))
    report["accept_all_baseline"] = accept_all
    best_key = (-1, -1, -1.0, -1.0, -1.0)
    selected: dict[str, Any] | None = None
    candidates = []
    for name, factory in candidate_factories():
        result = evaluate_candidate(samples, folds, factory)
        aggregate = result["aggregate_metrics"]
        beats_baseline = (
            float(aggregate["target_precision"])
            >= float(accept_all["target_precision"]) + 0.10
            and float(aggregate["macro_f1"])
            >= float(accept_all["macro_f1"]) + 0.05
        )
        result.update({
            "model_candidate": name,
            "beats_accept_all_baseline": beats_baseline,
            "stable_promotion_gate_met": (
                bool(result["stable_walk_forward_gate_met"]) and beats_baseline
            ),
        })
        candidates.append(result)
        key = (
            int(result["stable_promotion_gate_met"]),
            int(result["folds_passing_gate"]),
            float(aggregate["target_precision"]),
            float(aggregate["macro_f1"]),
            float(aggregate["balanced_accuracy"]),
        )
        if key > best_key:
            best_key = key
            selected = result
    report["training_performed"] = True
    report["fold_count"] = len(folds)
    report["candidates"] = candidates
    report["selected"] = selected
    report["stable_research_gate_met"] = bool(
        selected and selected["stable_promotion_gate_met"]
    )
    report["limitations"] = [
        "Only the Stage D Train partition is accepted by this tool.",
        "Validation and Test remain sealed and are not CLI inputs.",
        "A stable Train-only result cannot authorize Runtime or deployment.",
        "A nested estimate and untouched later period require later approval.",
    ]
    return report


def fit_preliminary_model(
    samples: list[dict[str, Any]], selected_name: str
) -> Any:
    for name, factory in candidate_factories():
        if name == selected_name:
            model = factory()
            model.fit(
                [sample["features"] for sample in samples],
                [sample["label"] for sample in samples],
            )
            return model
    raise ValueError(f"Unknown Stage D candidate: {selected_name}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    arguments = parser.parse_args()
    samples = read_train_samples(arguments.train)
    report = run_selection(samples)
    arguments.output_dir.mkdir(parents=True, exist_ok=True)
    report_path = arguments.output_dir / "setup_quality_walk_forward.json"
    model_path: Path | None = None
    selected = report.get("selected")
    if report.get("stable_research_gate_met") and isinstance(selected, dict):
        model = fit_preliminary_model(samples, str(selected["model_candidate"]))
        model_path = arguments.output_dir / "setup_quality_preliminary_no_go.joblib"
        joblib.dump(model, model_path)
        report["preliminary_model_file"] = str(model_path)
    else:
        report["preliminary_model_file"] = None
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({
        "selection_stage": report["selection_stage"],
        "readiness": report["readiness"],
        "training_performed": report["training_performed"],
        "selected": report.get("selected"),
        "stable_research_gate_met": report.get("stable_research_gate_met", False),
        "preliminary_model_file": str(model_path) if model_path else None,
        "diagnostics_file": str(report_path),
        "deployment_authorized": False,
    }, indent=2))


if __name__ == "__main__":
    main()
