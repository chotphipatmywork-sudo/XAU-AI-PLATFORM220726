# XAU AI PLATFORM

# CHANGELOG

## 2026-07-19 — Objective Setup Stage C compile gate

- Synchronized the approved CR-013 Stage C implementation to MT5 and compiled
  all ten focused, regression, and canonical targets with 0 errors and
  0 warnings; workspace logs independently confirm 10/10 passes.
- Kept Objective Forward use, model deployment, broker orders, and live
  execution prohibited. Three focused XAUUSD M15 runtime tests remain the next
  gate before a same-period Strategy Tester benchmark.
- Passed all three focused XAUUSD M15 Stage C runtime tests: Objective provider
  behavior, past-only M15/M5 timing, structural RR/price preservation, Risk
  boundary, lifecycle protections, and unchanged broker state all validated.
  The same-period Objective Strategy Tester benchmark is now authorized.
- Completed the same-period Objective M15/M5 real-tick benchmark: all safety,
  audit, provider-identity, and unchanged-broker-state gates passed, but six of
  six executed structural plans lost for -3,272 points. Closed Stage C as an
  operational success and rejected Objective Setup V1 for strategy promotion;
  Forward and deployment remain NO-GO.
- Approved CR-013 Stage D and froze a separate Setup Outcome Schema 1.0.0:
  64 completed M15 bars, Target/Stop/Timeout outcomes, ambiguous/unmatured
  quarantine, exact Feature Schema 4.0 inputs only, time-based leakage purge,
  strict sample readiness, and permanent Runtime/deployment isolation.
- Implemented and validated the Stage D offline builder, temporal splitter,
  readiness-gated Train-only ranker, focused tests, and operator tooling. The
  complete Python regression passed 37/37 after generation-parity validation.
  Current one-month evidence yielded
  only 11 trainable plans (1 Target / 10 Stop), so splitting and training were
  correctly refused pending expanded historical Objective evidence.

## 2026-07-18 — Historical and Runtime Session parity

- Corrected Historical Brain Replay to evaluate Session at the completed-bar
  observation timestamp, matching Runtime Brain instead of using bar open.
- Added one shared observation-time resolver, a focused boundary/progress test,
  and SHA-256 verified five-target MetaEditor compile tooling.
- Quarantined the pre-correction 26,900-row Dataset from model training while
  retaining it as full-label-horizon and structural-validation evidence.
- Completed the same-period Simple Baseline Strategy Tester benchmark: all
  operational safety checks passed, but Profit Factor 0.3329, expectancy
  -286.57 points, and 1/6 wins/losses rejected Forward promotion.
- Approved CR-013 Stage B for an isolated past-only M15/M5 confirmed-swing
  retest and sweep/reclaim adapter into the existing structure-aware Trade Plan.
- Implemented the Stage B input/config/evidence contracts, deterministic
  adapter, focused synthetic test, and verified sync/compile tooling without
  connecting Runtime, Risk, Execution, Forward, or broker mutation.
- Corrected MQL5 reserved-identifier and include-guard length constraints, then
  passed the Stage B focused MetaEditor compile: 1/1 target, 0 errors, 0 warnings.
- Closed CR-013 Stage B after the XAUUSD M15 focused runtime test passed all
  eight objective setup, timing, structural RR, and Risk-boundary contracts;
  Stage C integration and every Forward/broker path remain unapproved.
- Approved CR-013 Stage C for an isolated Strategy Tester-only Objective M15/M5
  provider, exact past-only source mapping, and Risk-gated structural paper
  execution; Forward, model deployment, and broker mutation remain prohibited.
- Implemented CR-013 Stage C in the workspace with an isolated Objective
  provider, Brain-owned closed M15/M5 source, Execution-owned absolute price
  plan, post-Risk structural paper execution, focused tests, and verified sync
  tooling. Local 33/33 Python regression and no-broker audits passed;
  MetaEditor and focused runtime validation remain pending.

## 2026-07-17 — Simple Baseline Strategy Tester benchmark

- Approved CR-012 and added a deterministic Trend-alignment provider using the
  existing closed-bar Feature Schema 4.0 request.
- Kept Legacy as the Forward default and blocked the Simple Baseline outside
  Strategy Tester with permanent deployment and live-execution NO-GO locks.
- Added isolated Backtest artifacts, a focused BUY/HOLD/SELL and fixed 1:2
  Shadow Risk:Reward contract test, and updated sync/compile tooling.

## 2026-07-17 — Full label-horizon correctness

- Corrected `CLabelGenerator` to reject historical rows without all sixteen
  approved future M15 bars instead of silently shortening the target horizon.
- Strengthened the focused Label test and added SHA-256 verified sync plus
  three-target MetaEditor compile tooling.
- Kept Label Schema 1.1.0 configuration unchanged; corrected Dataset
  regeneration and all safety gates are required before new model evidence.

## 2026-07-17 — Completed-tick microstructure research

- Approved CR-011 as bounded research without changing canonical Feature
  Schema 4.0 or the Shadow Runtime.
