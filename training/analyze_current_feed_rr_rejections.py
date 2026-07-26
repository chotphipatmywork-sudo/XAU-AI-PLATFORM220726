"""XAU AI PLATFORM | Offline Research | Version 1.0.0.

Attribute the frozen IMP-096 M5 Stop 2 plus M15 Target 1 Minimum-RR
rejections without changing geometry, costs, gates, or runtime behavior.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

from analyze_current_feed_joint_geometry import join_evidence
from build_setup_outcome_dataset import parse_time
from diagnose_current_feed_setup_funnel import TRAIN_END_EXCLUSIVE, sha256
from replay_current_feed_stops import read_stop_export
from replay_current_feed_targets import EXPECTED_DECISIONS_SHA256, read_requests
from replay_past_only_targets import geometry_and_rr, read_export


REPORT_SCHEMA_VERSION = "1.0.0"
DETAIL_SCHEMA_VERSION = "1.0.0"
STOP_NAME = "m5_stop_2"
TARGET_NAME = "m15_target_1"
POINT_SIZE = 0.01
EXPECTED_REQUEST_SHA256 = (
    "9BBD853742D16A015C6D3179B86986A3A209646A228E593DBBC98E8BDD715C0C"
)
EXPECTED_STOP_SHA256 = (
    "FB6E0073BDF0FD89E4B09324B6C092F0812DBA7D243608063B61E4F167627C75"
)
EXPECTED_TARGET_SHA256 = (
    "E930FFEEB5AF464DBCFD7FFD531D264AA9ED7D326CDAAD07ED2487CC72E7E2FA"
)
MINIMUM_GROUP_RECORDS = 20
SIGNIFICANCE_ALPHA = 0.05

DETAIL_COLUMNS = (
    "detail_schema_version", "request_id", "observation_time", "direction",
    "gate_result", "rejection_cause", "entry", "stop", "target",
    "entry_distance_points", "entry_distance_atr", "stop_distance_points",
    "stop_distance_atr", "target_distance_points", "target_distance_atr",
    "estimated_cost_points", "cost_to_risk_ratio", "raw_rr",
    "cost_adjusted_rr", "rr_cost_erosion", "session", "time_of_day",
    "volatility_regime", "trend_regime", "trend_alignment",
    "validation_dataset_used", "test_dataset_used",
    "deployment_authorized",
)


def quantile(values: Iterable[float], fraction: float) -> float | None:
    ordered = sorted(float(value) for value in values)
    if not ordered:
        return None
    position = (len(ordered) - 1) * fraction
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def numeric_summary(values: Iterable[float]) -> dict[str, float | int | None]:
    materialized = [float(value) for value in values]
    return {
        "records": len(materialized),
        "minimum": min(materialized) if materialized else None,
        "p25": quantile(materialized, 0.25),
        "median": quantile(materialized, 0.50),
        "mean": (
            sum(materialized) / len(materialized) if materialized else None
        ),
        "p75": quantile(materialized, 0.75),
        "maximum": max(materialized) if materialized else None,
    }


def wilson_interval(successes: int, total: int) -> list[float | None]:
    if total <= 0:
        return [None, None]
    z = 1.959963984540054
    proportion = successes / total
    denominator = 1.0 + z * z / total
    center = (proportion + z * z / (2.0 * total)) / denominator
    margin = (
        z
        * math.sqrt(
            proportion * (1.0 - proportion) / total
            + z * z / (4.0 * total * total)
        )
        / denominator
    )
    return [max(0.0, center - margin), min(1.0, center + margin)]


def two_proportion_p_value(
    group_rejected: int,
    group_total: int,
    rest_rejected: int,
    rest_total: int,
) -> float | None:
    if group_total <= 0 or rest_total <= 0:
        return None
    pooled = (group_rejected + rest_rejected) / (group_total + rest_total)
    variance = pooled * (1.0 - pooled) * (
        1.0 / group_total + 1.0 / rest_total
    )
    if variance <= 0.0:
        return 1.0
    difference = group_rejected / group_total - rest_rejected / rest_total
    z_score = difference / math.sqrt(variance)
    return math.erfc(abs(z_score) / math.sqrt(2.0))


def fixed_regime(value: float) -> str:
    if value < 33.3333333333:
        return "LOW"
    if value < 66.6666666667:
        return "MID"
    return "HIGH"


def session_label(context: dict[str, float]) -> str:
    active = [
        name
        for name, field in (
            ("ASIA", "session_asia"),
            ("LONDON", "session_london"),
            ("NEW_YORK", "session_new_york"),
        )
        if context[field] >= 50.0
    ]
    return "+".join(active) if active else "OFF_SESSION"


def time_of_day(observation: datetime) -> str:
    if observation.hour < 6:
        return "00_05"
    if observation.hour < 12:
        return "06_11"
    if observation.hour < 18:
        return "12_17"
    return "18_23"


def trend_alignment(direction: str, trend_score: float) -> str:
    if 33.3333333333 <= trend_score < 66.6666666667:
        return "NEUTRAL"
    aligned = (
        direction == "TRADE_SETUP_BUY" and trend_score >= 66.6666666667
    ) or (
        direction == "TRADE_SETUP_SELL" and trend_score < 33.3333333333
    )
    return "ALIGNED" if aligned else "COUNTER"


def load_contexts(
    path: Path, observations: set[datetime]
) -> dict[datetime, dict[str, float]]:
    required = {
        "recorded_at", "bar_close", "atr", "trend_regime",
        "volatility_regime", "session_asia", "session_london",
        "session_new_york",
    }
    contexts: dict[datetime, dict[str, float]] = {}
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or not required.issubset(reader.fieldnames):
            raise ValueError("IMP-097 Decision context schema changed")
        for row in reader:
            recorded_at = parse_time(row["recorded_at"]).replace(
                second=0, microsecond=0
            )
            if recorded_at not in observations:
                continue
            if recorded_at in contexts:
                raise ValueError("IMP-097 Decision context is duplicated")
            contexts[recorded_at] = {
                field: float(row[field])
                for field in required - {"recorded_at"}
            }
    if set(contexts) != observations:
        missing = sorted(observations - set(contexts))
        raise ValueError(
            f"IMP-097 Decision context coverage changed: missing={len(missing)}"
        )
    return contexts


def build_records(
    evidence: list[dict[str, Any]],
    contexts: dict[datetime, dict[str, float]],
) -> tuple[list[dict[str, Any]], Counter[str]]:
    records: list[dict[str, Any]] = []
    accounting: Counter[str] = Counter()
    for row in evidence:
        stop = float(row["stops"][STOP_NAME])
        target = float(row["targets"][TARGET_NAME])
        if stop <= 0.0 or target <= 0.0:
            accounting["missing_geometry"] += 1
            continue
        entry = float(row["entry"])
        direction = str(row["direction"])
        structurally_valid = (
            direction == "TRADE_SETUP_BUY" and stop < entry < target
        ) or (
            direction == "TRADE_SETUP_SELL" and target < entry < stop
        )
        if not structurally_valid:
            accounting["invalid_structural_geometry"] += 1
            continue
        accounting["structurally_valid_geometry"] += 1
        if not row["cost_known"]:
            accounting["unknown_cost"] += 1
            continue
        risk_distance = abs(entry - stop)
        reward_distance = abs(target - entry)
        raw_rr = reward_distance / risk_distance
        valid, adjusted_rr = geometry_and_rr(
            direction, entry, stop, target, float(row["cost_points"])
        )
        if not valid or adjusted_rr is None:
            accounting["non_positive_cost_adjusted_reward"] += 1
            continue
        accounting["valid_cost_aware_geometry"] += 1
        rejected = adjusted_rr + 1e-9 < float(row["minimum_rr"])
        if rejected:
            accounting["below_minimum_rr"] += 1
            cause = (
                "STRUCTURAL_RAW_RR_BELOW_MINIMUM"
                if raw_rr + 1e-9 < float(row["minimum_rr"])
                else "COST_EROSION_BELOW_MINIMUM"
            )
        else:
            accounting["minimum_rr_reached"] += 1
            cause = "NOT_REJECTED"
        observation = row["observation"]
        context = contexts[observation]
        atr = context["atr"]
        if atr <= 0.0:
            raise ValueError("IMP-097 ATR is not positive")
        cost_price = float(row["cost_points"]) * POINT_SIZE
        records.append({
            "request_id": row["request_id"],
            "observation": observation,
            "direction": direction,
            "gate_result": "REJECTED" if rejected else "ACCEPTED",
            "rejection_cause": cause,
            "entry": entry,
            "stop": stop,
            "target": target,
            "entry_distance_points": abs(entry - context["bar_close"]) / POINT_SIZE,
            "entry_distance_atr": abs(entry - context["bar_close"]) / atr,
            "stop_distance_points": risk_distance / POINT_SIZE,
            "stop_distance_atr": risk_distance / atr,
            "target_distance_points": reward_distance / POINT_SIZE,
            "target_distance_atr": reward_distance / atr,
            "estimated_cost_points": float(row["cost_points"]),
            "cost_to_risk_ratio": cost_price / risk_distance,
            "raw_rr": raw_rr,
            "cost_adjusted_rr": adjusted_rr,
            "rr_cost_erosion": raw_rr - adjusted_rr,
            "session": session_label(context),
            "time_of_day": time_of_day(observation),
            "volatility_regime": fixed_regime(context["volatility_regime"]),
            "trend_regime": fixed_regime(context["trend_regime"]),
            "trend_alignment": trend_alignment(
                direction, context["trend_regime"]
            ),
        })
    return records, accounting


def rejection_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    rejected = sum(row["gate_result"] == "REJECTED" for row in records)
    return {
        "records": len(records),
        "rejected": rejected,
        "accepted": len(records) - rejected,
        "rejection_rate": rejected / len(records) if records else None,
        "rejection_rate_wilson_95": wilson_interval(rejected, len(records)),
    }


def factor_analysis(
    records: list[dict[str, Any]], fields: tuple[str, ...]
) -> tuple[dict[str, list[dict[str, Any]]], list[dict[str, Any]]]:
    total_rejected = sum(row["gate_result"] == "REJECTED" for row in records)
    output: dict[str, list[dict[str, Any]]] = {}
    comparisons: list[dict[str, Any]] = []
    for field in fields:
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in records:
            grouped[str(row[field])].append(row)
        summaries: list[dict[str, Any]] = []
        for group, subset in sorted(grouped.items()):
            rejected = sum(
                row["gate_result"] == "REJECTED" for row in subset
            )
            rest_total = len(records) - len(subset)
            rest_rejected = total_rejected - rejected
            p_value = two_proportion_p_value(
                rejected, len(subset), rest_rejected, rest_total
            )
            item = {
                "group": group,
                **rejection_summary(subset),
                "rest_records": rest_total,
                "rest_rejection_rate": (
                    rest_rejected / rest_total if rest_total else None
                ),
                "rejection_rate_difference_vs_rest": (
                    rejected / len(subset) - rest_rejected / rest_total
                    if subset and rest_total else None
                ),
                "two_sided_p_value_unadjusted": p_value,
            }
            summaries.append(item)
            comparisons.append({"factor": field, **item})
        output[field] = summaries
    comparison_count = len(comparisons)
    for item in comparisons:
        p_value = item["two_sided_p_value_unadjusted"]
        item["bonferroni_p_value"] = (
            min(1.0, float(p_value) * comparison_count)
            if p_value is not None else None
        )
        item["statistically_significant"] = bool(
            item["records"] >= MINIMUM_GROUP_RECORDS
            and item["rest_records"] >= MINIMUM_GROUP_RECORDS
            and item["bonferroni_p_value"] is not None
            and item["bonferroni_p_value"] < SIGNIFICANCE_ALPHA
        )
    lookup = {
        (item["factor"], item["group"]): item for item in comparisons
    }
    for field, summaries in output.items():
        for item in summaries:
            comparison = lookup[(field, item["group"])]
            item["bonferroni_p_value"] = comparison["bonferroni_p_value"]
            item["statistically_significant"] = comparison[
                "statistically_significant"
            ]
    return output, comparisons


def distance_analysis(
    records: list[dict[str, Any]]
) -> dict[str, dict[str, dict[str, float | int | None]]]:
    metrics = (
        "entry_distance_points", "entry_distance_atr",
        "stop_distance_points", "stop_distance_atr",
        "target_distance_points", "target_distance_atr",
        "estimated_cost_points", "cost_to_risk_ratio",
        "raw_rr", "cost_adjusted_rr", "rr_cost_erosion",
    )
    groups = {
        "all": records,
        "rejected": [
            row for row in records if row["gate_result"] == "REJECTED"
        ],
        "accepted": [
            row for row in records if row["gate_result"] == "ACCEPTED"
        ],
    }
    return {
        group: {
            metric: numeric_summary(row[metric] for row in subset)
            for metric in metrics
        }
        for group, subset in groups.items()
    }


def write_details(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=DETAIL_COLUMNS)
        writer.writeheader()
        for row in records:
            writer.writerow({
                "detail_schema_version": DETAIL_SCHEMA_VERSION,
                "request_id": row["request_id"],
                "observation_time": row["observation"].strftime(
                    "%Y.%m.%d %H:%M"
                ),
                **{
                    key: row[key]
                    for key in DETAIL_COLUMNS
                    if key not in {
                        "detail_schema_version", "request_id",
                        "observation_time", "validation_dataset_used",
                        "test_dataset_used", "deployment_authorized",
                    }
                },
                "validation_dataset_used": "false",
                "test_dataset_used": "false",
                "deployment_authorized": "false",
            })


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", required=True, type=Path)
    parser.add_argument("--request-manifest", required=True, type=Path)
    parser.add_argument("--stop-export", required=True, type=Path)
    parser.add_argument("--target-export", required=True, type=Path)
    parser.add_argument("--decisions", required=True, type=Path)
    parser.add_argument("--joint-report", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--details", required=True, type=Path)
    arguments = parser.parse_args()

    expected_hashes = {
        arguments.request: EXPECTED_REQUEST_SHA256,
        arguments.stop_export: EXPECTED_STOP_SHA256,
        arguments.target_export: EXPECTED_TARGET_SHA256,
        arguments.decisions: EXPECTED_DECISIONS_SHA256,
    }
    for path, expected in expected_hashes.items():
        if sha256(path) != expected:
            raise ValueError(f"IMP-097 frozen evidence hash changed: {path}")

    requests = read_requests(arguments.request, arguments.request_manifest)
    evidence = join_evidence(
        read_stop_export(arguments.stop_export, requests),
        read_export(arguments.target_export, requests),
    )
    observations = {row["observation"] for row in evidence}
    contexts = load_contexts(arguments.decisions, observations)
    records, accounting = build_records(evidence, contexts)
    baseline = json.loads(
        arguments.joint_report.read_text(encoding="utf-8-sig")
    )
    baseline_accounting = baseline["combinations"][
        f"{STOP_NAME}__{TARGET_NAME}"
    ]["accounting"]
    parity = {
        "requests": len(evidence) == 597,
        "stop_candidate": STOP_NAME == "m5_stop_2",
        "target_candidate": TARGET_NAME == "m15_target_1",
        "minimum_rr": all(
            math.isclose(float(row["minimum_rr"]), 2.0) for row in evidence
        ),
        "valid_cost_aware_geometry": (
            accounting["valid_cost_aware_geometry"]
            == baseline_accounting["valid_cost_aware_geometry"]
        ),
        "below_minimum_rr": (
            accounting["below_minimum_rr"]
            == baseline_accounting["below_minimum_rr"]
        ),
        "minimum_rr_reached": (
            accounting["minimum_rr_reached"]
            == baseline_accounting["minimum_rr_reached"]
        ),
    }
    if not all(parity.values()):
        raise ValueError(f"IMP-097 frozen Baseline parity failed: {parity}")

    factor_fields = (
        "direction", "session", "time_of_day", "volatility_regime",
        "trend_regime", "trend_alignment",
    )
    factors, comparisons = factor_analysis(records, factor_fields)
    opportunities = [
        {
            "factor": item["factor"],
            "group": item["group"],
            "records": item["records"],
            "rejection_rate": item["rejection_rate"],
            "rest_rejection_rate": item["rest_rejection_rate"],
            "bonferroni_p_value": item["bonferroni_p_value"],
            "research_only": True,
        }
        for item in comparisons
        if item["statistically_significant"]
        and item["rejection_rate_difference_vs_rest"] < 0.0
    ]
    cause_counts = Counter(
        row["rejection_cause"]
        for row in records
        if row["gate_result"] == "REJECTED"
    )
    rejected_total = sum(cause_counts.values())
    report = {
        "report_schema_version": REPORT_SCHEMA_VERSION,
        "status": "IMP097_RR_REJECTION_ROOT_CAUSE_RESEARCH_NO_GO",
        "architecture_baseline": "ABR-1.0",
        "frozen_baseline": "IMP-096",
        "methodology": {
            "scope": "TRAIN_ONLY_FROZEN_M5_STOP_2_M15_TARGET_1",
            "train_end_exclusive": "2024.07.01 00:00",
            "minimum_rr": 2.0,
            "point_size": POINT_SIZE,
            "fixed_regime_bins": ["LOW_<33.3333", "MID_33.3333_66.6667", "HIGH_>=66.6667"],
            "fixed_time_bins": ["00_05", "06_11", "12_17", "18_23"],
            "minimum_group_records": MINIMUM_GROUP_RECORDS,
            "significance_alpha": SIGNIFICANCE_ALPHA,
            "multiple_comparison_correction": "BONFERRONI",
            "comparison_count": len(comparisons),
            "association_not_causation": True,
        },
        "source_hashes": {
            "request": sha256(arguments.request),
            "request_manifest": sha256(arguments.request_manifest),
            "stop_export": sha256(arguments.stop_export),
            "target_export": sha256(arguments.target_export),
            "decisions": sha256(arguments.decisions),
            "joint_report": sha256(arguments.joint_report),
        },
        "baseline_parity": parity,
        "accounting": dict(sorted(accounting.items())),
        "rr_rejection_distribution": {
            "overall": rejection_summary(records),
            "causes": {
                cause: {
                    "records": count,
                    "share_of_rejections": (
                        count / rejected_total if rejected_total else None
                    ),
                }
                for cause, count in sorted(cause_counts.items())
            },
        },
        "buy_vs_sell": factors["direction"],
        "entry_distance_statistics": {
            group: values["entry_distance_points"]
            for group, values in distance_analysis(records).items()
        },
        "stop_distance_statistics": {
            group: values["stop_distance_points"]
            for group, values in distance_analysis(records).items()
        },
        "target_distance_statistics": {
            group: values["target_distance_points"]
            for group, values in distance_analysis(records).items()
        },
        "cost_impact_analysis": {
            group: {
                metric: values[metric]
                for metric in (
                    "estimated_cost_points", "cost_to_risk_ratio",
                    "raw_rr", "cost_adjusted_rr", "rr_cost_erosion",
                )
            }
            for group, values in distance_analysis(records).items()
        },
        "all_distance_statistics": distance_analysis(records),
        "session_analysis": factors["session"],
        "time_of_day_analysis": factors["time_of_day"],
        "regime_analysis": {
            "volatility": factors["volatility_regime"],
            "trend": factors["trend_regime"],
            "trend_alignment": factors["trend_alignment"],
        },
        "dominant_rejection_causes": [
            {
                "cause": cause,
                "records": count,
                "share_of_rejections": (
                    count / rejected_total if rejected_total else None
                ),
            }
            for cause, count in cause_counts.most_common()
        ],
        "candidate_opportunities_research_only": opportunities,
        "gate_decision": {
            "decision": "NO_GO",
            "runtime_candidate_created": False,
            "minimum_rr_changed": False,
            "parameters_optimized": False,
            "validation_dataset_used": False,
            "test_dataset_used": False,
            "model_training_performed": False,
            "runtime_changed": False,
            "risk_changed": False,
            "execution_changed": False,
            "deployment_authorized": False,
        },
        "limitations": [
            "The selected geometry was found after a 49-combination Train frontier.",
            "Factor tests are exploratory associations and do not establish causality.",
            "Validation and Test remain sealed and were not read.",
            "No threshold, bin, geometry, cost, or Runtime behavior was optimized.",
        ],
    }
    write_details(arguments.details, records)
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    print(json.dumps({
        "status": report["status"],
        "accounting": report["accounting"],
        "dominant_rejection_causes": report["dominant_rejection_causes"],
        "candidate_opportunities_research_only": opportunities,
        "gate_decision": report["gate_decision"],
    }, indent=2))


if __name__ == "__main__":
    main()
