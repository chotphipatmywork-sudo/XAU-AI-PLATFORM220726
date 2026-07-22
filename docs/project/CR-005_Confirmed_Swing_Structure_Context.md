# CR-005 Proposed Confirmed Swing Structure Context

Version: 0.1.0

Date: 2026-07-16

Status: Research evaluated and rejected; no Brain or Feature Schema change

Architecture Baseline: ABR-1.0

Related Phase: Post-Phase-7 Model Improvement Research

## Problem

Source review found that the current Trend structure path does not yet provide independent market-structure information:

- `CStructureEngine` maps EMA Slope directly to higher-high/higher-low or lower-high/lower-low flags.
- `CBOSEngine` then maps those flags directly to a valid break.
- `CCHOCHEngine` intentionally returns its default result because Swing History is not implemented.
- `CTrendAssembler` already contains CHOCH-aware behavior, but CHOCH can never become valid under the current engine.

Consequently, the existing Trend Regime, Momentum, and Slope features do not receive confirmed swing-break or character-change context.

## Proposed research boundary

Create a research-only confirmed-swing engine and auxiliary exporter. It must use only bars known at each observation time and must not modify `CTrendResult`, `CTrendAnalyzer`, `CBrainFeatureAdapter`, Feature Schema 4.0, or live Runtime behavior.

The auxiliary fields are:

1. confirmed structure direction: bearish `0`, mixed/unknown `50`, bullish `100`
2. confirmed break direction: bearish `0`, none `50`, bullish `100`
3. confirmed CHOCH direction: bearish `0`, none `50`, bullish `100`
4. close position between the latest confirmed swing low/high: `0..100`

Pivots require bars on both sides, but every confirmation bar must already be closed before the M15 observation. No forming or future bar may be used.

## Research workflow

1. Implement one focused Swing Structure research engine under the Trend package.
2. Add a focused MetaEditor test for bullish, bearish, neutral, and timing behavior.
3. Export an auxiliary CSV keyed by canonical Dataset ID and Timestamp.
4. Verify exact joins, bounded values, no duplicates, and closed-bar timing.
5. Run a fixed controlled Train-only Baseline-versus-Structure comparison.
6. Run nested confirmation only if the predeclared controlled promotion gate passes.

The fixed candidate grid is:

- Schema 4.0 Baseline;
- Baseline plus Structure, Break, and CHOCH Direction;
- Baseline plus all four confirmed Swing Structure fields.

The fixed estimator is raw `random_forest_depth_5_balanced`; the decision
policy is argmax; evaluation is four Train-only expanding folds with a
16-record purge.

## Promotion boundary

The controlled candidate must:

- improve gate-floor ratio by at least `0.01`;
- not reduce Macro F1;
- pass at least one complete fold;
- use no Validation or Test data.

A canonical Brain/Feature change requires candidate selection and complete gate passes in all four nested Outer periods.

## Architecture and version impact

Research has no public-interface or Runtime impact. Canonical integration would change Trend behavior and historical feature semantics even if the tensor width stayed unchanged. It would require:

- explicit Architecture and Interface approval;
- Feature Schema version review;
- identical live/historical use of the same engine;
- complete Dataset regeneration;
- full MetaEditor and Python validation;
- later untouched evaluation.

## Risks

- Confirmed pivots are delayed by design.
- Swing parameters can overfit and must remain fixed before evaluation.
- Structure position may overlap existing Liquidity range position.
- A research pass on inspected Train data is not deployment evidence.

## Rollback

Remove the research engine, exporter, test, auxiliary CSV, and reports. Runtime and Feature Schema 4.0 remain unchanged.

## Approval record

- Research-only engine/exporter: approved under the project owner's 2026-07-16 improvement authorization
- Brain public behavior change: not approved
- Feature Schema change: not approved
- Deployment: not approved

## Research result

The auxiliary export completed with `26,864` exact Dataset-keyed records:

- exact ID/Timestamp order match: true
- duplicate keys: `0`
- invalid or out-of-range rows: `0`
- confirmed Swing Structure rows: `26,666` (`99.26%`)
- neutral unconfirmed rows: `198`

The fixed controlled comparison evaluated `9,394` purged Train-only forward
rows:

| Feature set | Macro F1 | Gate floor | BUY precision | Passing folds |
| --- | ---: | ---: | ---: | ---: |
| Schema 4.0 Baseline | 0.3948 | 0.9131 | 0.4938 | 0 |
| All Swing Structure | 0.3924 | 0.9110 | 0.4998 | 0 |
| Structure Core | 0.3870 | 0.8951 | 0.4882 | 0 |

Baseline ranked first. No candidate improved the gate floor by `0.01`, no
candidate preserved or improved Macro F1 while passing a complete fold, and
all candidates passed `0/4` folds.

## Decision

Reject CR-005 as a canonical Brain/Feature change.
`promoted_feature_set=null` and
`nested_confirmation_authorized=false`. Do not run nested confirmation, do not
change Feature Schema 4.0, do not regenerate the Dataset, and do not deploy.
