"""Evaluate matured Shadow decisions with Label Schema 1.1 triple barriers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from analyze_shadow_run import DECISION_COLUMNS, read_rows
from train_classifier import evaluation_metrics, meets_evaluation_contract


HORIZON_BARS = 16
BARRIER_ATR_MULTIPLIER = 1.5
DECISION_TO_LABEL = {
    "DECISION_SELL": -1,
    "DECISION_WAIT": 0,
    "DECISION_BUY": 1,
}


def generate_label(
    rows: list[dict[str, str]], entry_index: int
) -> tuple[int | None, str]:
    entry = rows[entry_index]
    entry_price = float(entry["bar_close"])
    atr = float(entry["atr"])
    if entry_price <= 0.0 or atr <= 0.0:
        return None, "invalid_entry"
    if entry_index + HORIZON_BARS >= len(rows):
        return None, "not_matured"
    upper = entry_price + atr * BARRIER_ATR_MULTIPLIER
    lower = entry_price - atr * BARRIER_ATR_MULTIPLIER
    for future_index in range(entry_index + 1, entry_index + HORIZON_BARS + 1):
        high = float(rows[future_index]["bar_high"])
        low = float(rows[future_index]["bar_low"])
        hit_upper = high >= upper
        hit_lower = low <= lower
        if hit_upper and hit_lower:
            return None, "ambiguous_barrier"
        if hit_upper:
            return 1, "upper_barrier"
        if hit_lower:
            return -1, "lower_barrier"
    return 0, "horizon_hold"


def evaluate(path: Path) -> dict[str, object]:
    rows = read_rows(path, DECISION_COLUMNS)
    keys = [(row["symbol"], row["timeframe"], row["closed_bar"]) for row in rows]
    if len(keys) != len(set(keys)):
        raise ValueError("Duplicate Shadow closed-bar key")

    actual: list[int] = []
    predicted: list[int] = []
    excluded = {
        "not_matured": 0,
        "invalid_entry": 0,
        "ambiguous_barrier": 0,
        "invalid_decision": 0,
    }
    label_reasons: dict[str, int] = {
        "upper_barrier": 0,
        "lower_barrier": 0,
        "horizon_hold": 0,
    }
    for index, row in enumerate(rows):
        decision = DECISION_TO_LABEL.get(row["decision"])
        if decision is None:
            excluded["invalid_decision"] += 1
            continue
        label, reason = generate_label(rows, index)
        if label is None:
            excluded[reason] += 1
            continue
        actual.append(label)
        predicted.append(decision)
        label_reasons[reason] += 1

    metrics = evaluation_metrics(actual, predicted) if actual else None
    return {
        "evaluation_stage": "matured_forward_shadow_observations_only",
        "training_performed": False,
        "historical_validation_dataset_used": False,
        "historical_test_dataset_used": False,
        "feature_schema_version": "4.0.0",
        "label_schema_version": "1.1.0",
        "label_horizon_bars": HORIZON_BARS,
        "label_barrier_atr_multiplier": BARRIER_ATR_MULTIPLIER,
        "model_status": "DEVELOPMENT_HEURISTIC_MODEL_NO_GO",
        "total_logged_rows": len(rows),
        "matured_evaluation_rows": len(actual),
        "excluded_rows": excluded,
        "label_reason_distribution": label_reasons,
        "metrics": metrics,
        "model_quality_gate_met": (
            meets_evaluation_contract(metrics) if metrics is not None else False
        ),
        "shadow_deployment_authorized": False,
        "live_deployment_authorized": False,
        "limitations": [
            "This evaluates the development heuristic currently producing Shadow intent.",
            "A favorable result cannot authorize deployment or replace nested research.",
            "The newest 16 observations are excluded until their label horizon matures.",
        ],
    }


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--decisions", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()
    report = evaluate(arguments.decisions)
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
