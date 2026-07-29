# DPC-001 Dataset Partition Contract

Version: 1.0.0

Status: Draft — Approval required; partition generation not authorized

Architecture Baseline: ABR-1.0 (Frozen)

## Purpose

This contract defines chronological Train, Validation, and Test partition requirements for the `CONTROLLED_RESEARCH_REGENERATION` track. It preserves the existing rule that Validation and Test remain sealed unless separately authorized.

## Partition Definitions

### Train

Train is the earliest approved time interval. It may support feature fitting, label development, and model development only under the approved experiment contract.

### Validation

Validation is a later, disjoint interval. It remains sealed by default and may be opened only by a separate approval. It must not be used for unapproved feature fitting or exploratory inspection.

### Test

Test is the final untouched interval. It remains sealed until final authorized evaluation and must not be used for model selection, feature fitting, label inspection, or exploratory analysis.

## Time-Based Partitioning

Each partition has an explicit start time and end-exclusive cutoff in one declared timezone. Partition intervals must be chronological, non-overlapping, and reproducible from the approved source snapshot.

## Leakage Prevention

The partition process must prevent future information from crossing boundaries. Label horizons require the approved purge or embargo interval before the next partition. Features may use only data available at the feature timestamp. Any leakage finding fails validation.

## End-Exclusive Boundaries

An end-exclusive boundary means records at the cutoff belong to the following interval, not the preceding one. Boundary rules, precision, timezone, and purge duration must be recorded in the manifest and applied identically on regeneration.

## Snapshot Freeze

Partition inputs are identified by Data Snapshot ID and source hash. After freeze, partition bytes, membership, boundaries, and metadata are immutable. Corrections require a new snapshot and dataset version.

## Partition Identity

Each partition receives a unique identity linked to Research Track ID, Dataset ID, Dataset Version, Partition Name, and Data Snapshot ID. The identity must be present in the manifest and validation report.

## Partition Version

Partition Version changes when boundaries, purge rules, schema, source snapshot, ordering, or membership semantics change. Existing versions are retained and never overwritten.

## Partition Hash

Each partition must have an exact-byte SHA-256 after authorized generation and deterministic serialization. The manifest records the hash, byte size where available, record count, and serialization contract.

## Access Policy

Train access is limited to approved research operations. Validation and Test access is denied by default, logged when authorized, and limited to the stated purpose. Unauthorized access is a validation failure and may require rejection of the run.

## Validation/Test Protection

Validation and Test contents remain sealed during foundation work and source approval. Hash-only verification is permitted where already authorized; content inspection, model selection, or feature fitting requires separate approval.

## Acceptance Rules

A partition set is acceptable only when:

- All three partition identities and versions are present.
- Boundaries are chronological, end-exclusive, and non-overlapping.
- Purge or embargo rules prevent label leakage.
- Record counts, hashes, byte sizes, and serialization details are recorded.
- Snapshot and partition bytes are frozen after acceptance.
- Validation/Test access status is evidenced.
- Project Owner acceptance is recorded.

## References

- [RFB-001 Research Foundation Blueprint](RFB-001_RESEARCH_FOUNDATION_BLUEPRINT.md)
- [RDR-001 Research Track Decision Record](RDR-001_RESEARCH_TRACK_DECISION_RECORD.md)
- [SRC-001 Source Data Contract](SRC-001_SOURCE_DATA_CONTRACT.md)

## Final Status

DPC-001 is documentation only. No partition is generated, opened, accepted, or frozen by this contract.
