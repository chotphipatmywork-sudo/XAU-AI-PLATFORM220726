# MSC-001 Model Schema Contract

Version: 1.0.0

Status: Draft — Specification only; model artifact generation not authorized

Document Type: Research model schema contract

Architecture Baseline: ABR-1.0 (Frozen)

## Purpose

Define the metadata structure and compatibility requirements for future research model records.

## Scope

The schema covers Model ID/version, training run, feature and label schema versions, input columns, output classes, preprocessing identity, evaluation references, status, and provenance. It does not define an algorithm or implementation.

## Ownership

The Research Owner proposes the schema. Technical Review verifies compatibility with Training and Evaluation contracts. The Project Owner approves the version.

## Inputs

Inputs are accepted TSC-001 dataset identity, FSC-001 feature schema, LSC-001 label schema, TEC-001 training run, ESC-001 evaluation records, and environment evidence.

## Outputs

An authorized model record may contain identity, schema versions, input contract, output contract, preprocessing identity, training and evaluation references, and lifecycle status.

## Invariants

A model record must resolve to one immutable training run and declared evaluation population. Feature and label identities remain distinct. Unknown preprocessing, classes, or input columns are invalid.

## Validation Rules

Reject missing identities, duplicate model keys, incompatible feature/label schemas, undeclared inputs or outputs, non-finite metadata, missing evaluation linkage, and manifest mismatch.

## Versioning

Changes to fields, types, input/output semantics, preprocessing, or serialization require a new schema version. Existing model records are immutable.

## Acceptance Criteria

Acceptance requires schema validation, complete lineage, matching hashes, approved evaluation evidence, independent backup, and Project Owner approval.

## References

MRC-001, TEC-001, TSC-001, TMS-001, EFC-001, ESC-001, EVC-001, EMS-001, RFB-001, RDR-001, ELC-001, and DAC-001.
