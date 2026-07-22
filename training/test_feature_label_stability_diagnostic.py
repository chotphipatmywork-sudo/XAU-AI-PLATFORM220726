"""Focused checks for feature-to-label relationship stability helpers."""

from feature_label_stability_diagnostic import (
    bucket_label_distribution,
    contract_metadata,
    feature_specs,
    jensen_shannon_divergence,
    relationship_summary,
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
        raise AssertionError(f"Feature-label diagnostic contract metadata is stale: {metadata}")
    if "session_progress" not in [name for name, _, _ in feature_specs()]:
        raise AssertionError("Active Session Progress feature is missing from stability analysis")

    stable = {"SELL": 0.5, "HOLD": 0.1, "BUY": 0.4}
    reversed_distribution = {"SELL": 0.2, "HOLD": 0.1, "BUY": 0.7}
    if jensen_shannon_divergence(stable, stable) != 0.0:
        raise AssertionError("Identical label distributions should have zero divergence")
    if jensen_shannon_divergence(stable, reversed_distribution) <= 0.05:
        raise AssertionError("Material label-distribution drift was not detected")

    features = [[10.0], [20.0], [80.0], [90.0]]
    labels = [-1, -1, 1, 1]
    buckets = bucket_label_distribution(
        features,
        labels,
        lambda row: "low" if row[0] < 50.0 else "high",
    )
    if buckets["low"]["label_distribution"]["SELL"] != 1.0:
        raise AssertionError("Low bucket labels are incorrect")
    if buckets["high"]["label_distribution"]["BUY"] != 1.0:
        raise AssertionError("High bucket labels are incorrect")

    fold_buckets = []
    for fold in range(4):
        low_buy = 5 if fold < 2 else 25
        high_buy = 25 if fold < 2 else 5
        fold_buckets.append({
            "low": {
                "sample_count": 40,
                "label_distribution": {
                    "SELL": (35 - low_buy) / 40,
                    "HOLD": 5 / 40,
                    "BUY": low_buy / 40,
                },
            },
            "high": {
                "sample_count": 40,
                "label_distribution": {
                    "SELL": (35 - high_buy) / 40,
                    "HOLD": 5 / 40,
                    "BUY": high_buy / 40,
                },
            },
        })
    summary = relationship_summary(fold_buckets, ordered=True)
    if not summary["directional_sign_changed"]:
        raise AssertionError("Directional feature-label reversal was not detected")
    if summary["positive_directional_folds"] != 2 or summary["negative_directional_folds"] != 2:
        raise AssertionError("Directional fold signs are incorrect")
    print("Feature-label stability diagnostic test passed")


if __name__ == "__main__":
    main()
