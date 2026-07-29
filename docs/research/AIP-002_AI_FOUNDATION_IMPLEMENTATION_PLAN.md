# AIP-002 AI Foundation Implementation Plan

Version: 1.0.0

Status: Approved plan; implementation not authorized by this document

Document Type: Research AI implementation plan

Architecture Baseline: ABR-1.0 (Frozen)

## Purpose

Define the smallest controlled implementation sequence for the approved AI Foundation contracts while preserving Specification First governance and protected architecture boundaries.

## Scope

The plan covers offline AI metadata, schema compatibility, validation, manifest linkage, focused tests, and acceptance evidence. It excludes model training, model creation, live inference, deployment, Runtime integration, Risk changes, Execution changes, and production use.

## Governing Contracts

Implementation must conform to AEC-001, ASC-001, AVC-001, AMS-001, TEC-001, TSC-001, TVC-001, TMS-001, EFC-001, ESC-001, EVC-001, EMS-001, MRC-001, MSC-001, MVC-001, MMS-002, RFB-001, and RDR-001.

## Implementation Phases

### Phase 1 — Contract and Identity Preparation

Confirm Research Track, Dataset, Feature Set, Label Set, Training Session, Execution, Evaluation, Model, and AI identity relationships. Freeze the required field and version map before code changes.

### Phase 2 — Offline AI Record Boundary

Implement only the approved offline record boundary. Preserve source identity fields and reject missing or incompatible upstream identities. No production or Runtime interface is permitted.

### Phase 3 — Manifest and Provenance Linkage

Emit and validate the AMS-001 manifest fields, including parent identities, schema versions, configuration/environment hashes, Git state, ordered commands, output hashes, validation state, acceptance state, storage, and backup evidence.

### Phase 4 — Validation and Focused Tests

Add standard-library unit tests for identity continuity, schema compatibility, deterministic ordering, hash mismatch, missing provenance, partition protection, and invalid lifecycle transitions. Tests must use `unittest.TestCase` and temporary directories where file operations are required.

### Phase 5 — Review and Acceptance

Run syntax and focused tests, review the diff for protected-module isolation, verify reproducibility evidence, record failures, obtain Technical Review, and obtain Project Owner acceptance. Freeze accepted metadata and manifests only after all gates pass.

## Required File Planning

Exact implementation paths remain to be proposed in a subsequent implementation specification. No source file is created by AIP-002. Any future file must remain under the offline research boundary and must not introduce Runtime, Brain, Risk, or Execution dependencies.

## Validation Sequence

1. Validate contract and schema versions.
2. Validate identity and parent linkage.
3. Validate input and configuration hashes.
4. Validate deterministic serialization and output hashes.
5. Validate partition and sealed-data access rules.
6. Validate manifest completeness.
7. Run focused tests with ResourceWarnings treated as errors.
8. Review Git scope and protected-module diff.
9. Record acceptance and backup evidence.

## Acceptance Gates

- Architecture boundary review: PASS.
- Contract compatibility review: PASS.
- Syntax validation: PASS.
- Focused test suite: all tests pass, no errors, no unexplained skips.
- Manifest/provenance validation: PASS.
- Independent backup: VERIFIED.
- Project Owner acceptance: RECORDED.

No gate authorizes training, model creation, deployment, or production use.

## Risks and Controls

| Risk | Control |
| --- | --- |
| Identity drift | Required parent identity map and fail-closed validation |
| Manifest divergence | Single AMS-001 field map and exact hash checks |
| Partition leakage | DPC-001 boundaries and sealed Validation/Test policy |
| Runtime coupling | Static dependency review and protected-module diff gate |
| Unreproducible output | ELC-001 environment, command, configuration, and Git evidence |
| Premature model use | Separate acceptance and execution authorization gates |

## Rollback Strategy

Reject the run, preserve failed evidence, and remove only unaccepted offline outputs. Never rewrite accepted history or modify Runtime. Any correction receives a new identity/version and repeats validation.

## Completion Criteria

The plan is complete when the implementation specification is approved, the focused implementation passes all gates, manifests and provenance are complete, acceptance and independent backup are recorded, and the resulting review is approved. AIP-002 itself does not authorize implementation.

## Final Status

AIP-002 is an approved planning document. Implementation requires a separate implementation specification and authorization.
