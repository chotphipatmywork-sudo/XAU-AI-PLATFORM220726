"""Chronologically calibrate a classifier without future-fold leakage."""

from __future__ import annotations

from math import log
from typing import Any, Sequence

from sklearn.linear_model import LogisticRegression


class ChronologicalCalibratedClassifier:
    """Fit a base estimator first, then calibrate it on the following time block."""

    def __init__(
        self,
        estimator: Any,
        calibration_fraction: float = 0.20,
        purge_bars: int = 16,
    ) -> None:
        if calibration_fraction <= 0.0 or calibration_fraction >= 0.50:
            raise ValueError("calibration_fraction must be within 0..0.50")
        if purge_bars <= 0:
            raise ValueError("purge_bars must be positive")
        self.estimator = estimator
        self.calibration_fraction = calibration_fraction
        self.purge_bars = purge_bars
        self.calibrator = LogisticRegression(max_iter=2000, random_state=42)
        self.classes_: Any = None
        self.estimator_fit_end_: int | None = None
        self.calibration_start_: int | None = None

    @staticmethod
    def _log_probabilities(probabilities: Sequence[Sequence[float]]) -> list[list[float]]:
        return [[log(max(float(value), 1.0e-12)) for value in row] for row in probabilities]

    def fit(self, features: Sequence[Sequence[float]], labels: Sequence[int]) -> "ChronologicalCalibratedClassifier":
        if len(features) != len(labels) or len(features) < 30:
            raise ValueError("Calibration requires aligned data with at least 30 samples")
        calibration_start = int(len(features) * (1.0 - self.calibration_fraction))
        estimator_fit_end = calibration_start - self.purge_bars
        if estimator_fit_end < 30 or len(features) - calibration_start < 3:
            raise ValueError("Insufficient samples after the calibration purge")
        fit_labels = list(labels[:estimator_fit_end])
        calibration_labels = list(labels[calibration_start:])
        if len(set(fit_labels)) < 3 or len(set(calibration_labels)) < 3:
            raise ValueError("Fit and calibration blocks must each contain SELL, HOLD, and BUY")

        self.estimator.fit(features[:estimator_fit_end], fit_labels)
        raw_probability = self.estimator.predict_proba(features[calibration_start:])
        self.calibrator.fit(self._log_probabilities(raw_probability), calibration_labels)
        self.classes_ = self.calibrator.classes_
        self.estimator_fit_end_ = estimator_fit_end
        self.calibration_start_ = calibration_start
        return self

    def predict_proba(self, features: Sequence[Sequence[float]]) -> Any:
        if self.classes_ is None:
            raise RuntimeError("Calibrated classifier is not fitted")
        raw_probability = self.estimator.predict_proba(features)
        return self.calibrator.predict_proba(self._log_probabilities(raw_probability))

    def predict(self, features: Sequence[Sequence[float]]) -> list[int]:
        probability = self.predict_proba(features)
        return [int(self.classes_[row.argmax()]) for row in probability]
