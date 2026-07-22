# Hybrid Professional Trading Question Catalog

Version: 1.1.0

Date: 2026-07-18

Status: CR-013 Stage D NO-GO recorded; CR-014 Setup V2 hypothesis registered

Architecture Baseline: ABR-1.0

Related: CR-013, CR-014, ADR-006, IMP-066, Feature Schema 4.0, Label Schema 1.1.0

## Purpose

Define the minimum questions a professional Hybrid trading system must answer,
the data required to answer each question, deterministic calculations, the
owning module, and controls that prevent future-data leakage.

This catalog translates human chart concepts into numerical contracts. Named
tools such as Fibonacci, EMA, ATR, support/resistance, or liquidity sweep are
measurements that may answer a question; they are not decision authorities.

## Protected architecture

The top-level path remains:

`Market -> Brain -> AI Runtime -> Decision -> Risk -> Execution -> Trade Lifecycle`

Internal CR-013 research may later use:

`Brain context -> Setup questions -> AI quality evaluation -> Trade Plan proposal`

- Brain owns market understanding.
- Strategy Setup inside AI Runtime owns candidate acceptance.
- Trade Planning owns proposed Entry, structural Stop, and structural Target.
- Risk owns final permission and position-risk constraints.
- Execution owns paper or broker mutation.
- Learning is offline and cannot modify a live model or bypass Risk.

## Design principles

1. One question has one owner and one explicit output contract.
2. Prefer continuous measurements over named levels and indicator votes.
3. Every price input exposes its source timeframe and source close time.
4. Feature, Setup, Trade Plan, Confidence, Risk, and Result remain distinct.
5. A missing answer produces `NO_SETUP` or `NO_TRADE`, never a guessed value.
6. AI ranks valid candidates; it does not invent arbitrary Stop or Target prices.
7. A new measurement is admitted only when it adds stable unseen-period value.

## Decision-time contract

For a decision made after a completed base bar:

```text
observation_time = base_bar_open_time + PeriodSeconds(base_timeframe)
```

Only information satisfying this rule is allowed:

```text
source_bar_open_time + PeriodSeconds(source_timeframe) <= observation_time
```

Mandatory controls:

- never use shift `0` for a price-derived decision;
- on another timeframe, select the latest bar whose close is not later than the
  observation time;
- a pivot with `right_bars = R` is available only after all R confirmation bars
  have closed;
- a zone, swing, and target records `known_at_time`;
- Dataset features stop at observation time; future bars belong only to the
  separate offline labeling path;
- Historical Replay and Runtime must produce the same values for the same
  `(symbol, timeframe, observation_time)` key.

## Current coverage and gaps

Feature Schema 4.0 already provides:

- Trend: regime, momentum, slope;
- Volatility: regime, change;
- Liquidity: activity, range position, sweep direction;
- Session: Asia, London, New York, progress.

Open gaps:

- canonical Trend structure infers HH/HL or LH/LL from slope, not confirmed
  swing history;
- canonical BOS is derived from that simplified structure;
- canonical CHOCH returns its default result and must not be used as evidence;
- confirmed past-only swing structure remains a research engine;
- there is no canonical POI lifecycle or lower-timeframe entry trigger;
- Shadow Execution still owns fixed-distance SL/TP;
- Setup Outcome learning does not yet exist;
- Historical Session Replay currently uses bar-open time while Runtime uses
  completed-bar time. This violates Historical/Runtime parity for Session
  identity and progress and must be corrected before a future training Dataset
  is accepted.

## Question registry

