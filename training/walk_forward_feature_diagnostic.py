"""Measure the active feature contract inside Train-only walk-forward folds."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import fmean, pstdev
from typing import Any

import numpy as np

from chronological_calibrated_classifier import ChronologicalCalibratedClassifier
from diagnose_features import class_counts, feature_summary
from select_candidate import predict_with_policy
from train_classifier import (
    FEATURE_COLUMNS,
    FEATURE_SCHEMA_VERSION,
    LABEL_SCHEMA_VERSION,
    TRAINING_CONTRACT_VERSION,
    evaluation_metrics,
    read_dataset,
)
from walk_forward_select import build_expanding_folds, fresh_model


DIAGNOSTIC_METRICS = ("macro_f1", "buy_precision", "buy_recall")
PERMUTATION_GROUPS = {
    "trend_regime": (0,),
    "trend_momentum": (1,),
    "trend_slope": (2,),
    "volatility_regime": (3,),
    "volatility_change": (4,),
    "liquidity_activity": (5,),
    "liquidity_range_position": (6,),
    "liquidity_sweep_direction": (7,),
    "session_context": (8, 9, 10, 11),
}


def fit_selected_variant(
    candidate_name: str,
    probability_variant: str,
    features: list[list[float]],
    labels: list[int],
) -> Any:
    """Fit the selected walk-forward model variant on one chronological history."""
    if probability_variant == "raw":
        model = fresh_model(candidate_name)
    elif probability_variant == "calibrated":
        model = ChronologicalCalibratedClassifier(fresh_model(candidate_name))
    else:
        raise ValueError(f"Unknown probability variant: {probability_variant}")
    model.fit(features, labels)
    return model


def policy_predictions(
    model: Any,
    features: np.ndarray,
    policy: dict[str, float | str],
) -> list[int]:
    """Apply the locked offline probability policy to one feature matrix."""
    probabilities = model.predict_proba(features).tolist()
    classes = [int(value) for value in model.classes_.tolist()]
    return predict_with_policy(probabilities, classes, policy)


def permutation_diagnostic(
    model: Any,
    features: list[list[float]],
    labels: list[int],
    policy: dict[str, float | str],
    repeats: int = 10,
    random_state: int = 42,
) -> tuple[dict[str, float | int], dict[str, dict[str, dict[str, float]]]]:
    """Return baseline metrics and metric drops after permuting each feature."""
    if repeats < 2:
        raise ValueError("Permutation diagnostic requires at least two repeats")
    matrix = np.asarray(features, dtype=float)
    if matrix.ndim != 2 or matrix.shape[1] != len(FEATURE_COLUMNS):
        raise ValueError(f"Expected {len(FEATURE_COLUMNS)} feature columns")
    baseline = evaluation_metrics(labels, policy_predictions(model, matrix, policy))
    random = np.random.default_rng(random_state)
    result: dict[str, dict[str, dict[str, float]]] = {}

    for feature_name, feature_indices in PERMUTATION_GROUPS.items():
        drops = {metric_name: [] for metric_name in DIAGNOSTIC_METRICS}
        for _ in range(repeats):
            permuted = matrix.copy()
            order = random.permutation(matrix.shape[0])
            for feature_index in feature_indices:
                permuted[:, feature_index] = matrix[order, feature_index]
            metrics = evaluation_metrics(labels, policy_predictions(model, permuted, policy))
            for metric_name in DIAGNOSTIC_METRICS:
                drops[metric_name].append(float(baseline[metric_name]) - float(metrics[metric_name]))
        result[feature_name] = {
            metric_name: {
                "mean_drop": fmean(values),
                "standard_deviation": pstdev(values),
            }
            for metric_name, values in drops.items()
        }
    return baseline, result


def aggregate_fold_importance(
    fold_importance: list[dict[str, dict[str, dict[str, float]]]],
) -> dict[str, dict[str, dict[str, float | int]]]:
    """Aggregate fold-level permutation drops without hiding temporal instability."""
    if not fold_importance:
        raise ValueError("At least one fold is required")
    result: dict[str, dict[str, dict[str, float | int]]] = {}
    for feature_name in PERMUTATION_GROUPS:
        result[feature_name] = {}
        for metric_name in DIAGNOSTIC_METRICS:
            values = [fold[feature_name][metric_name]["mean_drop"] for fold in fold_importance]
            result[feature_name][metric_name] = {
                "mean_drop_across_folds": fmean(values),
                "standard_deviation_across_folds": pstdev(values),
                "minimum_fold_drop": min(values),
                "maximum_fold_drop": max(values),
                "positive_folds": sum(value > 0.0 for value in values),
            }
    return result


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", required=True, type=Path)
    parser.add_argument("--selection-report", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--folds", type=int, default=4)
    parser.add_argument("--repeats", type=int, default=10)
    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()
    if not arguments.selection_report.is_file():
        raise ValueError(f"Walk-forward selection report not found: {arguments.selection_report}")
    selection_report = json.loads(arguments.selection_report.read_text(encoding="utf-8"))
    if selection_report.get("feature_schema_version") != FEATURE_SCHEMA_VERSION:
        raise ValueError(
            f"Feature diagnostic requires a Schema {FEATURE_SCHEMA_VERSION} selection report"
        )
    if selection_report.get("validation_dataset_used") or selection_report.get("test_dataset_used"):
        raise ValueError("Selection report is not Train-only")
    purge_bars = int(selection_report.get("purge_bars", 0))
    if purge_bars != 16:
        raise ValueError("Feature diagnostic requires the approved 16-bar purge")

    selected = selection_report["selected"]
    candidate_name = str(selected["model_candidate"])
    probability_variant = str(selected["probability_variant"])
    policy = dict(selected["decision_policy"])
    features, labels = read_dataset(arguments.train)
    folds = build_expanding_folds(len(features), arguments.folds, purge_bars=purge_bars)

    fold_reports: list[dict[str, Any]] = []
    fold_importance: list[dict[str, dict[str, dict[str, float]]]] = []
    aggregate_actual: list[int] = []
    aggregate_predicted: list[int] = []
    for fold_index, (train_end, evaluation_start, evaluation_end) in enumerate(folds, start=1):
        train_features = features[:train_end]
        train_labels = labels[:train_end]
        evaluation_features = features[evaluation_start:evaluation_end]
        evaluation_labels = labels[evaluation_start:evaluation_end]
        model = fit_selected_variant(candidate_name, probability_variant, train_features, train_labels)
        baseline, importance = permutation_diagnostic(
            model,
            evaluation_features,
            evaluation_labels,
            policy,
            repeats=arguments.repeats,
            random_state=42 + fold_index,
        )
        predictions = policy_predictions(model, np.asarray(evaluation_features, dtype=float), policy)
        aggregate_actual.extend(evaluation_labels)
        aggregate_predicted.extend(predictions)
        fold_importance.append(importance)
        fold_reports.append({
            "fold": fold_index,
            "train_records": train_end,
            "evaluation_start": evaluation_start,
            "purged_records": evaluation_start - train_end,
            "evaluation_end": evaluation_end,
            "evaluation_records": len(evaluation_labels),
            "baseline_metrics": baseline,
            "permutation_importance": importance,
        })

    aggregate_importance = aggregate_fold_importance(fold_importance)
    report = {
        "diagnostic_stage": "train_internal_walk_forward_feature_diagnostic_only",
        "validation_dataset_used": False,
        "test_dataset_used": False,
        "training_contract_version": TRAINING_CONTRACT_VERSION,
        "feature_schema_version": FEATURE_SCHEMA_VERSION,
        "label_schema_version": LABEL_SCHEMA_VERSION,
        "selected_model_candidate": candidate_name,
        "selected_probability_variant": probability_variant,
        "selected_decision_policy": policy,
        "fold_count": len(folds),
        "purge_bars": purge_bars,
        "permutation_repeats": arguments.repeats,
        "train_class_distribution": class_counts(labels),
        "train_feature_summary": feature_summary(features, labels),
        "aggregate_baseline_metrics": evaluation_metrics(aggregate_actual, aggregate_predicted),
        "aggregate_permutation_importance": aggregate_importance,
        "ranked_by_macro_f1_drop": sorted(
            list(PERMUTATION_GROUPS),
            key=lambda name: aggregate_importance[name]["macro_f1"]["mean_drop_across_folds"],
            reverse=True,
        ),
        "ranked_by_buy_precision_drop": sorted(
            list(PERMUTATION_GROUPS),
            key=lambda name: aggregate_importance[name]["buy_precision"]["mean_drop_across_folds"],
            reverse=True,
        ),
        "folds": fold_reports,
        "limitations": [
            "This diagnostic reads only the Train partition and the Train-only selection report.",
            "Permutation importance measures association with the locked development method, not causality.",
            "The report does not authorize Validation, Test, MQL5 deployment, or trading.",
        ],
    }
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({
        "diagnostic_stage": report["diagnostic_stage"],
        "validation_dataset_used": False,
        "test_dataset_used": False,
        "selected_model_candidate": candidate_name,
        "aggregate_baseline_metrics": report["aggregate_baseline_metrics"],
        "ranked_by_macro_f1_drop": report["ranked_by_macro_f1_drop"],
        "ranked_by_buy_precision_drop": report["ranked_by_buy_precision_drop"],
        "diagnostic_file": str(arguments.output),
    }, indent=2))


if __name__ == "__main__":
    main()
