# Shadow Trading Runbook

Version: 1.2.0

Status: Phase 8A operator guide

## Safety state

- Model deployment: not authorized
- Live execution: not authorized
- Broker order calls from Shadow: prohibited
- Recommended terminal state for initial testing: Algo Trading OFF
- Account: Demo only
- Chart: broker XAUUSD symbol, M15

## Validation order

1. Synchronize the workspace files to the MT5 project copy.
2. Compile `tests/TestClosedBarBrainContext.mq5`.
3. Compile `tests/TestShadowRiskGate.mq5`.
4. Compile `tests/TestShadowExecutionSafety.mq5`.
5. Compile `tests/TestShadowBacktestContract.mq5`.
6. Compile `tests/TestClosedBarFreshnessGuard.mq5`.
7. Compile `tests/TestShadowInferenceProvider.mq5`.
8. Compile `tests/TestShadowDirectionalInferenceProvider.mq5`.
9. Compile `tests/TestShadowSimpleBaselineInferenceProvider.mq5`.
10. Compile `XAU-AI-PLATFORM.mq5`.
11. Run all focused tests on XAUUSD M15.
12. Confirm broker order and position counts are unchanged.
13. Run the canonical EA in Strategy Tester and confirm its safety report.
14. Attach `XAU-AI-PLATFORM` to XAUUSD M15 with
   `ShadowEmergencyStop=false`.
15. Keep Algo Trading OFF for the initial observation.

