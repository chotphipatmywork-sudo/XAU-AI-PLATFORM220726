# DIC-001 AI Decision Inference Integration Contract

Version: 1.0.0

Status: Draft — Specification only; integration implementation not authorized

Document Type: Research AI decision-inference integration contract

Architecture Baseline: ABR-1.0 (Frozen)

## Purpose

Define the offline data-boundary relationship between validated inference records and decision records.

## Scope

This contract governs identity joins, schema compatibility, configuration linkage, deterministic integration, validation, provenance, and acceptance. It excludes Runtime, Risk, Execution, broker, and production integration.

## Ownership

Research Owner defines the integration question. Technical Reviewer verifies compatibility. Validator checks linkage. Project Owner approves acceptance.

## Inputs

Accepted inference records under IEC-001/ISC-001 and accepted decision configuration under DEC-001/DSC-001.

## Outputs

An authorized process may produce offline integrated evidence and a manifest. It must not grant Risk permission or create an order.

## Invariants

Inference and decision identities remain separately traceable. One source record maps deterministically to the approved decision population. Confidence is not Risk authorization.

## Validation Rules

Validate one-to-one identity joins, parent hashes, schema versions, chronology, configuration compatibility, prohibited statuses, deterministic ordering, and manifest completeness.

## Versioning

Changes to join rules, output fields, configuration, or serialization require a new integration version and review.

## Acceptance Criteria

Acceptance requires passing validation, complete lineage, independent backup, immutable evidence storage, and Project Owner approval.

## References

IEC-001, ISC-001, IVC-001, IMS-001, DEC-001, DSC-001, DVC-001, DMS-001, RFB-001, RDR-001, ELC-001, and DAC-001.
