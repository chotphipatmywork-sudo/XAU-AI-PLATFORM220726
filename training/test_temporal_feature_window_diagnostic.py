"""Focused checks for the canonical Brain temporal feature window."""

from temporal_feature_window_diagnostic import (
    contract_metadata,
    feature_set_specs,
    promotion_candidate,
    transform_features,
)
from train_classifier import (
    FEATURE_COLUMNS,
    FEATURE_SCHEMA_VERSION,
    LABEL_SCHEMA_VERSION,
    TRAINING_CONTRACT_VERSION,
)


def row(seed: float) -> list[float]:
    return [seed + index for index in range(len(FEATURE_COLUMNS))]


def metrics(macro_f1: float, buy_precision: float = 0.50) -> dict[str, float | int]:
    return {
        "sample_count": 500,
        "accuracy": 0.46,
        "macro_f1": macro_f1,
        "sell_precision": 0.51,
        "sell_recall": 0.35,
        "hold_precision": 0.30,
        "hold_recall": 0.35,
        "buy_precision": buy_precision,
        "buy_recall": 0.35,
    }


def main() -> None:
    if contract_metadata() != {
        "training_contract_version": TRAINING_CONTRACT_VERSION,
        "source_feature_schema_version": FEATURE_SCHEMA_VERSION,
        "label_schema_version": LABEL_SCHEMA_VERSION,
    }:
        raise AssertionError("Temporal-window contract metadata is stale")

    features = [row(float(index * 20)) for index in range(10)]
    lagged = transform_features(features, [1, 4, 8])
    width = len(FEATURE_COLUMNS)
    if len(lagged[9]) != width * 4:
        raise AssertionError("Temporal-window tensor width is incorrect")
    if lagged[9][width:width * 2] != features[8]:
        raise AssertionError("Lag 1 did not copy the exact prior Brain row")
    if lagged[9][width * 2:width * 3] != features[5]:
        raise AssertionError("Lag 4 did not copy the exact prior Brain row")
    if lagged[9][width * 3:width * 4] != features[1]:
        raise AssertionError("Lag 8 did not copy the exact prior Brain row")
    if transform_features(features, [8])[3][width:] != features[0]:
        raise AssertionError("Early temporal rows did not reuse earliest history")

    before = transform_features(features, [1, 4, 8])
    changed = [values[:] for values in features]
    changed[-1][0] += 999.0
    after = transform_features(changed, [1, 4, 8])
    if before[:-1] != after[:-1]:
        raise AssertionError("A future row changed an earlier temporal tensor")
    if [item["name"] for item in feature_set_specs()] != [
        "baseline",
        "lag_1",
        "lags_1_4",
        "lags_1_4_8",
    ]:
        raise AssertionError("Controlled temporal-window grid changed")

    baseline = {
        "feature_set": "baseline",
        "aggregate_metrics": metrics(0.40, 0.45),
        "gate_floor_ratio": 0.90,
        "folds_passing_gate": 0,
    }
    candidate = {
        "feature_set": "lags_1_4",
        "aggregate_metrics": metrics(0.42, 0.51),
        "gate_floor_ratio": 0.92,
        "folds_passing_gate": 1,
    }
    if promotion_candidate([baseline, candidate])["feature_set"] != "lags_1_4":
        raise AssertionError("Eligible temporal-window candidate was not promoted")
    candidate["gate_floor_ratio"] = 0.905
    if promotion_candidate([baseline, candidate]) is not None:
        raise AssertionError("Insufficient gate-floor improvement was promoted")

    print("Temporal Brain feature window diagnostic test passed")


if __name__ == "__main__":
    main()
