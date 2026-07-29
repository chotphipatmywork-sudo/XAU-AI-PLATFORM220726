# ESC-001 Evaluation Schema Contract

Version: 1.0.0

Status: Draft — Specification only; evaluation output generation not authorized

Document Type: Research evaluation schema contract

Architecture Baseline: ABR-1.0 (Frozen)

## Purpose

Define the structure and identity requirements for future evaluation records.

## Scope

The schema covers evaluation identity, input references, partition, metric identity and value, sample accounting, uncertainty evidence, status, and provenance. It does not define a model or metric implementation.

## Ownership

The Research Owner proposes the schema. The Technical Reviewer verifies compatibility with TEC-001 and TSC-001. The Project Owner approves the version.

## Inputs

Inputs are accepted evaluation definitions, dataset and model identities, partition identities, metric configuration, and environment evidence.

## Outputs

An authorized record may contain Evaluation ID, Experiment ID, Run ID, Dataset ID/version, Model ID/version, Partition ID, Metric ID/version, value, sample count, uncertainty fields, status, and missing reason where applicable.

## Invariants

Every metric is linked to exact input identities and a declared population. Metric values are not mixed across partitions or schema versions. Missing or inapplicable metrics are explicit and never silently imputed.

## Validation Rules

Reject missing identities, duplicate evaluation keys, unknown metrics, invalid numeric values, inconsistent sample counts, partition leakage, schema mismatch, and non-deterministic column ordering.

## Versioning

Any field, type, metric semantic, population, or serialization change requires a new schema version. Existing evaluation records remain immutable.

## Acceptance Criteria

Acceptance requires schema validation, complete input provenance, reproducible metric definitions, manifest agreement, independent backup, and Project Owner approval.

## References

EFC-001, TEC-001, TSC-001, TVC-001, TMS-001, RFB-001, RDR-001, MMS-001, DPC-001, ELC-001, and DAC-001.
