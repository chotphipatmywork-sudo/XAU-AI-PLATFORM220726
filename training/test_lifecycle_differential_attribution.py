"""Focused checks for paired lifecycle differential attribution."""

from __future__ import annotations

from diagnose_lifecycle_differential_attribution import (
    attribute_transition,
    summarize,
)


def result(outcome: str, realized_r: float | None) -> dict:
    return {"outcome": outcome, "realized_r": realized_r}


def record(
    baseline_outcome: str,
    candidate_outcome: str,
    baseline_r: float,
    candidate_r: float | None,
) -> dict:
    attributed = attribute_transition(
        result(baseline_outcome, baseline_r),
        result(candidate_outcome, candidate_r),
    )
    return {
        "baseline_outcome": baseline_outcome,
        "candidate_outcome": candidate_outcome,
        **attributed,
    }


def main() -> None:
    records = [
        record("TARGET_FIRST", "TARGET_FIRST", 2.0, 2.0),
        record("TARGET_FIRST", "MANAGED_STOP", 2.0, 0.0),
        record("STOP_FIRST", "MANAGED_STOP", -1.0, 0.0),
        record("STOP_FIRST", "STOP_FIRST", -1.0, -1.0),
        record("TARGET_FIRST", "AMBIGUOUS", 2.0, None),
    ]
    summary = summarize(records)
    if summary["effective_paired_records"] != 4 or (
        summary["ambiguous_quarantined"] != 1
    ):
        raise AssertionError("Lifecycle attribution paired accounting changed")
    if summary["positive_delta_r"] != 1.0 or summary["negative_delta_r"] != -2.0:
        raise AssertionError("Lifecycle attribution benefit/harm changed")
    if summary["net_delta_r"] != -1.0 or summary["mean_delta_r"] != -0.25:
        raise AssertionError("Lifecycle attribution net Delta changed")
    if summary["categories"]["TARGET_CLIPPED_BY_MANAGEMENT"] != 1 or (
        summary["categories"]["STOP_LOSS_IMPROVED_BY_MANAGEMENT"] != 1
    ):
        raise AssertionError("Lifecycle attribution categories changed")

    invalid = (
        ("TARGET_FIRST", "STOP_FIRST", 2.0, -1.0, "transition is invalid"),
        ("TARGET_FIRST", "MANAGED_STOP", 2.0, 2.1, "non-negative Delta R"),
        ("STOP_FIRST", "MANAGED_STOP", -1.0, -1.1, "non-positive Delta R"),
    )
    for baseline, candidate, baseline_r, candidate_r, expected in invalid:
        try:
            record(baseline, candidate, baseline_r, candidate_r)
        except ValueError as error:
            if expected not in str(error):
                raise
        else:
            raise AssertionError("Lifecycle attribution accepted invalid transition")

    print("Lifecycle differential attribution test passed")


if __name__ == "__main__":
    main()

