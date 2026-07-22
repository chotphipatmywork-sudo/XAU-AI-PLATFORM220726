"""Focused tests for confidence-versus-coverage reporting."""

from confidence_coverage_diagnostic import (
    CONFIDENCE_THRESHOLDS,
    contract_metadata,
    confidence_policy,
    prediction_counts,
    threshold_report,
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
        raise AssertionError(f"Confidence diagnostic contract metadata is stale: {metadata}")

    if CONFIDENCE_THRESHOLDS != (0.34, 0.38, 0.42, 0.46, 0.50, 0.55, 0.60, 0.65, 0.70):
        raise AssertionError("Diagnostic threshold grid changed")
    policy = confidence_policy(0.50)
    if policy != {"type": "confidence", "sell_minimum": 0.5, "buy_minimum": 0.5, "margin": 0.0}:
        raise AssertionError("Symmetric confidence policy changed")
    if prediction_counts([-1, -1, 0, 1]) != {"SELL": 2, "HOLD": 1, "BUY": 1}:
        raise AssertionError("Prediction counts do not follow the canonical label map")

    actual = [-1] * 25 + [1] * 25
    predicted = list(actual)
    report = threshold_report(actual, predicted)
    if report["directional_coverage"] != 1.0:
        raise AssertionError("All-directional predictions must have full coverage")
    if not report["directional_precision_supported"]:
        raise AssertionError("Synthetic directional counts should satisfy the support floor")
    if not report["directional_precision_gate_met"]:
        raise AssertionError("Exact synthetic predictions should pass the precision gate")

    print("Confidence coverage diagnostic test passed")


if __name__ == "__main__":
    main()
