# CR-014 Dual-Direction Structural Setup Research

Version: 1.3.0

Date: 2026-07-19

Status: Stage 1B frozen; residual Train evidence repeats Session hypotheses

Architecture Baseline: ABR-1.0

Related: CR-013, ADR-006, IMP-068, IMP-069, IMP-070, IMP-071, IMP-072

## Approval boundary

The project owner approved retaining the opposite-direction observation as a
future improvement hypothesis on 2026-07-19. Approval covers this design record
and isolated Train-only analysis. It does not authorize changing the canonical
Runtime, Feature Schema 4.0, Risk, Execution, Forward behavior, broker orders,
Validation/Test access, model deployment, or live trading.

## Evidence that motivated the hypothesis

Objective Setup V1 failed its five-year Stage D stability gate. A deliberately
naive Train-only counterfactual reversed direction and swapped each original
Stop and Target. It produced 177 apparent wins and 52 losses, or 77.29% wins,
but the reversed winning payoff averaged only 0.206R. Gross expectancy remained
negative at -0.0678R per trade, total return was -15.52R, and Profit Factor was
0.702.

The counterfactual rejects simple signal inversion. It nevertheless suggests a
useful question: does an observation support continuation, reversal, or neither
when each direction receives its own independently valid structural plan?

## Setup V2 research question

For the same completed M15 observation, evaluate two independent hypotheses:

1. `CONTINUATION`: M15 Trend context remains directionally coherent and the M5
   completed-bar trigger supports continuation from a valid POI.
2. `REVERSAL`: past-only evidence shows Trend deterioration or exhaustion and
   M5 completed structure confirms a liquidity sweep, opposite reclaim, and a
   defensible reversal location.

Failure of the continuation hypothesis is not evidence for reversal. Either,
both, or neither hypothesis may be rejected. If both are valid, the observation
is ambiguous until a separately approved deterministic tie-break contract
exists.

## Independent Trade Plan requirement

A reversal may not reuse the continuation plan by swapping levels. It must
recompute all of the following from levels known at observation time:

- reversal POI and invalidation evidence;
- Entry after a completed trigger;
- structural Stop beyond the reversal invalidation level plus approved costs;
- nearest confirmed Target in the reversal direction;
- cost-adjusted Risk:Reward using the existing conservative formula.

The default minimum remains 2.0R. Missing structure, a nearer obstacle, stale
evidence, or sub-minimum RR produces `NO_SETUP`.

## Candidate evidence under investigation

All measurements must remain inside the four canonical Brain groups:

- Trend: regime direction, momentum deterioration, slope deterioration, and
  confirmed past-only swing transition;
- Volatility: regime and change around the trigger;
- Liquidity: range position, completed sweep direction, penetration, and
  reclaim evidence;
- Session: identity and progress.

The current default CHOCH result is forbidden evidence. A reversal contract may
use only reviewed confirmed swings whose `known_at` time is not later than the
observation. Adding a model input requires a separate Feature Schema review.

## Leakage and selection controls

- use completed M15 and M5 bars only;
- never infer reversal because future price later moved in the opposite direction;
- keep candidate type, features, outcome, Risk, and Execution as separate data;
- conduct hypothesis discovery on Train only;
- do not open the existing sealed Validation or Test partitions;
- compare against Objective V1 and the accept-all Setup baseline;
- require all four purged Train-only folds to pass before requesting an
  untouched-period evaluation;
- retain permanent `NO_GO` until a later explicit promotion decision.

## Proposed controlled stages

1. Train-only diagnostic: identify stable continuation/reversal associations
   without adding Runtime code.
2. Synthetic contract: prove independent BUY/SELL geometry, abstention, timing,
   ambiguity, and minimum-RR rejection.
3. Historical adapter: export both hypotheses with exact closed-bar parity.
4. Purged Train-only comparison: require stable improvement over Setup V1.
5. Only after 4/4 stability, request approval for a new untouched period.

No Stage is automatically promoted. Runtime and deployment remain blocked.

## Stage 1 result

IMP-071 executed the registered fixed-question diagnostic against only the
229-row Stage D Train partition. None of the preregistered directional Trend or
Liquidity hypotheses produced sufficient support and the expected lift sign in
all four purged folds. Stage 2 therefore remains unauthorized.

Two exploratory associations were temporally stable: early Session progress
had a +12.94 percentage-point Target-rate lift, while late Session progress had
a -14.66 percentage-point lift. These were not preregistered directional
effects, so they are retained as new confirmation hypotheses only. They may not
be converted into Runtime filters using the same evidence. Confirmation
requires a new untouched later real-tick period; the existing Validation and
Test partitions remain sealed.

## Stage 1B frozen confirmation

On 2026-07-19, before inspecting any evidence after the existing source cutoff,
the project froze two later-period claims:

- the first Session third is expected to retain a positive Target-rate lift;
- the final Session third is expected to retain a negative Target-rate lift.

IMP-072 accepts only a separately named confirmation Dataset whose every
observation is later than `2026.06.26 21:30`. It requires at least 80 mature
plans and the expected sign in all four chronological blocks. Existing Train,
Validation, Test, and complete Dataset files are forbidden.

Passing confirmation would only allow a request for Stage 2 review. It would
not prove reversal geometry, modify Runtime, authorize deployment, or permit
broker trading. No qualifying fresh Dataset exists at registration time.

## Post-reclaim residual evidence

IMP-075 repeated fixed exploratory questions against the 182-row Train subset
created by the approved `0.10 ATR` reclaim contract. Early Session again had a
positive association (40.91% Target rate and +0.623R mean), while late Session
again had a negative association (4.55% Target rate and -0.845R mean). Both
effects kept their expected signs across three chronological descriptive
blocks and passed fixed support/effect thresholds.

This is not Stage 1B confirmation because it reuses the same historical source
period. It neither opens Validation/Test nor authorizes a Session filter,
Stage 2, Runtime integration, or deployment. Only the already frozen
post-2026.06.26 untouched-period contract may confirm these hypotheses.

## Success and rejection

Success requires better cost-aware Setup precision without destroying coverage,
positive expectancy under independently valid structural RR, and stable purged
folds. A high win rate alone is insufficient. The hypothesis is rejected if it
depends on swapped levels, future-confirmed structure, sub-minimum RR, or a
single favorable period.
