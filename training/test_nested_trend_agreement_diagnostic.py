"""Focused checks for nested Baseline-vs-Agreements selection."""

from nested_trend_agreement_diagnostic import FEATURE_SETS, choose_feature_set


def metrics(buy_precision: float, macro_f1: float) -> dict[str, float | int]:
    return {
        "sample_count": 500,
        "accuracy": 0.46,
        "macro_f1": macro_f1,
        "sell_precision": 0.52,
        "sell_recall": 0.40,
        "hold_precision": 0.30,
        "hold_recall": 0.35,
        "buy_precision": buy_precision,
        "buy_recall": 0.35,
    }


def main() -> None:
    if FEATURE_SETS != {"baseline": [], "trend_agreements": [1, 2, 3]}:
        raise AssertionError("Nested feature-set boundary changed unexpectedly")
    candidates = [
        {
            "feature_set": "baseline",
            "aggregate_metrics": metrics(0.40, 0.42),
            "folds_passing_gate": 0,
        },
        {
            "feature_set": "trend_agreements",
            "aggregate_metrics": metrics(0.46, 0.41),
            "folds_passing_gate": 0,
        },
    ]
    selected = choose_feature_set(candidates, fold_count=3)
    if selected["feature_set"] != "trend_agreements":
        raise AssertionError("Nested selection did not improve the weakest gate metric")
    print("Nested Trend agreement diagnostic test passed")


if __name__ == "__main__":
    main()
