# DSC-001 AI Decision Schema Contract

Version: 1.0.0

Status: Draft — Specification only; decision generation not authorized

Document Type: Research AI decision schema contract

Architecture Baseline: ABR-1.0 (Frozen)

## Purpose

Define the identity and field requirements for future offline AI decision records.

## Scope

The schema covers decision identity, source AI identity, timestamp, decision value, confidence, configuration version, status, and missing reason. It does not define Risk or Execution contracts.

## Ownership

Research Owner proposes the schema. Technical Reviewer checks AI compatibility and boundary separation. Project Owner approves the version.

## Inputs

Inputs are accepted AI records and approved decision configuration.

## Outputs

An authorized record may preserve `record_id`, `symbol`, `timestamp`, AI identity, decision identity, decision value, confidence, configuration version, and status.

## Invariants

Identity and chronology are preserved. Confidence is not Risk approval. Decision status cannot imply order execution. Missing values require explicit reasons.

## Validation Rules

Reject missing identities, duplicates, incompatible versions, invalid confidence range, unknown status, non-deterministic ordering, and manifest mismatch.

## Versioning

Changes to fields, types, meanings, confidence semantics, or serialization require a new schema version.

## Acceptance Criteria

Acceptance requires schema validation, complete parent identity linkage, deterministic serialization, independent backup, and Project Owner approval.

## References

DEC-001, AEC-001, ASC-001, AVC-001, AMS-001, RFB-001, RDR-001, DPC-001, ELC-001, and DAC-001.
