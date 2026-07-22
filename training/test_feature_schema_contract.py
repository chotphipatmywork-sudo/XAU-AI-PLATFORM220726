"""Focused checks for the strict Feature Schema 4.0 CSV contract."""

import csv
from pathlib import Path
from tempfile import TemporaryDirectory

from train_classifier import (
    FEATURE_COLUMNS,
    FEATURE_SCHEMA_VERSION,
    LABEL_SCHEMA_VERSION,
    REQUIRED_COLUMNS,
    TRAINING_CONTRACT_VERSION,
    read_dataset,
)


def write_row(path: Path, columns: tuple[str, ...]) -> None:
    values = {
        "id": "1",
        "timestamp": "2026.07.15 12:00:00",
        "symbol": "XAUUSD",
        "trend_regime": "50",
        "trend_momentum": "50",
        "trend_slope": "50",
        "volatility_regime": "50",
        "volatility_change": "50",
        "liquidity_activity": "50",
        "liquidity_range_position": "50",
        "liquidity_sweep_direction": "50",
        "session_asia": "0",
        "session_london": "100",
        "session_new_york": "0",
        "session_progress": "50",
        "label": "1",
    }
    with path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=columns)
        writer.writeheader()
        writer.writerow({name: values[name] for name in columns})


def main() -> None:
    if TRAINING_CONTRACT_VERSION != "4.0.0" or FEATURE_SCHEMA_VERSION != "4.0.0":
        raise AssertionError("Feature Schema 4.0 version constants changed")
    if LABEL_SCHEMA_VERSION != "1.1.0":
        raise AssertionError("CR-001 must not change the approved label schema")
    if len(FEATURE_COLUMNS) != 12 or FEATURE_COLUMNS[-1] != "session_progress":
        raise AssertionError("Session Progress must be the twelfth feature")

    with TemporaryDirectory() as directory:
        schema4_path = Path(directory) / "schema4.csv"
        write_row(schema4_path, REQUIRED_COLUMNS)
        features, labels = read_dataset(schema4_path)
        if features[0][-1] != 50.0 or labels != [1]:
            raise AssertionError("Schema 4.0 row was not read correctly")

        schema3_columns = tuple(
            column for column in REQUIRED_COLUMNS if column != "session_progress"
        )
        schema3_path = Path(directory) / "schema3.csv"
        write_row(schema3_path, schema3_columns)
        try:
            read_dataset(schema3_path)
        except ValueError:
            pass
        else:
            raise AssertionError("Strict Schema 4.0 reader accepted a Schema 3.0 CSV")

    print("Feature schema contract test passed")


if __name__ == "__main__":
    main()

