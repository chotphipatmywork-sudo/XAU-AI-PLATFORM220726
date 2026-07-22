"""Compare past-only Liquidity temporal context on purged Train folds."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import fmean
from typing import Any, Sequence

from nested_walk_forward_select import gate_floor_ratio, selection_key
from select_candidate import predict_with_policy
from train_classifier import (
    FEATURE_SCHEMA_VERSION,
    LABEL_SCHEMA_VERSION,
    TRAINING_CONTRACT_VERSION,
    evaluation_metrics,
    meets_evaluation_contract,
    read_dataset,
)
from walk_forward_select import build_expanding_folds, fresh_model, metrics_for_folds


PURGE_BARS = 16
MODEL_CANDIDATE = "random_forest_depth_5_balanced"
DECISION_POLICY: dict[str, str] = {"type": "argmax"}
SWEEP_LOOKBACK = 16
BUY_SWEEP = 0.0
NO_SWEEP = 50.0
SELL_SWEEP = 100.0


def contract_metadata() -> dict[str, str]:
    return {
        "training_contract_version": TRAINING_CONTRACT_VERSION,
        "source_feature_schema_version": FEATURE_SCHEMA_VERSION,
        "label_schema_version": LABEL_SCHEMA_VERSION,
    }


def bounded_delta(current: float, previous: float) -> float:
    """Map a -100..100 past-only change into 0..100 with neutral at 50."""
    return 50.0 + (float(current) - float(previous)) / 2.0


def sweep_mean(features: Sequence[Sequence[float]], index: int, lookback: int) -> float:
    """Return the mean canonical sweep encoding using current and past rows only."""
    start = max(0, index - lookback + 1)
    values = [float(features[item][7]) for item in range(start, index + 1)]
    if any(value not in (BUY_SWEEP, NO_SWEEP, SELL_SWEEP) for value in values):
        raise ValueError("Unexpected Liquidity sweep encoding")
    return fmean(values)


def sweep_freshness(
    features: Sequence[Sequence[float]],
    index: int,
    target: float,
    lookback: int = SWEEP_LOOKBACK,
) -> float:
    """Return linearly decaying freshness of the latest matching past sweep."""
    if target not in (BUY_SWEEP, SELL_SWEEP):
        raise ValueError("Freshness target must be a directional sweep")
    for age in range(lookback):
        cursor = index - age
        if cursor < 0:
            break
        if float(features[cursor][7]) == target:
            return 100.0 * (lookback - age) / lookback
    return 0.0


def derive_liquidity_temporal(
    features: Sequence[Sequence[float]],
) -> list[list[float]]:
    """Return eight bounded Liquidity temporal values without future rows."""
    derived_rows: list[list[float]] = []
    for index, row in enumerate(features):
        def delta(feature_index: int, lookback: int) -> float:
            if index < lookback:
                return 50.0
            return bounded_delta(
                float(row[feature_index]),
                float(features[index - lookback][feature_index]),
            )

        derived = [
            delta(5, 1),
            delta(5, 4),
            delta(6, 1),
            delta(6, 4),
            sweep_mean(features, index, 4),
            sweep_mean(features, index, 16),
            sweep_freshness(features, index, BUY_SWEEP),
            sweep_freshness(features, index, SELL_SWEEP),
        ]
        if any(value < 0.0 or value > 100.0 for value in derived):
            raise ValueError("Derived Liquidity temporal value is outside 0..100")
        derived_rows.append(derived)
    return derived_rows


def feature_set_specs() -> list[dict[str, Any]]:
    return [
        {"name": "baseline", "temporal_indices": []},
        {"name": "liquidity_changes", "temporal_indices": [0, 1, 2, 3]},
        {"name": "sweep_memory", "temporal_indices": [4, 5, 6, 7]},
        {"name": "all_liquidity_temporal", "temporal_indices": list(range(8))},
    ]


def transform_features(
    features: Sequence[Sequence[float]],
    temporal_indices: Sequence[int],
) -> list[list[float]]:
    temporal = derive_liquidity_temporal(features)
    return [
        [float(value) for value in row]
        + [temporal[index][item] for item in temporal_indices]
        for index, row in enumerate(features)
    ]


def promotion_candidate(results: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Apply the CR-003 predeclared promotion boundary."""
    baseline = next(item for item in results if item["feature_set"] == "baseline")
    candidates = [item for item in results if item["feature_set"] != "baseline"]
    eligible = [
        item
        for item in candidates
        if selection_key(
            item["aggregate_metrics"],
            int(item["folds_passing_gate"]),
            4,
        )
        > selection_key(
            baseline["aggregate_metrics"],
            int(baseline["folds_passing_gate"]),
            4,
        )
        and float(item["gate_floor_ratio"]) >= float(baseline["gate_floor_ratio"]) + 0.01
        and float(item["aggregate_metrics"]["macro_f1"])
        >= float(baseline["aggregate_metrics"]["macro_f1"])
        and int(item["folds_passing_gate"]) >= 1
    ]
    if not eligible:
        return None
    return max(
        eligible,
        key=lambda item: selection_key(
            item["aggregate_metrics"],
            int(item["folds_passing_gate"]),
            4,
        ),
    )


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--folds", type=int, default=4)
    parser.add_argument("--purge-bars", type=int, default=PURGE_BARS)
    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()
    if arguments.purge_bars != PURGE_BARS:
        raise ValueError(
            f"Feature/Label Contract {FEATURE_SCHEMA_VERSION}/{LABEL_SCHEMA_VERSION} "
            "requires a 16-bar purge"
        )
    if arguments.folds != 4:
        raise ValueError("CR-003 controlled comparison requires exactly four folds")

    features, labels = read_dataset(arguments.train)
    folds = build_expanding_folds(
        len(features), fold_count=arguments.folds, purge_bars=PURGE_BARS
    )
    results: list[dict[str, Any]] = []
    for feature_set in feature_set_specs():
        indices = list(feature_set["temporal_indices"])
        transformed = transform_features(features, indices)
        actual: list[int] = []
        predicted: list[int] = []
        fold_lengths: list[int] = []
        fold_reports: list[dict[str, Any]] = []
        for fold_index, (train_end, evaluation_start, evaluation_end) in enumerate(
            folds, start=1
        ):
            model = fresh_model(MODEL_CANDIDATE)
            model.fit(transformed[:train_end], labels[:train_end])
            evaluation_labels = labels[evaluation_start:evaluation_end]
            fold_prediction = predict_with_policy(
                model.predict_proba(
                    transformed[evaluation_start:evaluation_end]
                ).tolist(),
                [int(value) for value in model.classes_.tolist()],
                DECISION_POLICY,
            )
            metrics = evaluation_metrics(evaluation_labels, fold_prediction)
            actual.extend(evaluation_labels)
            predicted.extend(fold_prediction)
            fold_lengths.append(len(evaluation_labels))
            fold_reports.append({
                "fold": fold_index,
                "train_records": train_end,
                "purged_records": evaluation_start - train_end,
                "evaluation_records": len(evaluation_labels),
                "metrics": metrics,
                "gate_met": meets_evaluation_contract(metrics),
            })

        aggregate_metrics = evaluation_metrics(actual, predicted)
        fold_metrics = metrics_for_folds(actual, predicted, fold_lengths)
        folds_passing = sum(meets_evaluation_contract(item) for item in fold_metrics)
        results.append({
            "feature_set": feature_set["name"],
            "temporal_indices": indices,
            "derived_feature_count": len(indices),
            "aggregate_metrics": aggregate_metrics,
            "gate_floor_ratio": gate_floor_ratio(aggregate_metrics),
            "aggregate_gate_met": meets_evaluation_contract(aggregate_metrics),
            "folds_passing_gate": folds_passing,
            "stable_gate_met": (
                meets_evaluation_contract(aggregate_metrics)
                and folds_passing == len(folds)
            ),
            "folds": fold_reports,
        })

    ranked = sorted(
        results,
        key=lambda item: selection_key(
            item["aggregate_metrics"], int(item["folds_passing_gate"]), len(folds)
        ),
        reverse=True,
    )
    promoted = promotion_candidate(results)
    report = {
        "diagnostic_stage": "train_only_purged_liquidity_temporal_comparison",
        "validation_dataset_used": False,
        "test_dataset_used": False,
        **contract_metadata(),
        "purge_bars": PURGE_BARS,
        "future_rows_used": False,
        "model_candidate": MODEL_CANDIDATE,
        "probability_variant": "raw",
        "decision_policy": DECISION_POLICY,
        "derived_feature_names": [
            "liquidity_activity_delta_1",
            "liquidity_activity_delta_4",
            "liquidity_range_position_delta_1",
            "liquidity_range_position_delta_4",
            "liquidity_sweep_mean_4",
            "liquidity_sweep_mean_16",
            "buy_sweep_freshness_16",
            "sell_sweep_freshness_16",
        ],
        "feature_sets_ranked": [item["feature_set"] for item in ranked],
        "feature_sets": results,
        "promotion_rules": {
            "gate_floor_improvement_minimum": 0.01,
            "macro_f1_must_not_decrease": True,
            "minimum_complete_passing_folds": 1,
        },
        "promoted_feature_set": (
            promoted["feature_set"] if promoted is not None else None
        ),
        "nested_confirmation_authorized": promoted is not None,
        "limitations": [
            "The controlled comparison reuses inspected Train development periods.",
            "Derived columns are research-only and are not active Schema 4.0 inputs.",
            "Record lookbacks can span broker market closures.",
            "Validation and Test are not read and deployment remains unauthorized.",
        ],
    }
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({
        "diagnostic_stage": report["diagnostic_stage"],
        "validation_dataset_used": False,
        "test_dataset_used": False,
        "future_rows_used": False,
        "feature_sets_ranked": report["feature_sets_ranked"],
        "results": [
            {
                "feature_set": item["feature_set"],
                "aggregate_metrics": item["aggregate_metrics"],
                "gate_floor_ratio": item["gate_floor_ratio"],
                "folds_passing_gate": item["folds_passing_gate"],
            }
            for item in ranked
        ],
        "promoted_feature_set": report["promoted_feature_set"],
        "nested_confirmation_authorized": report["nested_confirmation_authorized"],
        "diagnostic_file": str(arguments.output),
    }, indent=2))


if __name__ == "__main__":
    main()
