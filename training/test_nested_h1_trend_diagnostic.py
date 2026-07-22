"""Focused contract checks for nested closed-H1 Trend selection."""

from nested_h1_trend_diagnostic import FEATURE_SETS


def main() -> None:
    if FEATURE_SETS != ("schema4_baseline", "schema4_plus_h1_trend"):
        raise AssertionError("Nested H1 Trend boundary changed")
    print("Nested H1 Trend diagnostic test passed")


if __name__ == "__main__":
    main()
