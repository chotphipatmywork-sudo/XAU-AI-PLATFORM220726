# IMP-062 Strategy Tester Inference Experiment

Version: 1.0.0

Status: Completed; safety accepted; Directional Forward promotion rejected

Related: CR-010, CR-009, ADR-005

## Purpose

Compare a bounded directional research policy with the locked legacy provider
through the complete canonical Shadow Strategy Tester pipeline without
changing Forward behavior or authorizing deployment.

## Runtime selection

`CShadowRuntimeConfig.InferenceProvider` defaults to
`SHADOW_INFERENCE_LEGACY_LOCKED`. The only alternate value is
`SHADOW_INFERENCE_DIRECTIONAL_RESEARCH`.

`InferenceProviderAllowed()` permits the alternate only when the caller is in
Strategy Tester. `CRuntimeManager.Initialize()` obtains `MQL_TESTER` and
rejects the alternate before initializing the Runtime pipeline when that flag
is false.

## Directional policy

`CDirectionalResearchInferenceProvider` consumes the approved Schema 4.0
request and calculates:

`score = 0.45 TrendRegime + 0.40 TrendMomentum + 0.15 TrendSlope`

- score below 40: SELL
- score above 60: BUY
- otherwise: HOLD

These weights and thresholds were declared in CR-010 from the bounded
counterfactual. The provider is identified as
`DIRECTIONAL_FEATURE_RESEARCH_TESTER_ONLY`, reports
`DIRECTIONAL_FEATURE_RESEARCH_NO_GO`, and always denies deployment.

## Evidence isolation

Directional Strategy Tester artifacts use:

- `XAU_AI_SHADOW_BACKTEST_DIRECTIONAL_DECISIONS_V4.csv`
- `XAU_AI_SHADOW_BACKTEST_DIRECTIONAL_AUDIT.csv`
- `XAU_AI_SHADOW_BACKTEST_DIRECTIONAL_STATE.csv`
- `XAU_AI_SHADOW_BACKTEST_DIRECTIONAL_TELEMETRY.csv`
- `XAU_AI_SHADOW_BACKTEST_DIRECTIONAL_REPORT.csv`

Legacy and Forward filenames remain unchanged. Backtest Report evidence now
contains the provider identity and dynamic NO-GO model status; Decision and
Report evidence must agree.

## Focused validation

`tests/TestShadowDirectionalInferenceProvider.mq5` verifies:

- Legacy remains the Forward default;
- Directional is rejected outside Strategy Tester;
- canonical Runtime initialization rejects Directional on a Forward chart;
- Directional is permitted in Strategy Tester;
- fixed inputs map to BUY, HOLD, and SELL correctly;
- identity, NO-GO status, and deployment lock remain valid.

## Known limitation

This provider is a research policy, not a trained or approved model. Even a
profitable historical paper result cannot authorize Forward or live use. Any
promotion requires separate untouched temporal evidence and explicit owner
approval.

## Local validation evidence

On 2026-07-17:

- the canonical include closure covered 106 files;
- broker-capable files and broker-mutation tokens: 0 / 0;
- provider-aware Legacy and Directional artifact audit tests passed;
- the complete Python regression passed 32/32 tests;
- Shadow sync and compile PowerShell scripts parsed successfully.

The managed Codex environment cannot write into the MT5 project copy or
launch MetaEditor. Exact 0-error/0-warning compilation and focused chart
runtime evidence remain required.

## Focused MT5 runtime evidence

On 2026-07-17 13:41:01, `TestShadowDirectionalInferenceProvider` ran on a
normal XAUUSD M15 chart and confirmed:

- the Runtime explicitly rejected the research provider outside Strategy
  Tester;
- Legacy remained the valid Forward default;
- configuration-level and canonical Runtime Forward locks passed;
- Strategy Tester permission contract passed;
- BUY, HOLD, and SELL mapping passed;
- provider identity and NO-GO deployment lock passed;
- the complete Directional inference contract passed;
- the focused EA removed itself normally.

The Forward isolation gate is accepted. The next evidence step is an isolated
Directional Strategy Tester run using the same period and Risk/Execution
inputs as the accepted Legacy V4 baseline.

## First full-period evidence finding

The first Directional full-period run completed on 2026-07-17 13:56:41 with
unchanged broker state, internal safety true, and `OnTester` result 1. Decision
rows correctly identified `DIRECTIONAL_FEATURE_RESEARCH_TESTER_ONLY`, but the
final Report identified `UNCONFIGURED_INFERENCE_PROVIDER`.

The cause was deterministic: `OnTester()` shuts down the Runtime to close the
paper lifecycle before capturing final counts. Shutdown correctly clears the
active provider pointer, so the Report accessor lost its evidence identity.
Trading decisions, Risk, Execution, and broker safety were not affected, but
the cross-file evidence contract was invalid and the run is not accepted.

Runtime now snapshots provider identity and model status immediately after
successful provider initialization and retains those immutable evidence
values after Shutdown. The active provider pointer is still cleared. Updated
compilation and a repeat Directional run are required.

The focused Directional provider test now also initializes the locked Legacy
Runtime with isolated temporary files, shuts it down, and verifies that the
provider identity and model status remain unchanged for final reporting.

The backtest safety contract was also strengthened to reject any Report whose
provider identity or model status contains `UNCONFIGURED`. The discovery run's
`OnTester` result 1 is therefore superseded: cross-file identity disagreement
already invalidated it, and the corrected contract now fails that condition
internally as well.

## Accepted corrected Directional evidence

The corrected XAUUSD M15 real-tick run completed on 2026-07-17 14:21:06 over
the available 2026-06-01 through 2026-06-29 history.

- provider / model status:
  `DIRECTIONAL_FEATURE_RESEARCH_TESTER_ONLY` /
  `DIRECTIONAL_FEATURE_RESEARCH_NO_GO`
- Decisions: 1,895 across 21 market days; duplicates: 0
- BUY / HOLD / SELL: 505 / 272 / 1,118
- Risk rejections / synthetic executions / closed trades: 1,888 / 7 / 7
- winning / losing / breakeven: 1 / 6 / 0
- profit factor: 0.3328
- expectancy: -286.4286 points per trade
- cumulative / maximum drawdown points: -2005 / 3005
- broker state unchanged, internal safety, and cross-file evidence: true
- model and live deployment authorization: false / false

The accepted Legacy baseline produced Profit Factor 0.7680 and expectancy
-83.9444 points per trade. Directional restored two-sided coverage but was
materially worse on both performance measures and hit the drawdown stop after
seven entries. CR-010 therefore rejects the Directional provider for Forward
promotion. Legacy remains the locked default and is also still model-quality
NO-GO.
