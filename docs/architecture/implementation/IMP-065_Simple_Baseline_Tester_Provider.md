# IMP-065 Simple Baseline Strategy Tester Provider

Status: Completed; operationally valid and rejected for Forward promotion

Related: CR-012, IMP-059, IMP-060, IMP-061, IMP-062

## Implementation

`CSimpleTrendBaselineInferenceProvider` implements the existing
`IAIInferenceProvider` boundary. It consumes the canonical closed-bar Schema
4.0 request and emits BUY only when Trend Regime, Momentum, and Slope are all
at least 55; SELL only when all are at most 45; otherwise HOLD.

The provider contains no training, model artifact, probability calibration,
Risk approval, order API, or broker mutation. It is a deterministic benchmark,
not an AI model.

## Runtime isolation

`SHADOW_INFERENCE_SIMPLE_TREND_BASELINE` is valid only in Strategy Tester.
Runtime initialization rejects it in Forward mode. Legacy remains the default.
The canonical flow remains:

`Market -> Brain -> Provider -> Decision -> Risk -> Shadow Execution -> Paper Lifecycle`

Dedicated `SIMPLE_BASELINE` filenames isolate Audit, State, Decision,
Telemetry, and Report evidence.

## Fixed risk comparison

The provider does not own Money Management. The existing Shadow Execution
configuration supplies Stop Loss `500` points and Take Profit `1000` points,
which is a fixed 1:2 ratio. Existing single-position protection, daily loss,
drawdown, stale-market, emergency-stop, and broker-mutation locks remain active.

## Focused validation

`tests/TestShadowSimpleBaselineInferenceProvider.mq5` verifies:

- Legacy Forward default remains unchanged;
- Simple Baseline is blocked in Forward and allowed in Strategy Tester;
- canonical Runtime initialization rejects the provider on a Forward chart;
- fixed Shadow Risk:Reward is 1:2;
- unanimous BUY/SELL and mixed HOLD mapping;
- provider identity and permanent deployment NO-GO lock.

## Implemented files

- `core/ai/inference/SimpleTrendBaselineInferenceProvider.mqh`
- `core/ai/inference/models/ShadowInferenceProviderMode.mqh`
- `core/runtime/models/ShadowRuntimeConfig.mqh`
- `core/runtime/RuntimeManager.mqh`
- `XAU-AI-PLATFORM.mq5`
- `tests/TestShadowSimpleBaselineInferenceProvider.mq5`
- `tools/sync_shadow_runtime_to_mt5.ps1`
- `tools/compile_shadow_runtime.ps1`

Dataset generation and all corrected Dataset gates are complete. MT5
synchronization now requires only a normal MT5/MetaEditor shutdown.

## Workspace validation

- canonical Shadow include closure: 108 files;
- broker-capable files in closure: 0;
- broker-mutation tokens in closure: 0;
- PowerShell sync/compile scripts parse: passed;
- complete Python regression: 33/33 passed;
- MetaEditor compilation: passed on 2026-07-18; nine of nine targets compiled
  with `0 errors / 0 warnings` after verified MT5 synchronization.
- Focused MT5 contract validation passed on XAUUSD M15 at
  `2026.07.18 22:41:17.846`: Forward default/isolation, tester permission,
  fixed 1:2 benchmark, BUY/HOLD/SELL mapping, strict Trend alignment, provider
  identity, and permanent deployment NO-GO lock all reported `true`.

## Preliminary Strategy Tester evidence

The first real-tick Simple Baseline run completed at
`2026.07.18 22:52:43.311` with unchanged broker state, internal safety, report
writing, provider identity, and independent cross-file evidence all valid. It
produced 1,804 Decisions across 20 market days, BUY/WAIT/SELL coverage of
222/899/683, seven closed trades, one win, six losses, Profit Factor 0.3329,
expectancy -286.57 points, and maximum drawdown 3,007 points.

This run is preliminary rather than the registered comparison because its last
observation was 2026-06-26. The accepted Legacy and Directional runs include
2026-06-29 and contain 1,895 Decisions across 21 market days. A corrected
Strategy Tester run with the end boundary set to 2026-06-30 is required for a
fair same-period benchmark. Deployment remains NO-GO regardless of the rerun.

## Accepted same-period Strategy Tester evidence

The corrected XAUUSD M15 real-tick run completed at
`2026.07.18 23:01:16.128` and covered the registered interval through
2026-06-29.

- Decisions: 1,895 across 21 market days; duplicate bars: 0
- BUY / WAIT / SELL: 223 / 965 / 707
- Risk rejections / synthetic executions: 1,888 / 7
- closed / winning / losing / breakeven trades: 7 / 1 / 6 / 0
- Take Profit / Stop Loss closes: 1 / 6
- win rate: 14.2857%
- Profit Factor: 0.3329
- expectancy: -286.57 points per closed paper trade
- cumulative result / maximum drawdown: -2,006 / 3,007 points
- broker state unchanged, internal safety, report writing, and independent
  cross-file evidence: all valid
- model and live deployment authorization: false / false

The benchmark restored two-sided directional coverage but was materially worse
than the accepted Legacy result of Profit Factor 0.7680 and expectancy -83.94
points. It was effectively level with the already rejected Directional
research provider and reached the drawdown halt after seven entries. CR-012 is
therefore rejected for Forward promotion. The fixed 1:2 provider remains only
an explainable benchmark for later CR-013 comparisons.
