"""XAU AI PLATFORM | Offline Research Diagnostic | Version 1.0.0.

Measure past-only separation of accepted Setup outcomes by deterministic
Entry geometry without selecting a threshold or reading sealed evidence.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter
from pathlib import Path
from statistics import fmean, median
from typing import Any, Sequence

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    f1_score,
    precision_recall_fscore_support,
)
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

from augment_pretrain_history import read_trainable, sha256
from build_setup_outcome_dataset import (
    SETUP_AUDIT_COLUMNS_V1,
    as_bool,
    finite_float,
    parse_time,
)
from diagnose_entry_stop_expectancy import load_audited_effective_rows


ATTRIBUTION_SCHEMA_VERSION = "1.0.0"
OUTCOME_CLASSES = ("STOP_FIRST", "TARGET_FIRST")
GEOMETRY_FIELDS = (
    "sweep_penetration_atr",
    "reclaim_distance_atr",
    "reclaim_sweep_balance",
    "entry_to_poi_r",
    "poi_to_stop_r",
    "gross_reward_r",
    "cost_fraction_gross_risk",
    "cost_aware_plan_rr",
)
GEOMETRY_VIEWS = {
    "full_geometry_control": tuple(range(8)),
    "trigger_shape": (0, 1, 2),
    "entry_invalidation_geometry": (3, 4),
    "payoff_geometry": (5, 6, 7),
}
NEIGHBOURS = 15
FOLDS = 4
INITIAL_TRAIN_FRACTION = 0.50
READINESS_GATE = {
    "minimum_support_gain": 0.03,
    "minimum_balanced_accuracy": 0.55,
    "minimum_macro_f1": 0.50,
    "minimum_nearest_match": 0.50,
    "positive_support_gain_folds": 4,
    "minimum_every_class_recall": 0.30,
    "positive_support_gain_directions": 2,
}


def valid_hash(value: str, name: str) -> str:
    normalized = value.strip().upper()
    if len(normalized) != 64 or any(
        character not in "0123456789ABCDEF" for character in normalized
    ):
        raise ValueError(f"Entry geometry {name} SHA-256 is invalid")
    return normalized


def close(left: float, right: float) -> bool:
    return math.isclose(left, right, rel_tol=1e-9, abs_tol=1e-8)


def geometry_views() -> dict[str, tuple[int, ...]]:
    return dict(GEOMETRY_VIEWS)


def validate_geometry(
    outcome: dict[str, str], effective: dict[str, Any], setup: dict[str, str]
) -> list[float]:
    """Validate exact accepted-plan parity and derive frozen geometry fields."""
    direction = str(effective["direction"])
    if direction not in {"TRADE_SETUP_BUY", "TRADE_SETUP_SELL"} or (
        outcome["direction"] != direction or setup["direction"] != direction
    ):
        raise ValueError("Entry geometry direction parity failed")
    if outcome["outcome"] not in OUTCOME_CLASSES or (
        outcome["outcome"] != effective["outcome"]
    ):
        raise ValueError("Entry geometry outcome class changed")
    if not as_bool(setup["poi_confirmed"]) or not as_bool(
        setup["trigger_confirmed"]
    ) or not as_bool(setup["plan_available"]):
        raise ValueError("Entry geometry accepted Setup evidence is incomplete")

    entry = finite_float(outcome["plan_entry"], "plan_entry")
    stop = finite_float(outcome["plan_stop"], "plan_stop")
    target = finite_float(outcome["plan_target"], "plan_target")
    plan_rr = finite_float(outcome["plan_rr"], "plan_rr")
    minimum_rr = finite_float(outcome["minimum_rr"], "minimum_rr")
    cost_points = finite_float(
        outcome["estimated_cost_points"], "estimated_cost_points"
    )
    point_size = finite_float(outcome["point_size"], "point_size")
    stored_risk_points = finite_float(outcome["risk_points"], "risk_points")
    if min(entry, stop, target, minimum_rr, point_size, stored_risk_points) <= 0.0:
        raise ValueError("Entry geometry accepted plan value is invalid")
    if plan_rr + 1e-9 < minimum_rr or minimum_rr + 1e-9 < 2.0 or cost_points < 0.0:
        raise ValueError("Entry geometry accepted RR contract changed")

    setup_parity = {
        "plan_entry": entry,
        "plan_stop": stop,
        "plan_target": target,
        "nearest_target": target,
        "structural_stop": stop,
        "plan_rr": plan_rr,
        "minimum_rr": minimum_rr,
        "estimated_cost_points": cost_points,
    }
    for name, expected in setup_parity.items():
        if not close(finite_float(setup[name], name), expected):
            raise ValueError(f"Entry geometry Setup/outcome {name} parity failed")
    effective_parity = {
        "entry": entry,
        "stop": stop,
        "target": target,
        "plan_rr": plan_rr,
        "estimated_cost_points": cost_points,
        "point_size": point_size,
    }
    for name, expected in effective_parity.items():
        if not close(float(effective[name]), expected):
            raise ValueError(f"Entry geometry effective {name} parity failed")

    buy = direction == "TRADE_SETUP_BUY"
    if (buy and not stop < entry < target) or (
        not buy and not target < entry < stop
    ):
        raise ValueError("Entry geometry plan direction is invalid")
    poi = finite_float(setup["reference_poi"], "reference_poi")
    if (buy and not stop < poi < entry) or (
        not buy and not entry < poi < stop
    ):
        raise ValueError("Entry geometry POI is not between Entry and Stop")

    gross_risk_price = abs(entry - stop)
    risk_points = gross_risk_price / point_size
    gross_reward_points = abs(target - entry) / point_size
    if not close(risk_points, stored_risk_points):
        raise ValueError("Entry geometry risk-point parity failed")
    expected_plan_rr = (
        (gross_reward_points - cost_points) / (risk_points + cost_points)
    )
    if not close(expected_plan_rr, plan_rr):
        raise ValueError("Entry geometry cost-aware RR parity failed")

    sweep = finite_float(setup["sweep_penetration_atr"], "sweep_penetration_atr")
    reclaim = finite_float(setup["reclaim_distance_atr"], "reclaim_distance_atr")
    if sweep <= 0.0 or reclaim <= 0.0:
        raise ValueError("Entry geometry trigger shape is invalid")
    values = [
        sweep,
        reclaim,
        reclaim / (sweep + reclaim),
        abs(entry - poi) / gross_risk_price,
        abs(poi - stop) / gross_risk_price,
        gross_reward_points / risk_points,
        cost_points / risk_points,
        plan_rr,
    ]
    if any(not math.isfinite(value) or value < 0.0 for value in values):
        raise ValueError("Entry geometry derived value is invalid")
    if not close(values[3] + values[4], 1.0):
        raise ValueError("Entry geometry POI risk decomposition changed")
    return values


def read_setup_evidence(
    path: Path,
    expected_sha256: str,
    wanted: set[Any],
    cutoff: Any,
    require_cutoff: bool,
) -> dict[Any, dict[str, str]]:
    if sha256(path) != valid_hash(expected_sha256, path.name):
        raise ValueError("Entry geometry Setup Audit SHA-256 mismatch")
    selected: dict[Any, dict[str, str]] = {}
    previous = None
    cutoff_reached = False
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or tuple(reader.fieldnames) != (
            SETUP_AUDIT_COLUMNS_V1
        ):
            raise ValueError("Entry geometry Setup Audit schema changed")
        for row in reader:
            observation = parse_time(row["observation_time"])
            if previous is not None and observation <= previous:
                raise ValueError("Entry geometry Setup Audit is not chronological")
            previous = observation
            if observation >= cutoff:
                cutoff_reached = True
                break
            if observation in wanted:
                if observation in selected:
                    raise ValueError("Entry geometry Setup key is duplicated")
                selected[observation] = row
    if require_cutoff and not cutoff_reached:
        raise ValueError("Entry geometry main Setup Audit did not reach Train cutoff")
    return selected


def verify_prior_evidence(
    manifest_path: Path,
    expected_manifest_sha256: str,
    imp086_path: Path,
    expected_imp086_sha256: str,
    pretrain_setup_hash: str,
    main_setup_hash: str,
    train_hash: str,
) -> tuple[Any, str, str]:
    manifest_hash = sha256(manifest_path)
    if manifest_hash != valid_hash(expected_manifest_sha256, "manifest"):
        raise ValueError("Entry geometry Target manifest SHA-256 mismatch")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    if manifest.get("validation_dataset_used") is not False or (
        manifest.get("test_dataset_used") is not False
    ) or manifest.get("runtime_changed") is not False or (
        manifest.get("deployment_authorized") is not False
    ):
        raise ValueError("Entry geometry Target manifest protected state changed")
    expected_sources = {
        "pretrain_setup": pretrain_setup_hash,
        "main_setup": main_setup_hash,
        "augmented_train": train_hash,
    }
    if any(
        manifest.get("source_hashes", {}).get(name) != value
        for name, value in expected_sources.items()
    ):
        raise ValueError("Entry geometry Target manifest source parity failed")
    cutoff = parse_time(str(manifest.get("train_end_exclusive", "")))

    imp086_hash = sha256(imp086_path)
    if imp086_hash != valid_hash(expected_imp086_sha256, "IMP-086"):
        raise ValueError("Entry geometry IMP-086 SHA-256 mismatch")
    imp086 = json.loads(imp086_path.read_text(encoding="utf-8-sig"))
    if imp086.get("records") != 232 or imp086.get("hypothesis_ready_group") is not None:
        raise ValueError("Entry geometry IMP-086 decision changed")
    for flag in (
        "threshold_selected",
        "filter_authorized",
        "candidate_selected",
        "validation_dataset_read",
        "test_dataset_read",
        "model_training_performed",
        "runtime_changed",
        "risk_changed",
        "runtime_change_request_authorized",
        "deployment_authorized",
    ):
        if imp086.get(flag) is not False:
            raise ValueError("Entry geometry IMP-086 protected state changed")
    if imp086.get("deployment_remains_no_go") is not True:
        raise ValueError("Entry geometry IMP-086 NO-GO lock changed")
    return cutoff, manifest_hash, imp086_hash


def load_records(
    train_path: Path,
    expected_train_sha256: str,
    audit_path: Path,
    expected_audit_sha256: str,
    pretrain_setup_path: Path,
    expected_pretrain_setup_sha256: str,
    main_setup_path: Path,
    expected_main_setup_sha256: str,
    manifest_path: Path,
    expected_manifest_sha256: str,
    imp086_path: Path,
    expected_imp086_sha256: str,
) -> tuple[list[dict[str, Any]], dict[str, str]]:
    effective, _, train_hash, audit_hash = load_audited_effective_rows(
        train_path, expected_train_sha256, audit_path, expected_audit_sha256
    )
    pretrain_hash = valid_hash(expected_pretrain_setup_sha256, "pre-Train Setup")
    main_hash = valid_hash(expected_main_setup_sha256, "main Setup")
    cutoff, manifest_hash, imp086_hash = verify_prior_evidence(
        manifest_path,
        expected_manifest_sha256,
        imp086_path,
        expected_imp086_sha256,
        pretrain_hash,
        main_hash,
        train_hash,
    )
    wanted = {row["start"] for row in effective}
    pretrain_setup = read_setup_evidence(
        pretrain_setup_path, pretrain_hash, wanted, cutoff, False
    )
    main_setup = read_setup_evidence(
        main_setup_path, main_hash, wanted, cutoff, True
    )
    setup_by_time = {**pretrain_setup, **main_setup}
    if len(setup_by_time) != len(effective) or set(setup_by_time) != wanted:
        raise ValueError("Entry geometry Effective Train/Setup join is incomplete")

    raw_rows = read_trainable(train_path)
    outcome_by_time = {parse_time(row["observation_time"]): row for row in raw_rows}
    records: list[dict[str, Any]] = []
    for selected in effective:
        observation = selected["start"]
        if observation not in outcome_by_time:
            raise ValueError("Entry geometry Effective Train key is missing")
        outcome = outcome_by_time[observation]
        setup = setup_by_time[observation]
        features = validate_geometry(outcome, selected, setup)
        records.append({
            "observation_time": selected["observation_time"],
            "observation": observation,
            "outcome_known_at": selected["end"],
            "symbol": outcome["symbol"],
            "direction": selected["direction"],
            "outcome": selected["outcome"],
            "outcome_index": OUTCOME_CLASSES.index(selected["outcome"]),
            "entry_bar_open": setup["entry_bar_open"],
            "entry": selected["entry"],
            "reference_poi": finite_float(setup["reference_poi"], "reference_poi"),
            "structural_stop": selected["stop"],
            "nearest_target": selected["target"],
            "point_size": selected["point_size"],
            "features": features,
        })
    if Counter(record["outcome"] for record in records) != Counter(
        {"STOP_FIRST": 173, "TARGET_FIRST": 59}
    ):
        raise ValueError("Entry geometry Effective Train outcome counts changed")
    return records, {
        "source_train_sha256": train_hash,
        "effective_sample_audit_sha256": audit_hash,
        "pretrain_setup_audit_sha256": sha256(pretrain_setup_path),
        "main_setup_audit_sha256": sha256(main_setup_path),
        "past_only_target_manifest_sha256": manifest_hash,
        "imp086_attribution_sha256": imp086_hash,
    }


def classification_metrics(actual: list[int], predicted: list[int]) -> dict[str, Any]:
    labels = [0, 1]
    precision, recall, class_f1, _ = precision_recall_fscore_support(
        actual, predicted, labels=labels, zero_division=0
    )
    return {
        "records": len(actual),
        "accuracy": float(accuracy_score(actual, predicted)),
        "balanced_accuracy": float(balanced_accuracy_score(actual, predicted)),
        "macro_f1": float(f1_score(
            actual, predicted, labels=labels, average="macro", zero_division=0
        )),
        "by_class": {
            name: {
                "precision": float(precision[index]),
                "recall": float(recall[index]),
                "f1": float(class_f1[index]),
                "support": sum(value == index for value in actual),
            }
            for index, name in enumerate(OUTCOME_CLASSES)
        },
    }


def evaluate_neighbourhood(
    train_features: Sequence[Sequence[float]],
    train_labels: Sequence[int],
    evaluation_features: Sequence[Sequence[float]],
    evaluation_labels: Sequence[int],
    evaluation_directions: Sequence[str],
    indices: Sequence[int],
    neighbours: int = NEIGHBOURS,
) -> tuple[dict[str, Any], list[int], list[dict[str, Any]]]:
    if not indices or neighbours <= 0 or not train_features or not evaluation_features:
        raise ValueError("Entry geometry neighbourhood input is invalid")
    if len(train_features) != len(train_labels) or len(evaluation_features) != len(
        evaluation_labels
    ) or len(evaluation_labels) != len(evaluation_directions):
        raise ValueError("Entry geometry neighbourhood lengths differ")
    train = np.asarray(train_features, dtype=float)[:, indices]
    evaluation = np.asarray(evaluation_features, dtype=float)[:, indices]
    scaler = StandardScaler()
    scaled_train = scaler.fit_transform(train)
    scaled_evaluation = scaler.transform(evaluation)
    effective_k = min(neighbours, len(train_labels))
    model = NearestNeighbors(n_neighbors=effective_k, metric="euclidean")
    model.fit(scaled_train)
    distances, neighbour_indices = model.kneighbors(scaled_evaluation)
    history = Counter(int(value) for value in train_labels)
    predicted: list[int] = []
    details: list[dict[str, Any]] = []
    for row_number, indices_for_row in enumerate(neighbour_indices):
        labels = [int(train_labels[index]) for index in indices_for_row]
        counts = [labels.count(index) for index in range(len(OUTCOME_CLASSES))]
        actual = int(evaluation_labels[row_number])
        prediction = max(range(len(counts)), key=lambda index: counts[index])
        predicted.append(prediction)
        support = counts[actual] / effective_k
        history_support = history[actual] / len(train_labels)
        details.append({
            "direction": evaluation_directions[row_number],
            "support": support,
            "history_support": history_support,
            "support_gain": support - history_support,
            "nearest_match": float(labels[0] == actual),
        })
    return ({
        "neighbours": effective_k,
        "records": len(evaluation_labels),
        "mean_true_class_support": fmean(item["support"] for item in details),
        "mean_history_true_class_support": fmean(
            item["history_support"] for item in details
        ),
        "mean_true_class_support_gain": fmean(
            item["support_gain"] for item in details
        ),
        "nearest_class_match_rate": fmean(item["nearest_match"] for item in details),
        "mean_nearest_distance": float(np.mean(distances[:, 0])),
        "classification": classification_metrics(list(evaluation_labels), predicted),
    }, predicted, details)


def expanding_folds(size: int) -> list[tuple[int, int, int]]:
    if size < 100:
        raise ValueError("Entry geometry attribution requires at least 100 records")
    initial = int(size * INITIAL_TRAIN_FRACTION)
    remaining = size - initial
    base = remaining // FOLDS
    folds: list[tuple[int, int, int]] = []
    start = initial
    for index in range(FOLDS):
        end = size if index == FOLDS - 1 else start + base
        folds.append((start, start, end))
        start = end
    return folds


def readiness(metrics: dict[str, Any]) -> dict[str, bool]:
    recalls = [
        float(metrics["classification"]["by_class"][name]["recall"])
        for name in OUTCOME_CLASSES
    ]
    direction_gains = metrics["support_gain_by_direction"]
    gates = {
        "support_gain": metrics["mean_true_class_support_gain"] >= (
            READINESS_GATE["minimum_support_gain"]
        ),
        "balanced_accuracy": metrics["classification"]["balanced_accuracy"] >= (
            READINESS_GATE["minimum_balanced_accuracy"]
        ),
        "macro_f1": metrics["classification"]["macro_f1"] >= (
            READINESS_GATE["minimum_macro_f1"]
        ),
        "nearest_match": metrics["nearest_class_match_rate"] >= (
            READINESS_GATE["minimum_nearest_match"]
        ),
        "fold_stability": metrics["positive_support_gain_folds"] == (
            READINESS_GATE["positive_support_gain_folds"]
        ),
        "every_class_recall": min(recalls) >= (
            READINESS_GATE["minimum_every_class_recall"]
        ),
        "direction_stability": len(direction_gains) == 2 and all(
            float(value) > 0.0 for value in direction_gains.values()
        ),
    }
    gates["hypothesis_ready"] = all(gates.values())
    return gates


def aggregate_view(records: list[dict[str, Any]], indices: Sequence[int]) -> dict[str, Any]:
    features = [record["features"] for record in records]
    labels = [int(record["outcome_index"]) for record in records]
    folds = expanding_folds(len(records))
    fold_reports: list[dict[str, Any]] = []
    all_actual: list[int] = []
    all_predicted: list[int] = []
    all_details: list[dict[str, Any]] = []
    positive_folds = 0
    for fold_number, (train_end, evaluation_start, evaluation_end) in enumerate(
        folds, start=1
    ):
        if records[train_end - 1]["outcome_known_at"] > records[evaluation_start][
            "observation"
        ]:
            raise ValueError("Entry geometry past-only fold overlaps maturity")
        report, predicted, details = evaluate_neighbourhood(
            features[:train_end],
            labels[:train_end],
            features[evaluation_start:evaluation_end],
            labels[evaluation_start:evaluation_end],
            [record["direction"] for record in records[evaluation_start:evaluation_end]],
            indices,
        )
        positive_folds += report["mean_true_class_support_gain"] > 0.0
        all_actual.extend(labels[evaluation_start:evaluation_end])
        all_predicted.extend(predicted)
        all_details.extend(details)
        fold_reports.append({
            "fold": fold_number,
            "train_records": train_end,
            "evaluation_start": evaluation_start,
            "evaluation_end": evaluation_end,
            **report,
        })
    direction_gains = {
        direction: fmean(
            item["support_gain"] for item in all_details
            if item["direction"] == direction
        )
        for direction in ("TRADE_SETUP_BUY", "TRADE_SETUP_SELL")
    }
    aggregate = {
        "records": len(all_details),
        "mean_true_class_support": fmean(item["support"] for item in all_details),
        "mean_history_true_class_support": fmean(
            item["history_support"] for item in all_details
        ),
        "mean_true_class_support_gain": fmean(
            item["support_gain"] for item in all_details
        ),
        "nearest_class_match_rate": fmean(
            item["nearest_match"] for item in all_details
        ),
        "classification": classification_metrics(all_actual, all_predicted),
        "positive_support_gain_folds": positive_folds,
        "support_gain_by_direction": direction_gains,
        "folds": fold_reports,
    }
    aggregate["hypothesis_readiness_gates"] = readiness(aggregate)
    return aggregate


def descriptive_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for outcome in OUTCOME_CLASSES:
        selected = [record for record in records if record["outcome"] == outcome]
        result[outcome] = {
            "records": len(selected),
            "geometry": {
                name: {
                    "mean": fmean(record["features"][index] for record in selected),
                    "median": median(record["features"][index] for record in selected),
                }
                for index, name in enumerate(GEOMETRY_FIELDS)
            },
        }
    return result


def diagnose(
    train_path: Path,
    expected_train_sha256: str,
    audit_path: Path,
    expected_audit_sha256: str,
    pretrain_setup_path: Path,
    expected_pretrain_setup_sha256: str,
    main_setup_path: Path,
    expected_main_setup_sha256: str,
    manifest_path: Path,
    expected_manifest_sha256: str,
    imp086_path: Path,
    expected_imp086_sha256: str,
) -> dict[str, Any]:
    records, hashes = load_records(
        train_path,
        expected_train_sha256,
        audit_path,
        expected_audit_sha256,
        pretrain_setup_path,
        expected_pretrain_setup_sha256,
        main_setup_path,
        expected_main_setup_sha256,
        manifest_path,
        expected_manifest_sha256,
        imp086_path,
        expected_imp086_sha256,
    )
    views = {
        name: aggregate_view(records, indices)
        for name, indices in GEOMETRY_VIEWS.items()
    }
    eligible = [
        name for name in GEOMETRY_VIEWS
        if name != "full_geometry_control"
        and views[name]["hypothesis_readiness_gates"]["hypothesis_ready"]
    ]
    eligible.sort(key=lambda name: (
        -min(
            views[name]["classification"]["by_class"][outcome]["recall"]
            for outcome in OUTCOME_CLASSES
        ),
        -min(views[name]["support_gain_by_direction"].values()),
        -views[name]["mean_true_class_support_gain"],
        -views[name]["classification"]["macro_f1"],
        -views[name]["classification"]["balanced_accuracy"],
        name,
    ))
    return {
        "entry_geometry_outcome_attribution_schema_version": ATTRIBUTION_SCHEMA_VERSION,
        "status": "ENTRY_GEOMETRY_OUTCOME_ATTRIBUTION_TRAIN_ONLY_NO_GO",
        **hashes,
        "records": len(records),
        "outcome_classes": list(OUTCOME_CLASSES),
        "outcome_counts": dict(sorted(Counter(
            record["outcome"] for record in records
        ).items())),
        "geometry_fields": list(GEOMETRY_FIELDS),
        "method": {
            "folds": FOLDS,
            "initial_train_fraction": INITIAL_TRAIN_FRACTION,
            "neighbours": NEIGHBOURS,
            "past_only_maturity_enforced": True,
            "readiness_gate": READINESS_GATE,
        },
        "geometry_views": views,
        "views_ranked_for_separate_confirmation": eligible,
        "hypothesis_ready_view": eligible[0] if eligible else None,
        "outcome_geometry_summary": descriptive_summary(records),
        "threshold_selected": False,
        "filter_authorized": False,
        "candidate_selected": False,
        "validation_dataset_read": False,
        "test_dataset_read": False,
        "model_training_performed": False,
        "feature_schema_changed": False,
        "runtime_changed": False,
        "risk_changed": False,
        "runtime_change_request_authorized": False,
        "deployment_authorized": False,
        "deployment_remains_no_go": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", required=True, type=Path)
    parser.add_argument("--expected-train-sha256", required=True)
    parser.add_argument("--effective-sample-audit", required=True, type=Path)
    parser.add_argument("--expected-audit-sha256", required=True)
    parser.add_argument("--pretrain-setup", required=True, type=Path)
    parser.add_argument("--expected-pretrain-setup-sha256", required=True)
    parser.add_argument("--main-setup", required=True, type=Path)
    parser.add_argument("--expected-main-setup-sha256", required=True)
    parser.add_argument("--past-only-target-manifest", required=True, type=Path)
    parser.add_argument("--expected-manifest-sha256", required=True)
    parser.add_argument("--imp086-attribution", required=True, type=Path)
    parser.add_argument("--expected-imp086-sha256", required=True)
    parser.add_argument("--output", required=True, type=Path)
    arguments = parser.parse_args()
    report = diagnose(
        arguments.train,
        arguments.expected_train_sha256,
        arguments.effective_sample_audit,
        arguments.expected_audit_sha256,
        arguments.pretrain_setup,
        arguments.expected_pretrain_setup_sha256,
        arguments.main_setup,
        arguments.expected_main_setup_sha256,
        arguments.past_only_target_manifest,
        arguments.expected_manifest_sha256,
        arguments.imp086_attribution,
        arguments.expected_imp086_sha256,
    )
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
