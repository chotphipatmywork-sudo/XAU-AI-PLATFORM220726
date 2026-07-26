"""Focused deterministic checks for the IMP-099 preregistration validator."""

import copy
import json
from pathlib import Path

from validate_imp099_preregistration import validate_spec


def rejected(spec: dict, mutation) -> bool:
    candidate = copy.deepcopy(spec)
    mutation(candidate)
    try:
        validate_spec(candidate)
    except ValueError:
        return True
    return False


def main() -> None:
    config = (
        Path(__file__).parent
        / "config"
        / "imp099_geometry_component_experiment_preregistration.json"
    )
    spec = json.loads(config.read_text(encoding="utf-8-sig"))
    validate_spec(spec)
    checks = [
        rejected(spec, lambda item: item["frozen_policy"].update(
            {"minimum_rr": 1.5}
        )),
        rejected(spec, lambda item: item["population"].update(
            {"validation_dataset_used": True}
        )),
        rejected(spec, lambda item: item["factorial_design"]["arms"].pop()),
        rejected(spec, lambda item: item["train_only_experiment_gate"].update(
            {"deployment_authorized": True}
        )),
        rejected(spec, lambda item: item["analysis_contract"].update(
            {"bonferroni_alpha": 0.05}
        )),
    ]
    if not all(checks):
        raise AssertionError("IMP-099 preregistration safety mutation accepted")
    print("IMP-099 preregistration focused test passed")


if __name__ == "__main__":
    main()
