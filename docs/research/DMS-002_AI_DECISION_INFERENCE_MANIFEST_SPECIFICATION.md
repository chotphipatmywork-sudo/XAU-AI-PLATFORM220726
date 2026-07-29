# DMS-002 AI Decision Inference Manifest Specification

Version: 1.0.0

Status: Draft — Specification only; integration generation not authorized

Document Type: Research AI decision-inference manifest specification

Architecture Baseline: ABR-1.0 (Frozen)

## Purpose

Define metadata required to trace integrated offline evidence from inference and decision parents through validation and acceptance.

## Scope

The manifest covers Research Track, Dataset, Feature, Label, Training, Evaluation, Model, Inference, Decision, Integration, configuration, validation, acceptance, storage, backup, and exact-byte hashes.

## Ownership

Research Owner prepares the manifest. Validator verifies it. Technical Reviewer reviews lineage. Project Owner approves acceptance and freeze.

## Inputs

Required references include all parent identities and versions, input hashes, integration configuration/hash, Git/environment evidence, commands, validation report, storage location, and approval record.

## Outputs

An authorized process may produce an immutable JSON manifest. This specification creates no integrated record or Runtime output.

## Invariants

Every output-affecting input is versioned and hash-linked. Integrated evidence remains separate from Risk, Execution, and production behavior. Missing provenance fails closed.

## Validation Rules

Verify required identities, parent relationships, schema compatibility, join accounting, hashes, deterministic ordering, validation state, acceptance state, storage, and independent backup.

## Versioning

Manifest schema or semantic changes require a new DMS-002 version and review. Existing manifests are immutable.

## Acceptance Criteria

Acceptance requires passing DVC-002 validation, matching parent manifests and hashes, independent backup verification, immutable storage, and Project Owner approval.

## References

DIC-001, DIS-001, DVC-002, IEC-001, ISC-001, IVC-001, IMS-001, DEC-001, DSC-001, DVC-001, DMS-001, RFB-001, RDR-001, ELC-001, and DAC-001.
