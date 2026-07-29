# FVC-001 Feature Validation Contract

Version: 1.0.0

Status: Draft — Approval required; validation does not authorize training

Document Type: Research feature validation contract

Architecture Baseline: ABR-1.0 (Frozen)

## Purpose

Define fail-closed validation for feature datasets and their manifests.

## Required Checks

Validation rejects missing identity columns, duplicate `record_id`, missing feature columns, non-numeric or non-finite values, invalid timestamps, non-deterministic feature ordering, manifest field mismatch, source hash mismatch, and feature hash mismatch.

## Acceptance Criteria

All required checks pass, identity and record count are preserved, feature names exactly match FSC-001, `labels_generated` is `false`, and manifest hashes match exact serialized bytes.

## Ownership and Versioning

The offline validator owns checks and emits a deterministic report. Validator changes require a version increment and review. Validation/Test contents remain sealed.

## References

FSC-001, FEC-001, FMC-001, RFB-001, RDR-001, SRC-001, MMS-001, DLC-001, DPC-001, ELC-001, DAC-001, SAP-001, and RDS-001.
