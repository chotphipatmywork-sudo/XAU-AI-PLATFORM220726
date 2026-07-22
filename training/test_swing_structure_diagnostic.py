"""Focused validation for strict Swing Structure joining and promotion."""

import csv
import tempfile
from pathlib import Path

from swing_structure_diagnostic import (
    SWING_COLUMNS,
    append_context,
    context_coverage,
    contract_metadata,
    feature_set_specs,
    promotion_candidate,
    read_swing_context,
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
    path: Path, valid: float = 100.0, values: tuple[float, ...] = (100, 0, 0, 25)
) -> tuple[int, str]:
    key = (7, "2026.07.16 08:45:00")
    with path.open("w", newline="", encoding="utf-8") as target:
        writer = csv.writer(target)
        writer.writerow(SWING_COLUMNS)
        writer.writerow([key[0], key[1], *values, valid])
    return key


def main() -> None:
    if contract_metadata() != {
        "training_contract_version": TRAINING_CONTRACT_VERSION,
        "source_feature_schema_version": FEATURE_SCHEMA_VERSION,
        "label_schema_version": LABEL_SCHEMA_VERSION,
    }:
        raise AssertionError("Swing Structure diagnostic contract metadata is stale")

    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "swing.csv"
        key = write_context(path)
        context = read_swing_context(path)
        neutral_path = Path(directory) / "neutral.csv"
        write_context(neutral_path, valid=0.0, values=(50, 50, 50, 50))
        neutral = read_swing_context(neutral_path)
        if context_coverage(neutral)["neutral_unconfirmed_records"] != 1:
            raise AssertionError("Neutral unconfirmed coverage was not reported")
        invalid_path = Path(directory) / "invalid.csv"
        write_context(invalid_path, valid=0.0)
        try:
            read_swing_context(invalid_path)
        except ValueError as error:
            if "not neutral" not in str(error):
                raise
        else:
            raise AssertionError("Non-neutral unconfirmed Swing Structure row was accepted")

    base = [[float(index) for index in range(12)]]
    core = append_context(base, [key], context, [0, 1, 2])
    if core != [base[0] + [100.0, 0.0, 0.0]]:
        raise AssertionError("Swing Structure core join changed feature order")
    all_context = append_context(base, [key], context, [0, 1, 2, 3])
    if all_context != [base[0] + [100.0, 0.0, 0.0, 25.0]]:
        raise AssertionError("Swing Structure range position was not appended")
    try:
        append_context(base, [(8, key[1])], context, [0, 1, 2])
    except ValueError as error:
        if "Missing Swing Structure context" not in str(error):
            raise
    else:
        raise AssertionError("Missing Swing Structure context was accepted")

    if [item["name"] for item in feature_set_specs()] != [
        "schema4_baseline",
        "structure_core",
        "all_swing_structure",
    ]:
        raise AssertionError("Controlled Swing Structure candidate grid changed")

    baseline = {
        "feature_set": "schema4_baseline",
        "aggregate_metrics": metrics(0.40, 0.45),
        "gate_floor_ratio": 0.90,
        "folds_passing_gate": 0,
    }
    candidate = {
        "feature_set": "structure_core",
        "aggregate_metrics": metrics(0.42, 0.51),
        "gate_floor_ratio": 0.92,
        "folds_passing_gate": 1,
    }
    if promotion_candidate([baseline, candidate])["feature_set"] != "structure_core":
        raise AssertionError("Eligible Swing Structure candidate was not promoted")
    candidate["folds_passing_gate"] = 0
    if promotion_candidate([baseline, candidate]) is not None:
        raise AssertionError("Candidate without a passing fold was promoted")

    print("Swing Structure diagnostic test passed")


if __name__ == "__main__":
    main()
