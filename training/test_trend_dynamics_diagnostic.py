"""Focused checks for leakage-free past-only Trend dynamics."""

from trend_dynamics_diagnostic import (
    bounded_delta,
    derive_trend_dynamics,
    feature_set_specs,
    transform_features,
)


def row(regime: float, momentum: float, slope: float) -> list[float]:
    return [regime, momentum, slope, *([50.0] * 8)]


def main() -> None:
    if bounded_delta(100.0, 0.0) != 100.0 or bounded_delta(0.0, 100.0) != 0.0:
        raise AssertionError("Bounded Trend delta endpoints are incorrect")
    features = [row(40.0 + index, 45.0 + index, 48.0 + index) for index in range(20)]
    dynamics = derive_trend_dynamics(features)
    if dynamics[0][:7] != [50.0] * 7:
        raise AssertionError("Unavailable early lookbacks must remain neutral")
    if dynamics[8][2] <= 50.0:
        raise AssertionError("Eight-record Regime increase was not detected")
    persistent = derive_trend_dynamics([row(60.0, 55.0, 52.0) for _ in range(20)])
    if persistent[15][7] != 100.0:
        raise AssertionError("Trend age did not cap at 16 records")

    before = derive_trend_dynamics(features)
    changed = [values[:] for values in features]
    changed[-1][0] = 100.0
    after = derive_trend_dynamics(changed)
    if before[:-1] != after[:-1]:
        raise AssertionError("A future row changed past Trend dynamics")
    transformed = transform_features(features, [0, 3, 7])
    if len(transformed[0]) != len(features[0]) + 3:
        raise AssertionError("Selected Trend dynamics were not appended")
    if len(feature_set_specs()) != 7:
        raise AssertionError("Unexpected controlled Trend dynamics grid")
    print("Trend dynamics diagnostic test passed")


if __name__ == "__main__":
    main()
