# IMP-061 Canonical Shadow Inference Evidence

Version: 1.0.0

Status: Implemented; local and focused MT5 validation passed

Related: CR-009, CR-008, ADR-005, Feature Schema 4.0

## Purpose

Make every canonical Shadow Decision reproducible against the approved
twelve-dimensional Feature Schema 4.0 and establish a controlled provider
boundary for later model integration without changing current trading
behavior or authorization.

## Implementation

`CRuntimeManager` now projects each valid closed-bar Brain analysis through
`CBrainFeatureAdapter`. The resulting twelve features and four legacy
compatibility scores form `CAIInferenceRequest`.

`IAIInferenceProvider` defines initialization, evaluation, shutdown, provider
identity, and model-authorization behavior. The active implementation,
`CDevelopmentHeuristicInferenceProvider`, delegates only the four
compatibility scores to the existing `CAIManager`. It rejects invalid Schema
4.0 ranges, identifies itself as
`DEVELOPMENT_HEURISTIC_4_SCALAR_NO_GO`, and always reports model deployment as
unauthorized.

The Decision audit now records:

- Feature Schema version and provider identity;
- model deployment lock;
- all twelve Feature Schema 4.0 values;
- the four compatibility scores;
- the existing bar, AI Decision, Risk, and Shadow Execution evidence.

Versioned filenames prevent rows with different headers from being mixed:

- `XAU_AI_SHADOW_DECISIONS_V4.csv`
- `XAU_AI_SHADOW_BACKTEST_DECISIONS_V4.csv`

## Behavior compatibility

The provider calls the same `CAIManager.Evaluate()` method with the same four
values previously supplied by `CRuntimeManager`. Decision, Risk, Shadow
Execution, lifecycle, freshness, and safety behavior are unchanged.

## Focused validation

`tests/TestShadowInferenceProvider.mq5` checks:

- all twelve request fields satisfy Schema 4.0 ranges;
- provider output matches direct legacy-manager output;
- provider identity is the locked development heuristic;
- model deployment authorization remains false.

## Known limitation

The new provider boundary does not contain an approved trained model. The
compatibility provider may remain directionally weak and is explicitly
`NO_GO`. Schema 4.0 Shadow evidence must be collected and diagnosed before a
separate model-selection and deployment proposal.

## Local validation evidence

On 2026-07-17:

- the canonical include-closure audit covered 104 files;
- broker-capable files in the closure: 0;
- broker-mutation tokens in the closure: 0;
- Forward, matured-label, and Strategy Tester artifact tests passed with the
  V4 Decision schema;
- the complete Python regression passed 32/32 tests;
- the Shadow sync and compile PowerShell scripts parsed successfully.

The managed Codex filesystem cannot write to the MT5 project directory or
launch MetaEditor. The synchronized focused test and canonical EA therefore
still require the operator's exact MetaEditor result of 0 errors and 0
warnings.

## Focused MT5 runtime evidence

On 2026-07-17 12:32:36, `TestShadowInferenceProvider` ran on XAUUSD M15 and
confirmed:

- Feature Schema 4.0 request valid: true
- legacy heuristic behavior parity valid: true
- provider identity valid: true
- model deployment lock valid: true
- complete inference-provider contract valid: true
- focused EA removed itself normally

This accepts the component-level CR-009 provider boundary. A canonical EA
Strategy Tester smoke run is still required to verify the V4 Decision file
through the complete Brain, Decision, Risk, and Shadow Execution pipeline.

## Accepted canonical V4 smoke evidence

The canonical XAUUSD M15 real-tick smoke run completed on 2026-07-17 12:39:54
for the 2026-07-13 test period.

- Decisions: 91; duplicate closed bars: 0
- Risk rejections / synthetic executions: 68 / 23
- closed winning / losing / breakeven trades: 9 / 14 / 0
- cumulative / maximum drawdown points: 2415 / 1513
- Decision distribution: WAIT 36, SELL 55, BUY 0
- broker state unchanged and internal safety valid: true / true
- report, Decision, Audit counts and realized points agreed: true
- Decision bars within the configured test period: true
- Feature Schema / provider / deployment lock: `4.0.0` /
  `DEVELOPMENT_HEURISTIC_4_SCALAR_NO_GO` / false
- independent cross-file `backtest_evidence_valid`: true

All twelve V4 feature columns contained valid values in the 0–100 contract.
Every continuous feature varied during the run; categorical session and sweep
features showed their expected bounded states. The audit result is stored at
`outputs/shadow/cr009_smoke_backtest_analysis.json`.

This accepts CR-009 end-to-end evidence compatibility. It does not accept
model quality: the unchanged compatibility heuristic again produced no BUY
coverage, so the model remains `NO_GO` and both deployment locks remain false.

## Accepted full-period V4 evidence

The canonical XAUUSD M15 real-tick run completed on 2026-07-17 12:49:14 over
the available 2026-06-01 through 2026-06-29 broker history.

- Decision bars: 1,895 across 21 market days; duplicates: 0
- Decision distribution: SELL 1,128, WAIT 767, BUY 0
- Risk rejections / synthetic executions / closed trades: 1,877 / 18 / 18
- winning / losing / breakeven trades: 5 / 13 / 0
- profit factor / expectancy: 0.7680 / -83.9444 points per trade
- cumulative / maximum drawdown points: -1511 / 3008
- drawdown halt detected: true
- Report, Decision, and Audit evidence agreement: true
- Feature Schema 4.0/provider/deployment lock valid on all rows: true
- independent `backtest_evidence_valid`: true

The full audit is stored at
`outputs/shadow/cr009_full_period_backtest_analysis.json`.

Maturing the approved 16-bar, 1.5 ATR labels produced 1,879 research rows:
SELL 979, HOLD 187, and BUY 713. The compatibility heuristic accuracy was
0.3401 and emitted no BUY despite 713 BUY outcomes. A purged four-fold
research-only diagnostic allowed Logistic and Random Forest candidates to use
all twelve features. They emitted both directions, but aggregate Macro F1
ranged only from 0.3236 to 0.3758 and varied materially by fold. No provider or
deployment promotion is supported.

A fixed directional Trend counterfactual also restored BUY coverage but
achieved BUY precision of only 0.366–0.376 and Macro F1 no higher than 0.3224.
It is therefore not suitable as a silent replacement for the compatibility
provider.
