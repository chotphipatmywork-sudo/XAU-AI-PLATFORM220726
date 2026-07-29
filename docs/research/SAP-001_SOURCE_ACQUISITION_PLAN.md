# SAP-001 Source Acquisition Plan

Version: 1.0.0

Status: Draft — Approval required; acquisition not authorized

Architecture Baseline: ABR-1.0 (Frozen)

## Purpose

This plan defines the controlled workflow for acquiring a future source for the `CONTROLLED_RESEARCH_REGENERATION` track. It is a plan, not an authorization or execution record.

## Approved Source Types

Only documented broker or provider exports, approved local archives, or another deterministic source expressly approved under SRC-001 may be used. The source type, provider, format, coverage, and access basis must be recorded before acquisition.

## Acquisition Workflow

1. Define the requested source identity and coverage.
2. Obtain source-approval authorization.
3. Acquire the exact source using the approved procedure.
4. Record command, operator, environment, timestamps, location, and exit status.
5. Preserve the unmodified acquisition output.
6. Run source validation and create the source registration record.
7. Obtain Project Owner source approval.
8. Freeze the approved source before downstream generation.

## Acquisition Validation

Validation must check format, schema, provider, symbol, timeframe, timezone, chronology, coverage, missing data, duplicates, record accounting, byte size, and exact-byte hash. Results and tool versions are stored as evidence. Validation or provenance failure rejects the acquisition.

## Source Registration

The registration record must include Source ID, source version, provider, location, acquisition method, configuration, schema version, symbol, timeframe, coverage, timezone, byte size where available, record count, hash after authorized validation, and immutable provenance references.

## Source ID Assignment

Source IDs are unique within the research track and assigned before downstream use. A changed provider, file, byte sequence, schema, coverage, configuration, or correction receives a new Source ID or explicitly approved new source version.

## Source Freeze

An approved source is frozen after acceptance. Its bytes, identity, provenance, validation report, and storage location cannot be overwritten. Corrections create a new source lineage and preserve the prior record.

## Source Approval Gate

The Project Owner may approve a source only after SRC-001 validation passes, provenance is complete, the source identity is unique, and an independent recovery path is documented. Approval does not authorize dataset generation unless a separate execution authorization exists.

## Prohibited Practices

- Silent source replacement is prohibited.
- Unregistered sources are prohibited.
- Partial provenance is prohibited.
- Inferred provider, timezone, symbol, or chronology values are prohibited.
- Historical source reuse without a new approval and identity is prohibited.

## References

- [RFB-001 Research Foundation Blueprint](RFB-001_RESEARCH_FOUNDATION_BLUEPRINT.md)
- [RDR-001 Research Track Decision Record](RDR-001_RESEARCH_TRACK_DECISION_RECORD.md)
- [SRC-001 Source Data Contract](SRC-001_SOURCE_DATA_CONTRACT.md)
- [MMS-001 Metadata Manifest Schema](MMS-001_METADATA_MANIFEST_SCHEMA.md)
- [DLC-001 Dataset Lifecycle Contract](DLC-001_DATASET_LIFECYCLE_CONTRACT.md)
- [DPC-001 Dataset Partition Contract](DPC-001_DATASET_PARTITION_CONTRACT.md)

## Final Status

SAP-001 is documentation only. Source acquisition, export, replay, dataset generation, training, and runtime changes remain unauthorized.
