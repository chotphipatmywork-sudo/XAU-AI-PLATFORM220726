"""Focused checks for the current-feed Train-only Setup funnel diagnostic."""

from __future__ import annotations

from copy import deepcopy

from diagnose_current_feed_setup_funnel import summarize_rows


def row(
    time: str,
    poi: bool,
    trigger: bool,
    context: bool,
    plan: bool,
    reason: str,
    rr: float = 0.0,
) -> dict[str, str]:
    return {
        "observation_time": time,
        "poi_confirmed": str(poi).lower(),
        "trigger_confirmed": str(trigger).lower(),
        "reversal_context_confirmed": str(context).lower(),
        "plan_available": str(plan).lower(),
        "plan_rr": str(rr),
        "setup_reason": reason,
        "execution_success": "false",
        "risk_allowed": "false",
    }


def expect_failure(rows: list[dict[str, str]], message: str) -> None:
    try:
        summarize_rows(rows)
    except ValueError:
        return
    raise AssertionError(message)


def main() -> None:
    rows = [
        row("2024.06.30 23:15", False, False, False, False, "POI missing"),
        row("2024.06.30 23:30", True, False, False, False, "Trigger missing"),
        row(
            "2024.06.30 23:45", True, True, True, True, "Plan available", 2.2
        ),
        row("2024.07.01 00:00", False, False, False, False, "sealed"),
    ]
    report = summarize_rows(rows)
    if report["funnel"]["observations"] != 3:
        raise AssertionError("Post-cutoff evidence was read")
    if report["funnel"]["plan_available"] != 1:
        raise AssertionError("Plan funnel count changed")
    if report["trigger_plan_rr"]["at_least_2r"] != 1:
        raise AssertionError("Frozen RR count changed")
    if report["validation_dataset_used_for_selection"]:
        raise AssertionError("Validation selection lock changed")
    if report["deployment_authorized"]:
        raise AssertionError("Deployment lock changed")

    bypass = deepcopy(rows)
    bypass[0]["trigger_confirmed"] = "true"
    expect_failure(bypass, "Trigger bypass was accepted")
    weak_plan = deepcopy(rows)
    weak_plan[2]["plan_rr"] = "1.9"
    expect_failure(weak_plan, "Plan below 2R was accepted")
    unordered = [rows[1], rows[0], rows[3]]
    expect_failure(unordered, "Unordered evidence was accepted")
    print("Current-feed Setup funnel focused test passed")


if __name__ == "__main__":
    main()
