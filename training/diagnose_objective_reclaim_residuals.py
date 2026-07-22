"""XAU AI PLATFORM | Offline Research | Version 1.0.0.

Describe residual failures after the 0.10 ATR reclaim contract using Train only.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from analyze_shadow_run import FEATURE_COLUMNS
from build_setup_outcome_dataset import (
    OUTCOME_AUDIT_COLUMNS,
    SETUP_AUDIT_COLUMNS,
    as_bool,
    finite_float,
    parse_time,
)


@dataclass(frozen=True)
class Hypothesis:
    name: str
    rule: str
    expected: str
    predicate: Callable[[dict[str, Any]], bool]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def directional_trend(sample: dict[str, Any]) -> float:
    values = [sample["features"][name] for name in (
        "trend_regime", "trend_momentum", "trend_slope"
    )]
    if sample["direction"] == "TRADE_SETUP_SELL":
        values = [100.0 - value for value in values]
    return sum(values) / len(values)


def hypotheses() -> tuple[Hypothesis, ...]:
    return (
        Hypothesis("buy_direction", "direction == BUY", "exploratory",
                   lambda row: row["direction"] == "TRADE_SETUP_BUY"),
        Hypothesis("sell_direction", "direction == SELL", "exploratory",
                   lambda row: row["direction"] == "TRADE_SETUP_SELL"),
        Hypothesis("stronger_reclaim", "reclaim_distance_atr >= 0.20", "positive",
                   lambda row: row["reclaim_distance_atr"] >= 0.20),
        Hypothesis("reclaim_dominates_sweep", "reclaim/sweep >= 1.0", "positive",
                   lambda row: row["reclaim_to_sweep"] >= 1.0),
        Hypothesis("deep_sweep", "sweep_penetration_atr >= 0.10", "positive",
                   lambda row: row["sweep_penetration_atr"] >= 0.10),
        Hypothesis("early_session", "session_progress <= 25", "positive",
                   lambda row: row["features"]["session_progress"] <= 25.0),
        Hypothesis("late_session", "session_progress >= 75", "negative",
                   lambda row: row["features"]["session_progress"] >= 75.0),
        Hypothesis("strong_directional_trend", "directional Trend mean >= 70", "positive",
                   lambda row: directional_trend(row) >= 70.0),
        Hypothesis("high_liquidity_activity", "liquidity_activity >= 70", "positive",
                   lambda row: row["features"]["liquidity_activity"] >= 70.0),
        Hypothesis("rr_at_least_three", "plan_rr >= 3.0", "exploratory",
                   lambda row: row["plan_rr"] >= 3.0),
    )


def read_train(path: Path) -> list[dict[str, Any]]:
    name = path.name.upper()
    if "VALIDATION" in name or "TEST" in name or "TRAIN" not in name:
        raise ValueError("Residual diagnostic accepts Train evidence only")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or tuple(reader.fieldnames) != OUTCOME_AUDIT_COLUMNS:
            raise ValueError("Unexpected residual Train schema")
        rows = list(reader)
    samples: list[dict[str, Any]] = []
    previous: datetime | None = None
    for row in rows:
        observation = parse_time(row["observation_time"])
        if previous is not None and observation <= previous:
            raise ValueError("Residual Train is not chronological")
        if not as_bool(row["trainable"]):
            raise ValueError("Residual Train contains quarantined evidence")
        features = {name: finite_float(row[name], name) for name in FEATURE_COLUMNS}
        if any(value < 0.0 or value > 100.0 for value in features.values()):
            raise ValueError("Residual Train feature is outside [0,100]")
        outcome = row["outcome"]
        plan_rr = finite_float(row["plan_rr"], "plan_rr")
        samples.append({
            "observation": observation,
            "direction": row["direction"],
            "features": features,
            "plan_rr": plan_rr,
            "target": outcome == "TARGET_FIRST",
            "return_r": plan_rr if outcome == "TARGET_FIRST" else -1.0,
        })
        previous = observation
    if not samples:
        raise ValueError("Residual Train is empty")
    return samples


def join_geometry(samples: list[dict[str, Any]], setup_path: Path) -> None:
    by_time = {sample["observation"]: sample for sample in samples}
    matched: set[datetime] = set()
    with setup_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or tuple(reader.fieldnames) != SETUP_AUDIT_COLUMNS:
            raise ValueError("Unexpected residual Setup Audit schema")
        for row in reader:
            observation = parse_time(row["observation_time"])
            sample = by_time.get(observation)
            if sample is None:
                continue
            if observation in matched or not as_bool(row["plan_available"]):
                raise ValueError("Residual Setup join is duplicate or unavailable")
            sweep = finite_float(row["sweep_penetration_atr"], "sweep")
            reclaim = finite_float(row["reclaim_distance_atr"], "reclaim")
            if sweep <= 0.0 or reclaim < 0.10 - 1e-9:
                raise ValueError("Residual Setup violates the 0.10 ATR contract")
            sample["sweep_penetration_atr"] = sweep
            sample["reclaim_distance_atr"] = reclaim
            sample["reclaim_to_sweep"] = reclaim / sweep
            matched.add(observation)
    if len(matched) != len(samples):
        raise ValueError("Residual Setup Audit does not cover every Train plan")


def metrics(rows: list[dict[str, Any]]) -> dict[str, float | int | None]:
    if not rows:
        return {"records": 0, "target_rate": None, "mean_r": None}
    return {
        "records": len(rows),
        "target_rate": sum(row["target"] for row in rows) / len(rows),
        "mean_r": sum(row["return_r"] for row in rows) / len(rows),
    }


def evaluate(samples: list[dict[str, Any]], hypothesis: Hypothesis) -> dict[str, Any]:
    blocks = [samples[index * len(samples) // 3:(index + 1) * len(samples) // 3]
              for index in range(3)]
    reports: list[dict[str, Any]] = []
    for index, block in enumerate(blocks, start=1):
        selected = [row for row in block if hypothesis.predicate(row)]
        base = metrics(block)
        chosen = metrics(selected)
        reports.append({
            "block": index,
            "base": base,
            "matched": chosen,
            "target_rate_lift": None if chosen["target_rate"] is None else
                float(chosen["target_rate"]) - float(base["target_rate"]),
            "mean_r_lift": None if chosen["mean_r"] is None else
                float(chosen["mean_r"]) - float(base["mean_r"]),
        })
    selected_all = [row for row in samples if hypothesis.predicate(row)]
    base_all = metrics(samples)
    chosen_all = metrics(selected_all)
    signs = [(report["target_rate_lift"], report["mean_r_lift"]) for report in reports]
    support = len(selected_all) >= 20 and all(
        int(report["matched"]["records"]) >= 5 for report in reports
    )
    positive = all(a is not None and a > 0 and b is not None and b > 0 for a, b in signs)
    negative = all(a is not None and a < 0 and b is not None and b < 0 for a, b in signs)
    expected_sign = (
        hypothesis.expected == "positive" and positive
    ) or (
        hypothesis.expected == "negative" and negative
    )
    target_lift = None if chosen_all["target_rate"] is None else (
        float(chosen_all["target_rate"]) - float(base_all["target_rate"])
    )
    mean_r_lift = None if chosen_all["mean_r"] is None else (
        float(chosen_all["mean_r"]) - float(base_all["mean_r"])
    )
    material_effect = (
        target_lift is not None and abs(target_lift) >= 0.05 and
        mean_r_lift is not None and abs(mean_r_lift) >= 0.10
    )
    return {
        "name": hypothesis.name,
        "fixed_rule": hypothesis.rule,
        "expected": hypothesis.expected,
        "aggregate_base": base_all,
        "aggregate_matched": chosen_all,
        "aggregate_target_rate_lift": target_lift,
        "aggregate_mean_r_lift": mean_r_lift,
        "temporal_blocks": reports,
        "support_met": support,
        "expected_sign_met_all_blocks": expected_sign,
        "material_effect_met": material_effect,
        "fresh_confirmation_priority": support and expected_sign and material_effect,
    }


def run_diagnostic(samples: list[dict[str, Any]]) -> dict[str, Any]:
    if any("reclaim_distance_atr" not in sample for sample in samples):
        raise ValueError("Residual diagnostic is missing Setup geometry")
    results = [evaluate(samples, item) for item in hypotheses()]
    priorities = [item["name"] for item in results if item["fresh_confirmation_priority"]]
    return {
        "diagnostic_stage": "objective_reclaim_residual_train_only_exploratory",
        "train_records": len(samples),
        "minimum_ranking_records": 200,
        "ranking_sample_gate_met": len(samples) >= 200,
        "validation_dataset_used": False,
        "test_dataset_used": False,
        "model_training_performed": False,
        "hypotheses": results,
        "fresh_confirmation_priorities": priorities,
        "setup_contract_change_authorized": False,
        "runtime_integration_authorized": False,
        "deployment_authorized": False,
        "limitations": [
            "This reuses historical Train evidence and is exploratory only.",
            "A priority requires new untouched evidence before contract review.",
            "The 200-record ranking gate remains unchanged.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", required=True, type=Path)
    parser.add_argument("--setup-audit", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    arguments = parser.parse_args()
    samples = read_train(arguments.train)
    join_geometry(samples, arguments.setup_audit)
    report = run_diagnostic(samples)
    report["train_sha256"] = sha256(arguments.train)
    report["setup_audit_sha256"] = sha256(arguments.setup_audit)
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({
        "diagnostic_stage": report["diagnostic_stage"],
        "train_records": report["train_records"],
        "ranking_sample_gate_met": report["ranking_sample_gate_met"],
        "fresh_confirmation_priorities": report["fresh_confirmation_priorities"],
        "setup_contract_change_authorized": False,
        "deployment_authorized": False,
        "output": str(arguments.output),
    }, indent=2))


if __name__ == "__main__":
    main()
