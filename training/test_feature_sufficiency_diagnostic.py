"""Focused tests for the Train-only feature sufficiency diagnostic."""

from feature_sufficiency_diagnostic import (
    contract_metadata,
    evaluate_neighbourhood,
    feature_groups,
    majority_label,
    normalized_entropy,
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
        raise AssertionError(f"Feature sufficiency contract metadata is stale: {metadata}")

    if normalized_entropy([25, 0, 0]) != 0.0:
        raise AssertionError("Pure labels must have zero entropy")
    if abs(normalized_entropy([10, 10, 10]) - 1.0) > 1e-12:
        raise AssertionError("Uniform labels must have maximum normalized entropy")
    if majority_label([3, 3, 1]) != -1:
        raise AssertionError("Label ties must use canonical deterministic order")

    groups = feature_groups()
    if groups["full_schema"] != list(range(12)) or groups["session_group"] != [8, 9, 10, 11]:
        raise AssertionError("Feature Schema 4.0 diagnostic groups changed")

    train_features = [[float(index), 0.0] for index in range(30)]
    train_labels = [-1] * 15 + [1] * 15
    evaluation_features = [[1.5, 0.0], [27.5, 0.0]]
    evaluation_labels = [-1, 1]
    result = evaluate_neighbourhood(
        train_features,
        train_labels,
        evaluation_features,
        evaluation_labels,
        [0],
        neighbours=5,
    )
    if result["mean_true_label_support"] < 0.99:
        raise AssertionError("Separated local labels should have high true-label support")
    if result["nearest_label_match_rate"] != 1.0:
        raise AssertionError("Nearest past labels should match the synthetic evaluation labels")
    if result["majority_vote_metrics"]["accuracy"] != 1.0:
        raise AssertionError("Synthetic local majority vote should be exact")

    print("Feature sufficiency diagnostic test passed")


if __name__ == "__main__":
    main()
