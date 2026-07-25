"""Focused checks for strict past-only trigger-event export validation."""

from __future__ import annotations

from build_trigger_event_requests import REQUEST_COLUMNS
from validate_trigger_event_export import EXPORT_COLUMNS, validate_row


def main() -> None:
    request = dict.fromkeys(REQUEST_COLUMNS, "")
    request.update({
        "request_schema_version": "1.0.0",
        "request_id": "trigger_event_20200101_0015",
        "observation_time": "2020.01.01 00:15",
        "symbol": "XAUUSD",
        "direction": "TRADE_SETUP_BUY",
        "entry_bar_open": "2020.01.01 00:10",
        "context_bar_open": "2020.01.01 00:05",
        "expected_entry": "104.0",
        "reference_poi": "100.0",
        "structural_stop": "97.0",
        "nearest_target": "110.0",
        "expected_sweep_penetration_atr": "1.0",
        "expected_reclaim_distance_atr": "2.0",
        "point_size": "0.01",
        "lookback_m5_bars": "64",
        "deployment_authorized": "false",
    })
    row = dict.fromkeys(EXPORT_COLUMNS, "")
    row.update({
        "export_schema_version": "1.1.0",
        "request_id": request["request_id"],
        "observation_time": request["observation_time"],
        "symbol": "XAUUSD",
        "data_symbol": "XAUUSD.sc",
        "direction": "TRADE_SETUP_BUY",
        "entry_bar_open": request["entry_bar_open"],
        "context_bar_open": request["context_bar_open"],
        "entry_atr": "2.0",
        "trigger_open": "100.0",
        "trigger_high": "105.0",
        "trigger_low": "98.0",
        "trigger_close": "104.0",
        "context_open": "99.0",
        "context_high": "101.0",
        "context_low": "98.0",
        "context_close": "100.0",
        "trigger_range_atr": "3.5",
        "trigger_body_atr": "2.0",
        "directional_trigger_body_atr": "2.0",
        "upper_wick_atr": "0.5",
        "lower_wick_atr": "1.0",
        "trigger_close_location": str(6.0 / 7.0),
        "context_body_atr": "0.5",
        "directional_context_body_atr": "0.5",
        "context_close_location": str(2.0 / 3.0),
        "trigger_followthrough_atr": "2.0",
        "sweep_penetration_atr": "1.0",
        "reclaim_distance_atr": "2.0",
        "entry_drift_atr": "0.0",
        "poi_level_age_bars": "5",
        "target_level_age_bars": "8",
        "prior_poi_touch_age_bars": "2",
        "prior_poi_touch_count_64": "4",
        "entry_parity_valid": "true",
        "structure_parity_valid": "true",
        "trigger_parity_valid": "true",
        "history_known_at_valid": "true",
        "deployment_authorized": "false",
    })
    validate_row(row, request)
    row["deployment_authorized"] = "true"
    try:
        validate_row(row, request)
    except ValueError as error:
        if "Deployment" not in str(error):
            raise
    else:
        raise AssertionError("Trigger-event Deployment flag should fail closed")

    print("Trigger-event export validation test passed")


if __name__ == "__main__":
    main()
