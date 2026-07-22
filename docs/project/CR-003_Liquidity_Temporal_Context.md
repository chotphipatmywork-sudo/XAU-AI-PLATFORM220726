# CR-003 Proposed Liquidity Temporal Context

Version: 0.1.0

Date: 2026-07-16

Status: Research evaluated and rejected; no Feature Contract change

Architecture Baseline: ABR-1.0

Related Phase: Post-Phase-7 Model Improvement Research

## Problem

Feature Schema 4.0 and the expanded 18,788-record Train partition failed the complete nested deployment gate. Trend-derived interactions, Trend dynamics, H1 context, history weighting, calibration, and confidence thresholds did not produce stable temporal generalization.

The current Liquidity group contains the present activity, range position, and sweep direction, but it does not represent how recently a sweep occurred or whether recent sweeps are directionally imbalanced. A single current snapshot can lose event persistence that may matter across the approved 16-bar label horizon.

## Proposed research boundary

Derive eight bounded research-only values from the current and earlier canonical Liquidity rows:

1. Liquidity activity change over 1 bar
2. Liquidity activity change over 4 bars
3. Liquidity range-position change over 1 bar
4. Liquidity range-position change over 4 bars
5. Mean sweep direction over 4 bars
6. Mean sweep direction over 16 bars
7. Buy-side sweep freshness over 16 bars
8. Sell-side sweep freshness over 16 bars

The candidates use only Feature Schema 4.0 Train rows. They do not read future rows, Validation, Test, labels during feature construction, or any execution result.

## Bounded experiment

The controlled comparison is fixed before results are inspected:

- Baseline
- Liquidity changes only
- Sweep memory only
- All Liquidity temporal values

The model is raw `random_forest_depth_5_balanced`, the policy is argmax, evaluation uses four purged Train-only folds, and every boundary purges 16 records.

Only one candidate may advance to nested confirmation. Promotion requires all of:

- it ranks above Baseline by the registered weakest-gate selection rule;
- gate-floor ratio improves by at least `0.01`;
- aggregate Macro F1 does not decrease;
- at least one complete controlled fold passes.

If no candidate meets every condition, CR-003 is rejected without nested search.

## Required nested evidence

If a candidate is promoted, three Inner folds must select Baseline or the promoted candidate before each of four unseen Outer periods. A canonical Feature Contract proposal requires:

- the candidate is selected before all four Outer periods;
- all four Outer periods pass the complete evaluation contract;
- aggregate Outer metrics pass every threshold;
- Validation and Test remain unread.

Anything less rejects the schema proposal.

## Architecture impact

Research has no Runtime impact. A later canonical implementation would remain within the Liquidity group but would change the public Feature Contract, Dataset schema, historical replay output, and live Brain projection. That implementation requires a separate explicit approval after the research gate passes.

Decision, Risk, Execution, and Trade Lifecycle remain unchanged.

## Risks

- Derived memory may repeat information already learnable from snapshots.
- Broker history gaps mean record lookbacks are observations rather than exact wall-clock intervals.
- Multiple temporal values can increase overfitting.
- Inspected Train periods cannot serve as final deployment evidence.

## Rollback

Delete the research scripts, tests, reports, and this proposal. Feature Schema 4.0 and all MQL5 Runtime code remain unchanged.

## Approval record

- Research-only bounded experiment: approved by project owner on 2026-07-16
- Canonical Feature Contract change: not approved
- MQL5 implementation: not approved
- Deployment: not approved

## Research result

The focused leakage and promotion-boundary test passed. The controlled experiment then evaluated 9,394 purged Train-only forward records without reading Validation or Test.

| Feature set | Macro F1 | SELL precision | BUY precision | Passing folds |
| --- | ---: | ---: | ---: | ---: |
| Baseline | 0.3948 | 0.4618 | 0.4938 | 0 |
| Sweep memory | 0.3926 | 0.4579 | 0.4944 | 0 |
| Liquidity changes | 0.3906 | 0.4587 | 0.4921 | 0 |
| All Liquidity temporal | 0.3895 | 0.4566 | 0.4973 | 0 |

Baseline ranked first. Every temporal candidate reduced the gate-floor ratio and Macro F1, and no candidate passed a complete controlled fold.

The predeclared promotion boundary therefore returned:

- `promoted_feature_set=null`
- `nested_confirmation_authorized=false`

## Decision

Reject CR-003 as a canonical Feature Contract change. Do not run nested selection, do not add Liquidity temporal fields to MQL5, and do not regenerate the Dataset. The report remains reproducibility evidence only.
