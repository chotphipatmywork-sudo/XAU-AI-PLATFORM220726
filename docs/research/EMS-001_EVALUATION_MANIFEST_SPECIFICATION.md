# EMS-001 Evaluation Manifest Specification

Version: 1.0.0

Status: Draft — Specification only; evaluation generation not authorized

Document Type: Research evaluation manifest specification

Architecture Baseline: ABR-1.0 (Frozen)

## Purpose

Define metadata required to trace future evaluation evidence to its approved question, inputs, configuration, environment, validation, and acceptance.

## Scope

The manifest covers evaluation identity, dataset and model identities, feature and label schema versions, partition, metric configuration, commands, hashes, validation, acceptance, storage, and backup. It creates no manifest instance here.

## Ownership

The Research Owner prepares the manifest. The Validator verifies it. The Technical Reviewer reviews traceability. The Project Owner approves acceptance and freeze.

## Inputs

Required references include Evaluation ID, Experiment ID, Run ID, Dataset ID/version, Model ID/version, Feature Set and Label Set versions, Partition ID, metric configuration, source and input hashes, Git commit, ELC-001 environment lock, validation report, and approval record.

## Outputs

An authorized operation may produce an immutable manifest containing the complete evaluation provenance and exact output hash. This specification does not generate evaluation results.

## Invariants

Every output-affecting input is versioned and hash-linked. Evaluation results remain separate from labels, features, risk, execution, and production decisions. Missing provenance fails closed.

## Validation Rules

The manifest validator must verify required fields, identity relationships, schema and partition compatibility, metric configuration, ordered commands, exit codes, timestamps, input/output hashes, validation status, acceptance state, storage location, and independent-backup status.

## Versioning

Manifest schema or semantic changes require a new EMS version and review. Existing manifests are immutable; corrections create a new manifest linked to the superseded record.

## Acceptance Criteria

Acceptance requires complete traceability, passing EVC-001 validation, matching input and output hashes, verified independent backup, immutable evidence storage, and Project Owner approval under DAC-001.

## References

EFC-001, ESC-001, EVC-001, TEC-001, TSC-001, TVC-001, TMS-001, RFB-001, RDR-001, MMS-001, DPC-001, ELC-001, and DAC-001.
