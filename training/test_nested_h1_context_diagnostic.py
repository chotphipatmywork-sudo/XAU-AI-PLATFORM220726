"""Focused checks for nested closed-H1 feature-set selection."""

from nested_h1_context_diagnostic import FEATURE_SETS, choose_feature_set


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
    if FEATURE_SETS != ("schema4_baseline", "schema4_plus_closed_h1"):
        raise AssertionError("Nested H1 feature-set boundary changed")
    candidates = [
        {"feature_set": FEATURE_SETS[0], "aggregate_metrics": metrics(0.40), "folds_passing_gate": 0},
        {"feature_set": FEATURE_SETS[1], "aggregate_metrics": metrics(0.46), "folds_passing_gate": 0},
    ]
    if choose_feature_set(candidates, 3)["feature_set"] != FEATURE_SETS[1]:
        raise AssertionError("Nested weakest-gate selection failed")
    print("Nested H1 context diagnostic test passed")


if __name__ == "__main__":
    main()