| ID | Question | Owner | Output | MVP |
| --- | --- | --- | --- | --- |
| D-01 | Is all information complete, synchronized, and known now? | Data/Runtime | observation validity | Required |
| M-01 | What is the primary market direction? | Brain/Trend | signed direction and confidence | Required |
| M-02 | Is the market trending or ranging? | Brain/Trend | trend efficiency/regime | Required |
| M-03 | What is the volatility state and change? | Brain/Volatility | normalized regime/change | Required |
| M-04 | Where are confirmed structure/liquidity levels? | Brain/Liquidity | levels and ATR distances | Required |
| M-05 | Which Session phase is active? | Brain/Session | identity and progress | Required |
| S-01 | Is price at a favorable structural location? | AI Runtime/Setup | location/retracement | Required |
| S-02 | Is the Point of Interest valid and unconsumed? | AI Runtime/Setup | POI validity/freshness | Required |
| S-03 | Has a completed-bar entry event occurred? | AI Runtime/Setup | trigger direction/strength | Required |
| S-04 | Is the candidate too late or stale? | AI Runtime/Setup | candidate freshness | Required |
| S-05 | Does evidence support continuation, reversal, or abstention? | AI Runtime/Setup | hypothesis type/validity | Later |
| P-01 | At what price is the idea invalid? | AI Runtime/Trade Plan | structural Stop | Required |
| P-02 | What is the nearest reachable Target? | AI Runtime/Trade Plan | conservative Target | Required |
| P-03 | Is reward worth risk after costs? | AI Runtime/Trade Plan | cost-adjusted RR | Required |
| E-01 | Can current operating conditions support a trade? | Market/Risk | execution feasibility | Required |
| A-01 | How strong and uncertain is the valid Setup? | AI Runtime | probabilities/abstention | Later |
| R-01 | Is account Risk allowed and at what maximum size? | Risk/Money | approval/bounded size | Required |
| L-01 | What happened and which assumption failed? | Offline Learning | matured outcome | Later |

## Detailed contracts

### D-01 — Information completeness

Data: symbol, timeframes, every source-bar open/close time, required lookback,
latest tick time, Bid, Ask, point, and tick size.

```text
source_close_time <= observation_time
lookback_available >= required_lookback
market_age_seconds = current_time - latest_tick_time
```

Reject forming, missing, future-dated, stale, or incorrectly mapped sources.
Historical and Runtime parity tests compare the complete output vector for the
same observation key.

### M-01 — Primary direction

Data: last two confirmed swing highs/lows, closed-bar EMA or regression values,
and ATR at observation time.

```text
bullish_structure = latest_high > previous_high
                    and latest_low > previous_low
bearish_structure = latest_high < previous_high
                    and latest_low < previous_low
normalized_slope  = (ema_now - ema_n_bars_ago) / (n * ATR_now)
```

Output signed direction in `[-1,1]`, component agreement, and each swing's
confirmation time. Do not infer HH/HL directly from slope. A pivot is unavailable
until its configured right-side confirmation bars close.

### M-02 — Trend or range

Data: closed prices over a fixed past window, ATR momentum, and confirmed
structure direction.

```text
efficiency_ratio = abs(close_now - close_n)
                   / sum(abs(close_i - close_i_minus_1))
momentum_atr     = (close_now - close_n) / (ATR_now * sqrt(n))
```

Keep direction and efficiency separate. The window ends at the completed
observation bar.

### M-03 — Volatility state

Data: ATR(14), the preceding ATR reference window, and current closed range.

```text
atr_regime = ATR_now / median(ATR_previous_1_to_N)
atr_change = ATR_now / ATR_previous_1 - 1
range_atr  = (high_now - low_now) / ATR_now
```

Normalize from past values only, never from future Dataset records.

### M-04 — Structure and liquidity map

Data: confirmed pivot highs/lows, preceding OHLC, ATR, point, and tick volume
when available.

```text
level_tolerance = max(configured_points * point,
                      configured_atr_fraction * ATR_now)
distance_atr    = abs(level_price - close_now) / ATR_now
```

Maintain nearest confirmed levels above/below, equal-level clusters, touch count,
`known_at_time`, and invalidation time. Never backfill a later-confirmed pivot
into earlier rows.

### M-05 — Session phase

Data: completed-bar observation time, documented platform/UTC conversion, and
configured Session boundaries.

```text
session_progress = 100 * elapsed_session_minutes / session_length_minutes
```

