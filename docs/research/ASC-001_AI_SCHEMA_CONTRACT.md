# ASC-001 AI Schema Contract

Version: 1.0.0

Status: Draft — Specification only; AI record generation not authorized

Document Type: Research AI schema contract

Architecture Baseline: ABR-1.0 (Frozen)

## Purpose

Define the identity and compatibility requirements for future offline AI records.

## Scope

The schema covers AI record identity, dataset/model references, feature and label versions, declared output fields, configuration identity, status, and missing-value semantics. It does not define a new feature, label, model, or trading decision.

## Ownership

The Research Owner proposes the schema. Feature, Label, Training, Evaluation, and Model Registry owners review their references. The Project Owner approves the version.

## Inputs

Inputs are accepted records governed by FSC-001, LSC-001, TSC-001, ESC-001, and MSC-001, joined through explicit immutable identities.

## Outputs

An authorized record may contain `record_id`, `symbol`, `timestamp`, Research Track ID, Dataset ID/version, Model ID/version, Feature Set version, Label Set version, AI configuration version, output status, and declared missing reason.

## Invariants

Identity fields are preserved and unique according to the source contract. Feature and label values are not silently changed. AI outputs cannot be interpreted as Risk permission, Execution approval, or production decisions.

## Validation Rules

Reject duplicate or missing identities, incompatible schema versions, undeclared fields, invalid output status, non-deterministic ordering, partition leakage, and manifest mismatch.

## Versioning

Any field, type, output semantic, configuration, or serialization change requires a new AI schema version. Existing records remain immutable.

## Acceptance Criteria

Acceptance requires compatibility validation, complete provenance, deterministic serialization, independent backup, and Project Owner approval.

## References

AEC-001, FSC-001, LSC-001, TSC-001, ESC-001, MSC-001, RFB-001, RDR-001, MMS-001, MMS-002, ELC-001, and DAC-001.
