"""Focused checks for controlled history strategies."""

from history_strategy_diagnostic import (
    contract_metadata,
    normalized_recency_weights,
    prepare_history,
    strategy_specs,
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
        raise AssertionError(f"History diagnostic contract metadata is stale: {metadata}")

    features = [[float(index)] for index in range(20)]
    labels = [index % 3 - 1 for index in range(20)]
    rolling = next(item for item in strategy_specs() if item["name"] == "rolling_1000")
    small_rolling = dict(rolling, parameter=5)
    selected_features, selected_labels, weights, start = prepare_history(
        features, labels, small_rolling
    )
    if selected_features != features[-5:] or selected_labels != labels[-5:] or start != 15:
        raise AssertionError("Rolling history did not retain the newest records")
    if weights is not None:
        raise AssertionError("Rolling history unexpectedly created sample weights")

    recency = normalized_recency_weights(100, 20)
    if recency[0] >= recency[-1]:
        raise AssertionError("Recency weights do not favor newer records")
    if abs(sum(recency) / len(recency) - 1.0) > 1.0e-12:
        raise AssertionError("Recency weights do not have mean one")
    if len(strategy_specs()) != 7:
        raise AssertionError("Unexpected controlled history strategy grid")
    print("History strategy diagnostic test passed")


if __name__ == "__main__":
    main()