Historical and Runtime paths use the same completed-bar timestamp. Future market
hours must version time offset and daylight-saving rules.

### S-01 — Structural location

Data: direction, confirmed impulse anchors, completed close, nearest POI, ATR.

```text
buy_retracement  = (impulse_high - close_now)
                   / (impulse_high - impulse_low)
sell_retracement = (close_now - impulse_low)
                   / (impulse_high - impulse_low)
poi_distance_atr = distance(close_now, poi_zone) / ATR_now
```

This captures the information inside Fibonacci as continuous depth. Named bands
may be logged for explanation, but both anchors must have been confirmed before
observation.

### S-02 — POI validity

Recommended first POI: confirmed swing-retest zone. Order Block and FVG remain
separate later hypotheses because their definitions are more ambiguous.

```text
zone_buffer = max(configured_points * point,
                  configured_atr_fraction * ATR_at_zone_creation)
poi_valid   = known_at_time <= observation_time
              and not closed_through_invalidation
              and touch_count <= maximum_touches
```

Never redraw a zone after seeing the outcome.

### S-03 — Completed-bar entry event

Recommended first trigger: sweep and reclaim.

BUY:

```text
low_now   < reference_low - tolerance
close_now > reference_low
close_now > open_now
```

SELL is symmetric above a confirmed reference high. Output type, direction,
penetration in ATR, reclaim distance, and trigger close time. Intrabar signals
that can disappear before close are forbidden.

### S-04 — Candidate freshness

Data: first POI touch, trigger close, current entry quote, ATR at trigger.

```text
bars_since_touch = closed_trigger_bars(first_touch, trigger_time)
entry_drift_atr  = abs(current_entry - trigger_close) / ATR_trigger
```

Reject above frozen maximum bars or drift. Do not retune after inspecting the
comparison period.

### S-05 - Continuation or reversal hypothesis

Data: completed M15 Trend components, confirmed past-only M15/M5 swings, M5
sweep/reclaim evidence, Volatility state, Liquidity state, and Session phase.

Continuation and reversal are independent hypotheses. Rejection of one does
not approve the other. A reversal requires its own confirmed POI, completed-bar
trigger, structural invalidation, nearest Target, and cost-adjusted RR. Swapping
the continuation Stop and Target is forbidden because it reverses the payoff
geometry and can create a high-win-rate strategy with negative expectancy.

Current Train-only evidence for naive inversion was 77.29% wins but only 0.206R
average reward per win, -0.0678R expectancy, and Profit Factor 0.702. This is a
rejected baseline, not a trading signal. CR-014 controls any later Setup V2
research, and the current default CHOCH result cannot support it.

### P-01 — Structural invalidation

Data: direction, POI invalidation or sweep extreme, ATR, spread, slippage.

```text
protective_buffer = max(configured_atr_fraction * ATR_trigger,
                        spread_price + estimated_slippage_price)
BUY stop  = structural_low  - protective_buffer
SELL stop = structural_high + protective_buffer
```

AI cannot widen this Stop.

### P-02 — Nearest reachable Target

Use the nearest confirmed opposing swing/liquidity level known at observation
time. Fibonacci extension is secondary and cannot ignore a nearer obstacle. If
no defensible target exists, reject the plan. Never select the level that later
price happened to reach.

### P-03 — Cost-adjusted RR

Data: entry, Stop, Target, point, spread, simulated slippage, commission.

```text
gross_risk_points   = abs(entry - stop) / point
gross_reward_points = abs(target - entry) / point
effective_risk      = gross_risk_points + estimated_cost_points
net_reward          = gross_reward_points - estimated_cost_points
cost_adjusted_RR    = net_reward / effective_risk
```

Keep actual structural RR above the minimum. Do not force 3R down to 2R and do
not skip a nearer obstacle to manufacture higher RR.

### E-01 — Operating conditions

Data: spread, latest tick time, symbol trade state, ATR, estimated costs, and
scheduled events only when historically reproducible.

```text
spread_atr_ratio = spread_price / ATR_trigger
market_age       = current_time - latest_tick_time
```

