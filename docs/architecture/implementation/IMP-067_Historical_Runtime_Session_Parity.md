# IMP-067 Historical and Runtime Session Observation Parity

Version: 1.0.0

Date: 2026-07-18

Status: Closed; corrected Dataset passed all safety gates

Related: CR-001, IMP-009, IMP-045, Feature Schema 4.0

## Problem

Runtime Brain evaluated Session context at the completed bar observation time:

```text
bar open timestamp + timeframe duration
```

Historical Brain Replay evaluated Session context at the bar open timestamp.
On M15 this made historical `session_progress` fifteen minutes earlier than
Runtime and assigned the wrong one-hot Session to bars that completed at the
00:00, 08:00, and 16:00 boundaries.

This defect did not read future price data, but it violated the approved CR-001
requirement that Runtime and historical replay use the same deterministic
Session encoding.

## Correction

`CClosedBarObservationTime` now owns the completed-bar timestamp calculation.
Both `CBrainContextBuilder` and `CHistoricalBrainReplay` use this single helper.

For an M15 row whose stored bar timestamp is `07:45`, the Session feature is
therefore observed at `08:00`, after that bar has completed. The Dataset row
timestamp remains the bar-open identity; it is not redefined as the observation
timestamp.

## Architecture and leakage controls

- Canonical Runtime flow and ABR-1.0 boundaries are unchanged.
- Brain remains the sole owner of Session market context.
- No AI decision, label, Risk, execution, or trade-result data enters the
  calculation.
- Only the duration of the completed bar is added; no later bar or future price
  is read.
- Feature Schema remains `4.0.0` because the intended public formula is
  unchanged; this is a parity defect correction to the existing contract.

## Focused validation

`tests/TestHistoricalRuntimeSessionParity.mq5` checks M15 closed-bar observation
time, Session boundary transitions at 08:00, 16:00, and midnight, intra-session
progress at 04:00, and rejection of an invalid bar timestamp.

The correction compile tool also compiles:

- `TestSessionFeatureProgress.mq5`
- `TestHistoricalBrainReplay.mq5`
- `TestClosedBarBrainContext.mq5`
- `TestHistoricalDatasetOrchestrator.mq5`

All five targets must report `0 errors / 0 warnings`.

MetaEditor validation passed on 2026-07-18: all five targets compiled with
`0 errors / 0 warnings`, including the focused parity test and Historical
Dataset Orchestrator dependency closure.

Focused MT5 validation passed on XAUUSD M15 at `2026.07.18 16:13:06.035`.
Observation timestamp, Session boundary, Session progress, and the complete
Historical/Runtime Session parity contract all reported `true`; the test then
called `ExpertRemove()`.

## Dataset consequence

The 26,900-row Dataset completed on 2026-07-18 remains valid evidence for the
full 16-bar label-horizon correction and structural CSV checks. It must not be
used for new model training because its Session features were generated before
this parity correction.

After focused tests pass, Dataset generation, validation, purged splitting,
partition validation, and readiness validation must be repeated before model
research resumes. Existing model deployment and live execution remain NO-GO.

Corrected Dataset regeneration completed on 2026-07-18 at
`22:04:19.125`. The one-shot Orchestrator wrote 26,850 records and called
`ExpertRemove()`. Content validation and all downstream Dataset gates remain
required before this Dataset may enter model research.

Content validation passed at `2026.07.18 22:11:40.910`: all 26,850 records
were readable; BUY/HOLD/SELL counts were 11,797/2,948/12,105; duplicate IDs,
duplicate timestamps, invalid features, and invalid labels were all zero. The
Dataset reported `valid: true`. Purged chronological splitting and downstream
partition gates remain pending.

Purged chronological splitting passed at `2026.07.18 22:17:00.897`.
Train/Validation/Test contain 18,779/4,011/4,028 records, 32 boundary records
were purged at sixteen bars per boundary, timestamps remain chronological, and
the split reported `valid: true`. Cross-partition validation remains pending.

Cross-partition validation passed at `2026.07.18 22:19:16.715`. Every
partition contains BUY/HOLD/SELL labels; duplicate and invalid counters are
zero; temporal ordering is valid; both boundary gaps are exactly 15,300
seconds; label-horizon purge and the complete partition Dataset are valid.
Training Readiness evaluation remains pending.

Training Readiness passed at `2026.07.18 22:21:46.214`. The purged partitions
contain 26,818 usable records against a 1,000-record minimum; partition
validity, size requirements, label coverage, and final model-training readiness
all reported `true`. IMP-067 is therefore closed. This authorizes controlled
Train-only model research, not model deployment or live execution.

The registered Train-only Walk-forward rerun used 18,779 Train rows and did not
read Validation or Test. Its selected development candidate reached Macro F1
0.4228 and BUY precision 0.4749, but Accuracy and both directional precision
floors failed; zero of four folds passed the complete contract. Deployment
therefore remains NO-GO. The associated Train-only diagnostic ranked Session
Context strongest and the three Trend fields weakest.
