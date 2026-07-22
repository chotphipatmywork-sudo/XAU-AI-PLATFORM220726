# IMP-060 Canonical Shadow Strategy Tester

Version: 1.0.0

Status: Corrected smoke Strategy Tester evidence accepted; full-period evidence pending

Related: CR-008, ADR-005, IMP-059

## Purpose

Close the Phase 8A.5 evidence gap by running the canonical
`XAU-AI-PLATFORM` EA through MT5 Strategy Tester before interpreting the
longer Demo Forward Shadow observation.

This is an end-to-end operational backtest of:

`Market -> Brain -> AI Runtime -> Decision -> Risk -> Shadow Execution -> Paper Trade Lifecycle`

It is not a model deployment test and cannot authorize live trading. The
active model remains `DEVELOPMENT_HEURISTIC_MODEL_NO_GO`.

## Isolation

Strategy Tester mode is detected with `MQL_TESTER`. In that mode:

- the terminal Global Variable checkpoint used by Forward Shadow is disabled;
- the run starts from the first closed bar supplied by Strategy Tester;
- the execution state, audit, decision, and telemetry files use isolated
  `XAU_AI_SHADOW_BACKTEST_*` names;
- existing Forward Shadow CSV files and its persistent checkpoint are not
  read, overwritten, or advanced;
- every Strategy Tester run deletes its prior isolated artifacts before
  initialization.

## Evidence contract

At the end of a complete Strategy Tester run, `OnTester()` shuts down the
paper lifecycle deterministically and writes
`XAU_AI_SHADOW_BACKTEST_REPORT.csv` with:

- first and last decision bars;
- Decision, Risk rejection, and synthetic execution counts;
- closed, winning, losing, and breakeven paper-trade counts;
- cumulative paper points and maximum paper drawdown points;
- model and live authorization flags;
- broker order/position count invariance;
- internal count consistency and the final safety result.

The custom Strategy Tester result is `1.0` only when the report is written and
the safety contract passes. Profit is deliberately not used as the custom
criterion because this stage validates integration and safety, not model
deployment eligibility.

## Files

- `XAU_AI_SHADOW_BACKTEST_DECISIONS_V4.csv` (CR-009 and later runs)
- `XAU_AI_SHADOW_BACKTEST_DECISIONS.csv` (historical pre-CR-009 evidence)
- `XAU_AI_SHADOW_BACKTEST_AUDIT.csv`
- `XAU_AI_SHADOW_BACKTEST_TELEMETRY.csv`
- `XAU_AI_SHADOW_BACKTEST_STATE.csv`
- `XAU_AI_SHADOW_BACKTEST_REPORT.csv`

Strategy Tester stores these in its local testing-agent `MQL5/Files` sandbox.
They do not share the Demo Forward `MQL5/Files` location.

## Focused validation

`tests/TestShadowBacktestContract.mq5` checks:

- paper-trade counts are internally consistent;
- model and live authorization remain false;
- unchanged broker state is required for a valid report;
- a report CSV can be written;
- simulated broker mutation invalidates the safety contract.

## Required MT5 validation

1. Compile `tests/TestShadowBacktestContract.mq5` with 0 errors and 0 warnings.
2. Compile `XAU-AI-PLATFORM.mq5` with 0 errors and 0 warnings.
3. Run `XAU-AI-PLATFORM` in Strategy Tester on XAUUSD M15 using real ticks.
4. Confirm the final Journal contains:
   - `Shadow backtest broker state unchanged: true`
   - `Shadow backtest report written: true`
   - `Shadow backtest safety valid: true`
   - `Shadow backtest deployment authorized: false`
5. Inspect the report and audit files for count agreement and zero broker
   mutation.

After copying the five tester artifacts to one readable directory, run
`training/analyze_shadow_backtest.py` with the Report, Decisions, and Audit
paths. The resulting `backtest_evidence_valid=true` requires agreement between
all three files, unique closed bars, synthetic ticket range, locked deployment
flags, and unchanged broker state. The analyzer never trains or deploys a
model.

