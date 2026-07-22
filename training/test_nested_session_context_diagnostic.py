"""Focused checks for nested Baseline-vs-Session-Progress selection."""

from nested_session_context_diagnostic import FEATURE_SETS, choose_feature_set


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
    if FEATURE_SETS != {"baseline": False, "session_progress": True}:
        raise AssertionError("Nested Session feature-set boundary changed")
    candidates = [
        {
            "feature_set": "baseline",
            "aggregate_metrics": metrics(0.40, 0.42),
            "folds_passing_gate": 0,
        },
        {
            "feature_set": "session_progress",
            "aggregate_metrics": metrics(0.46, 0.41),
            "folds_passing_gate": 0,
        },
    ]
    selected = choose_feature_set(candidates, fold_count=3)
    if selected["feature_set"] != "session_progress":
        raise AssertionError("Nested selection did not improve the weakest gate metric")
    print("Nested Session context diagnostic test passed")


if __name__ == "__main__":
    main()
