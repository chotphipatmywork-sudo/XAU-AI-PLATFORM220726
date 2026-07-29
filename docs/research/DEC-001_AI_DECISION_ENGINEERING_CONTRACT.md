# DEC-001 AI Decision Engineering Contract

Version: 1.0.0

Status: Draft — Specification only; implementation not authorized

Document Type: Research AI decision contract

Architecture Baseline: ABR-1.0 (Frozen)

## Purpose

Define the offline research boundary for transforming validated AI outputs into explicit decision records without granting Risk permission or initiating Execution.

## Scope

This contract governs decision identity, input compatibility, deterministic decision rules, confidence handling, validation, provenance, acceptance, and separation from Runtime, Risk, and Execution.

## Ownership

Research Owner defines the decision question and configuration. Technical Reviewer verifies compatibility. Validator checks evidence. Project Owner approves acceptance.

## Inputs

Inputs are accepted AI records governed by the AI Foundation contracts, approved decision configuration, and sealed partition permissions.

## Outputs

An authorized process may produce offline decision records and manifests. It must not place orders, grant Risk approval, or alter Runtime behavior.

## Invariants

Decision, confidence, Risk permission, Execution result, and trade lifecycle remain separate concepts. Decisions are deterministic, traceable, and fail closed on missing identity or provenance.

## Validation Rules

Validate identity continuity, schema/version compatibility, configuration hash, deterministic ordering, confidence domain, partition access, manifest completeness, and protected-boundary isolation.

## Versioning

Any decision rule, threshold, output field, configuration, or serialization change requires a new version and review.

## Acceptance Criteria

Acceptance requires passing validation, complete provenance, independent backup, immutable evidence storage, and Project Owner approval. No production or Runtime authorization is implied.

## References

AEC-001, ASC-001, AVC-001, AMS-001, RFB-001, RDR-001, DPC-001, ELC-001, and DAC-001.
