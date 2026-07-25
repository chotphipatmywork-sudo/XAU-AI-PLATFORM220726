# IMP-092 Current-Feed Causal M5 Lifecycle Replay

Version: 1.0.0

Date: 2026-07-24

Status: Completed; no lifecycle candidate passed

Architecture Baseline: ABR-1.0

Related: IMP-084, IMP-091

## Purpose and frozen scope

IMP-091 found that 100 stopped descriptive paths first reached at least
`+0.5R`, but M15 cannot establish intrabar ordering. IMP-092 collects causal
M5 paths only for current-feed plans that retain valid cost-aware geometry,
the frozen `>=2.0R` minimum, an unambiguous M15 Target/Stop baseline, and an
outcome known before `2024-07-01 00:00`.

## Preregistered candidates

1. `CURRENT_BASELINE`;
2. `COST_COVERED_BREAKEVEN_AFTER_CLOSE_1R`;
3. `TWO_STAGE_RATCHET_AFTER_CLOSE_1R_2R`.

Management activates only after a completed M5 close and is effective from the
next M5 bar. Cost multipliers are `1.0`, `1.25`, and `1.5`. The fixed gate
requires at least 200 effective paths, positive mean and moving-block CI lower
bound, four positive chronological blocks, both directions positive, profit
factor at least 1.10, maximum drawdown no more than 25R, longest loss sequence
no more than 10, and all cost-stress intervals positive.

## Protected boundaries

- Requests contain only the frozen Train window.
- Baseline parity is mandatory and M5 collisions are quarantined.
- Minimum RR, Entry, initial Stop, and Target are unchanged.
- No Validation/Test, Runtime, Risk, order action, or Deployment is permitted.
- Status remains `NO_GO`.

## Validation

Focused Python tests verify request accounting and the `2.0R` lock. The focused
MQL5 EA verifies lifecycle window and geometry contracts. MetaEditor must
report exactly `0 errors, 0 warnings` before collection.

The builder produced 31 requests from 597 source contexts. Twenty-three
contexts lacked known cost evidence and 543 were invalid or below the frozen
cost-aware `2.0R` minimum. All 31 retained paths have unambiguous M15 baseline
outcomes known before the Train cutoff.

- request SHA-256:
  `45C22ECF20D4D159AFCA4072379931761193C063238EAE01D5CE5EECB1C4EDD2`;
- exporter SHA-256:
  `441749ADF7722155B59E25B17A672A9D31505CD202FC763FDC4D5D4AA956B0DD`;
- focused EA SHA-256:
  `59DC9A28B6846B85BA4DE76542F1C614F4D9E409D81223BE381F34F1F123A5CA`;
- compile-log SHA-256:
  `0F8A8C980CB64F339CF502DA4211B43445A8D156FB2C0946FEE929ED206D976C`.

Three relevant regressions and Python syntax validation passed. MetaEditor
reported exactly `0 errors, 0 warnings`; the request was copied to MT5 Files
with verified hash.

## M5 collection and Train-only result

The owner exported all 31 requests as 420 causal M5 rows. Exact request,
numeric, window, sequence, safety, and Baseline outcome parity passed.

- M5 path export SHA-256:
  `A0544BD903A2E2F9B5330E9D6865D3E756396061FEFFFBC12280E84EB0276125`.

At base cost:

| Candidate | Mean R | Profit factor | Max drawdown | CI95 lower |
|---|---:|---:|---:|---:|
| Current Baseline | -0.261 | 0.663 | 14.36R | -0.669 |
| Cost-covered Breakeven | -0.132 | 0.772 | 10.36R | -0.528 |
| Two-stage Ratchet | -0.087 | 0.850 | 8.95R | -0.495 |

Both management candidates reduce average loss and drawdown, but neither has
positive expectancy, positive CI lower bound, sufficient sample, temporal
stability, both-direction robustness, profit factor, or cost-stress evidence.
Each remains positive in only one of four chronological blocks and one of two
directions. No candidate passed and Validation remains sealed.

No Runtime Change Request is authorized. The accepted IMP-089 scorecard
remains unchanged at Research `100.00`, Strategy `19.82`, Operational
`100.00`, Overall Readiness `49.00`, status `NO_GO_TRAIN`.

Replay report SHA-256:
`16F2A80834CDE543EF6B332FB0A78E7121012502DF0A595A268F43F6F6F43963`.
Three relevant regressions and Python syntax validation passed.
