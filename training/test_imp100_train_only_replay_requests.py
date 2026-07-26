"""Focused tests for IMP-100 contract and outcome-free request preparation."""

from __future__ import annotations

import copy
import json
import tempfile
from pathlib import Path

from build_imp100_train_only_replay_requests import (
    FORBIDDEN_OUTCOME_FIELDS,
    build,
    read_rows,
)
from diagnose_current_feed_setup_funnel import sha256
from validate_imp100_replay_contract import (
    EXPECTED_CONTRACT_SHA256,
    load_and_validate,
    validate_contract,
    verify_hash,
)


ROOT = Path(__file__).resolve().parent.parent
CONTRACT = ROOT / "training/config/imp100_train_only_replay_contract.json"


def mutation_rejected(contract: dict, mutate) -> bool:
    candidate = copy.deepcopy(contract)
    mutate(candidate)
    try:
        validate_contract(candidate)
    except ValueError:
        return True
    return False


def main() -> None:
    if sha256(CONTRACT) != EXPECTED_CONTRACT_SHA256:
        raise AssertionError("IMP-100 deterministic contract hash changed")
    contract = load_and_validate(CONTRACT, ROOT)
    mutations = [
        lambda item: item["replay_rules"].update({"minimum_rr": 1.5}),
        lambda item: item["verified_imp099_accounting"].update(
            {"common_support_opportunities": 361}
        ),
        lambda item: item["arms"].pop(),
        lambda item: item["strategy_gates"].update(
            {"profit_factor_minimum": 1.2}
        ),
        lambda item: item["prohibitions"].update({"modify_runtime": False}),
    ]
    if not all(mutation_rejected(contract, mutate) for mutate in mutations):
        raise AssertionError("IMP-100 contract mismatch was accepted")
    with tempfile.TemporaryDirectory() as temporary:
        probe = Path(temporary) / "hash_probe.txt"
        probe.write_text("source", encoding="utf-8")
        try:
            verify_hash(probe, "0" * 64, "probe")
        except ValueError:
            pass
        else:
            raise AssertionError("IMP-100 source hash mismatch was accepted")

    raw_source = (
        ROOT
        / contract["frozen_inputs"]["imp099_raw_experiment_records"]["path"]
    )
    raw_rows = read_rows(raw_source)
    first = build(contract, raw_rows, sha256(raw_source))
    second = build(contract, raw_rows, sha256(raw_source))
    if first != second:
        raise AssertionError("IMP-100 request ordering is not deterministic")
    active, ledger, manifest = first
    if len(active) != 685 or len(ledger) != 2388:
        raise AssertionError("IMP-100 request accounting changed")
    if manifest["common_support_opportunities"] != 362:
        raise AssertionError("IMP-100 common support changed")
    if len({row["request_id"] for row in ledger}) != 2388:
        raise AssertionError("IMP-100 request IDs are not unique")
    grouped: dict[str, set[str]] = {}
    for row in ledger:
        grouped.setdefault(row["base_opportunity_id"], set()).add(row["arm_id"])
    if len(grouped) != 597 or any(len(arms) != 4 for arms in grouped.values()):
        raise AssertionError("IMP-100 request-level pairing changed")
    mappings = {
        row["arm_id"]: (row["stop_identity"], row["target_identity"])
        for row in ledger
    }
    expected = {
        arm["arm_id"]: (arm["stop_identity"], arm["target_identity"])
        for arm in contract["arms"]
    }
    if mappings != expected:
        raise AssertionError("IMP-100 arm geometry mapping changed")
    if any(row["train_cutoff_compliant"] != "true" for row in ledger):
        raise AssertionError("IMP-100 Train cutoff validation changed")
    if any(row["validation_dataset_used"] != "false" for row in ledger):
        raise AssertionError("IMP-100 Validation data was enabled")
    if any(row["test_dataset_used"] != "false" for row in ledger):
        raise AssertionError("IMP-100 Test data was enabled")
    if any(field in row for row in ledger for field in FORBIDDEN_OUTCOME_FIELDS):
        raise AssertionError("IMP-100 replay outcome field was populated")
    missing = [
        row for row in ledger if row["no_trade_reason"] == "MISSING_GEOMETRY"
    ]
    if not missing or any(row["replay_requested"] == "true" for row in missing):
        raise AssertionError("IMP-100 missing geometry was imputed")
    control = [row for row in ledger if row["arm_id"] == "CONTROL"]
    if sum(row["geometry_eligible"] == "true" for row in control) != 459:
        raise AssertionError("IMP-100 Control eligible parity changed")
    if sum(row["rr_pass"] == "true" for row in control) != 76:
        raise AssertionError("IMP-100 Control pass parity changed")
    print("IMP-100 contract and request preparation focused test passed")


if __name__ == "__main__":
    main()
