# CR-013 Hybrid Rule and AI Entry Research

Version: 2.5.0

Date: 2026-07-19

Status: Minimum-reclaim contract implemented; fresh evidence required

Architecture Baseline: ABR-1.0

Related: CR-008, CR-009, CR-012, CR-014, Phase 7 closure, Phase 8A closure

Design catalog: `../architecture/HYBRID_PROFESSIONAL_TRADING_QUESTION_CATALOG.md`

## Approval

The project owner explicitly approved CR-013 on 2026-07-18. Approval covers
contract-first Strategy Setup research, a deterministic Setup Candidate engine,
a structure-aware Trade Plan validator, focused synthetic tests, isolated
synchronization/compilation tooling, and documentation.

Approval does not authorize Forward behavior changes, model deployment, broker
orders, live execution, automatic self-modification, or bypassing Risk.

On 2026-07-18 the project owner explicitly approved Stage B after CR-012
completed and failed its same-period strategy-quality benchmark. Stage B
approval is limited to an isolated objective M15/M5 adapter, new input/evidence
contracts, synthetic past-only tests, and compile tooling. It does not approve
Stage C Runtime or structure-aware paper execution integration.

On 2026-07-18 the project owner explicitly approved Stage C after the Stage B
compile and all eight focused runtime contracts passed. Approval is limited to
an isolated Strategy Tester provider, exact closed-bar M15/M5 source mapping,
Risk-gated structural paper execution, isolated audit files, focused tests, and
backtest evidence. Forward, Demo attachment, model deployment, broker orders,
live execution, and automatic promotion remain prohibited.

## Problem statement

The current Runtime can transform Brain output into BUY, SELL, or HOLD and can
safely simulate a fixed 500/1000-point paper trade. It does not yet represent a
professional trade setup with an explicit structural invalidation level and a
verified nearest structural target.

Consequently, current experiments answer mainly which direction to prefer. They
do not answer whether the current location provides a valid entry or whether the
available structural reward justifies the structural risk.

## Current design

The protected top-level path is:

`Market -> Brain -> AI Runtime -> Decision -> Risk -> Execution -> Trade Lifecycle`

Shadow Execution currently owns fixed Stop Loss and Take Profit distances. The
Simple Baseline in CR-012 intentionally preserves fixed 1:2 behavior so it can
act as an explainable benchmark.

## Approved Stage A change

Add an isolated Strategy Setup research package inside `core/ai/strategy/`.
Stage A introduces three distinct data contracts and two focused engines:

- `CHybridRuleSetupContext`: closed-bar confluence and structural price input;
- `CTradeSetupCandidate`: accepted directional setup evidence;
- `CStructureAwareTradePlan`: proposed Entry, structural Stop, structural Target,
  cost-adjusted risk/reward, and validation status;
- `CHybridRuleSetupEngine`: deterministic candidate acceptance;
- `CStructureAwareTradePlanner`: conservative geometry and minimum-RR validation.

The package is inside AI Runtime ownership. It is not a new top-level production
module and does not alter the ABR-1.0 top-level path.

## Approved Stage B change

Add a pure deterministic adapter inside `core/ai/strategy/` that converts
auditable closed-bar Brain/market evidence into the existing Stage A Setup
Context. It consumes:

- the existing M15 `CTrendResult` contract;
- the existing M5 `CConfirmedSwingStructureResult` research contract;
- the completed M5 trigger-bar OHLC and ATR;
- explicit M15/M5 bar-open, observation, Trend-known, and structure-known
  timestamps;
- point size, estimated cost points, and minimum Risk:Reward.

The adapter does not call `iHigh`, `iLow`, `CopyRates`, Dataset readers, Risk,
Execution, or broker APIs. A later Stage C source integration must supply these
inputs and prove Historical/Runtime parity separately.

### Frozen Stage B V1 rules

- timeframes are exactly M15 context and M5 setup;
- both source bars must close exactly at the declared observation time;
- M15 Trend must be valid and directionally agree with Trend Regime, Momentum,
  and Slope at the frozen 55/45 boundaries;
