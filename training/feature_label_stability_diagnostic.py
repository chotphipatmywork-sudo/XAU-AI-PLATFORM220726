"""Measure Train-only feature-to-label relationship stability across Outer periods."""

from __future__ import annotations

import argparse
import json
from itertools import combinations
from math import log2
from pathlib import Path
from statistics import fmean
from typing import Any, Callable, Sequence

from temporal_regime_diagnostic import normalized_distribution, numeric_bucket, session_name
from train_classifier import (
    FEATURE_SCHEMA_VERSION,
    LABEL_SCHEMA_VERSION,
    TRAINING_CONTRACT_VERSION,
    read_dataset,
)


MINIMUM_BUCKET_SAMPLES = 30
MINIMUM_FOLDS = 3


def contract_metadata() -> dict[str, str]:
    """Return the active training, feature, and label contract versions."""
    return {
        "training_contract_version": TRAINING_CONTRACT_VERSION,
        "feature_schema_version": FEATURE_SCHEMA_VERSION,
        "label_schema_version": LABEL_SCHEMA_VERSION,
    }


def sweep_bucket(value: float) -> str:
    if value == 0.0:
        return "down"
    if value == 50.0:
        return "neutral"
    if value == 100.0:
        return "up"
    raise ValueError(f"Unexpected liquidity sweep direction: {value}")


def jensen_shannon_divergence(
    left: dict[str, float],
    right: dict[str, float],
) -> float:
    """Return bounded base-2 divergence for fixed class distributions."""
    keys = sorted(set(left) | set(right))
    midpoint = {key: (left.get(key, 0.0) + right.get(key, 0.0)) / 2.0 for key in keys}

    def divergence(source: dict[str, float]) -> float:
        return sum(
            value * log2(value / midpoint[key])
            for key, value in source.items()
            if value > 0.0 and midpoint[key] > 0.0
        )

    return 0.5 * divergence(left) + 0.5 * divergence(right)


def bucket_label_distribution(
    features: Sequence[Sequence[float]],
    labels: Sequence[int],
    bucketer: Callable[[Sequence[float]], str],
) -> dict[str, dict[str, Any]]:
    """Return sample counts and SELL/HOLD/BUY ratios for every feature bucket."""
    grouped: dict[str, list[int]] = {}
    for row, label in zip(features, labels):
        grouped.setdefault(bucketer(row), []).append(int(label))
    return {
        bucket: {
            "sample_count": len(bucket_labels),
            "label_distribution": normalized_distribution(bucket_labels),
        }
        for bucket, bucket_labels in sorted(grouped.items())
    }


def relationship_summary(
    fold_buckets: list[dict[str, dict[str, Any]]],
    ordered: bool,
) -> dict[str, Any]:
    """Summarize cross-fold class-distribution drift for one feature."""
    bucket_names = sorted(set().union(*(fold.keys() for fold in fold_buckets)))
    bucket_reports: dict[str, dict[str, Any]] = {}
    weighted_divergences: list[tuple[float, int]] = []
    max_buy_range = 0.0
    for bucket in bucket_names:
        eligible = [
            (fold_index + 1, fold[bucket])
            for fold_index, fold in enumerate(fold_buckets)
            if bucket in fold and int(fold[bucket]["sample_count"]) >= MINIMUM_BUCKET_SAMPLES
        ]
        if len(eligible) < MINIMUM_FOLDS:
            bucket_reports[bucket] = {
                "eligible": False,
                "eligible_folds": len(eligible),
            }
            continue
        divergences = [
            jensen_shannon_divergence(
                left["label_distribution"], right["label_distribution"]
            )
            for (_, left), (_, right) in combinations(eligible, 2)
        ]
        buy_rates = [float(item["label_distribution"]["BUY"]) for _, item in eligible]
        sell_rates = [float(item["label_distribution"]["SELL"]) for _, item in eligible]
        dominant_labels = [
            max(item["label_distribution"], key=item["label_distribution"].get)
            for _, item in eligible
        ]
        mean_divergence = fmean(divergences)
        total_samples = sum(int(item["sample_count"]) for _, item in eligible)
        weighted_divergences.append((mean_divergence, total_samples))
        buy_range = max(buy_rates) - min(buy_rates)
        max_buy_range = max(max_buy_range, buy_range)
        bucket_reports[bucket] = {
            "eligible": True,
            "eligible_folds": len(eligible),
            "total_samples": total_samples,
            "mean_pairwise_js_divergence": mean_divergence,
            "maximum_pairwise_js_divergence": max(divergences),
            "buy_rate_range": buy_range,
            "sell_rate_range": max(sell_rates) - min(sell_rates),
            "dominant_labels_by_fold": dominant_labels,
            "dominant_label_changed": len(set(dominant_labels)) > 1,
        }

    if weighted_divergences:
        total_weight = sum(weight for _, weight in weighted_divergences)
        weighted_mean = sum(value * weight for value, weight in weighted_divergences) / total_weight
    else:
        weighted_mean = 0.0

    directional_spreads: list[dict[str, float | int]] = []
    if ordered:
        for fold_index, fold in enumerate(fold_buckets, start=1):
            if (
                "low" in fold
                and "high" in fold
                and int(fold["low"]["sample_count"]) >= MINIMUM_BUCKET_SAMPLES
                and int(fold["high"]["sample_count"]) >= MINIMUM_BUCKET_SAMPLES
            ):
                spread = (
                    float(fold["high"]["label_distribution"]["BUY"])
                    - float(fold["low"]["label_distribution"]["BUY"])
                )
                directional_spreads.append({"fold": fold_index, "buy_high_minus_low": spread})
    signs = [1 if item["buy_high_minus_low"] > 0.0 else -1 if item["buy_high_minus_low"] < 0.0 else 0
             for item in directional_spreads]
    return {
        "weighted_mean_pairwise_js_divergence": weighted_mean,
        "maximum_bucket_buy_rate_range": max_buy_range,
        "eligible_bucket_count": sum(bool(item.get("eligible")) for item in bucket_reports.values()),
        "buckets": bucket_reports,
        "directional_buy_spread_by_fold": directional_spreads,
        "directional_sign_changed": len(set(signs)) > 1 if signs else False,
        "positive_directional_folds": sum(sign > 0 for sign in signs),
        "negative_directional_folds": sum(sign < 0 for sign in signs),
    }


