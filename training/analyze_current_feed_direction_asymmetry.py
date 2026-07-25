"""XAU AI PLATFORM | Offline Research | Version 1.0.0.

Audit whether current-feed Train-only Stop replay evidence supports a stable
BUY/SELL asymmetry hypothesis. This diagnostic cannot authorize a filter.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from diagnose_current_feed_setup_funnel import sha256

EXPECTED_STATUS = "CURRENT_FEED_STOP_REPLAY_TRAIN_ONLY_NO_GO"
MINIMUM_DIRECTION_RECORDS = 40


def analyze(report: dict) -> dict:
    if report.get("status") != EXPECTED_STATUS:
        raise ValueError("Stop replay status changed")
    for lock in (
        "validation_dataset_used", "test_dataset_used", "runtime_changed",
        "risk_changed", "minimum_rr_changed", "deployment_authorized",
    ):
        if report.get(lock) is not False:
            raise ValueError(f"Stop replay lock changed: {lock}")
    if report.get("deployment_remains_no_go") is not True:
        raise ValueError("Stop replay NO-GO lock changed")

    candidates: dict = report["candidates"]
    audited: dict[str, dict] = {}
    positive_sell_candidates: list[str] = []
    confirmed: list[str] = []
    for name, candidate in candidates.items():
        by_direction = candidate.get("by_direction", {})
        buy = by_direction.get("TRADE_SETUP_BUY", {"records": 0, "mean_cost_aware_r": None})
        sell = by_direction.get("TRADE_SETUP_SELL", {"records": 0, "mean_cost_aware_r": None})
        buy_mean = buy.get("mean_cost_aware_r")
        sell_mean = sell.get("mean_cost_aware_r")
        gap = None if buy_mean is None or sell_mean is None else sell_mean - buy_mean
        enough = (
            int(buy.get("records", 0)) >= MINIMUM_DIRECTION_RECORDS
            and int(sell.get("records", 0)) >= MINIMUM_DIRECTION_RECORDS
        )
        sell_positive = sell_mean is not None and sell_mean > 0.0
        if sell_positive:
            positive_sell_candidates.append(name)
        # Confirmation is deliberately strict: enough evidence in both
        # directions, SELL positive, BUY negative, and overall candidate
        # already passed its frozen Train gate.
        direction_confirmed = bool(
            enough and sell_positive and buy_mean is not None and buy_mean < 0.0
            and candidate.get("train_gate_passed") is True
        )
        if direction_confirmed:
            confirmed.append(name)
        audited[name] = {
            "buy_records": int(buy.get("records", 0)),
            "buy_mean_cost_aware_r": buy_mean,
            "sell_records": int(sell.get("records", 0)),
            "sell_mean_cost_aware_r": sell_mean,
            "sell_minus_buy_mean_r": gap,
            "minimum_records_each_direction": MINIMUM_DIRECTION_RECORDS,
            "sample_gate_passed": enough,
            "sell_positive": sell_positive,
            "candidate_train_gate_passed": candidate.get("train_gate_passed") is True,
            "direction_asymmetry_confirmed": direction_confirmed,
        }
    return {
        "schema_version": "1.0.0",
        "status": "CURRENT_FEED_DIRECTION_ASYMMETRY_HYPOTHESIS_ONLY_NO_GO",
        "train_end_exclusive": report["train_end_exclusive"],
        "validation_dataset_used": False,
        "test_dataset_used": False,
        "runtime_changed": False,
        "risk_changed": False,
        "direction_filter_created": False,
        "deployment_authorized": False,
        "candidates": audited,
        "positive_sell_candidates": positive_sell_candidates,
        "confirmed_direction_asymmetry_candidates": confirmed,
        "new_independent_confirmation_required": True,
        "runtime_change_request_authorized": False,
        "deployment_remains_no_go": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stop-replay", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    arguments = parser.parse_args()
    report = json.loads(arguments.stop_replay.read_text(encoding="utf-8-sig"))
    result = analyze(report)
    result["source_stop_replay_sha256"] = sha256(arguments.stop_replay)
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