- the M5 POI is the latest confirmed swing-retest level;
- the trigger is a completed-bar sweep beyond the confirmed swing followed by
  a directional reclaim close;
- POI tolerance is `max(10 points, 0.10 * M5 ATR)`;
- minimum sweep penetration is `max(1 point, 0.02 * M5 ATR)`;
- Stop buffer is `max(0.10 * M5 ATR, estimated cost price)`;
- the nearest opposing confirmed swing is the only initial Target;
- the existing cost-adjusted Trade Planner enforces minimum 2R by default.

A technically valid observation may produce no actionable Setup. Invalid or
future-dated source timing is a contract failure; missing confluence is a normal
non-actionable result that Stage A rejects.

## Frozen Strategy Setup V1 contract

A candidate is accepted only when all of the following are explicit:

- completed-bar timing is confirmed;
- higher-timeframe Trend alignment is confirmed;
- a Point of Interest is confirmed;
- an entry trigger is confirmed;
- direction is BUY or SELL;
- Entry, structural Stop, and nearest structural Target geometry is valid;
- symbol, timeframe, closed-bar time, point size, estimated costs, and minimum
  Risk:Reward are valid.

Stage A does not define EMA, Order Block, swing, stochastic, or other detector
parameters. Those detectors must later provide objective past-only inputs to the
approved contract and require focused evidence before Runtime integration.

## Approved Stage C integration

Stage C adds one new inference-provider mode:

`OBJECTIVE_M15_M5_SETUP_TESTER_ONLY`

It is allowed only when `MQL_TESTER` is true and the canonical chart timeframe
is M15. The Runtime maps the last completed M15 observation and the exactly
aligned completed M5 trigger bar into Stage B. Confirmed M5 swing structure is
loaded through Brain ownership using only the trigger shift and older bars.

The accepted Stage A plan is converted into an Execution-owned price plan only
after the unchanged Risk evaluation returns explicit approval. Shadow Execution
may validate and apply the absolute structural Stop/Target but may not invent,
move, widen, or optimize them. It must reject direction mismatch, malformed
geometry, and cost-adjusted RR below the declared minimum at simulated entry.

Legacy, Directional, and Simple Baseline providers retain their existing fixed
Shadow SL/TP behavior. Objective artifacts use isolated file names and the
provider/model status remains permanently `NO_GO` in Stage C.

The approved Stage C code and focused tests were implemented in the workspace
on 2026-07-18. The complete 33/33 Python regression, PowerShell tool parsing,
and canonical no-broker include-closure audit passed. This is implementation
evidence only: MetaEditor compilation, focused chart execution, and a
same-period Strategy Tester report are still mandatory, and deployment remains
unauthorized.

The Stage C MetaEditor gate passed on 2026-07-19: 10/10 targets, 0 errors, and
0 warnings. Focused provider, closed-bar source, and structural paper-execution
chart tests remain pending; Strategy Tester quality comparison and every form
of deployment remain unauthorized until those gates pass.

All three focused Stage C XAUUSD M15 chart tests then passed. The evidence
confirms the Objective provider contract, past-only M15/M5 source timing, and
Risk-gated structural Shadow execution without broker mutation. Stage C now
proceeds to its registered same-period Strategy Tester safety benchmark;
Forward and deployment remain unauthorized regardless of benchmark results.

The same-period real-tick Strategy Tester benchmark completed on 2026-07-19
with 1,895 Decisions, 6 structural paper executions, 0 wins, 6 losses,
-3,272 cumulative points, and 3,272 maximum drawdown points. All operational
safety gates passed and broker state remained unchanged. Objective Setup V1 is
therefore rejected for promotion: Stage C proves the pipeline can safely carry
a structural plan, but does not prove that the current setup rules have a
trading edge.

The Objective audit narrows the next research problem to setup quality rather
than architecture. Only 12 of 1,895 observations formed valid plans; Risk
allowed the first 6 and correctly blocked the remaining 6 after the drawdown
limit. The accepted set was 9 SELL / 3 BUY with planned RR from about 2.12 to
6.12. No threshold, Stop buffer, Target, or Risk limit may be weakened from
this single interval. Stage D outcome analysis and setup-quality ranking remain
separately controlled and require approval before implementation.

