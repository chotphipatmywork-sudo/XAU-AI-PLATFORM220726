"""Focused checks for leakage-free Liquidity temporal context."""

from liquidity_temporal_diagnostic import (
    BUY_SWEEP,
    SELL_SWEEP,
    bounded_delta,
    contract_metadata,
    derive_liquidity_temporal,
    feature_set_specs,
    promotion_candidate,
    sweep_freshness,
    sweep_mean,
    transform_features,
)
from train_classifier import (
    FEATURE_SCHEMA_VERSION,
    LABEL_SCHEMA_VERSION,
    TRAINING_CONTRACT_VERSION,
)


def row(activity: float, position: float, sweep: float) -> list[float]:
    values = [50.0] * 12
    values[5] = activity
    values[6] = position
    values[7] = sweep
    return values


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
        raise AssertionError("Liquidity diagnostic contract metadata is stale")
    if bounded_delta(100.0, 0.0) != 100.0 or bounded_delta(0.0, 100.0) != 0.0:
        raise AssertionError("Bounded Liquidity delta endpoints are incorrect")

    features = [
        row(50.0, 50.0, 50.0),
        row(60.0, 55.0, BUY_SWEEP),
        row(70.0, 60.0, 50.0),
        row(80.0, 65.0, SELL_SWEEP),
    ]
    if sweep_mean(features, 3, 4) != 50.0:
        raise AssertionError("Sweep mean did not preserve canonical balance")
    if sweep_freshness(features, 1, BUY_SWEEP) != 100.0:
        raise AssertionError("Current buy sweep must have full freshness")
    if sweep_freshness(features, 3, BUY_SWEEP) != 87.5:
        raise AssertionError("Buy sweep freshness did not decay by observation age")
    if sweep_freshness(features, 3, SELL_SWEEP) != 100.0:
        raise AssertionError("Current sell sweep must have full freshness")

    derived = derive_liquidity_temporal(features)
    if derived[0][:4] != [50.0] * 4:
        raise AssertionError("Unavailable early Liquidity deltas must be neutral")
    if any(value < 0.0 or value > 100.0 for values in derived for value in values):
        raise AssertionError("Liquidity temporal value escaped 0..100")

    before = derive_liquidity_temporal(features)
    changed = [values[:] for values in features]
    changed[-1][5] = 0.0
    after = derive_liquidity_temporal(changed)
    if before[:-1] != after[:-1]:
        raise AssertionError("A future row changed past Liquidity temporal values")
    if len(transform_features(features, [4, 5, 6, 7])[0]) != 16:
        raise AssertionError("Sweep-memory values were not appended")
    if [item["name"] for item in feature_set_specs()] != [
        "baseline",
        "liquidity_changes",
        "sweep_memory",
        "all_liquidity_temporal",
    ]:
        raise AssertionError("Controlled Liquidity feature-set grid changed")

    baseline = {
        "feature_set": "baseline",
        "aggregate_metrics": metrics(0.40, 0.45),
        "gate_floor_ratio": 0.90,
        "folds_passing_gate": 0,
    }
    candidate = {
        "feature_set": "sweep_memory",
        "aggregate_metrics": metrics(0.42, 0.51),
        "gate_floor_ratio": 0.92,
        "folds_passing_gate": 1,
    }
    if promotion_candidate([baseline, candidate])["feature_set"] != "sweep_memory":
        raise AssertionError("Eligible Liquidity candidate was not promoted")
    candidate["folds_passing_gate"] = 0
    if promotion_candidate([baseline, candidate]) is not None:
        raise AssertionError("Candidate without a passing fold was promoted")

    print("Liquidity temporal diagnostic test passed")


if __name__ == "__main__":
    main()
