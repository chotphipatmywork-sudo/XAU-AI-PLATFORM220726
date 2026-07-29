# EFC-001 Evaluation Framework Contract

Version: 1.0.0

Status: Draft — Specification only; evaluation implementation not authorized

Document Type: Research evaluation framework contract

Architecture Baseline: ABR-1.0 (Frozen)

## Purpose

Define governance requirements for evaluating future controlled research outputs without changing Runtime or production behavior.

## Scope

This contract covers evaluation questions, approved datasets, metrics, partition use, validation, reproducibility, acceptance, and reporting. It does not authorize model training, evaluation code, deployment, or production use.

## Ownership

The Research Owner defines the evaluation question and preregistration. The Technical Reviewer reviews metric and partition compatibility. The Validator checks evidence. The Project Owner approves evaluation and acceptance.

## Inputs

Inputs must be accepted dataset and model identities, compatible TSC-001 schemas, approved evaluation configuration, sealed-partition permissions, and ELC-001 environment evidence.

## Outputs

An authorized evaluation may produce versioned metric records, reports, confidence intervals, and an evaluation manifest. This contract creates none of these outputs.

## Invariants

Evaluation is offline, deterministic where technically possible, traceable to exact inputs, and independent of Runtime, Brain, Risk, Execution, and protected modules. Test data remains untouched until its separately approved gate.

## Validation Rules

Validation must verify input identities and hashes, schema compatibility, partition permissions, metric definitions, sample accounting, missing-value handling, reproducibility evidence, and manifest completeness. Missing provenance fails closed.

## Versioning

Changes to questions, metrics, populations, partition policy, thresholds, or report semantics require a new evaluation version and approval.

## Acceptance Criteria

Acceptance requires an approved preregistration, passing validation, complete traceability, independent backup, immutable evidence storage, and Project Owner approval. Acceptance does not authorize deployment.

## References

RFB-001, RDR-001, TEC-001, TSC-001, TVC-001, TMS-001, MMS-001, DPC-001, ELC-001, and DAC-001.