## Stage D approval

The project owner explicitly approved Stage D on 2026-07-19. Approval covers a
separate Setup Outcome Schema 1.0.0, deterministic completed-M15 outcome
building, strict validation/readiness gates, Train-only temporal ranking, and
focused offline tests. It does not authorize a Feature Schema 4.0 change,
directional Label Schema 1.1.0 change, Runtime integration, Forward behavior,
Risk changes, broker mutation, or deployment.

Stage D uses only the twelve existing Feature Schema 4.0 values as model
inputs. Entry, Stop, Target, RR, MFE, MAE, close reason, and outcome remain
audit/label fields. The maximum outcome horizon is 64 completed M15 bars;
same-bar Stop/Target ambiguity and incomplete paths are excluded from training.
Training is blocked until at least 200 mature plans with adequate class coverage
are available.

Stage D offline infrastructure passed its focused tests and the complete 37/37
Python regression on 2026-07-19. The first real build joined the one-month
Objective evidence exactly and produced 12 plans: 10 Stop-first, one
Target-first, and one same-bar ambiguous row. Only 11 rows were trainable, so
the readiness gate refused splitting and model fitting. Expanded historical
Objective evidence is required; sample thresholds remain frozen.

A generation-model parity comparator now protects any attempt to use faster
`1 minute OHLC` history. Real-tick reference artifacts were preserved before
rerun. Only an exact same-month Feature/Setup/Plan match can authorize the
faster model for offline data generation; final quality evidence remains
real-tick only.

The 2026-07-19 same-month `1 minute OHLC` rerun failed that parity gate. All
1,895 Decision rows and Feature Schema 4.0 values matched and the same twelve
plan timestamps were found, but structural Stop, estimated cost, and planned-RR
fields produced 38 mismatches. Paper execution also changed from six trades to
five. The faster model is therefore rejected for Stage D generation. The gate
is not relaxed; expanded evidence must use `Every tick based on real ticks`.

The approved five-year real-tick generation then completed before the host
computer stopped. It covered 2021-07-01 through 2026-06-29 and wrote 116,688
Decision rows with all Backtest safety gates true and broker state unchanged.
The first Stage D build correctly stopped on a timestamp-contract defect in the
offline Builder: valid real-tick Decisions may be recorded after the exact M15
boundary while waiting for the first tick. All 6,070 delayed rows were between
one and 120 seconds late, none was early, and none exceeded the existing
freshness guard. The corrected Builder joins on `closed bar + 15 minutes` while
retaining the actual timestamp as a bounded validation field.

Source-quality review quarantined three plans whose observation and outcome
window touched MT5 dates with discarded or mismatched real ticks. The final
Dataset retained 329 plans, of which 327 were trainable. The chronological
Train partition contained 229 rows with 52 Target-first and 177 Stop-first
outcomes; Validation and Test remained sealed.

The Stage D four-fold Train-only ranker did not meet its stable gate. Its
selected bounded random forest produced 38.10% Target precision, 26.67% Target
recall, and 55.91% Macro F1 in aggregate, with only one of four folds passing.
No model artifact was emitted, Validation/Test were not opened, and deployment
remains unauthorized. Stage D closes as a controlled research `NO_GO`; Stage E
is blocked until a separately approved setup-quality improvement passes the
same Train-only stability contract.

CR-014 retains one bounded follow-up hypothesis from this rejection. A naive
opposite-direction counterfactual achieved a high Train win rate but remained
negative because its swapped structural payoff averaged only 0.206R. Future
Setup V2 research must therefore distinguish continuation from reversal and
build an independent structural plan; simple inversion remains rejected.

IMP-073 subsequently evaluated fixed, observation-time Setup geometry questions
against only the frozen Stage D Train and matching Setup Audit. A completed M5
reclaim of at least 0.10 ATR was the only finding whose Target-rate and
cost-aware expectancy lifts remained positive in all four purged folds. Its
aggregate Target-rate lift was +6.14 percentage points and expectancy lift was
+0.2303R. Plans below the threshold had a 4.00% Target rate and -0.8616R
expectancy in the evaluation windows.

