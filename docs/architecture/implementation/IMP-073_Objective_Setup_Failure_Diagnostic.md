# IMP-073 Objective Setup Failure Diagnostic

Version: 1.0.0

Date: 2026-07-19

Status: Train-only diagnostic complete; one contract-change candidate found

Architecture Baseline: ABR-1.0

Related: CR-013, CR-014, ADR-006, IMP-068, IMP-070

## Purpose and boundary

This diagnostic identifies why Objective Setup V1 plans fail without changing
the Setup contract. It reads only the frozen 229-row Stage D Train partition
and the matching frozen Objective Setup Audit. SHA-256 checks prevent evidence
substitution. Validation, Test, the post-cutoff confirmation period, Runtime,
Risk, Execution, and deployment are not accessed or modified.

Predicates use only evidence known at the Setup observation:

- sweep penetration in ATR;
- reclaim distance in ATR;
- reclaim-to-sweep ratio and combined trigger excursion;
- estimated-cost burden;
- cost-adjusted plan RR and RR headroom.

Outcome, bars observed, MFE, MAE, and realized R are forbidden predicates.
They may only serve as diagnostic responses. Plan geometry remains outside the
canonical AI Feature Schema 4.0.

## Frozen evaluation gate

Eleven fixed questions were registered before running the geometry diagnostic.
The existing four expanding, outcome-known-time-purged Train folds were reused.
A finding requires at least three matches per fold, 20 aggregate matches, the
expected Target-rate and cost-aware expectancy lift signs in all four folds,
at least five percentage points aggregate Target-rate lift, and at least 0.10R
aggregate expectancy lift.

Cost-aware diagnostic return is `plan_rr` for Target-first, `-1R` for
Stop-first, and `0R` for Timeout. No model is fitted.

## Result

Only the preregistered `strong_reclaim` question passed every gate:

```text
reclaim_distance_atr >= 0.10
```

Across the 115 aggregate evaluation plans:

- baseline: 26.09% Target rate and -0.0326R expectancy;
- strong reclaim: 90 plans, 32.22% Target rate and +0.1977R expectancy;
- lift: +6.14 percentage points and +0.2303R;
- fold Target-rate lift: +9.52, +8.77, +4.37, +1.78 percentage points;
- fold expectancy lift: +0.331R, +0.329R, +0.176R, +0.069R.

The 25-plan complement below 0.10 ATR contained one Target-first outcome: 4.00%
Target rate and -0.8616R expectancy. This is evidence for reviewing a minimum
reclaim threshold, not permission to deploy it.

Deep sweep, marginal sweep, weak reclaim, reclaim/sweep ratios, combined
excursion, cost burden, and RR groups failed support or four-fold sign
stability. Their thresholds must not be promoted from this run.

## Limitation

The Setup Audit does not store Entry ATR directly. Therefore Stop and Target
distance cannot be normalized to volatility without guessing. IMP-073 refuses
to infer ATR from Stop geometry. Adding Entry ATR to the audit is a separate
contract/schema decision and is not authorized here.

## Files and validation

- `training/diagnose_objective_setup_failures.py`
- `training/test_objective_setup_failure_diagnostic.py`
- `tools/run_objective_setup_failure_diagnostic.ps1`
- output `research/objective_setup_failure/objective_setup_failure_diagnostic.json`

The next controlled action, if explicitly approved, is a synthetic contract
change requiring completed M5 reclaim distance of at least 0.10 ATR, followed
by regeneration and the same Train-only four-fold comparison. Runtime and
deployment remain unchanged until that later evidence passes.
