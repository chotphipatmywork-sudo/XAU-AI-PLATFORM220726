# MRC-001 Model Registry Contract

Version: 1.0.0

Status: Draft — Specification only; model creation and registration not authorized

Document Type: Research model registry contract

Architecture Baseline: ABR-1.0 (Frozen)

## Purpose

Define governance requirements for identifying, registering, validating, accepting, freezing, and archiving future offline research models.

## Scope

This contract governs model identity, lineage, compatibility, provenance, validation, storage, approval, and lifecycle. It does not create models, integrate Runtime, or authorize deployment.

## Ownership

The Research Owner proposes a model record. The Technical Reviewer verifies schema and evaluation compatibility. The Validator verifies evidence. The Project Owner approves registration and acceptance.

## Inputs

Inputs must include an accepted training run, TSC-001-compatible dataset identity, feature and label versions, approved evaluation evidence, environment lock, Git commit, and model manifest.

## Outputs

An authorized process may produce a model registry record and immutable model manifest. No model artifact or registry entry is created by this contract.

## Invariants

Every model has a unique Model ID and version linked to exactly one training run and evaluation lineage. Models remain offline research evidence unless separately approved. No model may bypass Risk or Execution boundaries.

## Validation Rules

Validate identity uniqueness, schema compatibility, training provenance, evaluation status, hashes, environment, configuration, working-tree state, storage, backup, and acceptance evidence. Missing provenance fails closed.

## Versioning

Any model bytes, input schema, training configuration, preprocessing, or output contract change requires a new Model ID or version. Existing records and artifacts are immutable.

## Acceptance Criteria

Acceptance requires passing MVC-001 validation, complete TMS-001 and EMS-001 lineage, independent backup, immutable storage, and Project Owner approval. Acceptance does not authorize deployment or production use.

## References

TEC-001, TSC-001, TVC-001, TMS-001, EFC-001, ESC-001, EVC-001, EMS-001, RFB-001, RDR-001, ELC-001, and DAC-001.
