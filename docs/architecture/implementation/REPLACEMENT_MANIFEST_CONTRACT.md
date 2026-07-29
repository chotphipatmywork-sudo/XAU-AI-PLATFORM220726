# Replacement Artifact Manifest Contract

Version: 1.0.0

Status: Approved contract; execution not authorized

Document Type: Research Artifact Manifest Contract

Architecture Baseline: ABR-1.0 (Frozen)

## Required Fields

`replacement_id`, `artifact_name`, `artifact_schema_version`, `artifact_path`, `artifact_size_bytes`, `artifact_sha256`, `source_manifest_sha256`, `generation_commit`, `generation_timestamp_utc`, `source_schema_versions`, `train_only`, `validation_dataset_used`, `test_dataset_used`, `runtime_changed`, `deployment_authorized`, `validation_status`, and `review_status`.

## Rules

Hashes cover exact bytes. `train_only` must be true; Validation/Test use, Runtime change, and deployment authorization must be false. Manifest failure blocks acceptance.
