# FMC-001 Feature Manifest Contract

Version: 1.0.0

Status: Draft — Approval required; acceptance not authorized

Document Type: Research feature manifest contract

Architecture Baseline: ABR-1.0 (Frozen)

## Purpose

Define the manifest emitted with every feature dataset.

## Required Fields

The manifest contains `manifest_version`, `feature_schema_version`, `source_dataset_identity`, `source_dataset_sha256`, `feature_dataset_sha256`, `feature_names`, `feature_count`, `record_count`, `labels_generated` set to `false`, and `generated_at_utc`. It also records deterministic serialization and generator provenance.

## Integrity

Hashes are exact-byte SHA-256 values calculated after authorized generation. Feature names and count must match FSC-001 exactly. A manifest mismatch fails closed.

## Versioning

Any field semantic or serialization change requires a new manifest version. Existing manifests are immutable.

## References

FSC-001, RFB-001, RDR-001, SRC-001, MMS-001, DLC-001, DPC-001, ELC-001, DAC-001, SAP-001, and RDS-001.