Risk rejects stale data, excessive spread, unavailable trading state, or an
approved event blackout. Backtests may use news only from an archived calendar
snapshot that was available at the historical decision time.

### A-01 — AI quality and uncertainty

Stage A/B is deterministic. A later evaluator may start only after the rule-only
benchmark has sufficient Setup coverage.

Required output: class probabilities, maximum probability, top-two margin,
normalized entropy, drift status, and abstention reason.

```text
entropy = -sum(p_class * log(p_class)) / log(number_of_classes)
```

New model inputs stay inside Trend, Volatility, Liquidity, and Session and need a
reviewed Feature Schema. Trade prices, labels, Risk, and results are forbidden
inputs. Current model evidence remains NO-GO.

### R-01 — Account permission and size

Data: equity, Risk cap, tick value/size, structural Stop, exposure, daily loss,
drawdown, emergency state.

```text
risk_money = equity * risk_percent
volume     = risk_money / loss_money_per_lot_at_structural_stop
```

Round volume down and cap it. AI confidence may reduce size under an approved
policy; it cannot exceed the Risk cap.

### L-01 — Matured outcome

Offline record: immutable Setup/Plan, Decision/Risk/Execution reasons, fills,
costs, MFE, MAE, realized R, close reason, and market regime.

Label Schema 1.1.0 remains unchanged. A Setup Outcome Dataset is a separate
future contract requiring calibration, schema review, and explicit approval.

## Recommended MVP timeframes

- M15: direction, regime, volatility, structural/liquidity map, Session;
- M5: POI interaction, sweep/reclaim trigger, entry, invalidation, target.

Do not add H1 and M1 in the first rule-only comparison. Add them later as isolated
hypotheses so their incremental value can be measured.

## Question admission gate

Every question/measurement requires:

1. written hypothesis and owner;
2. exact source and observation timestamp;
3. deterministic calculation and missing-data behavior;
4. synthetic closed-bar/future-leakage test;
5. Historical/Runtime parity test;
6. isolated research export with strict key joining;
7. ablation against the simpler baseline;
8. purged walk-forward stability;
9. cost-aware Strategy Tester comparison;
10. explicit promotion or rejection record.

## Implementation order

### Gate B0 — Information correctness

- unify Historical Replay and Runtime observation-time semantics;
- test Session parity at 00:00, 08:00, and 16:00;
- prove no shift-0 or forming higher-timeframe bars enter a decision;
- regenerate Dataset only after parity passes.

### Gate B1 — Market and location answers

- promote a reviewed confirmed-swing contract;
- implement continuous retracement/location and POI lifecycle;
- preserve the four canonical Brain groups and keep Forward unchanged.

### Gate B2 — Trigger and Trade Plan

- implement M5 closed-bar sweep/reclaim;
- produce CR-013 Setup Candidate and structure-aware Trade Plan;
- preserve Risk approval and Shadow mutation boundaries.

### Gate B3 — Strategy Tester evidence

- compare fixed 1:2 CR-012 against structure-aware rule-only planning;
- freeze dates, tick model, costs, and Risk limits;
- evaluate coverage, expectancy, Profit Factor, drawdown, and average R.

### Gate C — AI setup ranking

- approve a separate Setup Outcome Dataset;
- train only after sufficient rule-only coverage;
- require nested purged stability and an untouched later period;
- keep deployment/live execution locked until explicit approval.

### Gate C1 - Dual-direction Setup V2 research

- keep simple BUY/SELL inversion as a rejected baseline;
- build continuation and reversal candidates independently;
- recompute structural Stop and Target for each valid hypothesis;
- use Train only for discovery and require all four purged folds to pass;
- request a new untouched period only after stable Train-only evidence.

## Success definition

The system succeeds when it can reject incomplete information, identify a
bounded Setup, produce a defensible structural plan, survive costs and Risk
controls, and remain stable on unseen periods. It does not succeed merely by
answering BUY or SELL on every bar.
