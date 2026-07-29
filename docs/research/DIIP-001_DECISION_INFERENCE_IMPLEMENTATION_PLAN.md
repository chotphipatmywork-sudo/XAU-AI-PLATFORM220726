# DIIP-001 Decision–Inference Integration Implementation Plan

Version: 1.0.0

Status: Draft — Approved for planning; implementation requires a separate execution approval

Document Type: Offline research implementation plan

Architecture Baseline: ABR-1.0 (Frozen)

## Objective

Define the controlled implementation sequence for joining validated offline inference evidence with validated offline decision evidence.

## Scope

The plan covers one-to-one identity joins, schema compatibility checks, deterministic integrated-record serialization, manifest generation, validation, and focused tests.

It excludes Runtime, Brain, AI live inference, Risk, Execution, broker communication, model training, and production artifact generation.

## Proposed Files

Implementation paths are proposed and require confirmation before coding:

- `training/decision_inference_pipeline.py`
- `training/test_decision_inference_pipeline.py`

No existing contract or protected module may be modified.

## Inputs and Outputs

Inputs are accepted inference records and accepted decision records governed by DIC-001, DIS-001, DVC-002, and DMS-002, including their manifests and hashes.

The output is an offline integrated evidence dataset and immutable manifest, subject to acceptance and independent backup. No output grants risk approval or execution authority.

## Implementation Phases

### Phase 1: Contract Binding

Bind the implementation to DIC-001, DIS-001, DVC-002, and DMS-002. Record schema and contract versions as constants and reject incompatible versions.

### Phase 2: Identity Join

Validate required parent identities and perform a deterministic one-to-one join by `record_id`. Reject missing, duplicate, or conflicting symbol and timestamp values.

### Phase 3: Canonical Serialization

Use an explicit column order, UTF-8 encoding, LF newlines, deterministic row ordering, stable timestamp formatting, and defined null representation.

### Phase 4: Manifest Generation

Generate a manifest containing parent identities, parent hashes, integration schema identity, configuration hash, output hash, record count, validation status, and provenance.

### Phase 5: Validation and Tests

Implement fail-closed validation and focused `unittest.TestCase` coverage for valid joins, duplicate IDs, missing joins, conflicting chronology, ordering, hash mismatch, and deterministic repeated generation.

### Phase 6: Review and Acceptance

Run syntax and focused tests, review protected-boundary compliance, obtain Technical Reviewer and Project Owner approval, then freeze accepted evidence.

## Dependencies

- DIC-001, DIS-001, DVC-002, and DMS-002.
- Existing inference and decision pipeline public interfaces.
- Python standard library only.
- Approved source manifests and hashes.

## Validation Plan

Run `py_compile` for both proposed files and `python -W error::ResourceWarning -m unittest training.test_decision_inference_pipeline -v` after implementation. Confirm no Runtime, Risk, Execution, dataset-generation, or model-training dependency.

## Acceptance Criteria

- All mandatory identity and schema checks pass.
- One-to-one join accounting is exact.
- Repeated generation from identical inputs produces identical bytes and SHA-256.
- Manifest references every parent and output identity.
- Validation is fail-closed and evidence is independently backed up before freeze.

## Risks and Controls

- Identity divergence: reject conflicting parent values and preserve both parent identities.
- Non-deterministic output: enforce fixed ordering and serialization rules.
- Boundary leakage: prohibit imports or calls into Runtime, Risk, or Execution.
- Unapproved evidence: keep acceptance and freeze as separate governance gates.

## Approval Gates

Implementation may begin only after approval of the proposed paths, contract binding, validation plan, and execution authorization. Dataset generation, replay, model training, and Runtime integration remain prohibited.

## References

DIC-001, DIS-001, DVC-002, DMS-002, IEC-001, ISC-001, IVC-001, IMS-001, DEC-001, DSC-001, DVC-001, DMS-001, RFB-001, and RDR-001.
