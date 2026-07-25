"""Focused checks for canonical Setup response attribution."""

from __future__ import annotations

from canonical_setup_response_attribution import (
    READINESS_GATE,
    RESPONSE_CLASSES,
    economic_summary,
    evaluate_neighbourhood,
    feature_groups,
    majority_class,
    normalized_entropy,
    readiness,
)


def main() -> None:
    groups = feature_groups()
    if groups != {
        "full_schema": tuple(range(12)),
        "trend_group": (0, 1, 2),
        "volatility_group": (3, 4),
        "liquidity_group": (5, 6, 7),
        "session_group": (8, 9, 10, 11),
    }:
        raise AssertionError("Canonical Setup feature groups changed")
    if normalized_entropy([15, 0, 0, 0]) != 0.0 or abs(
        normalized_entropy([5, 5, 5, 5])-1.0
    ) > 1e-12:
        raise AssertionError("Canonical Setup entropy changed")
    if majority_class([2, 2, 1, 0]) != 0:
        raise AssertionError("Canonical Setup class tie order changed")

    train_features: list[list[float]] = []
    train_labels: list[int] = []
    evaluation_features: list[list[float]] = []
    evaluation_labels: list[int] = []
    for label in range(4):
        for offset in range(10):
            train_features.append([label*20.0+offset*0.01, 0.0])
            train_labels.append(label)
        evaluation_features.append([label*20.0+0.05, 0.0])
        evaluation_labels.append(label)
    report, predicted = evaluate_neighbourhood(
        train_features, train_labels, evaluation_features, evaluation_labels,
        (0,), neighbours=5,
    )
    if predicted != evaluation_labels or report["classification"]["macro_f1"] != 1.0:
        raise AssertionError("Canonical Setup separable neighbourhood changed")
    gates = readiness(report, READINESS_GATE["positive_support_gain_folds"])
    if not gates["hypothesis_ready"]:
        raise AssertionError("Canonical Setup synthetic readiness should pass")

    records = [
        {
            "response_class": "TARGET_PRESERVED",
            "baseline_r": 2.0,
            "candidate_r": 2.0,
            "delta_r": 0.0,
        },
        {
            "response_class": "TARGET_CLIPPED_BY_MANAGEMENT",
            "baseline_r": 2.0,
            "candidate_r": 0.0,
            "delta_r": -2.0,
        },
        {
            "response_class": "STOP_LOSS_IMPROVED_BY_MANAGEMENT",
            "baseline_r": -1.0,
            "candidate_r": 0.0,
            "delta_r": 1.0,
        },
        {
            "response_class": "STOP_UNCHANGED",
            "baseline_r": -1.0,
            "candidate_r": -1.0,
            "delta_r": 0.0,
        },
    ]
    summary = economic_summary(records)
    if summary["baseline_target_rate"] != 0.5 or (
        summary["target_preservation_rate"] != 0.5
    ) or summary["stop_improvement_rate"] != 0.5 or summary["net_delta_r"] != -1.0:
        raise AssertionError("Canonical Setup bucket accounting changed")
    if tuple(summary["response_counts"]) != RESPONSE_CLASSES:
        raise AssertionError("Canonical Setup response order changed")

    print("Canonical Setup response attribution test passed")


if __name__ == "__main__":
    main()
