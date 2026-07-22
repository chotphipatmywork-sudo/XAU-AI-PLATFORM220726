"""Focused checks for closed-H1 canonical group decomposition."""

from h1_group_diagnostic import build_group_feature_sets


def main() -> None:
    key = (1, "2026.07.16 08:45:00")
    baseline = [[float(index) for index in range(12)]]
    context = {key: [101.0 / 2.0, 102.0 / 2.0, 103.0 / 2.0, 104.0 / 2.0, 105.0 / 2.0]}
    sets = build_group_feature_sets(baseline, [key], context)
    if tuple(sets) != (
        "schema4_baseline",
        "schema4_plus_h1_trend",
        "schema4_plus_h1_volatility",
        "schema4_plus_h1_trend_volatility",
    ):
        raise AssertionError("H1 group boundary changed")
    if len(sets["schema4_baseline"][0]) != 12:
        raise AssertionError("Baseline width changed")
    if len(sets["schema4_plus_h1_trend"][0]) != 15:
        raise AssertionError("H1 Trend width is not three")
    if len(sets["schema4_plus_h1_volatility"][0]) != 14:
        raise AssertionError("H1 Volatility width is not two")
    if len(sets["schema4_plus_h1_trend_volatility"][0]) != 17:
        raise AssertionError("Complete H1 width is not five")
    print("H1 group diagnostic test passed")


if __name__ == "__main__":
    main()
