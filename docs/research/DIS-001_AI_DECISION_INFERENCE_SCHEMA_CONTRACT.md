# DIS-001 AI Decision Inference Schema Contract

Version: 1.0.0

Status: Draft — Specification only; integration record generation not authorized

Document Type: Research AI decision-inference schema contract

Architecture Baseline: ABR-1.0 (Frozen)

## Purpose

Define the combined schema requirements for offline inference and decision evidence.

## Scope

The schema covers source identity, inference identity, decision identity, model and configuration versions, confidence, decision value, status, and missing reason. It does not define Risk or Execution fields.

## Ownership

Research Owner proposes the schema. Technical Reviewer verifies parent compatibility. Project Owner approves the version.

## Inputs

Accepted inference and decision records with compatible identities and configuration versions.

## Outputs

An authorized record may preserve all parent identity fields and add an explicit integration identity and status.

## Invariants

Identity, chronology, model, configuration, inference, decision, and confidence remain distinct. Prohibited statuses such as `EXECUTE` or `RISK_APPROVED` are invalid.

## Validation Rules

Reject missing or duplicate identities, mismatched timestamps/symbols, incompatible versions, invalid confidence, prohibited statuses, non-deterministic ordering, and manifest mismatch.

## Versioning

Field, type, semantic, join, or serialization changes require a new schema version.

## Acceptance Criteria

Acceptance requires schema validation, complete parent linkage, deterministic serialization, independent backup, and Project Owner approval.

## References

DIC-001, IEC-001, ISC-001, DEC-001, DSC-001, RFB-001, RDR-001, ELC-001, and DAC-001.
