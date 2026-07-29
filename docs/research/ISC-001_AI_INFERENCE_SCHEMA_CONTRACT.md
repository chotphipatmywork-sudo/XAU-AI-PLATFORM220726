# ISC-001 AI Inference Schema Contract

Version: 1.0.0

Status: Draft — Specification only; inference record generation not authorized

Document Type: Research AI inference schema contract

Architecture Baseline: ABR-1.0 (Frozen)

## Purpose

Define identity and field requirements for future offline inference records.

## Scope

The schema covers source identity, model identity, inference identity, timestamp, output values, confidence, configuration version, status, and missing reason. It does not define live Runtime interfaces.

## Ownership

Research Owner proposes the schema. Technical Reviewer checks model and feature compatibility. Project Owner approves the version.

## Inputs

Inputs are accepted feature records, approved model metadata, and approved inference configuration.

## Outputs

An authorized record may preserve `record_id`, `symbol`, `timestamp`, `inference_id`, `model_id`, `model_version`, `feature_set_version`, `configuration_version`, output value, confidence, and status.

## Invariants

Identity and chronology are preserved. Confidence is not Risk authorization. Output status cannot imply order execution. Nulls require explicit reasons.

## Validation Rules

Reject missing identities, duplicates, incompatible schema/model versions, invalid confidence, unknown status, non-deterministic ordering, and manifest mismatch.

## Versioning

Changes to fields, types, output meaning, confidence semantics, or serialization require a new schema version.

## Acceptance Criteria

Acceptance requires schema validation, complete model/configuration linkage, deterministic serialization, independent backup, and Project Owner approval.

## References

IEC-001, AEC-001, ASC-001, MRC-001, MSC-001, DEC-001, DSC-001, RFB-001, RDR-001, ELC-001, and DAC-001.
