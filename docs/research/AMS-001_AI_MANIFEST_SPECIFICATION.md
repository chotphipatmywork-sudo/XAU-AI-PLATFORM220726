# AMS-001 AI Manifest Specification

Version: 1.0.0

Status: Draft — Specification only; AI generation not authorized

Document Type: Research AI manifest specification

Architecture Baseline: ABR-1.0 (Frozen)

## Purpose

Define metadata required to trace future AI evidence to its approved source, schemas, training run, evaluation, model registry, configuration, environment, validation, and acceptance.

## Scope

The manifest covers Research Track, Dataset, Feature Set, Label Set, Training Session, Execution, Evaluation, Model, AI configuration, validation, acceptance, storage, backup, and exact-byte hashes. It creates no manifest instance here.

## Ownership

The Research Owner prepares the manifest. The Validator verifies it. The Technical Reviewer reviews lineage. The Project Owner approves acceptance and freeze.

## Inputs

Required references include all upstream identities and versions, source/configuration hashes, Git commit, working-tree state, ELC-001 environment lock, ordered commands, validation report, storage location, and approval record.

## Outputs

An authorized process may produce an immutable JSON manifest containing the complete AI provenance chain and output hash. This specification creates no AI record or artifact.

## Invariants

Every output-affecting input is versioned and hash-linked. AI evidence remains separate from Runtime, Risk, Execution, and production decisions. Missing provenance fails closed.

## Validation Rules

The manifest validator must verify required identities, parent relationships, schema compatibility, model status, configuration and environment evidence, commands and exit codes, timestamps, hashes, validation state, acceptance state, storage, and independent backup.

## Versioning

Manifest schema or semantic changes require a new AMS version and review. Existing manifests are immutable; corrections create a new linked manifest.

## Acceptance Criteria

Acceptance requires passing AVC-001 validation, matching upstream manifests and hashes, verified independent backup, immutable evidence storage, and Project Owner approval under DAC-001.

## References

AEC-001, ASC-001, AVC-001, FSC-001, LSC-001, TEC-001, TSC-001, TVC-001, TMS-001, EFC-001, ESC-001, EVC-001, EMS-001, MRC-001, MSC-001, MVC-001, MMS-002, RFB-001, RDR-001, ELC-001, and DAC-001.
