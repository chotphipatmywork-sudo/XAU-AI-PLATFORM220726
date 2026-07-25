"""Focused checks for strict direction-asymmetry confirmation gates."""

from analyze_current_feed_direction_asymmetry import analyze


def fixture(records: int, passed: bool) -> dict:
    return {
        "status": "CURRENT_FEED_STOP_REPLAY_TRAIN_ONLY_NO_GO",
        "validation_dataset_used": False, "test_dataset_used": False,
        "runtime_changed": False, "risk_changed": False,
        "minimum_rr_changed": False, "deployment_authorized": False,
        "deployment_remains_no_go": True, "train_end_exclusive": "2024.07.01 00:00",
        "candidates": {"candidate": {
            "by_direction": {
                "TRADE_SETUP_BUY": {"records": records, "mean_cost_aware_r": -0.2},
                "TRADE_SETUP_SELL": {"records": records, "mean_cost_aware_r": 0.2},
            },
            "train_gate_passed": passed,
        }},
    }


def main() -> None:
    small = analyze(fixture(39, True))
    if small["confirmed_direction_asymmetry_candidates"]:
        raise AssertionError("Small direction sample was confirmed")
    failed_candidate = analyze(fixture(40, False))
    if failed_candidate["confirmed_direction_asymmetry_candidates"]:
        raise AssertionError("Failed Train candidate was direction-confirmed")
    confirmed = analyze(fixture(40, True))
    if confirmed["confirmed_direction_asymmetry_candidates"] != ["candidate"]:
        raise AssertionError("Eligible synthetic asymmetry was not detected")
    if confirmed["direction_filter_created"] or confirmed["deployment_authorized"]:
        raise AssertionError("Diagnostic authorized a runtime action")
    print("Current-feed direction-asymmetry focused test passed")


if __name__ == "__main__":
    main()