- Added a completed-M15 tick microstructure engine, auxiliary historical
  exporter, synthetic timing/encoding test, and SHA-256 verified compile tool.
- Added a strict Train-only controlled diagnostic with fixed purged folds and
  predeclared promotion rules; Validation, Test, deployment, and broker
  mutation remain locked.
- Exported 26,864 auxiliary rows at 99.9814% valid coverage and completed the
  controlled comparison. Schema 4.0 Baseline ranked first; every tick candidate
  reduced Macro F1 and gate floor, so CR-011 was rejected and nested
  confirmation remained locked.

## 2026-07-17 — Strategy Tester inference experiment

- Approved CR-010 for a Strategy Tester-only Directional research provider.
- Kept Legacy as the Forward default and added initialization rejection when
  Directional is selected outside Strategy Tester.
- Added isolated Directional Report, Decision, Audit, State, and Telemetry
  artifacts with provider-aware NO-GO evidence.
- Added focused provider selection, directional mapping, identity, and lock
  validation.

## 2026-07-17 — Canonical Shadow inference evidence

- Approved CR-009 to expose Feature Schema 4.0 evidence at the canonical
  Shadow inference boundary without authorizing a model or live execution.
- Added a twelve-feature inference request, explicit provider interface, and
  locked development-heuristic compatibility provider.
- Versioned Forward and Strategy Tester Decision evidence as V4 so historical
  four-score CSV files remain immutable and schema-consistent.
- Added a focused provider parity, identity, Schema 4.0, and deployment-lock
  test.

---

## 2026-07-16 — Feature Schema 4.0 training gate review

