# LMS-001 Label Manifest Specification

Version: 1.0.0

Status: Draft — Specification only; label generation not authorized

Document Type: Research label manifest specification

Architecture Baseline: ABR-1.0 (Frozen)

## Purpose

Define the metadata required to identify, reproduce, validate, accept, freeze, and archive a future label dataset.

## Scope

The manifest covers label identity and provenance only. It does not create labels, assign generation-time values, or modify historical manifests or contracts.

## Ownership

The Research Owner prepares the manifest. The Validator verifies it. The Technical Reviewer reviews it. The Project Owner approves acceptance and freeze.

## Inputs

The manifest references Research Track ID, Dataset ID and version, Source ID and hash, Data Snapshot ID, Label Set ID and version, LSC-001 schema, generator and configuration identities, partition identities, environment lock, validation report, and acceptance record.

## Outputs

An authorized run may produce an immutable JSON manifest containing identity, schema, source, transformation, partition, validation, acceptance, storage, backup, and exact-byte hash evidence. This specification produces no manifest instance.

## Invariants

Every field affecting labels must be versioned and traceable. Hashes must describe exact bytes. Missing provenance, inconsistent identities, or incomplete approval fails closed. Labels remain distinct from features and outcomes.

## Validation

The manifest validator must verify required fields, identity relationships, schema and label-set versions, source and configuration hashes, partition evidence, validation status, acceptance status, storage location, and backup status.

## Versioning

Manifest schema or semantic changes require a new LMS version. Existing manifests are immutable; corrections create a new manifest linked to the superseded record.

## Acceptance Criteria

Acceptance requires complete provenance, passing LVC-001 validation, matching source and dataset hashes, verified independent backup, immutable accepted storage, and Project Owner approval under DAC-001.

## References

LEC-001, LSC-001, LVC-001, RFB-001, RDR-001, SRC-001, RDS-001, MMS-001, DLC-001, DPC-001, ELC-001, and DAC-001.
