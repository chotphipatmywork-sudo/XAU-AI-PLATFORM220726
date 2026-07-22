# CR-011 Completed-Tick Microstructure Context

Version: 1.0.0

Date: 2026-07-17

Status: Controlled evidence complete; rejected

## Approval

The project owner explicitly approved CR-011 on 2026-07-17. Approval covers
the isolated exporter, completed-bar timing/encoding tests, Train-only
controlled diagnostic, and documentation. It does not approve a canonical
schema change, Runtime integration, model deployment, or live execution.

Architecture Baseline: ABR-1.0

Related: Phase 7 closure, Phase 8A closure, Feature Schema 4.0

## Motivation

Legacy and Directional Shadow providers both failed the quality gate. Raising
the directional threshold did not create stable precision: the strongest SELL
region ranged from 0.4803 to 0.6077 across four chronological periods, while
the strongest BUY region ranged from 0.0870 to 0.5263.

Prior research already rejected bar-level temporal windows, H1 context,
Liquidity event memory, swing structure, completed-candle price action, and
price-path state. Further threshold tuning on inspected periods is prohibited.

The next bounded candidate is completed-tick microstructure, which is new
past-only information inside the existing Liquidity and Volatility feature
groups rather than another transformation of the same M15 OHLC bars.

## Proposed research fields

For each fully completed M15 bar only:

- signed tick-direction imbalance;
- tick arrival/burst concentration;
- mean and maximum spread regime;
- realized tick-path volatility;
- tick-path efficiency from first to last completed tick.

Every value must use ticks whose timestamps fall inside the completed source
bar. The current tick, future bar, label horizon, Risk result, execution result,
and trade outcome are forbidden inputs.

## Isolation

1. Export an auxiliary Dataset-keyed CSV; do not change canonical Schema 4.0.
2. Join only to the existing Train partition after exact timestamp and symbol
   validation.
3. Do not read Validation or Test.
4. Compare Baseline and bounded microstructure groups using the registered
   purged chronological method.
5. Run nested confirmation only if the controlled promotion gate passes.
6. Do not modify Runtime, inference providers, Risk, Execution, or deployment
   flags during research.

## Coverage and leakage gates

- completed-bar timing must pass a focused synthetic and historical test;
- duplicate Dataset keys must be zero;
- invalid numeric fields must be zero;
- joined timestamp equality must be exact;
- missing tick coverage must be reported by period and broker-history range;
- completed-tick validity coverage must be at least 80% before comparison;
- insufficient coverage rejects the experiment rather than filling future or
  synthetic values.

## Implementation state

The bounded exporter, synthetic encoding/timing test, SHA-256 verified sync and
compile tooling, strict auxiliary reader, and Train-only controlled diagnostic
are implemented under IMP-063. MetaEditor compilation passed with zero errors
and zero warnings; historical export evidence is pending operator execution.

## Promotion boundary

Research promotion requires all predeclared conditions:

- aggregate Macro F1 improvement of at least 0.01 over Baseline;
- no degradation of the complete evaluation-contract gate floor;
- improvement across at least two chronological folds;
- stable BUY and SELL precision/recall coverage;
- nested confirmation under the same 16-bar purges.

Passing research would authorize a separate schema-version review only. It
would not authorize Forward Shadow model deployment or live execution.

## Safety state

- active Forward provider remains Legacy NO-GO;
- Directional provider remains Strategy Tester-only and rejected;
- model deployment authorized: false;
- live execution authorized: false;
- broker mutation authorized: false.

## Decision

The exporter produced 26,864 exact Dataset-keyed rows with 26,859 valid rows
(99.9814% coverage). The registered four-fold Train-only comparison ranked the
unchanged Schema 4.0 Baseline first at Macro F1 `0.394773` and gate floor
`0.913112`. Liquidity Tick Flow, Volatility Tick State, and the combined set
all reduced both measurements and passed `0/4` complete folds.

No candidate reached the promotion boundary. Nested confirmation is not
authorized, Validation and Test remain unread, and CR-011 does not authorize a
schema review or Runtime change.
