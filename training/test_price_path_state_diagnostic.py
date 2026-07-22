"""Focused checks for strict CR-007 joining and promotion."""

import csv
import tempfile
from pathlib import Path

from price_path_state_diagnostic import (
    CONTEXT_COLUMNS,
    append_context,
    context_coverage,
    contract_metadata,
    feature_set_specs,
    promotion_candidate,
    read_price_path_context,
)
from train_classifier import (
    FEATURE_SCHEMA_VERSION,
    LABEL_SCHEMA_VERSION,
    TRAINING_CONTRACT_VERSION,
)


def metrics(macro_f1: float) -> dict[str, float | int]:
    return {
        "sample_count": 500,
        "accuracy": 0.46,
        "macro_f1": macro_f1,
        "sell_precision": 0.51,
        "sell_recall": 0.35,
        "hold_precision": 0.30,
        "hold_recall": 0.35,
        "buy_precision": 0.50,
        "buy_recall": 0.35,
    }


def write_context(
    path: Path,
    valid: float = 100.0,
    values: tuple[float, ...] = (10, 20, 30, 40, 50, 60, 70),
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
        raise AssertionError("Price Path diagnostic contract metadata is stale")
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "path.csv"
        key = write_context(path)
        context = read_price_path_context(path)
        if context_coverage(context)["valid_records"] != 1:
            raise AssertionError("Valid Price Path coverage was not reported")
        neutral_path = Path(directory) / "neutral.csv"
        write_context(neutral_path, 0.0, (50,) * 7)
        if context_coverage(read_price_path_context(neutral_path))[
            "neutral_invalid_records"
        ] != 1:
            raise AssertionError("Neutral Price Path coverage was not reported")
        invalid_path = Path(directory) / "invalid.csv"
        write_context(invalid_path, 0.0)
        try:
            read_price_path_context(invalid_path)
        except ValueError as error:
            if "not neutral" not in str(error):
                raise
        else:
            raise AssertionError("Non-neutral invalid Price Path row was accepted")

    base = [[float(index) for index in range(12)]]
    trend = append_context(base, [key], context, [0, 1, 2, 3])
    if trend[0][-4:] != [10.0, 20.0, 30.0, 40.0]:
        raise AssertionError("Trend-path feature order changed")
    if [item["name"] for item in feature_set_specs()] != [
        "schema4_baseline",
        "trend_path_state",
        "volatility_path_state",
        "all_price_path_state",
    ]:
        raise AssertionError("CR-007 candidate grid changed")

    baseline = {
        "feature_set": "schema4_baseline",
        "aggregate_metrics": metrics(0.40),
        "gate_floor_ratio": 0.90,
        "folds_passing_gate": 0,
    }
    candidate = {
        "feature_set": "trend_path_state",
        "aggregate_metrics": metrics(0.42),
        "gate_floor_ratio": 0.92,
        "folds_passing_gate": 1,
    }
    if promotion_candidate([baseline, candidate])["feature_set"] != "trend_path_state":
        raise AssertionError("Eligible CR-007 candidate was not promoted")
    candidate["folds_passing_gate"] = 0
    if promotion_candidate([baseline, candidate]) is not None:
        raise AssertionError("CR-007 candidate without passing fold was promoted")
    print("Price Path state diagnostic test passed")


if __name__ == "__main__":
    main()