This result permits a request for a controlled Setup-contract review only. It
does not authorize changing the Objective adapter, Runtime, Feature Schema,
Risk, Execution, Forward behavior, or deployment. All other tested geometry
thresholds remain rejected or inconclusive.

## Approved minimum-reclaim correction

The project owner explicitly approved the IMP-073 contract review on
2026-07-19. Objective Setup now requires completed directional reclaim distance
of at least `0.10 * M5 ATR` for both BUY and SELL triggers. A weaker reclaim is
recorded as a valid non-actionable observation and cannot reach Risk or
Execution.

This change does not alter Feature Schema 4.0, Label Schema 1.1.0, structural
Stop/Target geometry, the minimum 2R planner, Risk limits, or Execution. It
remains Strategy Tester research with every Forward/deployment lock intact.
Historical and Strategy Tester evidence produced under the earlier contract
cannot establish quality for this amendment; new real-tick evidence and the
same controlled evaluation gates are required.

The implementation gate passed on 2026-07-19: the complete 40/40 Python
regression and all 10 Objective Stage C MetaEditor compile targets completed
with zero errors and zero warnings. Focused chart behavior and newly generated
real-tick quality evidence remain required.

The focused Objective adapter chart gate subsequently passed every contract,
including exact-threshold BUY/SELL acceptance, sub-`0.10 ATR` reclaim
rejection, completed-bar timing, minimum structural RR, and preservation of
the Risk boundary. New real-tick evidence is now the only remaining validation
step for this amendment; deployment remains `NO_GO`.

The first amended one-month real-tick smoke run then passed every operational
safety gate. Plan count fell from 12 to 11 and removed exactly one prior
`STOP_FIRST` plan at `0.0980375 ATR`; the minimum retained reclaim was
`0.1012455 ATR`. Paper executions increased from six to eight only because the
removed loss altered the path-dependent Risk/drawdown sequence. All eight
executions lost and cumulative result was -3,439 points. This is a valid
contract smoke test but a quality `NO_GO`; a regenerated long-period Setup
Outcome comparison remains mandatory.

The amended five-year real-tick run subsequently completed with 116,688
Decisions and all operational safety gates true. Its 64 Risk-allowed paper
trades produced 10 wins, 54 losses, and -2,658 cumulative points. After frozen
source-quality exclusions, the Setup Outcome Dataset contained 260 trainable
plans. The chronological Train partition contained only 182 records, below the
unchanged 200-record gate, so ranking remained blocked and Validation/Test were
not used for selection.

Within the permitted Train description, Target rate improved from 22.71% to
25.27% and mean cost-aware return improved from -0.161R to -0.064R. The
threshold is directionally useful but insufficient: expectancy remains
negative and sample coverage is inadequate. CR-013 therefore remains a
quality `NO-GO`; no threshold, split ratio, sample gate, Risk limit, or
deployment lock is weakened.

## Structure-aware Risk:Reward policy

The planner never invents or stretches a Target. It uses the nearest verified
structural Target supplied by the setup context.

The conservative calculation is:

```text
effective risk points = gross structural risk points + estimated cost points
net reward points     = gross structural reward points - estimated cost points
planned RR            = net reward points / effective risk points
```

The default minimum is 2.0R. A valid 3.0R or larger structural opportunity keeps
its actual ratio; it is not shortened to fixed 2.0R. A nearest structural
obstacle below the minimum causes rejection.

## Protected boundaries

- Brain supplies market understanding only.
- Setup Candidate, AI features, labels, confidence, Risk result, and Execution
  result remain distinct concepts.
- The Stage A engines do not read Dataset files or train a model.
- The Stage A engines do not size positions or approve Risk.
- Risk remains the final permission gate.
- Execution remains the only owner of paper or broker mutation.
- No broker-capable include is allowed in the focused Stage A closure.
- Current Forward defaults, Feature Schema 4.0, Label Schema 1.1.0, and CR-012
  behavior remain unchanged.

