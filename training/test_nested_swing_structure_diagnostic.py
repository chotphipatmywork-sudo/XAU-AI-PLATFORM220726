"""Focused checks for conditional nested Swing Structure confirmation."""

from nested_swing_structure_diagnostic import (
    BASELINE,
    authorized_feature_sets,
    build_feature_sets,
)


def report(promoted: str | None, authorized: bool) -> dict[str, object]:
    return {
        "diagnostic_stage": "train_only_confirmed_swing_structure_comparison",
        "validation_dataset_used": False,
        "test_dataset_used": False,
        "source_feature_schema_version": "4.0.0",
        "label_schema_version": "1.1.0",
        "promoted_feature_set": promoted,
        "nested_confirmation_authorized": authorized,
    }


def main() -> None:
    try:
        authorized_feature_sets(report(None, False))
    except ValueError as error:
        if "did not authorize" not in str(error):
            raise
    else:
        raise AssertionError("Nested confirmation ran without controlled promotion")

    names = authorized_feature_sets(report("structure_core", True))
    if names != (BASELINE, "structure_core"):
        raise AssertionError("Nested Swing Structure pair changed")
    features = [[float(index) for index in range(12)]]
    keys = [(1, "2026.07.16 08:45:00")]
    context = {keys[0]: [100.0, 50.0, 50.0, 25.0, 100.0]}
    feature_sets = build_feature_sets(features, keys, context, names)
    if len(feature_sets[BASELINE][0]) != 12:
        raise AssertionError("Nested baseline width changed")
    if feature_sets["structure_core"][0][-3:] != [100.0, 50.0, 50.0]:
        raise AssertionError("Nested promoted feature order changed")

    print("Nested Swing Structure diagnostic test passed")


if __name__ == "__main__":
    main()
