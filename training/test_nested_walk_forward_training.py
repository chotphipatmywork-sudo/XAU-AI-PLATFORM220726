"""Focused checks for nested purged selection helpers."""

from nested_walk_forward_select import (
    gate_floor_ratio,
    nested_candidate_policies,
    selection_key,
)
from select_candidate import predict_with_policy
from walk_forward_select import build_expanding_folds


def main() -> None:
    outer = build_expanding_folds(1000, fold_count=4, purge_bars=16)
    if any(start - train_end != 16 for train_end, start, _ in outer):
        raise AssertionError("Outer fold does not purge 16 bars")
    first_inner = build_expanding_folds(outer[0][0], fold_count=3, purge_bars=16)
    if any(start - train_end != 16 for train_end, start, _ in first_inner):
        raise AssertionError("Inner fold does not purge 16 bars")

    policies = nested_candidate_policies()
    if len(policies) != 31 or len({name for name, _ in policies}) != len(policies):
        raise AssertionError("Unexpected or duplicate nested policy grid")
    strict_buy = next(policy for name, policy in policies if "buy_0_60_margin_0_05" in name)
    predicted = predict_with_policy(
        [[0.20, 0.25, 0.55], [0.15, 0.20, 0.65]],
        [-1, 0, 1],
        strict_buy,
    )
    if predicted != [0, 1]:
        raise AssertionError(f"Asymmetric BUY threshold is incorrect: {predicted}")

    weak_buy = {
        "sample_count": 500,
        "accuracy": 0.46,
        "macro_f1": 0.41,
        "sell_precision": 0.52,
        "sell_recall": 0.40,
        "hold_precision": 0.30,
        "hold_recall": 0.35,
        "buy_precision": 0.40,
        "buy_recall": 0.40,
    }
    balanced = dict(weak_buy, buy_precision=0.46, buy_recall=0.34)
    if gate_floor_ratio(balanced) <= gate_floor_ratio(weak_buy):
        raise AssertionError("Gate-floor ranking did not reward the stronger weakest metric")
    if selection_key(balanced, 0, 3) <= selection_key(weak_buy, 0, 3):
        raise AssertionError("Nested selection key ignored gate balance")

    print("Nested purged walk-forward training test passed")


if __name__ == "__main__":
    main()
