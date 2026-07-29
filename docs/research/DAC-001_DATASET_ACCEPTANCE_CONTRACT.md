# DAC-001 Dataset Acceptance Contract

Version: 1.0.0

Status: Draft — Approval required; acceptance not authorized

Architecture Baseline: ABR-1.0 (Frozen)

## Purpose

This contract defines the acceptance gate for a future dataset in the `CONTROLLED_RESEARCH_REGENERATION` track.

## Mandatory Acceptance Conditions

Acceptance requires all of the following:

- Source Approval is recorded for the exact Source ID and version.
- Dataset Validation status is `PASS`.
- The MMS-001 manifest is complete.
- Source, transformation, feature, label, and partition provenance is complete.
- Partition Validation status is `PASS`.
- Independent backup is verified at a separate approved destination.
- Project Owner approval is recorded.

## Acceptance Workflow

1. Confirm source approval and identity.
2. Confirm dataset and partition validation reports pass.
3. Check manifest completeness and exact hashes.
4. Verify provenance and reproducibility evidence.
5. Verify independent backup and retrieval evidence.
6. Obtain Project Owner acceptance.
7. Record acceptance state and freeze the accepted bytes.

## Rejection Workflow

Any failed mandatory condition moves the dataset to `REJECTED`. The rejection record preserves failed checks, inputs, hashes, and reports. Remediation requires a new dataset version and a new validation and approval cycle; accepted bytes are never overwritten.

## Freeze Rules

After acceptance, the dataset, partitions, manifest, validation reports, and provenance records are frozen together. The immutable-storage location and freeze timestamp must be recorded.

## Immutable Rules

Frozen and accepted objects cannot be edited, replaced, or silently reserialized. Corrections create new identities and versions linked to the superseded object. The internal `backups` directory is not an independent backup without separate approval and verification.

## References

- [RFB-001 Research Foundation Blueprint](RFB-001_RESEARCH_FOUNDATION_BLUEPRINT.md)
- [RDR-001 Research Track Decision Record](RDR-001_RESEARCH_TRACK_DECISION_RECORD.md)
- [SRC-001 Source Data Contract](SRC-001_SOURCE_DATA_CONTRACT.md)
- [MMS-001 Metadata Manifest Schema](MMS-001_METADATA_MANIFEST_SCHEMA.md)
- [DLC-001 Dataset Lifecycle Contract](DLC-001_DATASET_LIFECYCLE_CONTRACT.md)
- [DPC-001 Dataset Partition Contract](DPC-001_DATASET_PARTITION_CONTRACT.md)

## Final Status

DAC-001 is documentation only. No dataset is accepted, frozen, or made Train-eligible by this document.
