"""XAU AI PLATFORM | Offline Research Diagnostic | Version 1.0.0.

Measure effective-sample Entry/Stop path behavior, expectancy uncertainty, and
loss tails without selecting a strategy, opening Validation/Test, or changing
Runtime/Risk/Deployment state.
"""

from __future__ import annotations

import argparse
import json
import math
import random
from collections import Counter
from pathlib import Path
from typing import Any

from audit_effective_setup_sample import (
    AUDIT_SCHEMA_VERSION,
    METHOD,
    maximum_non_overlapping,
)
from augment_pretrain_history import read_trainable, sha256
from build_setup_outcome_dataset import finite_float, parse_time


DIAGNOSTIC_SCHEMA_VERSION = "1.0.0"
BOOTSTRAP_SEED = 20260722
BOOTSTRAP_SAMPLES = 10_000


def valid_hash(value: str, name: str) -> str:
    normalized = value.strip().upper()
    if len(normalized) != 64 or any(
        character not in "0123456789ABCDEF" for character in normalized
    ):
        raise ValueError(f"Entry/Stop {name} SHA-256 is invalid")
    return normalized


def quantile(values: list[float], fraction: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = fraction * (len(ordered) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def distribution(values: list[float]) -> dict[str, float | int | None]:
    return {
        "records": len(values),
        "minimum": min(values) if values else None,
        "p25": quantile(values, 0.25),
        "median": quantile(values, 0.50),
        "p75": quantile(values, 0.75),
        "maximum": max(values) if values else None,
        "mean": sum(values) / len(values) if values else None,
    }


def circular_moving_block_ci(
    values: list[float],
    samples: int = BOOTSTRAP_SAMPLES,
    seed: int = BOOTSTRAP_SEED,
) -> dict[str, float | int]:
    if len(values) < 4:
        raise ValueError("Entry/Stop bootstrap requires at least four records")
    if samples < 100:
        raise ValueError("Entry/Stop bootstrap sample count is too small")
    block_length = max(2, math.ceil(len(values) ** (1.0 / 3.0)))
    generator = random.Random(seed)
    means: list[float] = []
    count = len(values)
    for _ in range(samples):
        total = 0.0
        collected = 0
        while collected < count:
            start = generator.randrange(count)
            take = min(block_length, count - collected)
            total += sum(values[(start + offset) % count] for offset in range(take))
            collected += take
        means.append(total / count)
    lower = quantile(means, 0.025)
    upper = quantile(means, 0.975)
    if lower is None or upper is None:
        raise AssertionError("Entry/Stop bootstrap interval is empty")
    return {
        "method": "deterministic_circular_moving_block_percentile",
        "confidence": 0.95,
        "seed": seed,
        "bootstrap_samples": samples,
        "block_length_records": block_length,
        "lower": lower,
        "upper": upper,
    }


def maximum_drawdown(values: list[float]) -> float:
    equity = 0.0
    peak = 0.0
    drawdown = 0.0
    for value in values:
        equity += value
        peak = max(peak, equity)
        drawdown = max(drawdown, peak - equity)
    return drawdown


def longest_loss_sequence(values: list[float]) -> int:
    longest = 0
    current = 0
    for value in values:
        if value < 0.0:
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return longest


def outcome_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    returns = [float(row["realized_r"]) for row in rows]
    outcomes = Counter(str(row["outcome"]) for row in rows)
    positives = sum(value for value in returns if value > 0.0)
    negatives = -sum(value for value in returns if value < 0.0)
    return {
        "records": len(rows),
        "outcomes": dict(sorted(outcomes.items())),
        "target_rate": outcomes.get("TARGET_FIRST", 0) / len(rows),
        "mean_cost_aware_r": sum(returns) / len(returns),
        "cumulative_r": sum(returns),
        "profit_factor": positives / negatives if negatives > 0.0 else None,
        "maximum_drawdown_r": maximum_drawdown(returns),
        "longest_loss_sequence": longest_loss_sequence(returns),
    }


def load_audited_effective_rows(
    train_path: Path,
    expected_train_sha256: str,
    audit_path: Path,
    expected_audit_sha256: str,
) -> tuple[list[dict[str, Any]], dict[str, Any], str, str]:
    upper_name = train_path.name.upper()
    if "TRAIN" not in upper_name or "VALIDATION" in upper_name or "TEST" in upper_name:
        raise ValueError("Entry/Stop diagnostic accepts Train evidence only")
    train_hash = sha256(train_path)
    if train_hash != valid_hash(expected_train_sha256, "Train"):
        raise ValueError("Entry/Stop Train SHA-256 mismatch")
    audit_hash = sha256(audit_path)
    if audit_hash != valid_hash(expected_audit_sha256, "audit"):
        raise ValueError("Entry/Stop audit SHA-256 mismatch")

    audit = json.loads(audit_path.read_text(encoding="utf-8-sig"))
    if audit.get("effective_sample_audit_schema_version") != AUDIT_SCHEMA_VERSION:
        raise ValueError("Entry/Stop Effective Sample audit schema changed")
    if audit.get("method") != METHOD or audit.get("source_train_sha256") != train_hash:
        raise ValueError("Entry/Stop Effective Sample contract changed")
    for flag in (
        "validation_dataset_read", "test_dataset_read", "model_training_performed",
        "runtime_changed", "risk_changed", "deployment_authorized",
    ):
        if audit.get(flag) is not False:
            raise ValueError("Entry/Stop Effective Sample audit violated protected state")

    raw_rows = read_trainable(train_path)
    intervals: list[dict[str, Any]] = []
    for row in raw_rows:
        plan_rr = finite_float(row["plan_rr"], "plan_rr")
        stored_gross_r = finite_float(row["realized_r"], "realized_r")
        mfe_r = finite_float(row["mfe_r"], "mfe_r")
        mae_r = finite_float(row["mae_r"], "mae_r")
        if plan_rr + 1e-9 < 2.0 or mfe_r < 0.0 or mae_r < 0.0:
            raise ValueError("Entry/Stop path metric is invalid")
        entry = finite_float(row["plan_entry"], "plan_entry")
        stop = finite_float(row["plan_stop"], "plan_stop")
        target = finite_float(row["plan_target"], "plan_target")
        gross_risk = abs(entry - stop)
        if gross_risk <= 0.0:
            raise ValueError("Entry/Stop gross risk is invalid")
        expected_gross_r = (
            abs(target - entry) / gross_risk
            if row["outcome"] == "TARGET_FIRST" else
            -1.0 if row["outcome"] == "STOP_FIRST" else 0.0
        )
        if not math.isclose(
            stored_gross_r, expected_gross_r, rel_tol=1e-9, abs_tol=1e-9
        ):
            raise ValueError("Entry/Stop stored gross R is inconsistent with outcome")
        cost_aware_realized_r = (
            plan_rr if row["outcome"] == "TARGET_FIRST" else
            -1.0 if row["outcome"] == "STOP_FIRST" else 0.0
        )
        intervals.append({
            "start": parse_time(row["observation_time"]),
            "end": parse_time(row["outcome_known_at"]),
            "observation_time": row["observation_time"],
            "outcome_known_at": row["outcome_known_at"],
            "direction": row["direction"],
            "outcome": row["outcome"],
            "plan_rr": plan_rr,
            "entry": entry,
            "stop": stop,
            "target": target,
            "estimated_cost_points": finite_float(
                row["estimated_cost_points"], "estimated_cost_points"
            ),
            "point_size": finite_float(row["point_size"], "point_size"),
            "bars_observed": int(finite_float(row["bars_observed"], "bars_observed")),
            "realized_r": cost_aware_realized_r,
            "mfe_r": mfe_r,
            "mae_r": mae_r,
        })
    selected, excluded = maximum_non_overlapping(intervals)
    excluded_times = {item["observation_time"] for item in excluded}
    audited_excluded = {
        str(item.get("observation_time"))
        for item in audit.get("excluded_intervals", [])
        if isinstance(item, dict)
    }
    if excluded_times != audited_excluded:
        raise ValueError("Entry/Stop Effective Sample exclusion parity failed")
    if audit.get("raw_mature_records") != len(raw_rows) or (
        audit.get("effective_sample_records") != len(selected)
    ):
        raise ValueError("Entry/Stop Effective Sample counts changed")
    if not audit.get("effective_sample_requirement_met"):
        raise ValueError("Entry/Stop Effective Sample requirement is not met")
    return sorted(selected, key=lambda row: row["start"]), audit, train_hash, audit_hash


def grouped_metrics(rows: list[dict[str, Any]], key: str) -> dict[str, Any]:
    return {
        value: outcome_metrics([row for row in rows if str(row[key]) == value])
        for value in sorted({str(row[key]) for row in rows})
    }


def chronological_metrics(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    for index in range(4):
        start = index * len(rows) // 4
        end = (index + 1) * len(rows) // 4
        block = rows[start:end]
        if not block:
            raise ValueError("Entry/Stop chronological block is empty")
        blocks.append({
            "block": index + 1,
            "first_observation": block[0]["observation_time"],
            "last_observation": block[-1]["observation_time"],
            **outcome_metrics(block),
        })
    return blocks


def build_diagnostic(
    rows: list[dict[str, Any]],
    train_hash: str,
    audit_hash: str,
    bootstrap_samples: int = BOOTSTRAP_SAMPLES,
) -> dict[str, Any]:
    returns = [float(row["realized_r"]) for row in rows]
    winners = [row for row in rows if row["outcome"] == "TARGET_FIRST"]
    losers = [row for row in rows if row["outcome"] == "STOP_FIRST"]
    loser_mfe = [float(row["mfe_r"]) for row in losers]
    winner_mae = [float(row["mae_r"]) for row in winners]
    overall = outcome_metrics(rows)
    interval = circular_moving_block_ci(returns, bootstrap_samples)
    chronological = chronological_metrics(rows)
    directions = grouped_metrics(rows, "direction")
    return {
        "entry_stop_diagnostic_schema_version": DIAGNOSTIC_SCHEMA_VERSION,
        "diagnostic_stage": "effective_train_entry_stop_expectancy_tail_only",
        "source_train_sha256": train_hash,
        "effective_sample_audit_sha256": audit_hash,
        "effective_sample_records": len(rows),
        "overall": overall,
        "mean_r_ci95": interval,
        "mfe_r": distribution([float(row["mfe_r"]) for row in rows]),
        "mae_r": distribution([float(row["mae_r"]) for row in rows]),
        "plan_rr": distribution([float(row["plan_rr"]) for row in rows]),
        "stop_first_path": {
            "records": len(losers),
            "mfe_r": distribution(loser_mfe),
            "mfe_below_0_5r": sum(value < 0.5 for value in loser_mfe),
            "mfe_at_least_0_5r": sum(value >= 0.5 for value in loser_mfe),
            "mfe_at_least_1_0r": sum(value >= 1.0 for value in loser_mfe),
            "mfe_at_least_2_0r": sum(value >= 2.0 for value in loser_mfe),
        },
        "target_first_path": {
            "records": len(winners),
            "mae_r": distribution(winner_mae),
            "mae_at_least_0_5r": sum(value >= 0.5 for value in winner_mae),
            "mae_at_least_0_75r": sum(value >= 0.75 for value in winner_mae),
        },
        "by_direction": directions,
        "chronological_blocks": chronological,
        "positive_directions": sum(
            metrics["mean_cost_aware_r"] > 0.0 for metrics in directions.values()
        ),
        "positive_chronological_blocks": sum(
            block["mean_cost_aware_r"] > 0.0 for block in chronological
        ),
        "entry_stop_candidate_selected": False,
        "drawdown_gate_evaluated": False,
        "cost_stress_evaluated": False,
        "validation_dataset_read": False,
        "test_dataset_read": False,
        "model_training_performed": False,
        "runtime_changed": False,
        "risk_changed": False,
        "deployment_authorized": False,
        "status": "ENTRY_STOP_DIAGNOSTIC_TRAIN_ONLY_NO_GO",
        "limitations": [
            "MFE/MAE are bar-path excursions, not broker fill or slippage measurements.",
            "The diagnostic describes the current accepted plans and does not label rejected counterfactual Entries or Stops.",
            "No drawdown or cost-stress threshold is selected after observing these results.",
        ],
    }


def diagnose(
    train_path: Path,
    expected_train_sha256: str,
    audit_path: Path,
    expected_audit_sha256: str,
    bootstrap_samples: int = BOOTSTRAP_SAMPLES,
) -> dict[str, Any]:
    rows, _, train_hash, audit_hash = load_audited_effective_rows(
        train_path, expected_train_sha256, audit_path, expected_audit_sha256
    )
    return build_diagnostic(rows, train_hash, audit_hash, bootstrap_samples)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", required=True, type=Path)
    parser.add_argument("--expected-train-sha256", required=True)
    parser.add_argument("--effective-sample-audit", required=True, type=Path)
    parser.add_argument("--expected-audit-sha256", required=True)
    parser.add_argument("--output", required=True, type=Path)
    arguments = parser.parse_args()
    report = diagnose(
        arguments.train,
        arguments.expected_train_sha256,
        arguments.effective_sample_audit,
        arguments.expected_audit_sha256,
    )
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
