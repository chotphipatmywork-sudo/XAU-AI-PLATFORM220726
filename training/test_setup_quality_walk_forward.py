"""Focused leakage/readiness checks for the Stage D Setup-quality ranker."""

from __future__ import annotations

from datetime import datetime, timedelta

from analyze_shadow_run import FEATURE_COLUMNS
from setup_quality_walk_forward import (
    build_time_purged_folds,
    readiness,
    run_selection,
)


def samples(count: int = 300) -> list[dict[str, object]]:
    start = datetime(2025, 1, 1, 0, 0)
    rows: list[dict[str, object]] = []
    for index in range(count):
        observation = start + timedelta(hours=6 * index)
        label = 1 if index % 3 == 0 else 0
        features = [50.0] * len(FEATURE_COLUMNS)
        features[0] = 85.0 if label == 1 else 15.0
        rows.append({
            "observation": observation,
            "known_at": observation + timedelta(hours=1),
            "features": features,
            "label": label,
            "outcome": "TARGET_FIRST" if label == 1 else "STOP_FIRST",
        })
    return rows


def main() -> None:
    insufficient = run_selection(samples(60))
    if insufficient["training_performed"] or insufficient["readiness"]["ready"]:
        raise AssertionError("Insufficient Stage D data did not block training")

    adequate = samples()
    state = readiness(adequate)
    if not state["ready"]:
        raise AssertionError(f"Adequate Stage D data was rejected: {state}")
    folds = build_time_purged_folds(adequate)
    if len(folds) != 4:
        raise AssertionError("Stage D did not create four expanding folds")
    for train_indices, evaluation_indices in folds:
        evaluation_start = adequate[evaluation_indices[0]]["observation"]
        if any(adequate[index]["known_at"] >= evaluation_start for index in train_indices):
            raise AssertionError("A future-matured label crossed a Stage D fold boundary")

    report = run_selection(adequate)
    if not report["training_performed"]:
        raise AssertionError("Ready Stage D data did not run Train-only selection")
    if report["validation_dataset_used"] or report["test_dataset_used"]:
        raise AssertionError("Stage D selection read a sealed partition")
    if report["model_feature_order"] != list(FEATURE_COLUMNS):
        raise AssertionError("Stage D model feature boundary changed")
    forbidden = {
        "plan_entry", "plan_stop", "plan_target", "plan_rr", "outcome",
        "mfe_points", "mae_points", "realized_r",
    }
    if forbidden.intersection(report["model_feature_order"]):
        raise AssertionError("Post-observation or Trade Plan data entered model features")
    selected = report["selected"]
    if not selected or not selected["stable_promotion_gate_met"]:
        raise AssertionError(f"Predictable synthetic quality signal failed: {selected}")
    if report["deployment_authorized"]:
        raise AssertionError("Stage D research authorized deployment")

    print("Stage D Setup-quality walk-forward test passed")


if __name__ == "__main__":
    main()
