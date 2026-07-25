"""Build the isolated Stage D Setup Outcome Dataset from Objective artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import math
from bisect import bisect_left
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from analyze_shadow_run import DECISION_COLUMNS, FEATURE_COLUMNS


SETUP_OUTCOME_SCHEMA_VERSION = "1.0.0"
FEATURE_SCHEMA_VERSION = "4.0.0"
OBJECTIVE_PROVIDER = "OBJECTIVE_M15_M5_SETUP_TESTER_ONLY"
OBJECTIVE_MODEL_STATUS = "OBJECTIVE_STRUCTURAL_PLAN_RESEARCH_NO_GO"
MAX_HOLDING_BARS = 64
MAX_DECISION_LAG_SECONDS = 120
MINIMUM_TRAINABLE_ROWS = 200
MINIMUM_TARGET_ROWS = 40
MINIMUM_NON_TARGET_ROWS = 40

SETUP_AUDIT_COLUMNS_V1 = (
    "recorded_at", "observation_time", "symbol", "higher_bar_open",
    "entry_bar_open", "direction", "poi_confirmed", "trigger_confirmed",
    "reference_poi", "nearest_target", "structural_stop",
    "sweep_penetration_atr", "reclaim_distance_atr", "plan_available",
    "plan_entry", "plan_stop", "plan_target", "plan_rr", "minimum_rr",
    "estimated_cost_points", "setup_reason", "ai_action", "ai_confidence",
    "risk_valid", "risk_allowed", "risk_message", "execution_success",
    "execution_message", "synthetic_ticket",
)
SETUP_AUDIT_COLUMNS_V2 = (
    "recorded_at", "observation_time", "symbol", "higher_bar_open",
    "entry_bar_open", "confirmation_bar_open", "direction", "poi_confirmed",
    "trigger_confirmed", "continuation_confirmed", "reference_poi",
    "nearest_target", "structural_stop", "sweep_penetration_atr",
    "reclaim_distance_atr", "confirmation_extension_atr", "plan_available",
    "plan_entry", "plan_stop", "plan_target", "plan_rr", "minimum_rr",
    "estimated_cost_points", "setup_reason", "ai_action", "ai_confidence",
    "risk_valid", "risk_allowed", "risk_message", "execution_success",
    "execution_message", "synthetic_ticket",
)
SETUP_AUDIT_COLUMNS_V3 = (
    "recorded_at", "observation_time", "symbol", "higher_bar_open",
    "context_bar_open", "entry_bar_open", "direction", "poi_confirmed",
    "trigger_confirmed", "reversal_context_confirmed", "reference_poi",
    "nearest_target", "structural_stop", "sweep_penetration_atr",
    "reclaim_distance_atr", "trigger_engulfment_atr", "plan_available",
    "plan_entry", "plan_stop", "plan_target", "plan_rr", "minimum_rr",
    "estimated_cost_points", "setup_reason", "ai_action", "ai_confidence",
    "risk_valid", "risk_allowed", "risk_message", "execution_success",
    "execution_message", "synthetic_ticket",
)
# Backward-compatible alias used by the preserved V1 fixtures and artifacts.
SETUP_AUDIT_COLUMNS = SETUP_AUDIT_COLUMNS_V1

OUTCOME_AUDIT_COLUMNS = (
    "setup_outcome_schema_version", "feature_schema_version",
    "observation_time", "outcome_known_at", "symbol", "timeframe",
    "direction", "plan_entry", "plan_stop", "plan_target", "plan_rr",
    "minimum_rr", "estimated_cost_points", "point_size", "risk_points",
    "bars_observed", "outcome", "trainable", "mfe_points", "mae_points",
    "mfe_r", "mae_r", "realized_r", *FEATURE_COLUMNS,
)

TRAINABLE_OUTCOMES = {"TARGET_FIRST", "STOP_FIRST", "TIMEOUT"}
SOURCE_QUALITY_EXCLUSION_SCHEMA_VERSION = "1.0.0"


def parse_time(value: str) -> datetime:
    text = value.strip()
    for pattern in ("%Y.%m.%d %H:%M:%S", "%Y.%m.%d %H:%M"):
        try:
            return datetime.strptime(text, pattern)
        except ValueError:
            pass
    raise ValueError(f"Invalid Stage D timestamp: {value}")


def format_time(value: datetime | None) -> str:
    return value.strftime("%Y.%m.%d %H:%M") if value is not None else ""


def as_bool(value: str) -> bool:
    text = value.strip().lower()
    if text == "true":
        return True
    if text == "false":
        return False
    raise ValueError(f"Invalid Boolean value: {value}")


def finite_float(value: str, name: str) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"Non-finite {name}: {value}")
    return result


def load_quality_exclusion_dates(path: Path) -> frozenset[date]:
    if not path.exists():
        raise FileNotFoundError(f"Stage D quality-exclusion file not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if payload.get("quality_exclusion_schema_version") != (
        SOURCE_QUALITY_EXCLUSION_SCHEMA_VERSION
    ):
        raise ValueError("Unsupported Stage D quality-exclusion schema")
    entries = payload.get("excluded_dates")
    if not isinstance(entries, list) or not entries:
        raise ValueError("Stage D quality-exclusion dates are empty")
    dates: list[date] = []
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("date"), str):
            raise ValueError("Invalid Stage D quality-exclusion entry")
        dates.append(date.fromisoformat(entry["date"]))
    if len(dates) != len(set(dates)):
        raise ValueError("Duplicate Stage D quality-exclusion date")
    return frozenset(dates)


def read_exact_csv(path: Path, columns: tuple[str, ...]) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Stage D source artifact not found: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or tuple(reader.fieldnames) != columns:
            raise ValueError(f"Unexpected Stage D CSV schema in {path}")
        rows = list(reader)
    if not rows:
        raise ValueError(f"Stage D source artifact is empty: {path}")
    return rows


def read_setup_audit_csv(path: Path) -> tuple[list[dict[str, str]], str]:
    if not path.exists():
        raise FileNotFoundError(f"Stage D source artifact not found: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = tuple(reader.fieldnames or ())
        if fields == SETUP_AUDIT_COLUMNS_V1:
            version = "1.0.0"
        elif fields == SETUP_AUDIT_COLUMNS_V2:
            version = "2.0.0"
        elif fields == SETUP_AUDIT_COLUMNS_V3:
            version = "3.0.0"
        else:
            raise ValueError(f"Unexpected Stage D Setup Audit schema in {path}")
        rows = list(reader)
    if not rows:
        raise ValueError(f"Stage D source artifact is empty: {path}")
    return rows, version


def validate_decisions(
    rows: list[dict[str, str]],
) -> tuple[dict[datetime, dict[str, str]], list[dict[str, Any]]]:
    observation_index: dict[datetime, dict[str, str]] = {}
    bar_rows: list[dict[str, Any]] = []
    previous_recorded: datetime | None = None
    previous_bar: datetime | None = None

    for row in rows:
        recorded = parse_time(row["recorded_at"])
        closed_bar = parse_time(row["closed_bar"])
        observation = closed_bar + timedelta(minutes=15)
        if observation in observation_index:
            raise ValueError(f"Duplicate Decision observation: {format_time(observation)}")
        if previous_recorded is not None and recorded <= previous_recorded:
            raise ValueError("Decision observations are not strictly chronological")
        if previous_bar is not None and closed_bar <= previous_bar:
            raise ValueError("Decision closed bars are not strictly chronological")
        decision_lag_seconds = (recorded - observation).total_seconds()
        if not 0.0 <= decision_lag_seconds <= MAX_DECISION_LAG_SECONDS:
            raise ValueError(
                "Decision timestamp is early or exceeds the closed-bar freshness limit"
            )
        if row["timeframe"] != "PERIOD_M15":
            raise ValueError("Setup Outcome V1 accepts only PERIOD_M15 Decisions")
        if row["feature_schema_version"] != FEATURE_SCHEMA_VERSION:
            raise ValueError("Setup Outcome V1 requires Feature Schema 4.0.0")
        if row["inference_provider"] != OBJECTIVE_PROVIDER:
            raise ValueError("Decision artifact is not the Objective provider")
        if row["model_status"] != OBJECTIVE_MODEL_STATUS:
            raise ValueError("Decision artifact does not retain Objective NO-GO status")
        if as_bool(row["model_deployment_authorized"]):
            raise ValueError("A deployable Decision artifact is forbidden in Stage D")

        feature_values = {}
        for feature in FEATURE_COLUMNS:
            value = finite_float(row[feature], feature)
            if not 0.0 <= value <= 100.0:
                raise ValueError(f"Feature outside [0,100]: {feature}={value}")
            feature_values[feature] = value

        bar_open = finite_float(row["bar_open"], "bar_open")
        bar_high = finite_float(row["bar_high"], "bar_high")
        bar_low = finite_float(row["bar_low"], "bar_low")
        bar_close = finite_float(row["bar_close"], "bar_close")
        if bar_high < max(bar_open, bar_close) or bar_low > min(bar_open, bar_close):
            raise ValueError(f"Invalid completed-bar OHLC at {row['closed_bar']}")
        if bar_high < bar_low:
            raise ValueError(f"Completed-bar High is below Low at {row['closed_bar']}")

        observation_index[observation] = row
        bar_rows.append({
            "time": closed_bar,
            "high": bar_high,
            "low": bar_low,
            "close": bar_close,
            "features": feature_values,
        })
        previous_recorded = recorded
        previous_bar = closed_bar

    return observation_index, bar_rows


def validate_plan(
    row: dict[str, str], point_size: float
) -> tuple[str, float, float, float, float]:
    direction = row["direction"]
    entry = finite_float(row["plan_entry"], "plan_entry")
    stop = finite_float(row["plan_stop"], "plan_stop")
    target = finite_float(row["plan_target"], "plan_target")
    plan_rr = finite_float(row["plan_rr"], "plan_rr")
    minimum_rr = finite_float(row["minimum_rr"], "minimum_rr")
    estimated_cost_points = finite_float(
        row["estimated_cost_points"], "estimated_cost_points"
    )
    if direction == "TRADE_SETUP_BUY":
        geometry_valid = stop < entry < target
    elif direction == "TRADE_SETUP_SELL":
        geometry_valid = target < entry < stop
    else:
        raise ValueError(f"Invalid trainable Setup direction: {direction}")
    if not geometry_valid:
        raise ValueError(f"Invalid structural plan geometry at {row['observation_time']}")
    if minimum_rr < 2.0 or plan_rr + 1e-9 < minimum_rr:
        raise ValueError(f"Structural plan violates its minimum RR at {row['observation_time']}")
    cost_price = estimated_cost_points * point_size
    effective_risk = abs(entry - stop) + cost_price
    net_reward = abs(target - entry) - cost_price
    calculated_rr = net_reward / effective_risk
    if net_reward <= 0.0 or abs(calculated_rr - plan_rr) > 1e-6:
        raise ValueError(f"Structural plan RR is inconsistent at {row['observation_time']}")
    return direction, entry, stop, target, plan_rr


def evaluate_path(
    direction: str,
    entry: float,
    stop: float,
    target: float,
    bars: list[dict[str, Any]],
    start_index: int,
    point_size: float,
) -> dict[str, Any]:
    path = bars[start_index:start_index + MAX_HOLDING_BARS]
    risk_price = abs(entry - stop)
    mfe_price = 0.0
    mae_price = 0.0
    outcome = "UNMATURED"
    known_at: datetime | None = None
    observed = 0

    for bar in path:
        observed += 1
        if direction == "TRADE_SETUP_BUY":
            mfe_price = max(mfe_price, bar["high"] - entry)
            mae_price = max(mae_price, entry - bar["low"])
            target_hit = bar["high"] >= target
            stop_hit = bar["low"] <= stop
        else:
            mfe_price = max(mfe_price, entry - bar["low"])
            mae_price = max(mae_price, bar["high"] - entry)
            target_hit = bar["low"] <= target
            stop_hit = bar["high"] >= stop

        if target_hit and stop_hit:
            outcome = "AMBIGUOUS"
            known_at = bar["time"] + timedelta(minutes=15)
            break
        if target_hit:
            outcome = "TARGET_FIRST"
            known_at = bar["time"] + timedelta(minutes=15)
            break
        if stop_hit:
            outcome = "STOP_FIRST"
            known_at = bar["time"] + timedelta(minutes=15)
            break

    if outcome == "UNMATURED" and len(path) == MAX_HOLDING_BARS:
        outcome = "TIMEOUT"
        known_at = path[-1]["time"] + timedelta(minutes=15)

    realized_r: float | str
    if outcome == "TARGET_FIRST":
        realized_r = abs(target - entry) / risk_price
    elif outcome == "STOP_FIRST":
        realized_r = -1.0
    elif outcome == "TIMEOUT":
        realized_r = 0.0
    else:
        realized_r = ""

    return {
        "outcome": outcome,
        "known_at": known_at,
        "bars_observed": observed,
        "mfe_points": max(0.0, mfe_price) / point_size,
        "mae_points": max(0.0, mae_price) / point_size,
        "mfe_r": max(0.0, mfe_price) / risk_price,
        "mae_r": max(0.0, mae_price) / risk_price,
        "realized_r": realized_r,
    }


def build_dataset(
    setup_audit_path: Path,
    decisions_path: Path,
    point_size: float = 0.01,
    excluded_dates: frozenset[date] = frozenset(),
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if not math.isfinite(point_size) or point_size <= 0.0:
        raise ValueError("Stage D point size must be positive and finite")

    setup_rows, setup_audit_schema_version = read_setup_audit_csv(setup_audit_path)
    decision_rows = read_exact_csv(decisions_path, DECISION_COLUMNS)
    decision_index, bar_rows = validate_decisions(decision_rows)
    bar_times = [row["time"] for row in bar_rows]

    setup_observations: set[datetime] = set()
    output_rows: list[dict[str, Any]] = []
    source_quality_exclusions: list[dict[str, Any]] = []
    for setup in setup_rows:
        observation = parse_time(setup["observation_time"])
        if setup_audit_schema_version == "2.0.0":
            trigger_open = parse_time(setup["entry_bar_open"])
            confirmation_open = parse_time(setup["confirmation_bar_open"])
            if (trigger_open + timedelta(minutes=10) != observation
                    or confirmation_open + timedelta(minutes=5) != observation
                    or trigger_open + timedelta(minutes=5) != confirmation_open):
                raise ValueError("CR-016 Setup Audit contains invalid two-bar timing")
            trigger_confirmed = as_bool(setup["trigger_confirmed"])
            continuation_confirmed = as_bool(setup["continuation_confirmed"])
            confirmation_extension = finite_float(
                setup["confirmation_extension_atr"],
                "confirmation_extension_atr",
            )
            if confirmation_extension < 0.0:
                raise ValueError("CR-016 confirmation extension is negative")
            if continuation_confirmed and not trigger_confirmed:
                raise ValueError("CR-016 continuation bypassed its trigger")
            if as_bool(setup["plan_available"]) and (
                not trigger_confirmed or not continuation_confirmed
            ):
                raise ValueError("CR-016 plan bypassed trigger confirmation")
        elif setup_audit_schema_version == "3.0.0":
            context_open = parse_time(setup["context_bar_open"])
            trigger_open = parse_time(setup["entry_bar_open"])
            if (context_open + timedelta(minutes=10) != observation
                    or trigger_open + timedelta(minutes=5) != observation
                    or context_open + timedelta(minutes=5) != trigger_open):
                raise ValueError("CR-017 Setup Audit contains invalid two-bar timing")
            trigger_confirmed = as_bool(setup["trigger_confirmed"])
            reversal_context_confirmed = as_bool(
                setup["reversal_context_confirmed"]
            )
            trigger_engulfment = finite_float(
                setup["trigger_engulfment_atr"],
                "trigger_engulfment_atr",
            )
            if trigger_engulfment < 0.0:
                raise ValueError("CR-017 trigger engulfment is negative")
            if reversal_context_confirmed and not trigger_confirmed:
                raise ValueError("CR-017 reversal context bypassed its trigger")
            if as_bool(setup["plan_available"]) and (
                not trigger_confirmed or not reversal_context_confirmed
            ):
                raise ValueError("CR-017 plan bypassed reversal context")
        if observation in setup_observations:
            raise ValueError(f"Duplicate Objective Setup observation: {setup['observation_time']}")
        setup_observations.add(observation)
        if not as_bool(setup["plan_available"]):
            continue
        if observation not in decision_index:
            raise ValueError(f"Objective Setup has no exact Decision join: {setup['observation_time']}")

        decision = decision_index[observation]
        if setup["symbol"] != decision["symbol"]:
            raise ValueError(f"Objective Setup symbol mismatch at {setup['observation_time']}")
        direction, entry, stop, target, plan_rr = validate_plan(setup, point_size)
        start_index = bisect_left(bar_times, observation)
        path = evaluate_path(
            direction, entry, stop, target, bar_rows, start_index, point_size
        )
        quality_end = path["known_at"] or (
            observation + timedelta(minutes=15 * MAX_HOLDING_BARS)
        )
        matched_quality_dates = sorted(
            value.isoformat()
            for value in excluded_dates
            if observation.date() <= value <= quality_end.date()
        )
        if matched_quality_dates:
            source_quality_exclusions.append({
                "observation_time": format_time(observation),
                "outcome_known_at": format_time(path["known_at"]),
                "outcome": str(path["outcome"]),
                "excluded_dates": matched_quality_dates,
            })
            continue
        risk_price = abs(entry - stop)
        outcome = str(path["outcome"])
        row: dict[str, Any] = {
            "setup_outcome_schema_version": SETUP_OUTCOME_SCHEMA_VERSION,
            "feature_schema_version": FEATURE_SCHEMA_VERSION,
            "observation_time": format_time(observation),
            "outcome_known_at": format_time(path["known_at"]),
            "symbol": setup["symbol"],
            "timeframe": "PERIOD_M15",
            "direction": direction,
            "plan_entry": entry,
            "plan_stop": stop,
            "plan_target": target,
            "plan_rr": plan_rr,
            "minimum_rr": finite_float(setup["minimum_rr"], "minimum_rr"),
            "estimated_cost_points": finite_float(
                setup["estimated_cost_points"], "estimated_cost_points"
            ),
            "point_size": point_size,
            "risk_points": risk_price / point_size,
            "bars_observed": path["bars_observed"],
            "outcome": outcome,
            "trainable": str(outcome in TRAINABLE_OUTCOMES).lower(),
            "mfe_points": path["mfe_points"],
            "mae_points": path["mae_points"],
            "mfe_r": path["mfe_r"],
            "mae_r": path["mae_r"],
            "realized_r": path["realized_r"],
        }
        for feature in FEATURE_COLUMNS:
            row[feature] = finite_float(decision[feature], feature)
        output_rows.append(row)

    if not output_rows:
        raise ValueError("Objective audit contains no valid structural plans")
    output_rows.sort(key=lambda row: parse_time(str(row["observation_time"])))
    outcome_counts = Counter(str(row["outcome"]) for row in output_rows)
    trainable_count = sum(str(row["trainable"]).lower() == "true" for row in output_rows)
    target_count = outcome_counts.get("TARGET_FIRST", 0)
    non_target_count = (
        outcome_counts.get("STOP_FIRST", 0) + outcome_counts.get("TIMEOUT", 0)
    )
    summary = {
        "dataset_stage": "stage_d_setup_outcome_build_only",
        "setup_outcome_schema_version": SETUP_OUTCOME_SCHEMA_VERSION,
        "setup_audit_schema_version": setup_audit_schema_version,
        "feature_schema_version": FEATURE_SCHEMA_VERSION,
        "directional_label_schema_changed": False,
        "training_performed": False,
        "deployment_authorized": False,
        "maximum_holding_bars": MAX_HOLDING_BARS,
        "point_size": point_size,
        "decision_rows": len(decision_rows),
        "setup_audit_rows": len(setup_rows),
        "source_structural_plans": len(output_rows) + len(source_quality_exclusions),
        "source_quality_excluded_plans": len(source_quality_exclusions),
        "source_quality_exclusions": source_quality_exclusions,
        "structural_plans": len(output_rows),
        "trainable_rows": trainable_count,
        "outcome_distribution": dict(outcome_counts),
        "minimum_trainable_rows": MINIMUM_TRAINABLE_ROWS,
        "minimum_target_rows": MINIMUM_TARGET_ROWS,
        "minimum_non_target_rows": MINIMUM_NON_TARGET_ROWS,
        "sample_size_requirement_met": trainable_count >= MINIMUM_TRAINABLE_ROWS,
        "target_coverage_met": target_count >= MINIMUM_TARGET_ROWS,
        "non_target_coverage_met": non_target_count >= MINIMUM_NON_TARGET_ROWS,
        "ready_for_train_split": (
            trainable_count >= MINIMUM_TRAINABLE_ROWS
            and target_count >= MINIMUM_TARGET_ROWS
            and non_target_count >= MINIMUM_NON_TARGET_ROWS
        ),
        "limitations": [
            "Outcome ordering uses completed M15 bars, not intrabar ticks.",
            "Same-bar Target/Stop observations are quarantined as AMBIGUOUS.",
            "Raw plan prices and outcome fields are forbidden model inputs.",
            "This builder cannot train, deploy, or modify Runtime.",
        ],
    }
    return output_rows, summary


def write_dataset(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTCOME_AUDIT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--setup-audit", required=True, type=Path)
    parser.add_argument("--decisions", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--summary", required=True, type=Path)
    parser.add_argument("--point-size", type=float, default=0.01)
    parser.add_argument("--max-holding-bars", type=int, default=MAX_HOLDING_BARS)
    parser.add_argument("--quality-exclusions", type=Path)
    arguments = parser.parse_args()
    if arguments.max_holding_bars != MAX_HOLDING_BARS:
        raise ValueError("Setup Outcome Schema 1.0.0 fixes the horizon at 64 M15 bars")
    excluded_dates = (
        load_quality_exclusion_dates(arguments.quality_exclusions)
        if arguments.quality_exclusions is not None
        else frozenset()
    )
    rows, summary = build_dataset(
        arguments.setup_audit,
        arguments.decisions,
        point_size=arguments.point_size,
        excluded_dates=excluded_dates,
    )
    summary["quality_exclusion_file"] = (
        str(arguments.quality_exclusions)
        if arguments.quality_exclusions is not None
        else ""
    )
    write_dataset(arguments.output, rows)
    arguments.summary.parent.mkdir(parents=True, exist_ok=True)
    arguments.summary.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({
        **summary,
        "dataset_file": str(arguments.output),
        "summary_file": str(arguments.summary),
    }, indent=2))


if __name__ == "__main__":
    main()
