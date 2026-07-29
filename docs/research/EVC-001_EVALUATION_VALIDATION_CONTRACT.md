# EVC-001 Evaluation Validation Contract

Version: 1.0.0

Status: Draft — Specification only; validation implementation not authorized

Document Type: Research evaluation validation contract

Architecture Baseline: ABR-1.0 (Frozen)

## Purpose

Define fail-closed validation requirements for future evaluation evidence.

## Scope

Validation covers evaluation identity, input hashes, schema compatibility, partition protection, metric definitions, accounting, reproducibility, and manifest integrity. It does not evaluate a model during this task.

## Ownership

The Validator executes approved checks. The Technical Reviewer reviews results. The Project Owner accepts or rejects the evaluation evidence.

## Inputs

Inputs are ESC-001 records, EFC-001 configuration, accepted dataset and model manifests, partition permissions, and ELC-001 environment records.

## Outputs

The validator produces an immutable report with check identities, versions, input hashes, results, failures, warnings, and exit status.

## Invariants

Validation is deterministic and independent of Runtime and protected modules. Mandatory failures block acceptance. Validation and Test remain sealed unless separately authorized.

## Validation Rules

Checks must verify required fields and order, unique evaluation identities, finite values, sample counts, declared population, metric/version compatibility, partition boundaries, input and output hashes, environment evidence, and manifest completeness.

## Versioning

Changes to checks, thresholds, report fields, or interpretations require a new validator version and review. Reports are immutable evidence.

## Acceptance Criteria

Validation passes only when all mandatory checks pass, warnings are dispositioned, manifests agree, and Project Owner acceptance is recorded under DAC-001.

## References

EFC-001, ESC-001, TEC-001, TSC-001, TVC-001, TMS-001, RFB-001, RDR-001, MMS-001, DPC-001, ELC-001, and DAC-001.
