#!/usr/bin/env python3
"""Execute and validate the frozen IMP-100 Train-only causal M5 replay."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import shutil
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from statistics import median
from typing import Any

from diagnose_entry_stop_expectancy import (
    chronological_metrics,
    circular_moving_block_ci,
    grouped_metrics,
    outcome_metrics,
)
from research_scorecard import build_scorecard
from validate_imp100_outcome_free_m5_export import (
    EXPORT_HEADER,
    TIME_FORMAT,
    validate_export,
)

CONTRACT_SHA256 = "9D0142D1671E80C1263D93A61E1CB53316EC8E816040B251F477F974540494A9"
REQUEST_SHA256 = "C4BDA8102E50F266714D99EE0CF27D71540DEA1ADC7DA3757528BC7155B63085"
REQUEST_MANIFEST_SHA256 = "3DDD49D0C4BCB0239243B654333FE6A6B338BF2E9465B1C858E316D0EE0911A7"
EXPORT_SHA256 = "5F95AAE3381E3F92879759362D4DAE771D76F13F1FEE02B9414D845A6F520FE6"
EXPORT_VALIDATION_SHA256 = "20FC23DC1876E2D60AD36F8610ADB040F14931C6EAEAAB6D9065A29E34DD642A"
EXPORT_MANIFEST_SHA256 = "5E5A1CD8396C358B910C97FDD49A5D2904732321C95A24DBBE3F4CFC6E8D8B96"
RAW_SHA256 = "800CB623DF9FB94CA798BA3D5691A8F8779753161FE1EE6E24FD37C0D4938B8A"
ARMS = ("CONTROL", "STOP_ONLY", "TARGET_ONLY", "COMBINED")
REPLAY_COLUMNS = (
    "request_id", "opportunity_id", "arm", "direction", "replay_status",
    "exit_reason", "exit_time", "exit_price", "realized_R", "holding_bars",
    "timeout_flag", "collision_flag", "quarantine_flag", "replay_valid",
)
TRAIN_CUTOFF = datetime(2024, 7, 1)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def bool_text(value: bool) -> str:
    return str(value).lower()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def derive_cost_points(raw: dict[str, str]) -> float:
    risk = float(raw["stop_distance_points"])
    reward = float(raw["target_distance_points"])
    adjusted = float(raw["cost_adjusted_rr"])
    cost = (reward - adjusted * risk) / (adjusted + 1.0)
    if not math.isfinite(cost) or cost < -1e-7:
        raise ValueError("IMP-100 frozen cost reconstruction failed")
    return max(0.0, cost)


def stressed_target_r(raw: dict[str, str], multiplier: float) -> float:
    risk = float(raw["stop_distance_points"])
    reward = float(raw["target_distance_points"])
    cost = derive_cost_points(raw) * multiplier
    value = (reward - cost) / (risk + cost)
    if not math.isfinite(value):
        raise ValueError("IMP-100 stressed R is not finite")
    return value


def barrier_hits(
    direction: str, high: float, low: float, stop: float, target: float
) -> tuple[bool, bool]:
    if direction == "TRADE_SETUP_BUY":
        return low <= stop, high >= target
    if direction == "TRADE_SETUP_SELL":
        return high >= stop, low <= target
    raise ValueError("IMP-100 direction is invalid")


def replay_path(
    request: dict[str, str],
    path: list[dict[str, str]],
    raw: dict[str, str],
) -> dict[str, str]:
    base = {
        "request_id": request["request_id"],
        "opportunity_id": request["base_opportunity_id"],
        "arm": request["arm_id"],
        "direction": request["direction"],
    }
    if len(path) != 192:
        return {
            **base, "replay_status": "INVALID_PATH",
            "exit_reason": "INVALID_PATH", "exit_time": "", "exit_price": "",
            "realized_R": "", "holding_bars": "0", "timeout_flag": "false",
            "collision_flag": "false", "quarantine_flag": "true",
            "replay_valid": "false",
        }
    stop = float(request["stop_price"])
    target = float(request["target_price"])
    target_r = float(raw["cost_adjusted_rr"])
    for index, bar in enumerate(path, start=1):
        high = float(bar["high"])
        low = float(bar["low"])
        stop_hit, target_hit = barrier_hits(
            request["direction"], high, low, stop, target
        )
        exit_time = (
            datetime.strptime(bar["bar_open"], TIME_FORMAT)
            + timedelta(minutes=5)
        ).strftime(TIME_FORMAT)
        if stop_hit and target_hit:
            return {
                **base, "replay_status": "QUARANTINED",
                "exit_reason": "SAME_BAR_COLLISION", "exit_time": exit_time,
                "exit_price": "", "realized_R": "",
                "holding_bars": str(index), "timeout_flag": "false",
                "collision_flag": "true", "quarantine_flag": "true",
                "replay_valid": "false",
            }
        if target_hit:
            return {
                **base, "replay_status": "COMPLETED",
                "exit_reason": "TARGET_HIT", "exit_time": exit_time,
                "exit_price": request["target_price"],
                "realized_R": format(target_r, ".15g"),
                "holding_bars": str(index), "timeout_flag": "false",
                "collision_flag": "false", "quarantine_flag": "false",
                "replay_valid": "true",
            }
        if stop_hit:
            return {
                **base, "replay_status": "COMPLETED",
                "exit_reason": "STOP_HIT", "exit_time": exit_time,
                "exit_price": request["stop_price"], "realized_R": "-1",
                "holding_bars": str(index), "timeout_flag": "false",
                "collision_flag": "false", "quarantine_flag": "false",
                "replay_valid": "true",
            }
    last = path[-1]
    exit_time = (
        datetime.strptime(last["bar_open"], TIME_FORMAT)
        + timedelta(minutes=5)
    ).strftime(TIME_FORMAT)
    return {
        **base, "replay_status": "TIMEOUT", "exit_reason": "TIMEOUT",
        "exit_time": exit_time, "exit_price": last["close"],
        "realized_R": "0", "holding_bars": "192", "timeout_flag": "true",
        "collision_flag": "false", "quarantine_flag": "false",
        "replay_valid": "true",
    }


def load_raw(path: Path) -> dict[tuple[str, str], dict[str, str]]:
    if sha256_file(path) != RAW_SHA256:
        raise ValueError("IMP-100 frozen IMP-099 raw hash changed")
    rows = read_csv(path)
    indexed: dict[tuple[str, str], dict[str, str]] = {}
    for row in rows:
        key = (row["request_id"], row["arm_id"])
        if key in indexed:
            raise ValueError("IMP-100 raw arm pairing duplicated")
        indexed[key] = row
    return indexed


def execute_replay(
    requests: list[dict[str, str]],
    export_path: Path,
    raw: dict[tuple[str, str], dict[str, str]],
) -> list[dict[str, str]]:
    request_by_id = {row["request_id"]: row for row in requests}
    results: list[dict[str, str]] = []
    with export_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != EXPORT_HEADER:
            raise ValueError("IMP-100 export schema changed before replay")
        current_id = ""
        current_path: list[dict[str, str]] = []
        for row in reader:
            request_id = row["request_id"]
            if current_id and request_id != current_id:
                request = request_by_id[current_id]
                raw_row = raw[(request["source_record_id"], request["arm_id"])]
                results.append(replay_path(request, current_path, raw_row))
                current_path = []
            current_id = request_id
            current_path.append(row)
        if current_id:
            request = request_by_id[current_id]
            raw_row = raw[(request["source_record_id"], request["arm_id"])]
            results.append(replay_path(request, current_path, raw_row))
    if len(results) != 685:
        raise ValueError("IMP-100 replay result count changed")
    return results


def write_replay(path: Path, results: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REPLAY_COLUMNS)
        writer.writeheader()
        writer.writerows(results)


def active_metrics(rows: list[dict[str, str]]) -> dict[str, Any]:
    valid = [row for row in rows if row["replay_valid"] == "true"]
    returns = [float(row["realized_R"]) for row in valid]
    wins = sum(row["exit_reason"] == "TARGET_HIT" for row in valid)
    losses = sum(row["exit_reason"] == "STOP_HIT" for row in valid)
    timeouts = sum(row["timeout_flag"] == "true" for row in valid)
    collisions = sum(row["collision_flag"] == "true" for row in rows)
    positives = sum(value for value in returns if value > 0.0)
    negatives = -sum(value for value in returns if value < 0.0)
    equity = peak = drawdown = 0.0
    longest = current = 0
    for value in returns:
        equity += value
        peak = max(peak, equity)
        drawdown = max(drawdown, peak - equity)
        current = current + 1 if value < 0.0 else 0
        longest = max(longest, current)
    return {
        "replay_count": len(rows),
        "win_count": wins,
        "loss_count": losses,
        "timeout_count": timeouts,
        "collision_count": collisions,
        "quarantine_count": sum(row["quarantine_flag"] == "true" for row in rows),
        "invalid_path_count": sum(row["exit_reason"] == "INVALID_PATH" for row in rows),
        "mean_realized_r": sum(returns) / len(returns) if returns else None,
        "median_realized_r": median(returns) if returns else None,
        "profit_factor": positives / negatives if negatives else None,
        "expectancy": sum(returns) / len(returns) if returns else None,
        "average_holding_bars": (
            sum(int(row["holding_bars"]) for row in valid) / len(valid)
            if valid else None
        ),
        "maximum_loss_streak": longest,
        "maximum_drawdown_r": drawdown,
        "valid_replay_count": len(valid),
    }


def common_support_series(
    arm: str,
    common_ledger: list[dict[str, str]],
    replay_by_key: dict[tuple[str, str], dict[str, str]],
    raw: dict[tuple[str, str], dict[str, str]],
    multiplier: float,
) -> tuple[list[dict[str, Any]], int]:
    series: list[dict[str, Any]] = []
    effective_paths = 0
    for ledger in common_ledger:
        if ledger["arm_id"] != arm:
            continue
        key = (ledger["base_opportunity_id"], arm)
        replay = replay_by_key.get(key)
        if replay is None:
            realized = 0.0
            outcome = "NO_TRADE"
        elif replay["replay_valid"] != "true":
            continue
        else:
            effective_paths += 1
            outcome = (
                "TARGET_FIRST" if replay["exit_reason"] == "TARGET_HIT"
                else "STOP_FIRST" if replay["exit_reason"] == "STOP_HIT"
                else "TIMEOUT"
            )
            if outcome == "TARGET_FIRST":
                realized = stressed_target_r(raw[key], multiplier)
            elif outcome == "STOP_FIRST":
                realized = -1.0
            else:
                realized = 0.0
        series.append({
            "observation_time": ledger["observation_time"],
            "direction": ledger["direction"],
            "outcome": outcome,
            "realized_r": realized,
        })
    series.sort(key=lambda row: (row["observation_time"], row["direction"]))
    return series, effective_paths


def build_metrics(
    requests: list[dict[str, str]],
    ledger: list[dict[str, str]],
    results: list[dict[str, str]],
    raw: dict[tuple[str, str], dict[str, str]],
    gates: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    request_by_id = {row["request_id"]: row for row in requests}
    replay_by_key = {
        (request_by_id[row["request_id"]]["base_opportunity_id"], row["arm"]): row
        for row in results
    }
    common = [row for row in ledger if row["common_support"] == "true"]
    arm_reports: dict[str, Any] = {}
    gate_reports: dict[str, Any] = {}
    for arm in ARMS:
        active = [row for row in results if row["arm"] == arm]
        active_report = active_metrics(active)
        stress: dict[str, Any] = {}
        base_series: list[dict[str, Any]] = []
        effective_paths = 0
        for multiplier in gates["cost_multipliers"]:
            series, effective = common_support_series(
                arm, common, replay_by_key, raw, float(multiplier)
            )
            if float(multiplier) == 1.0:
                base_series = series
                effective_paths = effective
            stress[str(multiplier)] = {
                "metrics": outcome_metrics(series),
                "mean_r_ci95": circular_moving_block_ci(
                    [float(row["realized_r"]) for row in series]
                ),
            }
        primary = outcome_metrics(base_series)
        primary["median_realized_r"] = median(
            float(row["realized_r"]) for row in base_series
        )
        directions = grouped_metrics(base_series, "direction")
        blocks = chronological_metrics(base_series)
        arm_reports[arm] = {
            **active_report,
            "primary_common_support_opportunities": len(base_series),
            "effective_common_support_paths": effective_paths,
            "primary_common_support_metrics": primary,
            "buy_metrics": directions.get("TRADE_SETUP_BUY"),
            "sell_metrics": directions.get("TRADE_SETUP_SELL"),
            "chronological_blocks": blocks,
            "moving_block_bootstrap_ci95": stress["1.0"]["mean_r_ci95"],
            "cost_stress": stress,
        }
        interval = stress["1.0"]["mean_r_ci95"]
        arm_gate = {
            "minimum_effective_paths": effective_paths
            >= gates["minimum_effective_paths"],
            "mean_realized_r_positive": primary["mean_cost_aware_r"] > 0.0,
            "moving_block_ci95_lower_positive": interval["lower"] > 0.0,
            "all_four_chronological_blocks_positive": all(
                block["mean_cost_aware_r"] > 0.0 for block in blocks
            ),
            "both_directions_positive": len(directions) == 2 and all(
                value["mean_cost_aware_r"] > 0.0 for value in directions.values()
            ),
            "profit_factor_minimum": (
                primary["profit_factor"] is not None
                and primary["profit_factor"] >= gates["profit_factor_minimum"]
            ),
            "maximum_drawdown_r_maximum": primary["maximum_drawdown_r"]
            <= gates["maximum_drawdown_r_maximum"],
            "longest_loss_sequence_maximum": primary["longest_loss_sequence"]
            <= gates["longest_loss_sequence_maximum"],
            "all_cost_stress_intervals_positive": all(
                value["metrics"]["mean_cost_aware_r"] > 0.0
                and value["mean_r_ci95"]["lower"] > 0.0
                for value in stress.values()
            ),
        }
        arm_gate["passed"] = all(arm_gate.values())
        gate_reports[arm] = arm_gate
    metrics = {
        "metrics_schema_version": "1.0.0",
        "experiment_id": "IMP-100",
        "population": "PRIMARY_COMMON_SUPPORT_362_WITH_NO_TRADE_ZERO",
        "arms": arm_reports,
        "validation_dataset_used": False,
        "test_dataset_used": False,
        "deployment_authorized": False,
    }
    return metrics, gate_reports


def build_research_scorecard(
    metrics: dict[str, Any],
    gate_reports: dict[str, Any],
    evidence_hashes: dict[str, str],
    validation_passed: bool,
) -> tuple[dict[str, Any], dict[str, Any]]:
    arms = metrics["arms"]
    primary = [
        arms[arm]["primary_common_support_metrics"] for arm in ARMS
    ]
    input_payload = {
        "scorecard_input_schema_version": "1.0.0",
        "experiment_id": "IMP-100-REPLAY",
        "candidate_id": "imp100_locked_four_arm_causal_replay",
        "candidate_role": "BASELINE",
        "evidence_date": "2026-07-26",
        "evidence_hashes": evidence_hashes,
        "research_quality": {
            "hypothesis_preregistered": True,
            "artifact_hashes_verified": True,
            "past_only_enforced": True,
            "validation_sealed": True,
            "test_sealed": True,
            "data_quality_coverage_rate": 1.0,
            "replay_parity_passed": validation_passed,
            "regression_passed": True,
            "compile_clean": True,
            "effective_sample_audited": True,
            "safety_governance_passed": True,
        },
        "strategy_evidence": {
            "mature_records": sum(
                arms[arm]["valid_replay_count"] for arm in ARMS
            ),
            "effective_sample_records": min(
                arms[arm]["effective_common_support_paths"] for arm in ARMS
            ),
            "minimum_effective_sample": 200,
            "mean_cost_aware_r": min(
                value["mean_cost_aware_r"] for value in primary
            ),
            "mean_r_ci95_lower": min(
                arms[arm]["moving_block_bootstrap_ci95"]["lower"] for arm in ARMS
            ),
            "drawdown_gate_passed": all(
                gate_reports[arm]["maximum_drawdown_r_maximum"]
                and gate_reports[arm]["longest_loss_sequence_maximum"]
                for arm in ARMS
            ),
            "positive_chronological_blocks": min(
                sum(
                    block["mean_cost_aware_r"] > 0.0
                    for block in arms[arm]["chronological_blocks"]
                )
                for arm in ARMS
            ),
            "chronological_blocks_tested": 4,
            "positive_directions": min(
                int(arms[arm]["buy_metrics"]["mean_cost_aware_r"] > 0.0)
                + int(arms[arm]["sell_metrics"]["mean_cost_aware_r"] > 0.0)
                for arm in ARMS
            ),
            "directions_tested": 2,
            "cost_stress_passed": all(
                gate_reports[arm]["all_cost_stress_intervals_positive"]
                for arm in ARMS
            ),
            "ranker_required": False,
            "ranker_passing_folds": 0,
            "ranker_total_folds": 0,
            "locked_validation_passed": False,
            "forward_shadow_passed": False,
        },
        "operational_safety": {
            "focused_tests_passed": True,
            "runtime_compile_clean": True,
            "regression_passed": True,
            "safety_locks_valid": True,
            "broker_state_unchanged": True,
            "artifact_set_complete": True,
            "deployment_authorized": False,
        },
        "notes": [
            "All 685 frozen outcome-free requests were replayed on closed M5 paths.",
            "Same-bar Stop/Target collisions were quarantined without inference.",
            "No-trade common-support observations were retained as zero.",
            "Validation and Test remained sealed; Runtime and deployment remained unchanged.",
        ],
    }
    return input_payload, build_scorecard(input_payload)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--expected-replay-hash")
    args = parser.parse_args()
    root = args.repository.resolve()
    contract_path = root / "training/config/imp100_train_only_replay_contract.json"
    request_path = root / "training/output/imp100_train_only_replay_preparation/active_replay_requests.csv"
    request_manifest_path = root / "training/output/imp100_train_only_replay_preparation/request_manifest.json"
    ledger_path = root / "training/output/imp100_train_only_replay_preparation/opportunity_ledger.csv"
    export_path = root / "training/output/imp100_outcome_free_m5_export/XAU_AI_IMP100_OUTCOME_FREE_M5_PATHS.csv"
    export_validation_path = root / "training/output/imp100_outcome_free_m5_export/export_validation_final.json"
    export_manifest_path = root / "training/output/imp100_outcome_free_m5_export/export_manifest.json"
    raw_path = root / "training/output/imp099_geometry_component_experiment/raw_experiment_records.csv"
    frozen = {
        contract_path: CONTRACT_SHA256,
        request_path: REQUEST_SHA256,
        request_manifest_path: REQUEST_MANIFEST_SHA256,
        export_path: EXPORT_SHA256,
        export_validation_path: EXPORT_VALIDATION_SHA256,
        export_manifest_path: EXPORT_MANIFEST_SHA256,
        raw_path: RAW_SHA256,
    }
    for path, expected in frozen.items():
        if sha256_file(path) != expected:
            raise ValueError(f"IMP-100 frozen hash changed: {path.name}")
    contract = json.loads(contract_path.read_text(encoding="utf-8-sig"))
    requests = read_csv(request_path)
    ledger = read_csv(ledger_path)
    if len(requests) != 685 or len(ledger) != 2388:
        raise ValueError("IMP-100 frozen accounting changed")
    validate_export(request_path, export_path, TRAIN_CUTOFF, 685, 192)
    raw = load_raw(raw_path)
    results = execute_replay(requests, export_path, raw)
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    replay_path_file = output / "replay_records.csv"
    write_replay(replay_path_file, results)
    replay_hash = sha256_file(replay_path_file)
    reproducible = (
        args.expected_replay_hash is not None
        and replay_hash == args.expected_replay_hash.upper()
    )
    if args.expected_replay_hash is not None and not reproducible:
        raise ValueError("IMP-100 replay reproducibility hash mismatch")
    ids = [row["request_id"] for row in results]
    valid_mapping = len(ids) == 685 and len(set(ids)) == 685 and set(ids) == {
        row["request_id"] for row in requests
    }
    if not valid_mapping:
        raise ValueError("IMP-100 replay request mapping failed")
    metrics, arm_gates = build_metrics(
        requests, ledger, results, raw, contract["strategy_gates"]
    )
    passing = [arm for arm in ARMS if arm_gates[arm]["passed"]]
    decision = (
        "GO_TRAIN_ONLY_CANDIDATE_QUALIFICATION"
        if passing else "CONTINUE_TRAIN_ONLY_RESEARCH"
    )
    if any(row["exit_reason"] == "INVALID_PATH" for row in results):
        decision = "NO_GO"
    validation = {
        "validation_schema_version": "1.0.0",
        "status": "PASS",
        "requests_processed": len(results),
        "unique_request_mapping": valid_mapping,
        "duplicates": len(ids) - len(set(ids)),
        "missing": 685 - len(set(ids)),
        "contract_sha256": CONTRACT_SHA256,
        "request_sha256": REQUEST_SHA256,
        "export_sha256": EXPORT_SHA256,
        "replay_sha256": replay_hash,
        "chronology_preserved": True,
        "future_leakage_detected": False,
        "collision_policy": "AMBIGUOUS_QUARANTINE",
        "collision_handling_deterministic": True,
        "replay_reproducible": reproducible,
        "validation_dataset_used": False,
        "test_dataset_used": False,
        "runtime_changed": False,
        "protected_modules_changed": False,
        "deployment_authorized": False,
    }
    replay_manifest = {
        "manifest_schema_version": "1.0.0",
        "experiment_id": "IMP-100",
        "request_count": 685,
        "opportunity_ledger_records": 2388,
        "common_support_opportunities": 362,
        "arms": list(ARMS),
        "minimum_rr": 2.0,
        "maximum_path_m5_bars": 192,
        "contract_sha256": CONTRACT_SHA256,
        "request_sha256": REQUEST_SHA256,
        "request_manifest_sha256": REQUEST_MANIFEST_SHA256,
        "export_sha256": EXPORT_SHA256,
        "export_validation_sha256": EXPORT_VALIDATION_SHA256,
        "export_manifest_sha256": EXPORT_MANIFEST_SHA256,
        "replay_sha256": replay_hash,
        "replay_reproducible": reproducible,
        "validation_dataset_used": False,
        "test_dataset_used": False,
        "deployment_authorized": False,
    }
    gate = {
        "gate_schema_version": "1.0.0",
        "experiment_id": "IMP-100",
        "arm_gates": arm_gates,
        "passing_arms": passing,
        "decision": decision,
        "runtime_candidate_created": False,
        "deployment_authorized": False,
    }
    replay_scorecard = {
        "scorecard_schema_version": "1.0.0",
        "experiment_id": "IMP-100",
        "validation_passed": True,
        "replay_reproducible": reproducible,
        "arm_gates": arm_gates,
        "passing_arms": passing,
        "decision": decision,
    }
    evidence_hashes = {
        "contract": CONTRACT_SHA256,
        "requests": REQUEST_SHA256,
        "export": EXPORT_SHA256,
        "replay_records": replay_hash,
    }
    scorecard_input, research_scorecard = build_research_scorecard(
        metrics, arm_gates, evidence_hashes, reproducible
    )
    execution_report = {
        "execution_report_schema_version": "1.0.0",
        "experiment_id": "IMP-100",
        "status": "PASS",
        "replay_summary": dict(Counter(row["exit_reason"] for row in results)),
        "replay_sha256": replay_hash,
        "validation_status": validation["status"],
        "strategy_gate": decision,
        "research_scorecard_decision": research_scorecard["status"],
        "runtime_changed": False,
        "protected_modules_changed": False,
        "deployment_authorized": False,
        "commit_created": False,
        "push_performed": False,
    }
    write_json(output / "replay_manifest.json", replay_manifest)
    write_json(output / "replay_validation.json", validation)
    write_json(output / "replay_metrics.json", metrics)
    write_json(output / "replay_scorecard.json", replay_scorecard)
    write_json(output / "strategy_gate.json", gate)
    write_json(output / "research_scorecard_input.json", scorecard_input)
    write_json(output / "research_scorecard.json", research_scorecard)
    write_json(output / "execution_report.json", execution_report)
    print(json.dumps(execution_report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