Only after this evidence exists may Phase 8A.5 Strategy Tester validation be
called complete. Forward Shadow observation remains a separate time-based
gate.

## Local validation evidence

On 2026-07-17:

- the canonical include-closure audit covered 98 files;
- broker-capable files in the closure: 0;
- broker-mutation tokens in the closure: 0;
- PowerShell sync, compile, and no-broker scripts parsed successfully;
- `training/test_analyze_shadow_backtest.py` passed;
- the complete Python regression passed 32/32 tests.

The Codex filesystem sandbox could not launch the MetaEditor GUI. Therefore
these local checks are not a substitute for the required MetaEditor result of
0 errors and 0 warnings or for the Strategy Tester Journal evidence.

## MetaEditor compile evidence

The synchronized MT5 project copy was compiled on 2026-07-17:

- `tests/TestClosedBarBrainContext.mq5`: 0 errors, 0 warnings
- `tests/TestShadowRiskGate.mq5`: 0 errors, 0 warnings
- `tests/TestShadowExecutionSafety.mq5`: 0 errors, 0 warnings
- `tests/TestShadowBacktestContract.mq5`: 0 errors, 0 warnings
- `XAU-AI-PLATFORM.mq5`: 0 errors, 0 warnings

The new focused test and canonical EA `.ex5` files were verified present in
the MT5 project copy. Compile logs are stored under
`outputs/compile/shadow/`.

## Focused runtime evidence

On XAUUSD M15 at 2026-07-17 09:08:21:

- backtest trade-count consistency: true
- safe report contract: true
- simulated broker mutation was rejected: true
- complete Shadow backtest contract: true
- the focused EA removed itself normally

The existing Demo Forward Shadow Runtime continued its heartbeat after the
compile and focused test. At 09:08 local terminal time it reported 14 closed-
bar decisions, 12 Risk rejections, two synthetic executions, no active paper
position, and `live_execution_authorized=false`.

## Smoke Strategy Tester finding

The first XAUUSD M15 real-tick smoke run completed at 2026-07-17 09:23:31.
The internal report recorded 92 Decisions, 68 Risk rejections, 24 synthetic
executions, 24 closed paper trades, unchanged broker state, and safety valid.
The custom `OnTester` result was `1`.

Artifact inspection found that the first Decision bar was
`2026-07-10 23:45`, before the configured test start at
`2026-07-13 00:00`. This represented the last Friday bar being evaluated on
the first Monday tick. The internal safety report did not detect this temporal
boundary defect, so the smoke run is retained as discovery evidence and is
not accepted as final Strategy Tester evidence.

The Runtime now initializes non-persistent tester context from the current
closed bar and applies a closed-bar freshness guard before Brain/AI processing.
The default maximum decision lag is 120 seconds. A delayed weekend or restart
bar is checkpointed and skipped, while the next newly closed bar can proceed.
The offline artifact analyzer also requires every Decision bar to fall within
the configured test interval and to agree with the report boundaries.

The strengthened offline audit reproduced all 92 Decisions, 24 opens, 24
closes, win/loss counts, realized points, synthetic tickets, and zero duplicate
bars from the smoke artifacts. It intentionally returned
`backtest_evidence_valid=false` solely because
`decisions_within_test_period=false`. This proves the temporal defect is now
detectable rather than silently accepted.

After the freshness change, the canonical include closure contains 99 files
with zero broker-capable files and zero broker-mutation tokens. The focused
Python artifact-audit test passes, and the complete Python regression passes
32/32. Updated MetaEditor compilation and a repeat Strategy Tester run are
required before accepting the fix.

The corrected synchronized MT5 copy was compiled on 2026-07-17. All six
targets passed with 0 errors and 0 warnings, including
`tests/TestClosedBarFreshnessGuard.mq5` and the canonical EA. Their generated
`.ex5` files were verified present. Focused runtime output and repeat tester
artifacts remain required.

