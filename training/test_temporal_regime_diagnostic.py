"""Focused checks for temporal regime drift helpers."""

from temporal_regime_diagnostic import (
    contract_metadata,
    normalized_distribution,
    numeric_bucket,
    segment_metrics,
    standardized_mean_difference,
)
from train_classifier import (
    FEATURE_SCHEMA_VERSION,
    LABEL_SCHEMA_VERSION,
    TRAINING_CONTRACT_VERSION,
)


def main() -> None:
    metadata = contract_metadata()
    if metadata != {
        "training_contract_version": TRAINING_CONTRACT_VERSION,
        "feature_schema_version": FEATURE_SCHEMA_VERSION,
        "label_schema_version": LABEL_SCHEMA_VERSION,
    }:
        raise AssertionError(f"Diagnostic contract metadata is stale: {metadata}")

    shift = standardized_mean_difference([0.0, 1.0, 2.0], [2.0, 3.0, 4.0])
    if shift <= 1.0:
        raise AssertionError(f"Expected a material positive standardized shift: {shift}")
    if standardized_mean_difference([5.0, 5.0], [5.0, 5.0]) != 0.0:
        raise AssertionError("Constant identical blocks should have zero shift")

    distribution = normalized_distribution([-1, -1, 0, 1])
    if distribution != {"SELL": 0.5, "HOLD": 0.25, "BUY": 0.25}:
        raise AssertionError(f"Unexpected fixed class distribution: {distribution}")
    if [numeric_bucket(value) for value in (0.0, 50.0, 100.0)] != [
        "low", "middle", "high"
    ]:
        raise AssertionError("Numeric regime bucketing is incorrect")

    metrics = segment_metrics(
        [-1, 1, 0, 1],
        [-1, 0, 0, 1],
        ["ASIA", "ASIA", "LONDON", "LONDON"],
    )
    if metrics["ASIA"]["sample_count"] != 2 or metrics["LONDON"]["sample_count"] != 2:
        raise AssertionError("Segment metrics lost rows")
    print("Temporal regime diagnostic test passed")


if __name__ == "__main__":
    main()
