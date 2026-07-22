"""Focused checks for the Schema 4.0 Session Progress ablation."""

from schema4_session_progress_ablation import (
    FEATURE_SETS,
    choose_feature_set,
    transform_feature_set,
)


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
    if FEATURE_SETS != {
        "without_session_progress": False,
        "with_session_progress": True,
    }:
        raise AssertionError("Schema 4.0 ablation boundary changed")

    row = [float(index) for index in range(12)]
    if transform_feature_set([row], True) != [row]:
        raise AssertionError("Full Schema 4.0 tensor changed")
    if transform_feature_set([row], False) != [row[:-1]]:
        raise AssertionError("Ablation did not remove only Session Progress")

    candidates = [
        {
            "feature_set": "without_session_progress",
            "aggregate_metrics": metrics(0.40, 0.42),
            "folds_passing_gate": 0,
        },
        {
            "feature_set": "with_session_progress",
            "aggregate_metrics": metrics(0.46, 0.41),
            "folds_passing_gate": 0,
        },
    ]
    selected = choose_feature_set(candidates, fold_count=3)
    if selected["feature_set"] != "with_session_progress":
        raise AssertionError("Selection did not improve the weakest gate metric")
    print("Schema 4.0 Session Progress ablation test passed")


if __name__ == "__main__":
    main()
