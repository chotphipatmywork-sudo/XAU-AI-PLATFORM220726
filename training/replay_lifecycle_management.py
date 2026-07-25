"""XAU AI PLATFORM | Offline Research Replay | Version 1.0.0.

Replay frozen lifecycle-management candidates on mature M5 paths. The tool is
Train-only, fail-closed on M5 collisions, and cannot change Runtime or deploy.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter
from datetime import timedelta
from pathlib import Path
from typing import Any

from augment_pretrain_history import sha256
from build_lifecycle_path_requests import (
    CANDIDATES,
    COST_MULTIPLIERS,
    MANIFEST_SCHEMA_VERSION,
    REQUEST_COLUMNS,
    REQUEST_SCHEMA_VERSION,
)
from build_setup_outcome_dataset import as_bool, finite_float, parse_time
from diagnose_entry_stop_expectancy import (
    chronological_metrics,
    circular_moving_block_ci,
    grouped_metrics,
    outcome_metrics,
)


REPLAY_SCHEMA_VERSION = "1.0.0"
EXPORT_SCHEMA_VERSION = "1.0.0"
EXPORT_COLUMNS = (
    "export_schema_version", "request_id", "observation_time",
    "outcome_known_at", "symbol", "direction", "sequence", "bar_open",
    "open", "high", "low", "close", "tick_volume", "spread",
    "real_volume", "entry", "initial_stop", "target",
    "estimated_cost_points", "point_size", "plan_rr", "baseline_outcome",
    "path_within_mature_window", "deployment_authorized",
)


def read_exact_csv(path: Path, columns: tuple[str, ...]) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or tuple(reader.fieldnames) != columns:
            raise ValueError(f"Lifecycle replay schema mismatch: {path}")
        rows = list(reader)
    if not rows:
        raise ValueError(f"Lifecycle replay source is empty: {path}")
    return rows


def read_requests(
    request_path: Path, manifest_path: Path
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    if manifest.get("lifecycle_request_manifest_schema_version") != (
        MANIFEST_SCHEMA_VERSION
    ) or manifest.get("request_schema_version") != REQUEST_SCHEMA_VERSION:
        raise ValueError("Lifecycle request manifest schema changed")
    if manifest.get("request_file_sha256") != sha256(request_path):
        raise ValueError("Lifecycle request file hash mismatch")
    if tuple(manifest.get("candidates", [])) != CANDIDATES or tuple(
        manifest.get("cost_multipliers", [])
    ) != COST_MULTIPLIERS:
        raise ValueError("Lifecycle pre-registration changed")
    for flag in (
        "validation_dataset_read", "test_dataset_read", "model_training_performed",
        "runtime_changed", "risk_changed", "deployment_authorized",
    ):
        if manifest.get(flag) is not False:
            raise ValueError("Lifecycle request manifest violated protected state")

    raw_rows = read_exact_csv(request_path, REQUEST_COLUMNS)
    if manifest.get("requests") != len(raw_rows):
        raise ValueError("Lifecycle request count changed")
    requests: list[dict[str, Any]] = []
    seen: set[str] = set()
    previous = None
    for row in raw_rows:
        request_id = row["request_id"]
        observation = parse_time(row["observation_time"])
        known_at = parse_time(row["outcome_known_at"])
        if request_id in seen or (previous is not None and observation <= previous):
            raise ValueError("Lifecycle requests are duplicated or non-chronological")
        seen.add(request_id)
        previous = observation
        if row["request_schema_version"] != REQUEST_SCHEMA_VERSION or (
            as_bool(row["deployment_authorized"])
        ):
            raise ValueError("Lifecycle request row changed protected state")
        direction = row["direction"]
        entry = finite_float(row["entry"], "entry")
        stop = finite_float(row["initial_stop"], "initial_stop")
        target = finite_float(row["target"], "target")
        cost = finite_float(row["estimated_cost_points"], "cost")
        point = finite_float(row["point_size"], "point_size")
        plan_rr = finite_float(row["plan_rr"], "plan_rr")
        max_bars = int(finite_float(row["maximum_path_m5_bars"], "maximum bars"))
        buy = direction == "TRADE_SETUP_BUY"
        sell = direction == "TRADE_SETUP_SELL"
        if (not buy and not sell) or entry <= 0.0 or stop <= 0.0 or target <= 0.0:
            raise ValueError("Lifecycle request geometry is invalid")
        if (buy and not stop < entry < target) or (sell and not target < entry < stop):
            raise ValueError("Lifecycle request direction geometry is invalid")
        if cost < 0.0 or point <= 0.0 or plan_rr + 1e-9 < 2.0:
            raise ValueError("Lifecycle request cost/RR is invalid")
        if known_at <= observation or int(
            (known_at-observation).total_seconds()
        ) % 300 != 0 or not 1 <= max_bars <= 192:
            raise ValueError("Lifecycle request M5 window changed")
        if row["baseline_outcome"] not in {"TARGET_FIRST", "STOP_FIRST"}:
            raise ValueError("Lifecycle baseline outcome is invalid")
        requests.append({
            "request_id": request_id,
            "observation": observation,
            "observation_time": row["observation_time"],
            "known_at": known_at,
            "outcome_known_at": row["outcome_known_at"],
            "symbol": row["symbol"],
            "direction": direction,
            "entry": entry,
            "initial_stop": stop,
            "target": target,
            "estimated_cost_points": cost,
            "point_size": point,
            "plan_rr": plan_rr,
            "baseline_outcome": row["baseline_outcome"],
            "maximum_path_m5_bars": max_bars,
        })
    return requests, manifest


def close(left: float, right: float) -> bool:
    return math.isclose(left, right, rel_tol=1e-9, abs_tol=1e-6)


def read_paths(
    export_path: Path, requests: list[dict[str, Any]]
) -> dict[str, list[dict[str, Any]]]:
    indexed = {request["request_id"]: request for request in requests}
    grouped: dict[str, list[dict[str, Any]]] = {key: [] for key in indexed}
    for row in read_exact_csv(export_path, EXPORT_COLUMNS):
        if row["export_schema_version"] != EXPORT_SCHEMA_VERSION or (
            as_bool(row["deployment_authorized"])
        ) or not as_bool(row["path_within_mature_window"]):
            raise ValueError("Lifecycle M5 export changed protected state")
        request_id = row["request_id"]
        if request_id not in indexed:
            raise ValueError("Lifecycle M5 export has an unknown request")
        request = indexed[request_id]
        for field in (
            "observation_time", "outcome_known_at", "symbol", "direction",
            "baseline_outcome",
        ):
            if row[field] != request[field]:
                raise ValueError(f"Lifecycle M5 request parity failed: {field}")
        numeric_parity = {
            "entry": request["entry"],
            "initial_stop": request["initial_stop"],
            "target": request["target"],
            "estimated_cost_points": request["estimated_cost_points"],
            "point_size": request["point_size"],
            "plan_rr": request["plan_rr"],
        }
        if any(
            not close(finite_float(row[name], name), expected)
            for name, expected in numeric_parity.items()
        ):
            raise ValueError("Lifecycle M5 numeric request parity failed")
        bar_open = parse_time(row["bar_open"])
        values = {
            name: finite_float(row[name], name)
            for name in ("open", "high", "low", "close")
        }
        if not request["observation"] <= bar_open < request["known_at"]:
            raise ValueError("Lifecycle M5 bar crossed the mature window")
        if values["high"] < max(values["open"], values["close"]) or (
            values["low"] > min(values["open"], values["close"])
        ):
            raise ValueError("Lifecycle M5 OHLC is invalid")
        grouped[request_id].append({
            "sequence": int(finite_float(row["sequence"], "sequence")),
            "bar_open": bar_open,
            **values,
            "spread": finite_float(row["spread"], "spread"),
        })
    for request in requests:
        bars = grouped[request["request_id"]]
        if not bars or len(bars) > request["maximum_path_m5_bars"]:
            raise ValueError("Lifecycle M5 path is empty or too long")
        bars.sort(key=lambda bar: bar["sequence"])
        if [bar["sequence"] for bar in bars] != list(range(1, len(bars)+1)):
            raise ValueError("Lifecycle M5 path sequence changed")
        if bars[0]["bar_open"] != request["observation"] or (
            bars[-1]["bar_open"] + timedelta(minutes=5) != request["known_at"]
        ):
            raise ValueError("Lifecycle M5 path boundary is incomplete")
        if any(
            bars[index]["bar_open"] <= bars[index-1]["bar_open"]
            for index in range(1, len(bars))
        ):
            raise ValueError("Lifecycle M5 path is non-chronological")
    return grouped


def barrier_hits(
    direction: str, bar: dict[str, Any], stop: float, target: float
) -> tuple[bool, bool]:
    if direction == "TRADE_SETUP_BUY":
        return bar["low"] <= stop, bar["high"] >= target
    return bar["high"] >= stop, bar["low"] <= target


def managed_return_r(
    direction: str, entry: float, exit_price: float, initial_risk: float,
    cost_price: float,
) -> float:
    movement = exit_price-entry if direction == "TRADE_SETUP_BUY" else entry-exit_price
    return (movement-cost_price)/(initial_risk+cost_price)


def simulate_path(
    request: dict[str, Any],
    bars: list[dict[str, Any]],
    candidate: str,
    cost_multiplier: float,
) -> dict[str, Any]:
    if candidate not in CANDIDATES or cost_multiplier not in COST_MULTIPLIERS:
        raise ValueError("Lifecycle replay candidate or cost level changed")
    direction = request["direction"]
    entry = float(request["entry"])
    initial_stop = float(request["initial_stop"])
    target = float(request["target"])
    risk = abs(entry-initial_stop)
    cost_price = (
        float(request["estimated_cost_points"])
        * float(request["point_size"])
        * cost_multiplier
    )
    active_stop = initial_stop
    stop_stage = "INITIAL"
    for bar in bars:
        stop_hit, target_hit = barrier_hits(direction, bar, active_stop, target)
        if stop_hit and target_hit:
            return {
                "outcome": "AMBIGUOUS",
                "realized_r": None,
                "reason": "target_and_active_stop_same_m5_bar",
            }
        if target_hit:
            return {
                "outcome": "TARGET_FIRST",
                "realized_r": managed_return_r(
                    direction, entry, target, risk, cost_price
                ),
                "reason": "target_hit",
            }
        if stop_hit:
            return {
                "outcome": (
                    "STOP_FIRST" if stop_stage == "INITIAL" else "MANAGED_STOP"
                ),
                "realized_r": managed_return_r(
                    direction, entry, active_stop, risk, cost_price
                ),
                "reason": stop_stage,
            }

        if candidate == "CURRENT_BASELINE":
            continue
        favorable_close_r = (
            (bar["close"]-entry)/risk
            if direction == "TRADE_SETUP_BUY"
            else (entry-bar["close"])/risk
        )
        if candidate == "COST_COVERED_BREAKEVEN_AFTER_CLOSE_1R" and (
            favorable_close_r >= 1.0
        ):
            proposed = entry+cost_price if direction == "TRADE_SETUP_BUY" else entry-cost_price
            active_stop = max(active_stop, proposed) if direction == "TRADE_SETUP_BUY" else min(active_stop, proposed)
            stop_stage = "COST_COVERED_BREAKEVEN"
        elif candidate == "TWO_STAGE_RATCHET_AFTER_CLOSE_1R_2R":
            if favorable_close_r >= 2.0:
                proposed = entry+risk if direction == "TRADE_SETUP_BUY" else entry-risk
                active_stop = max(active_stop, proposed) if direction == "TRADE_SETUP_BUY" else min(active_stop, proposed)
                stop_stage = "LOCKED_1R"
            elif favorable_close_r >= 1.0:
                proposed = entry+cost_price if direction == "TRADE_SETUP_BUY" else entry-cost_price
                active_stop = max(active_stop, proposed) if direction == "TRADE_SETUP_BUY" else min(active_stop, proposed)
                stop_stage = "COST_COVERED_BREAKEVEN"
    return {"outcome": "UNRESOLVED", "realized_r": None, "reason": "path_ended"}


def summarize_results(results: list[dict[str, Any]]) -> dict[str, Any]:
    valid = [result for result in results if result["realized_r"] is not None]
    accounting = Counter(result["outcome"] for result in results)
    if len(valid) < 4:
        return {
            "requests": len(results),
            "effective_records": len(valid),
            "accounting": dict(sorted(accounting.items())),
            "metrics": None,
            "mean_r_ci95": None,
            "by_direction": {},
            "chronological_blocks": [],
        }
    metrics = outcome_metrics(valid)
    directions = grouped_metrics(valid, "direction")
    blocks = chronological_metrics(valid)
    return {
        "requests": len(results),
        "effective_records": len(valid),
        "accounting": dict(sorted(accounting.items())),
        "metrics": metrics,
        "mean_r_ci95": circular_moving_block_ci(
            [float(result["realized_r"]) for result in valid]
        ),
        "by_direction": directions,
        "chronological_blocks": blocks,
        "positive_directions": sum(
            value["mean_cost_aware_r"] > 0.0 for value in directions.values()
        ),
        "positive_chronological_blocks": sum(
            value["mean_cost_aware_r"] > 0.0 for value in blocks
        ),
    }


def replay(
    request_path: Path,
    manifest_path: Path,
    export_path: Path,
) -> dict[str, Any]:
    requests, manifest = read_requests(request_path, manifest_path)
    paths = read_paths(export_path, requests)
    candidate_results: dict[str, dict[str, Any]] = {}
    baseline_parity_failures: list[str] = []
    raw: dict[str, dict[float, dict[str, Any]]] = {}
    for candidate in CANDIDATES:
        raw[candidate] = {}
        candidate_results[candidate] = {}
        for multiplier in COST_MULTIPLIERS:
            results: list[dict[str, Any]] = []
            for request in requests:
                result = simulate_path(
                    request, paths[request["request_id"]], candidate, multiplier
                )
                result.update({
                    "observation_time": request["observation_time"],
                    "direction": request["direction"],
                })
                results.append(result)
                if candidate == "CURRENT_BASELINE" and multiplier == 1.0 and (
                    result["outcome"] != request["baseline_outcome"]
                ):
                    baseline_parity_failures.append(request["request_id"])
            raw[candidate][multiplier] = {"results": results}
            candidate_results[candidate][str(multiplier)] = summarize_results(results)
    if baseline_parity_failures:
        raise ValueError(
            "Lifecycle M5 baseline parity failed: " + ",".join(baseline_parity_failures)
        )

    passing: list[str] = []
    gate_reports: dict[str, dict[str, bool]] = {}
    for candidate in CANDIDATES[1:]:
        base = candidate_results[candidate]["1.0"]
        metrics = base["metrics"]
        interval = base["mean_r_ci95"]
        gates = {
            "effective_sample": base["effective_records"] >= 200,
            "positive_expectancy": (
                metrics is not None and metrics["mean_cost_aware_r"] > 0.0
                and interval is not None and interval["lower"] > 0.0
            ),
            "temporal_stability": base.get("positive_chronological_blocks") == 4,
            "direction_robustness": base.get("positive_directions") == 2,
            "profit_factor": metrics is not None and metrics["profit_factor"] is not None
            and metrics["profit_factor"] >= 1.10,
            "drawdown_tail": metrics is not None
            and metrics["maximum_drawdown_r"] <= 25.0
            and metrics["longest_loss_sequence"] <= 10,
            "cost_stress": all(
                candidate_results[candidate][str(multiplier)]["metrics"] is not None
                and candidate_results[candidate][str(multiplier)]["metrics"]["mean_cost_aware_r"] > 0.0
                and candidate_results[candidate][str(multiplier)]["mean_r_ci95"] is not None
                and candidate_results[candidate][str(multiplier)]["mean_r_ci95"]["lower"] > 0.0
                for multiplier in COST_MULTIPLIERS
            ),
        }
        gates["train_gate_passed"] = all(gates.values())
        gate_reports[candidate] = gates
        if gates["train_gate_passed"]:
            passing.append(candidate)

    return {
        "lifecycle_replay_schema_version": REPLAY_SCHEMA_VERSION,
        "status": "LIFECYCLE_MANAGEMENT_TRAIN_ONLY_NO_GO",
        "request_file_sha256": sha256(request_path),
        "request_manifest_sha256": sha256(manifest_path),
        "m5_path_export_sha256": sha256(export_path),
        "requests": len(requests),
        "baseline_parity_valid": True,
        "candidate_results": candidate_results,
        "candidate_train_gates": gate_reports,
        "train_gate_passing_candidates": passing,
        "locked_validation_candidate_ready": bool(passing),
        "validation_dataset_read": False,
        "test_dataset_read": False,
        "model_training_performed": False,
        "runtime_changed": False,
        "risk_changed": False,
        "runtime_change_request_authorized": False,
        "deployment_authorized": False,
        "deployment_remains_no_go": True,
        "pre_registration": {
            "candidates": manifest["candidates"],
            "cost_multipliers": manifest["cost_multipliers"],
            "frozen_train_gates": manifest["frozen_train_gates"],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", required=True, type=Path)
    parser.add_argument("--request-manifest", required=True, type=Path)
    parser.add_argument("--m5-path-export", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    arguments = parser.parse_args()
    report = replay(
        arguments.request, arguments.request_manifest, arguments.m5_path_export
    )
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
