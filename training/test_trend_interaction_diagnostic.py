"""Focused checks for deterministic Trend interaction candidates."""

from trend_interaction_diagnostic import (
    feature_set_specs,
    transform_features,
    trend_interactions,
)


def main() -> None:
    neutral = [50.0, 50.0, 50.0, *([50.0] * 8)]
    if trend_interactions(neutral) != [0.0, 50.0, 50.0, 50.0, 50.0, 50.0]:
        raise AssertionError("Neutral Trend interactions are incorrect")

    aligned_bullish = [100.0, 100.0, 100.0, *([50.0] * 8)]
    values = trend_interactions(aligned_bullish)
    if values[:4] != [100.0, 100.0, 100.0, 100.0]:
        raise AssertionError(f"Bullish agreement interactions are incorrect: {values}")
    disagreement = [100.0, 0.0, 0.0, *([50.0] * 8)]
    values = trend_interactions(disagreement)
    if values[1] != 0.0 or values[2] != 0.0 or values[4] != 0.0 or values[5] != 0.0:
        raise AssertionError(f"Trend disagreement interactions are incorrect: {values}")

    transformed = transform_features([neutral], [0, 1, 4])
    if len(transformed[0]) != len(neutral) + 3:
        raise AssertionError("Selected Trend interactions were not appended")
    if len(feature_set_specs()) != 6:
        raise AssertionError("Unexpected controlled Trend feature-set grid")
    print("Trend interaction diagnostic test passed")


if __name__ == "__main__":
    main()
