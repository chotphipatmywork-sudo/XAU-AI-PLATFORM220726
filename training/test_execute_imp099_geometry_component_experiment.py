"""Focused deterministic tests for the locked IMP-099 executor."""

from execute_imp099_geometry_component_experiment import (
    evaluate_arm,
    exact_mcnemar_p_value,
    paired_bootstrap_interval,
)


def main() -> None:
    stop_row = {
        "direction": "TRADE_SETUP_BUY",
        "entry": "100.0",
        "estimated_cost_points": "0.0",
        "cost_known": "true",
        "m5_stop_1": "99.0",
        "m5_stop_2": "98.0",
    }
    target_row = {"m15_target_1": "104.0", "m15_target_2": "106.0"}
    arm = {"arm_id": "CONTROL", "stop": "m5_stop_2",
           "target": "m15_target_1"}
    result = evaluate_arm(stop_row, target_row, arm, 2.0)
    if not result["eligible"] or not result["rr_pass"]:
        raise AssertionError("IMP-099 locked geometry evaluation changed")
    if result["cost_adjusted_rr"] != 2.0:
        raise AssertionError("IMP-099 frozen RR calculation changed")
    if exact_mcnemar_p_value(3, 0) != 0.25:
        raise AssertionError("IMP-099 exact McNemar calculation changed")
    interval = paired_bootstrap_interval([0, 0, 1], [1, 1, 1])
    if interval[0] < 0.0 or interval[1] > 1.0:
        raise AssertionError("IMP-099 paired bootstrap bounds changed")
    print("IMP-099 execution focused test passed")


if __name__ == "__main__":
    main()