- Validated the recovered Feature Schema 4.0 dataset and purged Train/Validation/Test partitions.
- Added the Train-only nested Schema 4.0 Session Progress ablation and focused test.
- Reevaluated nested purged model selection; the model failed the deployment gate and Validation/Test remained unread.
- Added the Model Training and Deployment Gate Review with a formal Shadow Deployment NO-GO decision.
- Synchronized the AI Model Training Contract with the implemented 12-field Feature Schema 4.0 contract.
- Proposed CR-002 and added a leakage-safe closed-H1 research exporter plus strict Train-only controlled diagnostic.
- Completed closed-H1 full/group/nested research; H1 Trend and Volatility failed temporal confirmation, so CR-002 was rejected without a schema or deployment change.
- Snapshotted the complete 2026-07-16 Schema 4.0 evidence set and proposed a 40,000-calendar-bar expanded development-history cycle instead of further tuning inspected folds.
- Completed the expanded-history cycle with 26,864 Dataset records and 18,788 purged Train records; all Dataset safety gates passed.
- Reran the registered Train-only nested method on the wider history; no Outer fold passed, Validation/Test remained unread, and Shadow Deployment remained NO-GO.
- Updated the Temporal Regime Diagnostic to emit active Training, Feature, and Label contract versions instead of stale Schema 3.0 metadata.
- Confirmed on the expanded Train history that Trend remains the dominant temporal shift and that Fold 2 calibration caused a HOLD collapse; the raw counterfactual still failed the deployment gate.
- Updated the History Strategy Diagnostic to emit the active contract versions before the expanded-history comparison.
- Compared expanding, rolling, and recency histories on expanded Train data; rolling 1,000 ranked first but every strategy passed 0/4 complete gates.
- Updated the Feature-Label Stability Diagnostic for active Schema 4.0 metadata and Session Progress coverage.
- Expanded stability evidence found Session relationship drift, Trend Regime sign reversal, and consistent but insufficient Session Progress directionality.
- Updated Feature Sufficiency and Confidence Coverage diagnostics to emit active Training/Feature/Label contract metadata before final phase evidence.
- Completed final expanded Feature Sufficiency and Confidence Coverage evidence; neither representation nor thresholding reached a stable deployment region.
- Added the Phase 7 closure report and evidence manifest. The training workflow is complete, while Shadow and live deployment remain formally denied.
- Registered CR-003 and IMP-054 for a bounded Train-only Liquidity temporal-context experiment; Runtime, canonical Schema, Validation/Test, and deployment remain unchanged.
- Added the CR-003 controlled Liquidity temporal diagnostic and focused leakage/promotion-boundary test.
- Rejected CR-003 after Baseline outperformed all Liquidity temporal candidates; nested confirmation was correctly not authorized.
- Registered CR-004 and IMP-055 for a bounded Train-only temporal window of canonical Brain feature rows.
- Added the CR-004 controlled temporal Brain-window diagnostic and focused tensor/leakage/promotion test.
- Rejected CR-004: temporal lags improved Macro F1 slightly but failed the predeclared gate-floor and passing-fold promotion requirements.
- Added CR-005/IMP-056 after source audit confirmed that Structure/BOS are slope-derived and CHOCH is still default; research remains isolated from Runtime.
- Implemented the confirmed-swing research engine, Dataset-keyed exporter, synthetic/timing test EA, and verified sync tool without changing Runtime behavior.
- Added the strict Train-only Swing Structure join/comparison diagnostic with predeclared promotion rules and explicit neutral coverage handling; workspace MetaEditor compile passed with 0 errors and 0 warnings.
- Registered conditional nested Swing Structure confirmation before controlled evidence; it refuses to run without a valid promoted feature set and never authorizes deployment.
- Rejected CR-005 after exact 26,864-row export validation and controlled Train-only evidence showed Baseline outperforming both Swing Structure candidates; nested confirmation, schema change, and deployment remained unauthorized.
- Registered CR-006/IMP-057 before evidence to test bounded past-only 1/4/16-bar price displacement, completed-candle impulse, and prior-range context under the existing Train-only gate.
- Implemented the CR-006 Dataset-keyed research exporter, synthetic encoding/timing test EA, and verified MT5 sync tool without changing Runtime behavior.
- Added the strict CR-006 Train-only controlled diagnostic and focused join/coverage/promotion-boundary test.
- Registered conditional CR-006 nested confirmation before evidence; it refuses to run without controlled promotion and cannot authorize deployment.
- Compiled the CR-006 research exporter in MetaEditor with 0 errors and 0 warnings; the auxiliary MT5 export remains the next evidence step.
- Rejected CR-006 after exact 26,864-row export validation: Price Action improved controlled metrics slightly but missed the 0.01 gate-floor promotion threshold and passed 0/4 folds.
- Registered CR-007/IMP-058 before evidence to test bounded past-only 16-bar path efficiency, persistence, travel, and range expansion under the existing Train-only gate.
- Implemented the CR-007 research result, engine, Dataset-keyed exporter, synthetic/timing test EA, and MT5 sync tool without changing Runtime behavior.
- Added the strict CR-007 Train-only controlled comparison and conditional nested confirmation; both focused tests and the complete 29-test Python regression passed.
- Verified SHA-256 equality for all four CR-007 MQL5 files between the workspace and the MT5 project copy; MetaEditor compile and auxiliary export remain pending.
- Rejected CR-007 after an exact 26,864-row Price Path export: Baseline ranked first, every candidate reduced Macro F1 and gate floor, and all candidates passed 0/4 folds; Nested, schema change, Validation/Test use, and deployment remained unauthorized.
- Approved CR-008 and ADR-005 for phased Shadow Trading integration with an explicit Risk approval boundary, safe-default execution mode, paper lifecycle, audit logging, and a hard live-order lock.
- Implemented the Phase 8A Shadow safety foundation, closed-bar Brain observation, explicit AI-to-Decision adapter, Decision-aware Risk gate, paper SL/TP/time lifecycle, loss/drawdown/stale-market controls, emergency stop, audit CSV, telemetry heartbeat, focused tests, and verified sync tooling.
- Added one-row-per-bar Shadow decision evidence, an offline operational readiness auditor with a focused safety test, and a beginner-oriented Shadow Trading runbook; neither tool can authorize deployment.
- Added an atomic closed-bar checkpoint, graceful paper-position closure on emergency/shutdown, and a reusable canonical include-closure audit proving the Shadow entry path contains no broker-capable file or mutation token.
- Added a focused Shadow Risk Gate test covering safe-default mode, live lock, explicit approval, active exposure, stale market, daily loss, drawdown, and emergency stop; corrected the Risk approval result initializer before Runtime integration.
- Completed the Shadow synchronization manifest and added an automated four-target MetaEditor compile runner that rejects every error or warning.
- Extended closed-bar decision evidence with OHLC and ATR and added a forward-only matured Shadow evaluator using the approved 16-bar, 1.5 ATR triple barrier; the evaluator cannot authorize Shadow or live deployment.
- Added paper-position state persistence and abnormal-restart recovery without broker reconciliation or broker mutation.
- Synchronized all Phase 8A files to MT5 with matching SHA-256 hashes and compiled three focused tests plus the canonical EA with 0 errors and 0 warnings; all four `.ex5` artifacts were verified.
- Executed the first Phase 8A focused runtime test on XAUUSD M15; Trend, Liquidity, Session timing, and the complete closed-bar Brain context all passed.
- Executed the Shadow Risk Gate runtime test; safe-default/live lock, explicit approval, exposure, staleness, daily loss, drawdown, and emergency-stop checks all passed.
- Executed the Shadow Execution Safety runtime test; rejection, synthetic entry, duplicate protection, restart recovery, paper lifecycle, emergency stop, and unchanged broker order/position counts all passed.

## Version 0.1.0
Status : In Development

### Foundation
- Initial Project Architecture
- Folder Structure
- Project Constitution
- Roadmap
- Decision Log

### Brain Layer
- Trend Package Foundation
- Trend Analyzer
- Trend Engines
- Trend Models

### Indicator Layer
- IndicatorContext
- IndicatorCache
- EMAProvider
- ATRProvider
- ProviderManager

### Market Layer
- Market Layer Initialized
