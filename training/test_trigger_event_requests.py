"""Focused checks for outcome-blind past-only trigger-event requests."""

from __future__ import annotations

import csv
import json
from datetime import datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory

from build_trigger_event_requests import (
    LOOKBACK_M5_BARS,
    REQUEST_COLUMNS,
    build_request_rows,
    write_requests,
)


def records() -> list[dict[str, object]]:
    start = datetime(2020, 1, 1, 0, 15)
    result: list[dict[str, object]] = []
    for index in range(232):
        observation = start + timedelta(minutes=15 * index)
        result.append({
            "observation": observation,
            "observation_time": observation.strftime("%Y.%m.%d %H:%M"),
            "symbol": "XAUUSD",
            "direction": (
                "TRADE_SETUP_BUY" if index % 2 == 0 else "TRADE_SETUP_SELL"
            ),
            "entry_bar_open": (
                observation - timedelta(minutes=5)
            ).strftime("%Y.%m.%d %H:%M"),
            "entry": 2000.0,
            "reference_poi": 1999.0,
            "structural_stop": 1998.0,
            "nearest_target": 2004.0,
            "point_size": 0.01,
            "features": [0.2, 0.3],
            "outcome": "TARGET_FIRST",
        })
    return result


def main() -> None:
    rows = build_request_rows(records())
    if len(rows) != 232 or tuple(rows[0]) != REQUEST_COLUMNS:
        raise AssertionError("Trigger-event request contract changed")
    if any("outcome" in key.lower() for key in rows[0]):
        raise AssertionError("Trigger-event request leaked its outcome")
    if rows[0]["context_bar_open"] != "2020.01.01 00:05" or (
        rows[0]["entry_bar_open"] != "2020.01.01 00:10"
    ) or rows[0]["lookback_m5_bars"] != LOOKBACK_M5_BARS or (
        rows[0]["deployment_authorized"] != "false"
    ):
        raise AssertionError("Trigger-event timing/safety contract changed")

    invalid = records()
    invalid[0]["entry_bar_open"] = "2020.01.01 00:05"
    try:
        build_request_rows(invalid)
    except ValueError as error:
        if "timing" not in str(error):
            raise
    else:
        raise AssertionError("Trigger-event invalid timing should fail closed")

    with TemporaryDirectory() as directory:
        output = Path(directory) / "requests.csv"
        manifest_path = Path(directory) / "manifest.json"
        manifest = write_requests(
            rows,
            {"source_train_sha256": "A" * 64},
            "B" * 64,
            output,
            manifest_path,
        )
        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written = list(reader)
        stored = json.loads(manifest_path.read_text(encoding="utf-8"))
        if len(written) != 232 or manifest != stored or (
            manifest["outcome_label_in_request"] is not False
        ) or manifest["deployment_authorized"] is not False:
            raise AssertionError("Trigger-event manifest safety changed")

    print("Trigger-event request test passed")


if __name__ == "__main__":
    main()
