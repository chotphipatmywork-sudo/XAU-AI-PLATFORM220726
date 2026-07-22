"""Focused checks for the Train-only walk-forward feature diagnostic."""

import numpy as np
from sklearn.ensemble import RandomForestClassifier

from train_classifier import FEATURE_COLUMNS
from walk_forward_feature_diagnostic import (
    PERMUTATION_GROUPS,
    aggregate_fold_importance,
    permutation_diagnostic,
)


def main() -> None:
    random = np.random.default_rng(42)
    matrix = random.normal(size=(360, len(FEATURE_COLUMNS)))
    matrix[:, 7] = np.where(np.arange(len(matrix)) % 3 == 0, 0.0,
                            np.where(np.arange(len(matrix)) % 3 == 1, 50.0, 100.0))
    session_index = np.arange(len(matrix)) % 3
    matrix[:, 8:11] = 0.0
    matrix[np.arange(len(matrix)), session_index + 8] = 100.0
    labels = np.where(matrix[:, 0] > 0.55, 1, np.where(matrix[:, 0] < -0.55, -1, 0)).tolist()
    features = matrix.tolist()
    model = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
    model.fit(features, labels)
    baseline, importance = permutation_diagnostic(
        model,
        features,
        labels,
        {"type": "argmax"},
        repeats=5,
    )
    if float(baseline["macro_f1"]) < 0.90:
        raise AssertionError(f"Synthetic baseline is unexpectedly weak: {baseline}")
    signal_drop = importance[FEATURE_COLUMNS[0]]["macro_f1"]["mean_drop"]
    noise_drop = importance[FEATURE_COLUMNS[1]]["macro_f1"]["mean_drop"]
    if signal_drop <= noise_drop or signal_drop <= 0.20:
        raise AssertionError("Permutation diagnostic did not rank the synthetic signal correctly")
    if "session_context" not in importance or any(name.startswith("session_") for name in importance if name != "session_context"):
        raise AssertionError("Session fields were not preserved as one permutation group")
    if PERMUTATION_GROUPS["session_context"] != (8, 9, 10, 11):
        raise AssertionError("Session permutation group does not match Feature Contract 4.0")
    aggregate = aggregate_fold_importance([importance, importance])
    if aggregate[FEATURE_COLUMNS[0]]["macro_f1"]["positive_folds"] != 2:
        raise AssertionError("Fold aggregation lost positive-fold stability")
    print("Walk-forward feature diagnostic test passed")


if __name__ == "__main__":
    main()
