# IMP-074 Objective Minimum Reclaim Contract

Version: 1.0.0

Date: 2026-07-19

Status: Implemented; long-period evidence remains quality NO-GO

Architecture Baseline: ABR-1.0

Related: CR-013, ADR-006, IMP-068, IMP-073

## Purpose

Apply the only IMP-073 observation-time geometry predicate that passed every
frozen Train-only fold: a completed M5 directional reclaim of at least
`0.10 ATR`. The objective is to remove weak sweep/reclaim triggers without
changing module ownership, structural plan geometry, Risk, or Execution.

## Contract

`CObjectiveHybridSetupConfig.MinimumReclaimAtr` defaults to `0.10` and must be
positive. The Objective adapter calculates reclaim distance from the completed
M5 close to the confirmed swing POI:

```text
BUY  reclaim ATR = max(0, (close - swing low) / ATR_M5)
SELL reclaim ATR = max(0, (swing high - close) / ATR_M5)
```

The existing POI, sweep, candle-direction, timing, and Trend requirements still
apply. Trigger confirmation additionally requires reclaim ATR to meet or exceed
the configured minimum. A sub-minimum reclaim remains a valid observation but
is non-actionable.

## Protected boundaries

- Feature Schema 4.0 and Label Schema 1.1.0 are unchanged.
- The threshold uses only completed-bar information known at observation time.
- Stop, Target, minimum 2R, Risk limits, and Execution are unchanged.
- No Forward, model deployment, broker order, or live authorization is added.
- Earlier datasets remain evidence for the review, not validation of the new
  contract.

## Validation gate

- exact `0.10 ATR` BUY and SELL reclaim examples remain actionable;
- a `0.05 ATR` BUY reclaim with otherwise valid POI and sweep is rejected;
- all Objective Stage C compile targets report zero errors and zero warnings;
- new real-tick Strategy Tester evidence is required before any quality claim.

## Files

- `core/ai/strategy/models/ObjectiveHybridSetupConfig.mqh`
- `core/ai/strategy/ObjectiveMultiTimeframeSetupAdapter.mqh`
- `tests/TestObjectiveMultiTimeframeSetupAdapter.mq5`

## Validation result

Workspace validation on 2026-07-19 passed:

- all 40 Python regression scripts;
- Objective Stage C synchronization;
- MetaEditor compile for 10/10 affected targets;
- zero compile errors and zero warnings.

At that point the focused chart test and new real-tick quality evidence were
the remaining operator gates. Deployment remains unauthorized regardless of
their result.

Operator evidence received on 2026-07-19 confirms the focused XAUUSD M15 test:

- exact-threshold BUY and SELL setups remained valid;
- the `0.10 ATR` configuration and sweep/reclaim evidence were valid;
- sub-minimum reclaim remained non-actionable;
- future/forming timing and insufficient RR were rejected;
- the Risk boundary was preserved;
- the complete adapter contract reported `true` and removed itself normally.

The remaining gate is newly generated `Every tick based on real ticks`
Strategy Tester evidence under this amended contract.

## One-month real-tick smoke result

The 2026-06-01 through 2026-06-29 XAUUSD M15 real-tick run completed on
2026-07-19. Operational safety passed, broker state was unchanged, the report
was written, provider identity was correct, and deployment remained false.

The amended contract produced 11 plans versus 12 in the frozen reference. It
removed exactly the 2026-06-12 04:00 BUY plan whose reclaim was
`0.0980375 ATR`; that plan was previously `STOP_FIRST`. No new plan appeared,
and the minimum retained reclaim was `0.1012455 ATR`.

Paper execution changed from six to eight because removing the earlier loss
changed the path-dependent drawdown gate and allowed later plans. The eight
executed plans all lost, producing -3,439 cumulative points and 3,439 maximum
drawdown points. Therefore the smoke test proves contract behavior and safety,
not strategy quality. The amended strategy remains `NO_GO`; full regenerated
real-tick Setup outcomes are required for a stable quality comparison.

The four source artifacts were preserved before the next Tester run under
`training/output/objective_minimum_reclaim_smoke_202606/`. The Setup Audit
SHA-256 is `6ABB1E9A908EB3CF48CF244C21D653165C9E4B9214A5DB5FFE39BE36907188E7`
and the Report SHA-256 is
`3A7E7E5681702A61B2C92E1447612979B4D896F0E9A54A6719F7AF55A97F22D8`.

## Five-year real-tick result

The amended Objective contract completed the 2021-07-01 through 2026-06-29
XAUUSD M15 run on 2026-07-19. It processed 116,688 Decisions and 324,765,990
ticks. Broker state was unchanged, report and safety gates were valid, and
deployment remained false. Risk allowed 64 paper executions: 10 won and 54
lost, for -2,658 cumulative points and 3,079 maximum drawdown points.

The versioned source-quality exclusions removed two affected plans. The
resulting Dataset contained 262 plans, 260 trainable outcomes, 60 Target-first,
200 Stop-first, and two ambiguous outcomes. Its chronological split produced
182 Train, 39 Validation, and 39 Test records. Because Train remained below the
frozen 200-record minimum, Train-only ranking correctly stayed blocked;
Validation and Test were not used for selection.

Descriptive Train-only comparison moved in the intended direction but did not
prove an edge: Target rate increased from 22.71% to 25.27% and mean cost-aware
return improved from -0.161R to -0.064R. The result remains negative and below
the sample gate. Neither the minimum sample size nor the temporal split may be
weakened to force promotion.

Source artifacts are preserved under
`training/output/objective_minimum_reclaim_real_ticks_202107_202606/`.
