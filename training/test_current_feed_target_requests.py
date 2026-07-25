"""Focused checks for current-feed past-only Target requests."""

from __future__ import annotations

from datetime import datetime, timedelta

from build_setup_outcome_dataset import SETUP_AUDIT_COLUMNS_V3
from build_current_feed_target_requests import build_requests


def setup_row(observation: datetime, known: bool) -> dict[str, str]:
    row = {name: "" for name in SETUP_AUDIT_COLUMNS_V3}
    row.update({
        "observation_time": observation.strftime("%Y.%m.%d %H:%M"),
        "entry_bar_open": (
            observation - timedelta(minutes=5)
        ).strftime("%Y.%m.%d %H:%M"),
        "symbol": "XAUUSD",
        "direction": "TRADE_SETUP_BUY",
        "poi_confirmed": "true",
        "trigger_confirmed": "true",
        "reversal_context_confirmed": "true",
        "structural_stop": "90.0",
        "nearest_target": "121.0",
        "plan_entry": "100.0" if known else "0.0",
        "estimated_cost_points": "2.0" if known else "0.0",
        "minimum_rr": "2.0" if known else "0.0",
    })
    return row


def expect_failure(rows: list[dict[str, str]], message: str) -> None:
    try:
        build_requests(rows)
    except ValueError:
        return
    raise AssertionError(message)


def main() -> None:
    first = datetime(2024, 6, 30, 23, 30)
    rows = [
        setup_row(first, True),
        setup_row(first + timedelta(minutes=15), False),
        setup_row(datetime(2024, 7, 1), True),
    ]
    requests, audit = build_requests(rows)
    if len(requests) != 2 or audit["reversal_context_rows"] != 2:
        raise AssertionError("Current-feed context request count changed")
    if requests[0]["entry_known"] != "true":
        raise AssertionError("Known Entry flag changed")
    if requests[1]["entry_known"] != "false":
        raise AssertionError("Unknown Entry flag changed")
    if "outcome" in requests[0]:
        raise AssertionError("Outcome leaked into Target request")
    bypass = [dict(rows[0]), rows[-1]]
    bypass[0]["trigger_confirmed"] = "false"
    expect_failure(bypass, "Causal gate bypass was accepted")
    weak = [dict(rows[0]), rows[-1]]
    weak[0]["minimum_rr"] = "1.9"
    expect_failure(weak, "Known evidence below 2R was accepted")
    print("Current-feed Target request focused test passed")


if __name__ == "__main__":
    main()
