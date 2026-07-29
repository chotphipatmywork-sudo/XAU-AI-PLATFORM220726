# FEC-001 Feature Engineering Contract

Version: 1.0.0

Status: Draft — Approval required; generation not authorized

Document Type: Research feature engineering contract

Architecture Baseline: ABR-1.0 (Frozen)

## Purpose

Define the deterministic transformation from canonical CSV records to feature records.

## Ownership and Boundaries

The offline research pipeline owns extraction. It has no Runtime, Brain, Risk, Execution, Learning-runtime, model-training, or replay dependency.

## Formulas

`return_1 = close[t] / close[t-1] - 1`; `return_3 = close[t] / close[t-3] - 1`; `candle_range = high[t] - low[t]`; `candle_body = close[t] - open[t]`; `upper_wick = high[t] - max(open[t], close[t])`; `lower_wick = min(open[t], close[t]) - low[t]`; `body_ratio = candle_body / candle_range`; `range_ratio = candle_range / close[t]`; `rolling_mean` and `rolling_std` are trailing statistics over the current and preceding closes using the configured window.

Insufficient history produces null warm-up values, never future-derived values. Zero denominators produce null and a validation-visible missing reason.

## Prohibited Behavior

Look-ahead access, label generation, imputation, random transforms, nondeterministic ordering, and silent schema changes are prohibited.

## References

FSC-001, RFB-001, RDR-001, SRC-001, MMS-001, DLC-001, DPC-001, ELC-001, DAC-001, SAP-001, and RDS-001.
