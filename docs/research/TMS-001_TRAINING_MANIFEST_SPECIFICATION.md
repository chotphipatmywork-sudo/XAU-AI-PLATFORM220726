# TMS-001 Training Manifest Specification

Version: 1.0.0

Status: Draft — Specification only; training and artifact generation not authorized

Document Type: Research training manifest specification

Architecture Baseline: ABR-1.0 (Frozen)

## Purpose

Define the metadata required to trace a future assembled dataset and training run to its approved sources, schemas, environment, configuration, and validation evidence.

## Scope

The manifest covers identity, feature and label compatibility, partition provenance, configuration, environment, commands, hashes, validation, acceptance, storage, and backup. It creates no manifest instance during this specification task.

## Ownership

The Research Owner prepares the manifest. The Validator verifies it. The Technical Reviewer reviews traceability. The Project Owner approves acceptance and freeze.

## Inputs

Required references include Research Track ID, Dataset ID/version, Feature Set ID/version, Label Set ID/version, TSC-001 schema version, Source ID and hashes, partition identities, training configuration, Git commit, working-tree state, ELC-001 environment lock, validation report, and approval records.

## Outputs

An authorized run may produce an immutable manifest containing the complete identity and provenance chain. This document does not generate training outputs or models.

## Invariants

Every output-affecting input is versioned and hash-linked. Feature and label identities remain distinct. Exact-byte dataset and output hashes are recorded after authorized generation. Missing provenance fails closed.

## Validation Rules

The manifest validator must verify required fields, identity relationships, schema compatibility, partition evidence, source/configuration/environment hashes, ordered commands, exit codes, timestamps, output hashes, validation status, acceptance state, storage location, and independent-backup status.

## Versioning

Manifest schema or semantic changes require a new TMS version and review. Existing manifests are immutable; corrections create a new manifest linked to the superseded record.

## Acceptance Criteria

Acceptance requires complete traceability, passing TVC-001 validation, matching dataset and configuration hashes, verified independent backup, immutable accepted storage, and Project Owner approval under DAC-001.

## References

TEC-001, TSC-001, TVC-001, RFB-001, RDR-001, RDS-001, FSC-001, LSC-001, MMS-001, DLC-001, DPC-001, ELC-001, and DAC-001.