The repository provides:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\tools\sync_shadow_runtime_to_mt5.ps1

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\tools\compile_shadow_runtime.ps1
```

The compile runner accepts only `0 errors, 0 warnings` for all affected
targets.

## Canonical Strategy Tester backtest

### CR-010 Directional research comparison

The `ShadowInferenceProvider` input defaults to
`SHADOW_INFERENCE_LEGACY_LOCKED`. Select
`SHADOW_INFERENCE_DIRECTIONAL_RESEARCH` only inside Strategy Tester. The EA
must reject that value on a normal Forward chart.

Run the Directional experiment with the same symbol, M15 timeframe, real-tick
period, Risk limits, and Execution inputs as the accepted Legacy run. Its
artifacts contain `BACKTEST_DIRECTIONAL` in their names and cannot overwrite
Legacy or Forward evidence. A successful safety report is research evidence
only and never authorizes deployment.

### CR-012 Simple Baseline benchmark

Select `SHADOW_INFERENCE_SIMPLE_TREND_BASELINE` only inside Strategy Tester.
It requires unanimous Trend Regime/Momentum/Slope alignment at the frozen
55/45 boundaries and otherwise emits HOLD. Use the same completed interval and
recommended Inputs as the Legacy and Directional comparisons.

The Simple Baseline artifacts contain `BACKTEST_SIMPLE_BASELINE` in their
names. Require provider identity
`SIMPLE_TREND_ALIGNMENT_BASELINE_TESTER_ONLY`, model status
`SIMPLE_BASELINE_BENCHMARK_NO_GO`, broker state unchanged, and safety valid.
This is a benchmark only; Forward, deployment, and live execution remain
prohibited regardless of profitability.

The Backtest and Forward Shadow tests are separate. Forward Shadow may remain
running while Strategy Tester uses its own local testing agent.

Open MT5 Strategy Tester with `Ctrl+R`, then select:

```text
Expert: XAU-AI-PLATFORM
Symbol: XAUUSD
Timeframe: M15
Mode: Every tick based on real ticks
Optimization: Disabled
Inputs: the recommended Shadow values below
```

Use a completed historical interval with enough data. The first operational
run should cover at least one full month. At completion, open the Strategy
Tester Journal and require:

```text
Shadow backtest broker state unchanged: true
Shadow backtest report written: true
Shadow backtest safety valid: true
Shadow backtest model status: DEVELOPMENT_HEURISTIC_MODEL_NO_GO
Shadow backtest deployment authorized: false
```

Backtest files use `XAU_AI_SHADOW_BACKTEST_*` names inside the testing-agent
file sandbox. They never overwrite the Forward Shadow files. A successful
safety report proves the pipeline ran without broker mutation; it does not
prove profitability or authorize deployment.

## CR-014 fresh Session confirmation evidence

This is a later research run, not Forward Shadow and not live trading. Use:

```text
Expert: XAU-AI-PLATFORM
Symbol: XAUUSD
Timeframe: M15
Date start: 2026.06.27
Date end: latest completed date available
Mode: Every tick based on real ticks
Optimization: Disabled
ShadowInferenceProvider: SHADOW_INFERENCE_OBJECTIVE_M15_M5_SETUP
ObjectiveMinimumRiskReward: 2.0
```

At completion, require `broker state unchanged`, `report written`, and `safety
valid` to be true, with Objective provider identity and deployment false.
Review the Journal for real-tick quality warnings before building evidence.
The first short post-cutoff run will probably be below the 80-plan confirmation
minimum; that is an expected safe refusal, not a system failure. Never use the
old Train, Validation, or Test CSV as confirmation evidence.

Recommended initial Inputs:

```text
ShadowVolume = 0.01
ShadowStopLossPoints = 500
ShadowTakeProfitPoints = 1000
ShadowSlippagePoints = 2
ShadowMaximumHoldingBars = 64
ShadowMaximumDailyLossPoints = 2000
ShadowMaximumDrawdownPoints = 3000
ShadowMaximumMarketAgeSeconds = 120
ShadowMaximumDecisionLagSeconds = 120
```

## Expected startup messages

```text
XAU AI PLATFORM Shadow Runtime Started.
Model deployment authorized: false
Live execution authorized: false
Shadow emergency stop: false
```

Within 60 seconds, the Experts tab should print a Shadow heartbeat. A new
decision is evaluated only after a new M15 bar starts, using the preceding
closed bar.

## Output files

Open MT5 `File -> Open Data Folder -> MQL5 -> Files`.

- `XAU_AI_SHADOW_DECISIONS_V4.csv`: one complete Schema 4.0 pipeline record per closed bar
- `XAU_AI_SHADOW_AUDIT.csv`: rejected/opened/closed paper lifecycle events
- `XAU_AI_SHADOW_TELEMETRY.csv`: 60-second health snapshots
- `XAU_AI_SHADOW_STATE.csv`: latest recoverable paper-position state

No row in these files represents a broker order.

## Emergency stop

Remove the EA, set `ShadowEmergencyStop=true`, and attach it again. Risk and
Shadow Execution will both reject new paper entries. Existing paper state is
memory-only and ends when the EA is removed.

## Observation target

Before model research:

- at least 1,000 closed-bar decisions;
- at least 100 completed paper trades;
- at least 20 distinct observation days;
- zero duplicate closed bars;
- zero Risk-bypass or non-synthetic-ticket violations.

Run:

```powershell
cd C:\Users\poowa\Documents\Codex\2026-07-13\9v\training
.\.venv\Scripts\python.exe analyze_shadow_run.py `
  --decisions "<MQL5 Files>\XAU_AI_SHADOW_DECISIONS_V4.csv" `
  --audit "<MQL5 Files>\XAU_AI_SHADOW_AUDIT.csv" `
  --output ".\output\shadow_run_report.json"
```

`ready_for_model_research=true` permits only a new offline research review. It
does not authorize Shadow model deployment or live trading.

After at least 16 later bars have matured, evaluate predictions against the
approved Label Schema 1.1:

```powershell
.\.venv\Scripts\python.exe evaluate_shadow_predictions.py `
  --decisions "<MQL5 Files>\XAU_AI_SHADOW_DECISIONS_V4.csv" `
  --output ".\output\shadow_prediction_evaluation.json"
```

This uses the logged closed-bar OHLC and ATR, then applies the same next-16-bar
`+/-1.5 ATR(14)` barrier rules. Ambiguous same-bar double touches are excluded.
Even `model_quality_gate_met=true` remains research evidence only.
