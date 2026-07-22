"""Focused checks for expanding folds and chronological calibration."""

from sklearn.linear_model import LogisticRegression

from chronological_calibrated_classifier import ChronologicalCalibratedClassifier
from walk_forward_select import build_expanding_folds


def main() -> None:
    folds = build_expanding_folds(100, 4)
    if folds != [(34, 50, 62), (46, 62, 74), (58, 74, 86), (70, 86, 100)]:
        raise AssertionError(f"Unexpected walk-forward folds: {folds}")
    if any(evaluation_start - train_end != 16 for train_end, evaluation_start, _ in folds):
        raise AssertionError("A walk-forward fold does not purge the 16-bar label horizon")

    features = [[float(index % 11), float((index * 3) % 17)] for index in range(180)]
    labels = [(-1, 0, 1)[index % 3] for index in range(180)]
    model = ChronologicalCalibratedClassifier(LogisticRegression(max_iter=1000, random_state=42))
    model.fit(features, labels)
    if model.calibration_start_ is None or model.estimator_fit_end_ is None:
        raise AssertionError("Calibration boundaries were not recorded")
    if model.calibration_start_ - model.estimator_fit_end_ != 16:
        raise AssertionError("Calibration does not purge the 16-bar label horizon")
    probabilities = model.predict_proba(features[-10:])
    if len(probabilities) != 10:
        raise AssertionError("Calibrated classifier returned the wrong row count")
    if any(abs(float(sum(row)) - 1.0) > 0.000001 for row in probabilities):
        raise AssertionError("Calibrated probabilities do not sum to one")

    print("Walk-forward training test passed")


if __name__ == "__main__":
    main()
