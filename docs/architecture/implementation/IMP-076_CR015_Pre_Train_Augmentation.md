# IMP-076 CR-015 Pre-Train Augmentation

Version: 1.0.0

Date: 2026-07-22

Status: Implemented offline; Train-only research NO-GO

Architecture Baseline: ABR-1.0

Related: CR-015, IMP-070, IMP-074, IMP-075

## Purpose

Safely prepend quality-controlled Objective Setup outcomes from a strictly
earlier real-tick interval to the frozen Train partition. This change exists
only in the offline research layer and does not alter Runtime, Risk, Execution,
the Feature Schema, the Setup contract, or any broker-facing behavior.

## Fail-closed controls

- source outcomes must use Setup Outcome Schema 1.0.0 and Feature Schema 4.0.0;
- the archived-log quality audit must pass with no uncovered warning date, and
  the Dataset build summary must name the same versioned exclusion file;
- every row must be mature, trainable, unique, and strictly chronological;
- the last pre-Train outcome must be known before the first frozen Train row;
- frozen Train, Validation, and Test SHA-256 values must match CR-015 before
  augmentation and remain unchanged afterward;
- Validation and Test are hashed as opaque files and are never parsed;
- readiness remains fixed at 200 Train, 40 Target, and 40 non-Target records;
- output remains research-only with training and deployment unauthorized.

## Files and validation

- `training/augment_pretrain_history.py`
- `training/test_pretrain_history_augmentation.py`
- `training/audit_real_tick_quality.py`
- `training/test_real_tick_quality_audit.py`
- `training/config/cr015_real_tick_quality_exclusions_202001_202106.json`

The focused tests cover successful chronological augmentation, sealed
Validation hash drift, overlap refusal, daily `no real ticks` parsing, daily
price-mismatch parsing, and aggregate-range exclusion. No MQL5 source changed,
so MetaEditor compilation is not applicable; the existing 0-error, 0-warning
Runtime compile remains valid.

## Recorded result

The archived real-tick log exposed 52 daily anomaly dates and the versioned
exclusion file covered all 52. Dataset construction retained 51 of 60
structural plans after excluding nine affected paths. Augmentation produced 233
Train rows (59 Target, 174 non-Target), passed the fixed readiness gate, and
preserved the frozen partition hashes exactly.

Train-only descriptive comparison showed nearly unchanged Target rate
(25.27% to 25.32%) and a weaker mean cost-aware return (-0.0641R to -0.0780R).
The additional history passes the sample gate but does not improve expected
strategy quality.

The existing four-fold purged ranker then evaluated Train only. Balanced
logistic regression was selected with 41.18% Target precision, 60.00% Target
recall, and 59.55% Macro F1 in aggregate, but only one fold passed. The stable
gate therefore failed, no model file was emitted, and research remains NO-GO.
The complete offline Python regression passed 44/44 after the change.

## Safety state

The augmented file may be used only by the existing Train-only purged
walk-forward ranker after readiness passes. It cannot authorize Validation/Test
access, Forward Shadow, model deployment, broker orders, or live execution.
