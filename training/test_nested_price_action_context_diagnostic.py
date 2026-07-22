"""Focused checks for conditional CR-006 nested confirmation."""

from nested_price_action_context_diagnostic import (
    BASELINE,
    authorized_feature_sets,
    build_feature_sets,
)


def report(promoted: str | None, authorized: bool) -> dict[str, object]:
    return {
        "diagnostic_stage": "train_only_past_price_action_context_comparison",
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
        raise AssertionError("CR-006 nested confirmation ran without promotion")
    names = authorized_feature_sets(report("direct_price_momentum", True))
    if names != (BASELINE, "direct_price_momentum"):
        raise AssertionError("CR-006 nested candidate pair changed")
    features = [[float(index) for index in range(12)]]
    keys = [(1, "2026.07.16 08:45:00")]
    context = {keys[0]: [10, 20, 30, 40, 50, 60, 70, 80, 100]}
    sets = build_feature_sets(features, keys, context, names)
    if len(sets[BASELINE][0]) != 12:
        raise AssertionError("CR-006 nested baseline width changed")
    if sets["direct_price_momentum"][0][-3:] != [10, 20, 30]:
        raise AssertionError("CR-006 nested promoted order changed")
    print("Nested Price Action context diagnostic test passed")


if __name__ == "__main__":
    main()
