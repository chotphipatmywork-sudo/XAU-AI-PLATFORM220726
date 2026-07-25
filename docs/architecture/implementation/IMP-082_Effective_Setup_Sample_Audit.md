# IMP-082 Effective Setup Sample Audit

Version: 1.0.0

Date: 2026-07-22

Status: Implemented; G1 passed; Train remains NO-GO

Architecture Baseline: ABR-1.0

Related: RSCS-1.0, CR-013, IMP-076, IMP-080, IMP-081

## Purpose

Measure whether the frozen 233-record Setup Outcome Train baseline contains
duplicate or overlapping outcome windows that inflate its apparent sample
size. This closes RSCS-1.0 Effective Sample uncertainty before any further
Entry/Stop hypothesis is evaluated.

## Frozen audit contract

- source: `XAU_AI_SETUP_OUTCOME_AUGMENTED_TRAIN.csv`;
- source SHA-256:
  `F31E6DED4E0AC3B20FDD7964D3E634902736C8AD3316AA15A4E63D5C3C7E9A7E`;
- interval: half-open `[observation_time,outcome_known_at)`;
- selection: earliest-finish greedy interval scheduling, which returns the
  maximum-cardinality non-overlapping interval set;
- boundary equality is non-overlapping because the earlier outcome is known
  when the next observation begins;
- duplicate/non-chronological observations, schema drift, non-mature outcomes,
  and source hash drift fail closed;
- Validation and Test paths are not accepted by the tool.

This is a conservative independence count for overlapping Setup labels. It is
not a claim that every retained observation is statistically independent of
market regime autocorrelation; that question remains covered by temporal and
direction gates.

## Implementation

- `training/audit_effective_setup_sample.py` implements the strict audit and
  emits a versioned evidence report;
- `training/test_effective_setup_sample_audit.py` covers optimal interval
  selection, half-open boundaries, overlap diagnostics, source-hash drift,
  duplicate observations, and protected-state locks;
- `tools/audit_effective_setup_sample.ps1` provides a path-with-spaces-safe
  command using the Workspace virtual environment;
- `training/config/research_scorecard_imp082_effective_sample.json` records the
  audited Baseline and immutable evidence hashes.

## Result

| Measure | Result |
| --- | ---: |
| raw mature records | 233 |
| maximum non-overlapping records | 232 |
| overlap discount | 1 |
| retention | 99.57% |
| duplicate observation times | 0 |
| overlapping clusters | 1 |
| maximum concurrent intervals | 2 |
| G1 minimum effective sample | **passed (232/200)** |

The one discounted record is a `STOP_FIRST` observation at
`2020.05.27 18:45`; its outcome window overlaps the selected observation at
`2020.05.27 18:30`. No strategy rule was changed.

## RSCS-1.0 delta from IMP-080

| Score | IMP-080 | IMP-082 | Delta |
| --- | ---: | ---: | ---: |
| Research Quality | 90.00 | 100.00 | +10.00 |
| Strategy Evidence | 12.50 | 20.00 | +7.50 |
| Operational Safety | 100.00 | 100.00 | 0.00 |
| Raw Overall | 53.25 | 60.00 | +6.75 |
| Hard-Gated Overall | 49.00 | 49.00 | 0.00 |

G1 now passes. G2-G8 remain false and status remains `NO_GO_TRAIN` because the
current 233-record replay mean is still `-0.078R`, chronological/direction
stability is absent, cost/drawdown gates are open, and the ranker passed only
one of four folds.

## Safety and validation

The focused audit test passed and the complete Python regression passed
`49/49`. The PowerShell wrapper parsed and executed successfully from the
space-containing Workspace path. The report SHA-256 is
`2646BBD8E881B6BB7F8621E27D1933BE1376711C75558E046B9EA964A1393414`; the
resulting Scorecard SHA-256 is
`BC60A485312EC662FE49D494FFDD76C686B6CEAEED2B2FAD9F37CC2AB75E6468`.

No MQL5, Runtime, Risk, Execution, Feature Schema, or Label Schema file changed.
The last verified Runtime compile therefore remains `0 errors, 0 warnings`.
Training, Validation, Test, Forward, Live Execution, and Deployment remain
unauthorized.

## Next phase

Use only the audited Train evidence to measure Entry/Stop MFE/MAE opportunity,
effective-sample expectancy, a 95% confidence interval, normalized drawdown,
and loss-tail behavior before pre-registering another strategy Candidate.
