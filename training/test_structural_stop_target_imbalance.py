"""Focused deterministic checks for the IMP-098 imbalance analyzer."""

from datetime import datetime

from analyze_structural_stop_target_imbalance import (
    build_records,
    classify_imbalance,
    cliffs_delta,
    numeric_comparison,
)


def main() -> None:
    observation = datetime(2024, 6, 1, 12, 0)
    details = [{
        "request_id": "synthetic",
        "observation_time": "2024.06.01 12:00",
        "direction": "TRADE_SETUP_BUY",
        "entry": "100.0",
        "stop_distance_points": "200.0",
        "gate_result": "REJECTED",
    }]
    stops = {"synthetic": {
        "m5_stop_1": "99.0", "m5_stop_2": "98.0", "m5_stop_3": "97.0"
    }}
    targets = {"synthetic": {
        "m5_target_1": "100.5", "m5_target_2": "101.0",
        "m5_target_3": "0.0", "m15_target_1": "102.0",
    }}
    contexts = {observation: {
        "atr": 2.0, "volatility_change": 55.0,
        "trend_regime": 80.0, "volatility_regime": 50.0,
        "session_asia": 0.0, "session_london": 100.0,
        "session_new_york": 0.0,
    }}
    records = build_records(details, stops, targets, contexts)
    row = records[0]
    if row["stop_1_to_2_increment_points"] != 100.0:
        raise AssertionError("IMP-098 Stop depth increment changed")
    if row["intervening_target_barriers"] != 2:
        raise AssertionError("IMP-098 target barrier counting changed")
    if row["target_obstruction_gap_points"] != 150.0:
        raise AssertionError("IMP-098 target obstruction gap changed")
    if row["stop_to_target_ratio"] != 1.0:
        raise AssertionError("IMP-098 Stop/Target ratio changed")
    synthetic = [
        {"rejected": True, "stop": 20.0, "target": 5.0},
        {"rejected": True, "stop": 22.0, "target": 6.0},
        {"rejected": False, "stop": 10.0, "target": 20.0},
        {"rejected": False, "stop": 11.0, "target": 22.0},
    ]
    comparisons = {
        "stop_distance_points": numeric_comparison(synthetic, "stop"),
        "target_distance_points": numeric_comparison(synthetic, "target"),
    }
    diagnosis = classify_imbalance(comparisons)
    if diagnosis["classification"] != "BOTH_OVERSIZED_STOP_AND_UNDERSIZED_TARGET":
        raise AssertionError("IMP-098 imbalance classification changed")
    if cliffs_delta([2.0, 3.0], [1.0]) != 1.0:
        raise AssertionError("IMP-098 effect-size direction changed")
    print("IMP-098 structural imbalance focused test passed")


if __name__ == "__main__":
    main()