def feature_specs() -> list[tuple[str, Callable[[Sequence[float]], str], bool]]:
    """Return active approved dimensions with stable categorical buckets."""
    return [
        ("trend_regime", lambda row: numeric_bucket(float(row[0])), True),
        ("trend_momentum", lambda row: numeric_bucket(float(row[1])), True),
        ("trend_slope", lambda row: numeric_bucket(float(row[2])), True),
        ("volatility_regime", lambda row: numeric_bucket(float(row[3])), True),
        ("volatility_change", lambda row: numeric_bucket(float(row[4])), True),
        ("liquidity_activity", lambda row: numeric_bucket(float(row[5])), True),
        ("liquidity_range_position", lambda row: numeric_bucket(float(row[6])), True),
        ("liquidity_sweep_direction", lambda row: sweep_bucket(float(row[7])), False),
        ("session", session_name, False),
        ("session_progress", lambda row: numeric_bucket(float(row[11])), True),
    ]


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", required=True, type=Path)
    parser.add_argument("--nested-report", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()
    nested = json.loads(arguments.nested_report.read_text(encoding="utf-8"))
    if nested.get("selection_stage") != "train_internal_nested_purged_walk_forward_only":
        raise ValueError("Feature-label diagnostic requires a nested Train-only report")
    if nested.get("validation_dataset_used") or nested.get("test_dataset_used"):
        raise ValueError("Nested report is not Train-only")
    if int(nested.get("purge_bars", 0)) != 16:
        raise ValueError("Feature-label diagnostic requires the approved 16-bar purge")

    features, labels = read_dataset(arguments.train)
    periods: list[tuple[list[list[float]], list[int]]] = []
    period_boundaries: list[dict[str, int]] = []
    for outer in nested["outer_folds"]:
        start = int(outer["evaluation_start"])
        end = int(outer["evaluation_end"])
        periods.append((features[start:end], labels[start:end]))
        period_boundaries.append({
            "fold": int(outer["fold"]),
            "start_index": start,
            "end_index": end,
            "records": end - start,
        })

    feature_reports: dict[str, dict[str, Any]] = {}
    fold_bucket_details: dict[str, list[dict[str, dict[str, Any]]]] = {}
    for feature_name, bucketer, ordered in feature_specs():
        fold_buckets = [
            bucket_label_distribution(period_features, period_labels, bucketer)
            for period_features, period_labels in periods
        ]
        fold_bucket_details[feature_name] = fold_buckets
        feature_reports[feature_name] = relationship_summary(fold_buckets, ordered)

    ranked = sorted(
        feature_reports,
        key=lambda name: feature_reports[name]["weighted_mean_pairwise_js_divergence"],
        reverse=True,
    )
    report = {
        "diagnostic_stage": "train_only_outer_feature_label_stability",
        "validation_dataset_used": False,
        "test_dataset_used": False,
        **contract_metadata(),
        "purge_bars": 16,
        "minimum_bucket_samples": MINIMUM_BUCKET_SAMPLES,
        "minimum_eligible_folds": MINIMUM_FOLDS,
        "periods": period_boundaries,
        "features_ranked_by_label_relationship_instability": ranked,
        "feature_relationship_summary": feature_reports,
        "fold_bucket_details": fold_bucket_details,
        "limitations": [
            "The diagnostic reuses already-inspected non-overlapping Train Outer periods.",
            "Fixed buckets simplify continuous relationships and can hide within-bucket effects.",
            "Jensen-Shannon divergence measures association drift, not causality.",
            "Validation and Test are not read and deployment remains unauthorized.",
        ],
    }
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({
        "diagnostic_stage": report["diagnostic_stage"],
        "validation_dataset_used": False,
        "test_dataset_used": False,
        "period_count": len(periods),
        "features_ranked_by_label_relationship_instability": ranked,
        "summary": [
            {
                "feature": name,
                "weighted_mean_pairwise_js_divergence": feature_reports[name][
                    "weighted_mean_pairwise_js_divergence"
                ],
                "maximum_bucket_buy_rate_range": feature_reports[name][
                    "maximum_bucket_buy_rate_range"
                ],
                "directional_sign_changed": feature_reports[name]["directional_sign_changed"],
                "positive_directional_folds": feature_reports[name]["positive_directional_folds"],
                "negative_directional_folds": feature_reports[name]["negative_directional_folds"],
            }
            for name in ranked
        ],
        "diagnostic_file": str(arguments.output),
    }, indent=2))


if __name__ == "__main__":
    main()
