"""Focused checks for strict CR-011 joining and promotion."""

import csv
import tempfile
from pathlib import Path

from tick_microstructure_diagnostic import (
    CONTEXT_COLUMNS,
    append_context,
    context_coverage,
    contract_metadata,
    feature_set_specs,
    promotion_candidate,
    read_tick_context,
)
from train_classifier import FEATURE_SCHEMA_VERSION, LABEL_SCHEMA_VERSION, TRAINING_CONTRACT_VERSION


def metrics(macro_f1: float, directional: float = 0.40) -> dict[str, float | int]:
    return {
        "sample_count": 500, "accuracy": 0.46, "macro_f1": macro_f1,
        "sell_precision": directional, "sell_recall": directional,
        "hold_precision": 0.30, "hold_recall": 0.35,
        "buy_precision": directional, "buy_recall": directional,
    }


def result(name: str, macro_f1: float, gate: float, folds: list[float], directional: float = 0.40):
    return {
        "feature_set": name,
        "aggregate_metrics": metrics(macro_f1, directional),
        "gate_floor_ratio": gate,
        "folds_passing_gate": 0,
        "folds": [{"metrics": metrics(value, directional)} for value in folds],
    }


def write_context(path: Path, valid: float = 100.0, values=(10, 20, 30, 40, 50, 60)):
    key = (7, "2026.07.16 08:45:00")
    with path.open("w", newline="", encoding="utf-8") as target:
        writer = csv.writer(target)
        writer.writerow(CONTEXT_COLUMNS)
        writer.writerow([key[0], key[1], *values, 42, valid])
    return key


def main() -> None:
    if contract_metadata() != {
        "training_contract_version": TRAINING_CONTRACT_VERSION,
        "source_feature_schema_version": FEATURE_SCHEMA_VERSION,
        "label_schema_version": LABEL_SCHEMA_VERSION,
    }:
        raise AssertionError("Tick diagnostic contract metadata is stale")
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "ticks.csv"
        key = write_context(path)
        context = read_tick_context(path)
        coverage = context_coverage(context)
        if coverage["valid_records"] != 1 or coverage["minimum_tick_count"] != 42:
            raise AssertionError("Valid tick coverage was not reported")
        neutral = Path(directory) / "neutral.csv"
        write_context(neutral, 0.0, (50,) * 6)
        if context_coverage(read_tick_context(neutral))["neutral_invalid_records"] != 1:
            raise AssertionError("Neutral invalid coverage was not reported")
        invalid = Path(directory) / "invalid.csv"
        write_context(invalid, 0.0)
        try:
            read_tick_context(invalid)
        except ValueError as error:
            if "not neutral" not in str(error):
                raise
        else:
            raise AssertionError("Non-neutral invalid tick row was accepted")

    base = [[float(index) for index in range(12)]]
    joined = append_context(base, [key], context, [0, 1, 5])
    if joined[0][-3:] != [10.0, 20.0, 60.0]:
        raise AssertionError("Liquidity tick feature order changed")
    if [item["name"] for item in feature_set_specs()] != [
        "schema4_baseline", "liquidity_tick_flow",
        "volatility_tick_state", "all_tick_microstructure",
    ]:
        raise AssertionError("CR-011 candidate grid changed")

    baseline = result("schema4_baseline", 0.40, 0.90, [0.40] * 4)
    candidate = result("liquidity_tick_flow", 0.42, 0.91, [0.41, 0.42, 0.39, 0.40], 0.41)
    promoted = promotion_candidate([baseline, candidate])
    if promoted is None or promoted["feature_set"] != "liquidity_tick_flow":
        raise AssertionError("Eligible CR-011 candidate was not promoted")
    candidate["folds"] = [{"metrics": metrics(value, 0.41)} for value in [0.41, 0.40, 0.40, 0.40]]
    if promotion_candidate([baseline, candidate]) is not None:
        raise AssertionError("Candidate improving fewer than two folds was promoted")
    candidate = result("liquidity_tick_flow", 0.42, 0.91, [0.41, 0.42, 0.39, 0.40], 0.39)
    if promotion_candidate([baseline, candidate]) is not None:
        raise AssertionError("Candidate degrading directional coverage was promoted")
    print("Tick microstructure diagnostic test passed")


if __name__ == "__main__":
    main()
