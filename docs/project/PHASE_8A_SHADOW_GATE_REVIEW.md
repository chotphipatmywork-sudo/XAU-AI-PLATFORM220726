# Phase 8A Shadow Trading Gate Review

Version: 1.0.0

Date: 2026-07-17

Architecture Baseline: ABR-1.0

Status: Closed — Operational safety PASS; Schema 4.0 evidence PASS; model-quality NO-GO

## Scope

Review Phase 8A stages 1 through 6 without authorizing broker orders or model
deployment.

## Gate summary

| Stage | Gate | Status | Evidence |
| --- | --- | --- | --- |
| 8A.1 | Safe-default execution mode, explicit Risk result, synthetic state | PASS | focused Risk and Execution tests |
| 8A.2 | Canonical Market-to-paper-lifecycle Runtime | PASS | Demo heartbeat and Decision/Audit/State agreement |
| 8A.3 | Paper Open, recovery, duplicate protection, SL/TP, shutdown | PASS | focused lifecycle test and Strategy Tester audit |
| 8A.4 | heartbeat, CSV evidence, emergency, stale data, loss/drawdown protection | PASS | runtime telemetry and drawdown stop evidence |
| 8A.5 | corrected real-tick Strategy Tester plus Demo Forward operation | PASS | 1895-bar V4 full-period backtest and 50-bar Forward audit |
| 8A.6 | model improvement and deployment eligibility | NO-GO | no BUY coverage, negative expectancy, unstable research candidates |

## Strategy Tester evidence

The accepted full-period XAUUSD M15 real-tick run covered 1847 closed-bar
Decisions over 21 market days.

- SELL/WAIT/BUY: 1094/753/0
- Risk passed / synthetic executions / closed trades: 18/18/18
- TP/SL: 5/13
- win rate: 27.7778%
- profit factor: 0.7680
- expectancy: -83.9444 paper points per trade
- cumulative result: -1511 paper points
- maximum drawdown: 3008 paper points
- drawdown-limit rejections: 1058
- duplicate bars: 0
- broker state unchanged: true
- independent artifact audit: valid

The Risk drawdown gate stopped new paper entries as designed. The final
account balance remained unchanged because no broker trades existed.

## Forward comparison

The Demo Forward audit contained 50 closed-bar observations across two days.

- SELL/WAIT/BUY: 35/15/0
- Risk allowed / rejected: 13/37
- closed trades: 13
- winning/losing trades: 4/9
- realized result: -1301 paper points
- duplicate bars: 0
- safety violations: 0
- model and live deployment: false/false

The same one-sided directional behavior appeared independently in historical
real-tick and Demo Forward operation.

## CR-009 Schema 4.0 evidence

The approved CR-009 follow-up now projects the complete twelve-dimensional
Feature Schema 4.0 vector inside the canonical Runtime and records it through
an explicit locked inference-provider boundary. The active compatibility
provider deliberately preserves the legacy four-score behavior and remains
`DEVELOPMENT_HEURISTIC_4_SCALAR_NO_GO`.

The accepted V4 full-period rerun contained 1,895 Decisions across 21 market
days. Report, Decision, and Audit evidence agreed, all Schema 4.0 values were
valid, broker state was unchanged, and the independent audit returned true.
It produced SELL/WAIT/BUY of 1,128/767/0, Profit Factor 0.7680, expectancy
-83.9444 points, and maximum drawdown 3008 points.

Approved labels matured on 1,879 rows with SELL/HOLD/BUY coverage of
979/187/713. The compatibility heuristic accuracy was 0.3401 and missed all
BUY output. Research-only purged walk-forward candidates using all twelve
features restored two-sided output but achieved aggregate Macro F1 of only
0.3236–0.3758 with material fold instability. No provider promotion is
supported.

## Root-cause boundary

The canonical Runtime currently invokes `CAIManager` with four legacy scalar
values:

- `Trend.Strength`
- `Volatility.ExpansionScore`
- `Liquidity.Score`
- `Session.Confidence`

`Trend.Strength` is magnitude, not bullish/bearish direction. The legacy
decision engine averages these values and maps a score below 40 to SELL. In
the accepted backtest it produced no BUY Decision.

The canonical Shadow Runtime now consumes and logs the Feature Schema 4.0
vector, but the locked compatibility provider intentionally evaluates the
four legacy scores. This isolates the defect and creates reliable research
evidence without silently changing behavior. The twelve-feature research
candidates remain unstable, and the trained Phase 7 candidate remains
undeployable.

## Decision

Phase 8A operational integration and safety are accepted. Phase 8A is not
eligible for deployment because model-quality stage 8A.6 remains NO-GO. The
phase is operationally closed with deployment denied; NO-GO is its accepted
quality-gate outcome.

- Continue collecting closed-bar Forward evidence safely.
- Do not interpret the development heuristic's paper result as AI model
  performance.
- Do not weaken Risk limits to manufacture more trades.
- Do not authorize Shadow model deployment or live execution.
- CR-009 evidence logging and the inference-provider contract are accepted.
- Any alternate provider must be introduced as a controlled Strategy
  Tester-only experiment before it can affect Forward Shadow behavior.
- Model behavior may change only after fresh offline evaluation passes the
  approved model contract and receives explicit project-owner approval.

CR-010 completed the permitted Strategy Tester comparison. Directional
restored BUY coverage but reduced Profit Factor from 0.7680 to 0.3328 and
worsened expectancy from -83.9444 to -286.4286 points per trade. It is rejected
for Forward promotion. See `PHASE_8A_SHADOW_CLOSURE.md` for the final boundary.

CR-012 then completed the same-period Simple Trend Baseline comparison. It
produced two-sided decisions but only seven trades, one win, six losses, Profit
Factor 0.3329, expectancy -286.57 points, and maximum drawdown 3,007 points.
All safety and cross-file evidence checks passed. Simple Baseline is rejected
for Forward promotion and retained only as the fixed 1:2 explanatory benchmark
for CR-013 Hybrid research.