## Expected benefits

- separates direction prediction from entry quality;
- makes invalidation and target assumptions auditable;
- supports adaptive structural RR without allowing arbitrary AI price levels;
- establishes a controlled foundation for later AI setup ranking;
- permits a fair comparison with the fixed 1:2 Simple Baseline.

## Risks

- ambiguous POI or trigger definitions can create hidden discretion;
- optimistic targets can exaggerate expected reward;
- adding many strategies simultaneously can create selection bias;
- future Runtime integration can accidentally mix setup quality with Risk
  approval unless the contracts remain separate.

Stage A mitigates these risks by accepting explicit synthetic inputs only,
using the nearest structural target, applying estimated costs conservatively,
and remaining disconnected from the canonical Runtime.

## Impact analysis

- Architecture: adds an internal AI Runtime research package; top-level flow is
  unchanged.
- Public contracts: adds Setup Context, Setup Candidate, and Trade Plan without
  changing an existing interface.
- Runtime: no Stage A integration or default behavior change.
- Brain: unchanged.
- Feature/Label/Dataset contracts: unchanged.
- Risk/Execution/Trade Lifecycle: unchanged.
- Tests: one focused synthetic contract test is required.
- Deployment: remains NO-GO.

## Alternatives considered

1. Put Stop/Target directly in AI Decision. Rejected because it mixes setup
   planning with model output before structural validation.
2. Let Shadow Execution calculate adaptive targets. Rejected because Execution
   must not create strategy logic.
3. Keep fixed 1:2 only. Retained as the CR-012 baseline, but insufficient for
   testing location-aware structural opportunities.

## Validation gates

Stage A is complete only when:

- focused BUY and SELL structural plans pass;
- valid structural RR above 2.0 is preserved rather than truncated;
- missing confluence, invalid geometry, open-bar timing, and sub-minimum RR are
  rejected;
- include direction and broker-mutation scans pass;
- MetaEditor compiles the focused test with 0 errors and 0 warnings.

MetaEditor synchronization and compilation must wait until the active Dataset
export has completed and MT5/MetaEditor are closed.

Stage B is complete only when:

- objective synthetic BUY and SELL M15/M5 setup plans pass;
- sweep/reclaim evidence is positive and auditable;
- valid non-trigger observations remain non-actionable;
- forming-bar and future-known timing is rejected;
- the existing planner rejects insufficient structural RR;
- the focused include closure contains no market-loading or broker-mutation
  token;
- all existing Python regression tests remain green;
- MetaEditor compiles the focused Stage B test with 0 errors and 0 warnings.

The Stage B focused MetaEditor compile gate passed on 2026-07-18: 1/1 target,
0 errors, and 0 warnings. Focused chart execution then passed all eight
objective M15/M5 contracts on XAUUSD M15. Stage B is closed; Stage C Runtime,
Strategy Tester provider, and paper-execution integration remain unapproved.

## Rollback plan

Remove the CR-013 package, focused test, and isolated tools. No existing Runtime,
Brain, AI provider, Decision, Risk, Execution, Dataset, or Forward configuration
needs restoration because Stage A does not modify them.

## Later controlled stages

- Stage B: objective closed-bar multi-timeframe context adapter (approved);
- Stage C: isolated Strategy Tester provider and structure-aware paper execution
  (approved; implementation/evidence in progress);
- Stage D: offline Setup Outcome Dataset and AI setup-quality ranking
  (complete; five-year Train-only stability gate NO-GO);
- Stage E: Shadow/Demo evidence after complete Backtest gates pass (blocked);

Each later stage requires its documented evidence gate before it can affect the
next boundary.

The question, data, calculation, ownership, and future-leakage design is recorded
in `HYBRID_PROFESSIONAL_TRADING_QUESTION_CATALOG.md`. The catalog identifies
Historical/Runtime Session timestamp parity as Gate B0 and blocks acceptance of
a future training Dataset until that parity is corrected and retested.
