"""Compare purged expanding, rolling, and recency-weighted histories inside Train only."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

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


def contract_metadata() -> dict[str, str]:
    """Return the active training, feature, and label contract versions."""
    return {
        "training_contract_version": TRAINING_CONTRACT_VERSION,
        "feature_schema_version": FEATURE_SCHEMA_VERSION,
        "label_schema_version": LABEL_SCHEMA_VERSION,
    }


def strategy_specs() -> list[dict[str, int | str | None]]:
    """Return a bounded, predeclared history strategy grid."""
    return [
        {"name": "expanding", "type": "expanding", "parameter": None},
        {"name": "rolling_1000", "type": "rolling", "parameter": 1000},
        {"name": "rolling_1500", "type": "rolling", "parameter": 1500},
        {"name": "rolling_2000", "type": "rolling", "parameter": 2000},
        {"name": "recency_half_life_500", "type": "recency", "parameter": 500},
        {"name": "recency_half_life_1000", "type": "recency", "parameter": 1000},
        {"name": "recency_half_life_2000", "type": "recency", "parameter": 2000},
    ]


def normalized_recency_weights(sample_count: int, half_life: int) -> list[float]:
    """Return exponential weights with mean one and greatest weight on newest data."""
    if sample_count <= 0 or half_life <= 0:
        raise ValueError("Recency weighting requires positive sample count and half-life")
    raw = [2.0 ** (-(sample_count - 1 - index) / half_life) for index in range(sample_count)]
    scale = sample_count / sum(raw)
    return [value * scale for value in raw]


def prepare_history(
    features: list[list[float]],
    labels: list[int],
    strategy: dict[str, int | str | None],
) -> tuple[list[list[float]], list[int], list[float] | None, int]:
    """Apply one history strategy without changing chronological order."""
    if len(features) != len(labels) or not features:
        raise ValueError("History features and labels must be non-empty and aligned")
    strategy_type = str(strategy["type"])
    parameter = strategy["parameter"]
    if strategy_type == "expanding":
        return features, labels, None, 0
    if not isinstance(parameter, int) or parameter <= 0:
        raise ValueError("Rolling and recency strategies require a positive integer parameter")
    if strategy_type == "rolling":
        start = max(0, len(features) - parameter)
        return features[start:], labels[start:], None, start
    if strategy_type == "recency":
        return features, labels, normalized_recency_weights(len(features), parameter), 0
    raise ValueError(f"Unknown history strategy: {strategy_type}")


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
    features, labels = read_dataset(arguments.train)
    folds = build_expanding_folds(
        len(features), fold_count=arguments.folds, purge_bars=PURGE_BARS
    )

    strategy_results: list[dict[str, Any]] = []
    for strategy in strategy_specs():
        aggregate_actual: list[int] = []
        aggregate_predicted: list[int] = []
        fold_lengths: list[int] = []
        fold_reports: list[dict[str, Any]] = []
        for fold_index, (train_end, evaluation_start, evaluation_end) in enumerate(
            folds, start=1
        ):
            history_features = features[:train_end]
            history_labels = labels[:train_end]
            train_features, train_labels, sample_weights, history_start = prepare_history(
                history_features, history_labels, strategy
            )
            model = fresh_model(MODEL_CANDIDATE)
            model.fit(train_features, train_labels, sample_weight=sample_weights)
            evaluation_features = features[evaluation_start:evaluation_end]
            evaluation_labels = labels[evaluation_start:evaluation_end]
            predictions = predict_with_policy(
                model.predict_proba(evaluation_features).tolist(),
                [int(value) for value in model.classes_.tolist()],
                DECISION_POLICY,
            )
            metrics = evaluation_metrics(evaluation_labels, predictions)
            aggregate_actual.extend(evaluation_labels)
            aggregate_predicted.extend(predictions)
            fold_lengths.append(len(evaluation_labels))
            fold_reports.append({
                "fold": fold_index,
                "available_history_records": train_end,
                "training_start_index": history_start,
                "training_records": len(train_features),
                "purged_records": evaluation_start - train_end,
                "evaluation_records": len(evaluation_labels),
                "metrics": metrics,
                "gate_met": meets_evaluation_contract(metrics),
            })

        aggregate_metrics = evaluation_metrics(aggregate_actual, aggregate_predicted)
        per_fold_metrics = metrics_for_folds(
            aggregate_actual, aggregate_predicted, fold_lengths
        )
        folds_passing = sum(meets_evaluation_contract(metrics) for metrics in per_fold_metrics)
        strategy_results.append({
            "strategy": strategy,
            "aggregate_metrics": aggregate_metrics,
            "gate_floor_ratio": gate_floor_ratio(aggregate_metrics),
            "aggregate_gate_met": meets_evaluation_contract(aggregate_metrics),
            "folds_passing_gate": folds_passing,
            "stable_gate_met": (
                meets_evaluation_contract(aggregate_metrics) and folds_passing == len(folds)
            ),
            "folds": fold_reports,
        })

    ranked = sorted(
        strategy_results,
        key=lambda item: selection_key(
            item["aggregate_metrics"], int(item["folds_passing_gate"]), len(folds)
        ),
        reverse=True,
    )
    report = {
        "diagnostic_stage": "train_only_purged_history_strategy_comparison",
        "validation_dataset_used": False,
        "test_dataset_used": False,
        **contract_metadata(),
        "purge_bars": PURGE_BARS,
        "model_candidate": MODEL_CANDIDATE,
        "probability_variant": "raw",
        "decision_policy": DECISION_POLICY,
        "fold_count": len(folds),
        "comparison_control": "only_training_history_strategy_changes",
        "strategies_ranked": [item["strategy"]["name"] for item in ranked],
        "strategies": strategy_results,
        "best_diagnostic_strategy": ranked[0]["strategy"]["name"],
        "limitations": [
            "This controlled diagnostic reuses already-inspected Train Outer periods.",
            "It compares history strategies for one fixed raw model and argmax policy only.",
            "A better strategy here is a hypothesis, not unbiased deployment evidence.",
            "Validation and Test are not read and deployment remains unauthorized.",
        ],
    }
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({
        "diagnostic_stage": report["diagnostic_stage"],
        "validation_dataset_used": False,
        "test_dataset_used": False,
        "purge_bars": PURGE_BARS,
        "model_candidate": MODEL_CANDIDATE,
        "decision_policy": DECISION_POLICY,
        "strategies_ranked": report["strategies_ranked"],
        "results": [
            {
                "strategy": item["strategy"]["name"],
                "aggregate_metrics": item["aggregate_metrics"],
                "gate_floor_ratio": item["gate_floor_ratio"],
                "folds_passing_gate": item["folds_passing_gate"],
            }
            for item in ranked
        ],
        "diagnostic_file": str(arguments.output),
    }, indent=2))


if __name__ == "__main__":
    main()
