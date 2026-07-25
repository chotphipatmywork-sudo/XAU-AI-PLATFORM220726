"""Focused checks for existing Entry geometry outcome attribution."""

from __future__ import annotations

from entry_geometry_outcome_attribution import (
    GEOMETRY_FIELDS,
    READINESS_GATE,
    evaluate_neighbourhood,
    geometry_views,
    readiness,
    validate_geometry,
)


def synthetic(direction: str) -> tuple[dict[str, str], dict[str, object], dict[str, str]]:
    buy = direction == "TRADE_SETUP_BUY"
    entry = 100.0
    stop = 99.0 if buy else 101.0
    target = 102.5 if buy else 97.5
    poi = 99.5 if buy else 100.5
    point_size = 0.01
    risk_points = 100.0
    cost_points = 10.0
    plan_rr = (250.0 - cost_points) / (risk_points + cost_points)
    outcome = {
        "direction": direction,
        "outcome": "TARGET_FIRST",
        "plan_entry": str(entry),
        "plan_stop": str(stop),
        "plan_target": str(target),
        "plan_rr": str(plan_rr),
        "minimum_rr": "2.0",
        "estimated_cost_points": str(cost_points),
        "point_size": str(point_size),
        "risk_points": str(risk_points),
    }
    effective: dict[str, object] = {
        "direction": direction,
        "outcome": "TARGET_FIRST",
        "entry": entry,
        "stop": stop,
        "target": target,
        "plan_rr": plan_rr,
        "estimated_cost_points": cost_points,
        "point_size": point_size,
    }
    setup = {
        "direction": direction,
        "poi_confirmed": "true",
        "trigger_confirmed": "true",
        "plan_available": "true",
        "plan_entry": str(entry),
        "plan_stop": str(stop),
        "plan_target": str(target),
        "nearest_target": str(target),
        "structural_stop": str(stop),
        "plan_rr": str(plan_rr),
        "minimum_rr": "2.0",
        "estimated_cost_points": str(cost_points),
        "reference_poi": str(poi),
        "sweep_penetration_atr": "0.2",
        "reclaim_distance_atr": "0.3",
    }
    return outcome, effective, setup


def main() -> None:
    if geometry_views() != {
        "full_geometry_control": tuple(range(8)),
        "trigger_shape": (0, 1, 2),
        "entry_invalidation_geometry": (3, 4),
        "payoff_geometry": (5, 6, 7),
    } or len(GEOMETRY_FIELDS) != 8:
        raise AssertionError("Entry geometry frozen views changed")

    for direction in ("TRADE_SETUP_BUY", "TRADE_SETUP_SELL"):
        values = validate_geometry(*synthetic(direction))
        if len(values) != 8 or abs(values[2] - 0.6) > 1e-12 or (
            abs(values[3] + values[4] - 1.0) > 1e-12
        ):
            raise AssertionError("Entry geometry derivation changed")

    outcome, effective, setup = synthetic("TRADE_SETUP_BUY")
    setup["reference_poi"] = "101.0"
    try:
        validate_geometry(outcome, effective, setup)
    except ValueError as error:
        if "POI" not in str(error):
            raise
    else:
        raise AssertionError("Entry geometry invalid POI should fail closed")

    train_features = [[float(index) * 0.01] for index in range(20)] + [
        [10.0 + float(index) * 0.01] for index in range(20)
    ]
    train_labels = [0] * 20 + [1] * 20
    evaluation_features = [[0.05], [10.05], [0.08], [10.08]]
    evaluation_labels = [0, 1, 0, 1]
    directions = [
        "TRADE_SETUP_BUY",
        "TRADE_SETUP_BUY",
        "TRADE_SETUP_SELL",
        "TRADE_SETUP_SELL",
    ]
    report, predicted, details = evaluate_neighbourhood(
        train_features,
        train_labels,
        evaluation_features,
        evaluation_labels,
        directions,
        (0,),
        neighbours=5,
    )
    if predicted != evaluation_labels or report["classification"]["macro_f1"] != 1.0:
        raise AssertionError("Entry geometry separable neighbourhood changed")
    report["positive_support_gain_folds"] = READINESS_GATE[
        "positive_support_gain_folds"
    ]
    report["support_gain_by_direction"] = {
        direction: sum(
            item["support_gain"] for item in details
            if item["direction"] == direction
        ) / 2.0
        for direction in ("TRADE_SETUP_BUY", "TRADE_SETUP_SELL")
    }
    if not readiness(report)["hypothesis_ready"]:
        raise AssertionError("Entry geometry synthetic readiness should pass")

    print("Entry geometry outcome attribution test passed")


if __name__ == "__main__":
    main()
