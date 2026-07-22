"""Focused checks for nested Baseline-vs-past-Trend-change selection."""

from nested_trend_dynamics_diagnostic import FEATURE_SETS, choose_feature_set


def metrics(buy_precision: float) -> dict[str, float | int]:
    return {
        "sample_count": 500,
        "accuracy": 0.46,
        "macro_f1": 0.41,
        "sell_precision": 0.52,
        "sell_recall": 0.40,
        "hold_precision": 0.30,
        "hold_recall": 0.35,
        "buy_precision": buy_precision,
        "buy_recall": 0.35,
    }


def main() -> None:
    if FEATURE_SETS != {
        "baseline": [],
        "trend_change_only": [0, 1, 2, 3, 4, 5, 6],
    }:
        raise AssertionError("Nested Trend dynamics boundary changed unexpectedly")
    selected = choose_feature_set([
        {"feature_set": "baseline", "aggregate_metrics": metrics(0.40), "folds_passing_gate": 0},
        {"feature_set": "trend_change_only", "aggregate_metrics": metrics(0.45), "folds_passing_gate": 0},
    ], fold_count=3)
    if selected["feature_set"] != "trend_change_only":
        raise AssertionError("Nested selection ignored stronger past-only dynamics")
    print("Nested Trend dynamics diagnostic test passed")


if __name__ == "__main__":
    main()
