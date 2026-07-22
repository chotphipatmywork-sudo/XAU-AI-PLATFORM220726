"""Focused validation for strict H1 research context joining and selection."""

import csv
import tempfile
from pathlib import Path

from h1_context_diagnostic import (
    H1_COLUMNS,
    append_h1_context,
    choose_result,
    read_h1_context,
)


def metrics(buy_precision: float) -> dict[str, float | int]:
    return {
        "sample_count": 500,
        "accuracy": 0.46,
        "macro_f1": 0.41,
        "sell_precision": 0.52,
        "sell_recall": 0.40,
        "hold_precision": 0.30,
        "hold_recall": 0.35,
        "buy_precision": buy_precision,
        "buy_recall": 0.35,
    }


def main() -> None:
    key = (7, "2026.07.16 08:45:00")
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "h1.csv"
        with path.open("w", newline="", encoding="utf-8") as target:
            writer = csv.writer(target)
            writer.writerow(H1_COLUMNS)
            writer.writerow([key[0], key[1], 10, 20, 30, 40, 50])
        context = read_h1_context(path)
    combined = append_h1_context([[float(index) for index in range(12)]], [key], context)
    if combined != [[float(index) for index in range(12)] + [10, 20, 30, 40, 50]]:
        raise AssertionError("H1 context join changed feature order")
    try:
        append_h1_context([[0.0] * 12], [(8, key[1])], context)
    except ValueError as error:
        if "Missing H1 context" not in str(error):
            raise
    else:
        raise AssertionError("Missing H1 context was accepted")

    candidates = [
        {"feature_set": "schema4_baseline", "aggregate_metrics": metrics(0.40), "folds_passing_gate": 0},
        {"feature_set": "schema4_plus_closed_h1", "aggregate_metrics": metrics(0.46), "folds_passing_gate": 0},
    ]
    if choose_result(candidates, 4)["feature_set"] != "schema4_plus_closed_h1":
        raise AssertionError("Weakest-gate improvement was not selected")
    print("H1 context diagnostic test passed")


if __name__ == "__main__":
    main()
