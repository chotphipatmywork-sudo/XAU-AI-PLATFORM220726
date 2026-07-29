# DMS-001 AI Decision Manifest Specification

Version: 1.0.0

Status: Draft — Specification only; decision generation not authorized

Document Type: Research AI decision manifest specification

Architecture Baseline: ABR-1.0 (Frozen)

## Purpose

Define metadata required to trace an offline decision record to its AI input, configuration, validation, acceptance, and storage evidence.

## Scope

The manifest covers Research Track, Dataset, Feature, Label, Training, Evaluation, Model, AI, Decision, configuration, validation, acceptance, storage, backup, and exact-byte hashes.

## Ownership

Research Owner prepares the manifest. Validator verifies it. Technical Reviewer reviews lineage. Project Owner approves acceptance and freeze.

## Inputs

Required references include parent identities and versions, decision configuration and hash, Git/environment evidence, ordered commands, validation report, storage location, and approval record.

## Outputs

An authorized process may produce an immutable JSON manifest. This specification creates no decision record or runtime output.

## Invariants

All output-affecting inputs are versioned and hash-linked. Decision evidence remains separate from Risk, Execution, and production decisions. Missing provenance fails closed.

## Validation Rules

Verify required identities, parent relationships, schema compatibility, configuration hash, deterministic ordering, validation status, acceptance state, storage, and independent backup.

## Versioning

Manifest schema or semantic changes require a new DMS version and review. Existing manifests are immutable.

## Acceptance Criteria

Acceptance requires passing DVC-001 validation, matching upstream manifests/hashes, independent backup verification, immutable storage, and Project Owner approval.

## References

DEC-001, DSC-001, DVC-001, AEC-001, ASC-001, AVC-001, AMS-001, RFB-001, RDR-001, ELC-001, and DAC-001.