At 2026-07-17 10:58:18 on XAUUSD M15, the focused freshness test confirmed:

- a recently completed bar was accepted: true
- a delayed weekend bar was rejected: true
- a future/unclosed bar was rejected: true
- the complete closed-bar freshness guard was valid: true
- the focused EA removed itself normally

The temporal correction is now proven at component level. Canonical repeat
Strategy Tester evidence is still required.

## Accepted corrected smoke evidence

The corrected XAUUSD M15 real-tick smoke run completed at
2026-07-17 11:22:58 for the configured 2026-07-13 test period.

- first Decision bar: 2026-07-13 01:00
- last Decision bar: 2026-07-13 23:30
- Decisions: 91
- Risk rejections: 68
- synthetic executions and closed trades: 23/23
- winning/losing/breakeven trades: 9/14/0
- cumulative paper points: 2415.0000000001
- maximum paper drawdown points: 1512.9999999999654
- broker state unchanged: true
- report count consistency: true
- internal safety valid: true
- model and live authorization: false/false

The offline cross-file audit matched the Report, Decisions, and Audit files.
It confirmed zero duplicate closed bars, all Decision bars within the test
period, valid synthetic ticket range, matching realized points, and returned
`backtest_evidence_valid=true`. It retained both Shadow and live deployment as
false. This accepts the temporal correction and one-day operational smoke
test; it does not provide sufficient duration for performance conclusions.

## Long-run tester I/O control

The accepted smoke run showed that rewriting the recoverable state file on
every market tick creates unnecessary Strategy Tester I/O. State persistence
does not need tick-level frequency because entry, SL, TP, and close levels are
already written immediately and current mark-to-market state is recalculated
from the next tick after recovery.

The Shadow engine now writes state immediately on Open and Close, every 60
seconds during Demo Forward mark-to-market, and every 900 seconds during
Strategy Tester mark-to-market. This preserves restart recovery while making
the required month-long real-tick test practical. Decision, Audit, and
Telemetry evidence frequency is unchanged.

The optimized synchronized MT5 copy compiled on 2026-07-17. All six targets
passed with 0 errors and 0 warnings, and the updated Shadow Execution Safety
and canonical EA `.ex5` artifacts were verified present. Repeat focused
lifecycle evidence is required before the full-period tester run.

At 2026-07-17 11:45:14 on XAUUSD M15, the optimized lifecycle test confirmed
rejected Risk, synthetic entry, duplicate protection, persisted-state
recovery, paper close, emergency stop, unchanged broker counts, and complete
Shadow execution safety were all true. The focused EA removed itself normally.
The I/O optimization is therefore accepted for the full-period tester run.

## Accepted full-period Strategy Tester evidence

The optimized XAUUSD M15 real-tick run completed at
2026-07-17 11:58:53 over the available 2026-06-01 through 2026-06-29 broker
history.

- Decision bars: 1847 across 21 distinct market days
- Decision distribution: SELL 1094, WAIT 753, BUY 0
- Risk passed: 18
- active-exposure rejections: 18
- non-actionable Decision rejections: 753
- drawdown-limit rejections: 1058
- closed paper trades: 18
- take-profit/stop-loss closes: 5/13
- win rate: 27.7778%
- gross winning/losing points: 5003/-6514
- profit factor: 0.7680
- expectancy: -83.9444 points per closed paper trade
- cumulative paper result: -1511 points
- maximum paper drawdown: 3008 points
- duplicate Decision bars: 0
- broker state unchanged: true
- internal safety valid and `OnTester` result: true/1

The independent cross-file audit returned
`backtest_evidence_valid=true`: Report, Decisions, and Audit counts, realized
points, boundaries, and synthetic tickets all agreed. Model and live
deployment remained false.

The operational integration and Risk stop are accepted. Strategy quality is
not accepted: the development heuristic produced no BUY coverage, profit
factor below 1, negative expectancy, and reached the configured drawdown stop.
This is a model/decision NO-GO, not a Shadow safety failure.
