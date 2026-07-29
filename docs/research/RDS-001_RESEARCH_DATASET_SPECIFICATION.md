# RDS-001 Research Dataset Specification

Version: 1.0.0

Status: Draft — Approval required; dataset generation not authorized

Architecture Baseline: ABR-1.0 (Frozen)

## Dataset Purpose

This specification defines the canonical structure and serialization expectations for every dataset created under the `CONTROLLED_RESEARCH_REGENERATION` track. It does not alter historical IMP-099, IMP-100, or IMP-101C contracts.

## Dataset Identity

Each dataset must carry a unique Research Track ID, Dataset ID, Dataset Version, Schema Version, Data Snapshot ID, partition identity, and Manifest ID. Identity values must be assigned before acceptance and must not be reused across different bytes, sources, schemas, or transformation rules.

## Source Mapping

Every record set must map to exactly one approved Source ID and source version. The manifest must link the dataset to source location, provider, acquisition configuration, source schema, source hash, and transformation provenance as required by SRC-001 and MMS-001.

## Symbol Rules

Each record must use the approved normalized research symbol. The source symbol, provider symbol, and normalized symbol mapping must be recorded. Undocumented aliases, suffixes, contract specifications, or symbol substitutions invalidate the dataset.

## Timeframe Rules

The dataset timeframe must be explicitly declared and must match the approved research contract. Any aggregation or resampling must record source timeframe, target timeframe, boundary convention, and deterministic transformation version.

## Timestamp Rules

Each record must have a timestamp with declared precision and deterministic serialization. Timestamps must be chronologically interpretable, unique where the schema requires uniqueness, and aligned to the declared bar or event boundary. End-exclusive partition cutoffs are governed by DPC-001.

## Timezone Rules

The source timezone, normalized research timezone, and conversion rule must be recorded. Timestamp conversion must preserve the instant and use a declared daylight-saving policy. Unknown or conflicting timezone metadata fails closed.

## Record Identity

Every record must have a deterministic Record ID or a deterministic composite identity defined by the schema. Record identity must remain stable across validation and regeneration when inputs and contracts are unchanged. Duplicate identities are validation failures unless an approved source contract explicitly defines a distinct event sequence.

## Required Columns

The approved dataset schema must define, at minimum, Record ID, normalized symbol, timestamp, partition identity, source reference, and the declared research fields required by the applicable feature and label contracts. Column names, data types, units, nullability, and serialization order must be versioned; this document does not invent concrete feature or label fields.

## Optional Columns

Optional columns may contain non-authoritative diagnostics or provider metadata only when declared in the schema version and manifest. Optional columns must not replace required provenance, alter record identity, or change feature and label semantics without a new schema version.

## Feature Placeholder Rules

Feature placeholders are permitted only when the schema explicitly marks them as nullable, not computed, and not usable for training or evaluation. A placeholder must have a documented missing reason. Silent default values, zero-filling, or inferred features are prohibited.

## Label Placeholder Rules

Label placeholders are permitted only when the applicable label contract declares the field not applicable or unavailable for the research stage. Missing labels must carry an approved missing reason and must never be imputed silently. Historical label semantics remain unchanged.

## Missing Value Rules

Missing values must be represented using the schema’s declared null representation and accompanied by an approved reason when required. Missing source fields, timestamps, identities, or required research fields fail validation. No missing value may be silently discarded or inferred.

## Duplicate Rules

Duplicate Record IDs, duplicate identity composites, and prohibited duplicate timestamps must be detected and reported. Deduplication is allowed only under an approved deterministic source or transformation rule; otherwise the dataset is rejected.

## Ordering Rules

Records must use deterministic ordering defined by the schema, normally partition order followed by timestamp and Record ID as a tie-breaker. Column order, encoding, newline convention, decimal precision, timestamp format, and null representation must be fixed in the manifest and preserved for hashing.

## Partition Compatibility

The dataset must comply with DPC-001: Train, Validation, and Test are distinct, chronological, non-overlapping, end-exclusive, and identified by immutable partition versions. Purge or embargo requirements must prevent future-label leakage. Validation and Test remain sealed unless separately authorized.

## Manifest Compatibility

Every dataset must produce an MMS-001-compatible manifest containing identity, source, transformation, feature, label, partition, validation, acceptance, storage, and reproducibility evidence. The manifest references this dataset Schema Version and the exact serialized output hash.

## Validation Requirements

Validation must check schema, required and optional columns, types, units, nullability, record identity, symbol, timeframe, timestamp chronology, timezone, duplicates, ordering, partition boundaries, leakage controls, manifest completeness, and exact-byte serialization. Failed mandatory checks block lifecycle progression.

## Freeze Requirements

After DAC-001 acceptance, dataset bytes, partitions, manifest, validation reports, and provenance records are frozen together in approved immutable storage. Corrections or schema changes create a new Dataset ID or version and preserve the prior evidence.

## Acceptance Requirements

Acceptance requires approved source mapping, complete manifest and provenance, passing dataset and partition validation, verified independent backup, deterministic serialization, and Project Owner approval under DAC-001. Acceptance does not grant training, replay, or execution authorization.

## References

- [RFB-001 Research Foundation Blueprint](RFB-001_RESEARCH_FOUNDATION_BLUEPRINT.md)
- [RDR-001 Research Track Decision Record](RDR-001_RESEARCH_TRACK_DECISION_RECORD.md)
- [SRC-001 Source Data Contract](SRC-001_SOURCE_DATA_CONTRACT.md)
- [MMS-001 Metadata Manifest Schema](MMS-001_METADATA_MANIFEST_SCHEMA.md)
- [DLC-001 Dataset Lifecycle Contract](DLC-001_DATASET_LIFECYCLE_CONTRACT.md)
- [DPC-001 Dataset Partition Contract](DPC-001_DATASET_PARTITION_CONTRACT.md)
- [DAC-001 Dataset Acceptance Contract](DAC-001_DATASET_ACCEPTANCE_CONTRACT.md)

## Final Status

RDS-001 is documentation only. No dataset is generated, accepted, frozen, or made Train-eligible by this specification.
