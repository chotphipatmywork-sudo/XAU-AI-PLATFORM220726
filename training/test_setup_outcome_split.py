"""Focused checks for Stage D chronological Setup Outcome splitting."""

from __future__ import annotations

from datetime import datetime, timedelta

from analyze_shadow_run import FEATURE_COLUMNS
from build_setup_outcome_dataset import (
    FEATURE_SCHEMA_VERSION,
    OUTCOME_AUDIT_COLUMNS,
    SETUP_OUTCOME_SCHEMA_VERSION,
)
from split_setup_outcome_dataset import split_rows


def build_rows(count: int = 300) -> list[dict[str, str]]:
    start = datetime(2025, 1, 1, 0, 0)
    rows: list[dict[str, str]] = []
    for index in range(count):
        observation = start + timedelta(minutes=15 * index)
        known_at = observation + timedelta(minutes=30)
        outcome = "TARGET_FIRST" if index % 3 == 0 else "STOP_FIRST"
        row = {column: "0" for column in OUTCOME_AUDIT_COLUMNS}
        row.update({
            "setup_outcome_schema_version": SETUP_OUTCOME_SCHEMA_VERSION,
            "feature_schema_version": FEATURE_SCHEMA_VERSION,
            "observation_time": observation.strftime("%Y.%m.%d %H:%M"),
            "outcome_known_at": known_at.strftime("%Y.%m.%d %H:%M"),
            "symbol": "XAUUSD",
            "timeframe": "PERIOD_M15",
            "direction": "TRADE_SETUP_BUY",
            "outcome": outcome,
            "trainable": "true",
        })
        for feature_index, feature in enumerate(FEATURE_COLUMNS):
            row[feature] = str(40.0 + feature_index)
        rows.append(row)
    return rows


def main() -> None:
    rows = build_rows()
    train, validation, test, summary = split_rows(rows)
    if (len(train), len(validation), len(test)) != (208, 43, 45):
        raise AssertionError(
            f"Unexpected purged split sizes: {len(train)}/{len(validation)}/{len(test)}"
        )
    if summary["purged_train_records"] != 2 or summary["purged_validation_records"] != 2:
        raise AssertionError(f"Unexpected temporal purge: {summary}")
    if not summary["outcome_time_purge_valid"]:
        raise AssertionError("Outcome-time purge was not valid")
    if not summary["ready_for_train_only_ranking"]:
        raise AssertionError("Adequate synthetic Train partition was rejected")
    validation_start = datetime.strptime(
        summary["validation_start"], "%Y.%m.%d %H:%M"
    )
    if any(
        datetime.strptime(row["outcome_known_at"], "%Y.%m.%d %H:%M")
        >= validation_start for row in train
    ):
        raise AssertionError("A Train outcome crosses the Validation boundary")

    print("Stage D Setup Outcome split test passed")


if __name__ == "__main__":
    main()
