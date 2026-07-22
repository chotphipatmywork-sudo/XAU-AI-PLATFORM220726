"""Focused checks for strict CR-006 joining and promotion."""

import csv
import tempfile
from pathlib import Path

from price_action_context_diagnostic import (
    CONTEXT_COLUMNS,
    append_context,
    context_coverage,
    contract_metadata,
    feature_set_specs,
    promotion_candidate,
    read_price_action_context,
)
from train_classifier import (
    FEATURE_SCHEMA_VERSION,
    LABEL_SCHEMA_VERSION,
    TRAINING_CONTRACT_VERSION,
)


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


def write_context(
    path: Path,
    valid: float = 100.0,
    values: tuple[float, ...] = (10, 20, 30, 40, 50, 60, 70, 80),
) -> tuple[int, str]:
    key = (7, "2026.07.16 08:45:00")
    with path.open("w", newline="", encoding="utf-8") as target:
        writer = csv.writer(target)
        writer.writerow(CONTEXT_COLUMNS)
        writer.writerow([key[0], key[1], *values, valid])
    return key


def main() -> None:
    if contract_metadata() != {
        "training_contract_version": TRAINING_CONTRACT_VERSION,
        "source_feature_schema_version": FEATURE_SCHEMA_VERSION,
        "label_schema_version": LABEL_SCHEMA_VERSION,
    }:
        raise AssertionError("Price Action diagnostic contract metadata is stale")
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "context.csv"
        key = write_context(path)
        context = read_price_action_context(path)
        if context_coverage(context)["valid_records"] != 1:
            raise AssertionError("Valid Price Action coverage was not reported")
        neutral_path = Path(directory) / "neutral.csv"
        write_context(neutral_path, 0.0, (50,) * 8)
        if context_coverage(read_price_action_context(neutral_path))[
            "neutral_invalid_records"
        ] != 1:
            raise AssertionError("Neutral invalid coverage was not reported")
        invalid_path = Path(directory) / "invalid.csv"
        write_context(invalid_path, 0.0)
        try:
            read_price_action_context(invalid_path)
        except ValueError as error:
            if "not neutral" not in str(error):
                raise
        else:
            raise AssertionError("Non-neutral invalid Price Action row was accepted")

    base = [[float(index) for index in range(12)]]
    momentum = append_context(base, [key], context, [0, 1, 2])
    if momentum[0][-3:] != [10.0, 20.0, 30.0]:
        raise AssertionError("Price Action momentum order changed")
    if [item["name"] for item in feature_set_specs()] != [
        "schema4_baseline",
        "direct_price_momentum",
        "completed_candle_impulse",
        "prior_range_context",
        "all_price_action_context",
    ]:
        raise AssertionError("CR-006 candidate grid changed")

    baseline = {
        "feature_set": "schema4_baseline",
        "aggregate_metrics": metrics(0.40, 0.45),
        "gate_floor_ratio": 0.90,
        "folds_passing_gate": 0,
    }
    candidate = {
        "feature_set": "direct_price_momentum",
        "aggregate_metrics": metrics(0.42, 0.51),
        "gate_floor_ratio": 0.92,
        "folds_passing_gate": 1,
    }
    if promotion_candidate([baseline, candidate])["feature_set"] != (
        "direct_price_momentum"
    ):
        raise AssertionError("Eligible CR-006 candidate was not promoted")
    candidate["gate_floor_ratio"] = 0.905
    if promotion_candidate([baseline, candidate]) is not None:
        raise AssertionError("Insufficient gate-floor improvement was promoted")

    print("Price Action context diagnostic test passed")


if __name__ == "__main__":
    main()
