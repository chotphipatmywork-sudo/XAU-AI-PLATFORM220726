# CR-012 Simple Baseline Tester Benchmark

Version: 1.0.0

Date: 2026-07-17

Status: Completed and rejected for Forward promotion

Architecture Baseline: ABR-1.0

Related: CR-008, CR-009, CR-010, Phase 8A closure

## Approval

The project owner explicitly approved CR-012 on 2026-07-17. Approval covers a
deterministic Strategy Tester-only benchmark provider, isolated Backtest
artifacts, focused safety/decision tests, and documentation. It does not
authorize Forward use, model deployment, broker orders, or live execution.

## Purpose

Establish a simple, explainable benchmark before adding more AI complexity.
The experiment asks whether a fixed Trend-alignment policy using the existing
closed-bar Brain representation and the existing 1:2 Shadow SL/TP can outperform
the rejected Legacy and Directional development providers.

## Frozen benchmark policy

- input: existing Feature Schema 4.0 Trend Regime, Momentum, and Slope;
- BUY: all three values are at least `55`;
- SELL: all three values are at most `45`;
- HOLD: every other combination;
- no model fitting, calibration, threshold search, or Dataset input;
- fixed Shadow Stop Loss/Take Profit: `500/1000` points;
- one active Paper position, Risk Gate, loss/drawdown controls, emergency stop,
  and Trade Lifecycle remain canonical.

## Protected boundaries

- provider is allowed only when `MQL_TESTER=true`;
- Legacy remains the Forward default;
- model status is always NO-GO;
- model deployment authorization is always false;
- live execution authorization is always false;
- no Brain, Feature Schema, Label Schema, Dataset, Risk, or Execution bypass;
- dedicated Audit, State, Decision, Telemetry, and Report filenames prevent
  evidence mixing with Legacy or Directional runs.

## Evidence boundary

The first benchmark must use the same symbol, timeframe, dates, tick model,
deposit, spread assumptions, 500/1000-point SL/TP, and holding/loss limits as
the registered comparison run. Results are descriptive benchmark evidence,
not deployment evidence.

## Preliminary evidence

The 2026-07-18 real-tick run passed every safety and cross-file consistency
check, but covered only 20 market days through 2026-06-26. It is not accepted
as the final comparison against the 21-day Legacy/Directional interval through
2026-06-29. The corrected MT5 end boundary must be 2026-06-30. The preliminary
performance was seven trades, one win, six losses, Profit Factor 0.3329, and
expectancy -286.57 points; model and live deployment remain locked.

## Final same-period decision

The corrected full-period run completed on 2026-07-18 with 1,895 Decisions
across the same 21 market days as Legacy and Directional. Independent
Report/Decision/Audit validation passed every consistency and safety check.

Simple Baseline produced BUY/WAIT/SELL of 223/965/707, seven closed trades,
one win, six losses, Profit Factor 0.3329, expectancy -286.57 points, and
maximum drawdown 3,007 points. It restored two-sided coverage but was worse
than Legacy and essentially matched the rejected Directional provider.

CR-012 is closed as a valid explanatory benchmark and rejected for Forward
promotion. It does not authorize model deployment, live execution, or weaker
Risk controls. Its fixed 1:2 behavior remains the registered comparator for
CR-013 structure-aware research.
