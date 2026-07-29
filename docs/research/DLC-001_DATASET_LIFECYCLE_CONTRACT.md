# DLC-001 Dataset Lifecycle Contract

Version: 1.0.0

Status: Draft — Approval required; dataset generation not authorized

Architecture Baseline: ABR-1.0 (Frozen)

## Purpose

This contract defines the controlled lifecycle for new research datasets. Historical IMP-099, IMP-100, and IMP-101C datasets and artifacts remain closed, read-only evidence.

## Lifecycle States

```text
DEFINED
    → SOURCE_PENDING
        → SOURCE_APPROVED
            → GENERATED
                → VALIDATION_PASSED
                    → FROZEN
                        → TRAIN_ELIGIBLE
                            → ARCHIVED
```

Failure transitions may move a dataset from `SOURCE_PENDING`, `SOURCE_APPROVED`, `GENERATED`, or `VALIDATION_PASSED` to `REJECTED`. A rejected object may be archived as evidence but cannot become Train-eligible without a new approved version.

## Allowed Transitions

- `DEFINED → SOURCE_PENDING`: source requirements are recorded.
- `SOURCE_PENDING → SOURCE_APPROVED`: SRC-001 validation passes and Project Owner approval is recorded.
- `SOURCE_APPROVED → GENERATED`: authorized generation completes and produces a manifest.
- `GENERATED → VALIDATION_PASSED`: all mandatory validators pass.
- `VALIDATION_PASSED → FROZEN`: acceptance evidence and immutable storage are confirmed.
- `FROZEN → TRAIN_ELIGIBLE`: Project Owner approves Train use.
- `TRAIN_ELIGIBLE → ARCHIVED`: use is complete and retention evidence is preserved.
- Any permitted pre-freeze state → `REJECTED`: a mandatory check fails or approval is withdrawn.

No transition may skip a required validation or approval gate.

## Approval Requirements

Project Owner approval is required for `SOURCE_APPROVED`, `FROZEN`, and `TRAIN_ELIGIBLE`. Automated validation is required before `VALIDATION_PASSED`. Execution Authorization remains separate and is not granted by this contract.

## Immutable States

`FROZEN`, `TRAIN_ELIGIBLE`, `REJECTED`, and `ARCHIVED` are immutable. Corrections create a new dataset identity and version; existing bytes, manifests, and reports are retained.

## Rejection Flow

Validation failures, incomplete provenance, identity conflicts, leakage findings, or unauthorized access move the dataset to `REJECTED`. The failure report must identify the failed checks and preserve the rejected inputs. Remediation requires a new version and a new approval path.

## Responsibilities

- Research owner: prepares definitions, evidence, and transition requests.
- Implementer: creates only the approved offline object.
- Validator: executes deterministic checks and records results.
- Technical reviewer: reviews contracts, provenance, and validation evidence.
- Project Owner: grants approval, acceptance, freeze, and Train eligibility.
- Storage custodian: preserves immutable accepted evidence and backup records.

## References

- [RFB-001 Research Foundation Blueprint](RFB-001_RESEARCH_FOUNDATION_BLUEPRINT.md)
- [RDR-001 Research Track Decision Record](RDR-001_RESEARCH_TRACK_DECISION_RECORD.md)
- [SRC-001 Source Data Contract](SRC-001_SOURCE_DATA_CONTRACT.md)

## Final Status

DLC-001 is documentation only. No dataset is generated, accepted, frozen, or classified as Train-eligible by this contract.
