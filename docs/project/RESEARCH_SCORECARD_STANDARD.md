# XAU AI PLATFORM Research Scorecard Standard

Standard: RSCS-1.0

Version: 1.0.0

Date: 2026-07-22

Status: Active for all new research experiments

Architecture Baseline: ABR-1.0

## Purpose

Provide a frozen, repeatable measurement of whether each experiment improves
research reliability, strategy evidence, operational safety, and overall
readiness. A single attractive score may never override a failed evidence or
Safety gate.

Formal score comparisons begin with the IMP-080 current Target baseline.
Earlier results are retained as a factual evidence ledger because several
inputs required by RSCS-1.0 were not measured at those times. They may not be
backfilled with invented values.

## Four reported scores

Every Baseline and Candidate scorecard reports:

1. `Research Quality` — reliability and reproducibility of the experiment;
2. `Strategy Evidence` — economic edge and statistical stability;
3. `Operational Safety` — test, compile, Safety Lock, broker, and artifact
   integrity;
4. `Overall Readiness` — weighted result subject to non-compensating Hard Gate
   caps.

The raw overall formula is:

```text
30% Research Quality + 50% Strategy Evidence + 20% Operational Safety
```

## Research Quality — 100 points

| Component | Points |
| --- | ---: |
| hypothesis pre-registered | 10 |
| source Artifact hashes verified | 15 |
| past-only causality enforced | 15 |
| Validation/Test remain sealed | 5 |
| data-quality warning coverage | 15 |
| independent replay parity | 15 |
| complete Python regression | 5 |
| clean affected MetaEditor compile | 5 |
| effective-sample/overlap audit | 10 |
| Safety and governance valid | 5 |

Quality coverage is proportional only where a versioned quality manifest
defines the denominator. All other components are Boolean and receive no
partial credit.

## Strategy Evidence — 100 points

| Component | Points | Frozen rule |
| --- | ---: | --- |
| effective mature sample | 15 | full at effective N >= 200 |
| positive expectancy | 25 | full only when Mean R and 95% CI lower bound are positive |
| drawdown/loss-tail gate | 10 | pre-registered normalized-R limit passes |
| chronological stability | 15 | proportional positive blocks; Gate needs all |
| direction robustness | 10 | proportional positive pre-declared directions; Gate needs all |
| spread/slippage stress | 10 | positive under every pre-registered cost level |
| purged ranker stability | 5 | proportional passing folds, or full if ranker not required |
| locked Validation | 5 | one locked confirmation only after Train passes |
| Forward Shadow | 5 | approved Forward contract passes |

If effective sample size has not been audited, raw mature count may earn at
most half of the sample points. Positive Mean R without a positive 95% lower
confidence bound may earn at most half of the expectancy points. Negative or
zero Mean R earns zero expectancy points.

## Operational Safety — 100 points

| Component | Points |
| --- | ---: |
| focused tests pass | 20 |
| affected Runtime compile is clean | 20 |
| complete regression passes | 20 |
| Safety Locks remain valid | 20 |
| broker state unchanged and Artifact set complete | 20 |

An offline-only change uses the last verified unchanged Runtime compile and
must state that no MQL5 file was affected.

## Hard Gates and caps

| Gate | Requirement | Failure result |
| --- | --- | --- |
| G0 | integrity, causality, quality, parity, tests, compile, Safety | invalid evidence; overall 0 |
| G1 | audited effective N >= 200 | Train NO-GO; overall capped at 49 |
| G2 | Mean R > 0 and 95% CI lower bound > 0 | Train NO-GO; cap 49 |
| G3 | every chronological block positive | Train NO-GO; cap 49 |
| G4 | every pre-declared direction positive | Train NO-GO; cap 49 |
| G5 | drawdown and cost stress pass | Train NO-GO; cap 49 |
| G6 | every required purged ranker fold passes | Train NO-GO; cap 49 |
| G7 | locked Validation passes | Validation NO-GO; cap 69 |
| G8 | approved Forward Shadow passes | Forward NO-GO; cap 84 |

Passing G0-G8 with Deployment still false produces
`READY_FOR_DEPLOYMENT_REVIEW` and caps overall at 94. Deployment authorization
requires a separate explicit governance decision; the scorecard cannot grant
it.

## Baseline and Candidate progression rules

- Every experiment creates one immutable Baseline scorecard and one scorecard
  per Candidate using the same RSCS version.
- A rejected Candidate never replaces or lowers the accepted Baseline. It is
  recorded as a negative result and may improve Research Quality by closing a
  bounded uncertainty.
- Baseline Strategy Evidence may decrease only when new valid evidence
  directly invalidates or weakens the Baseline. Such a decrease must not be
  hidden to preserve a monotonic chart.
- No scoring weight, threshold, denominator, or Hard Gate may change after an
  experiment starts. A future standard revision requires a version change and
  parallel reporting against the old standard.
- Unknown values receive zero or explicitly capped credit; they are never
  imputed.
- Promotion requires the Candidate to pass its current gate and improve the
  relevant Baseline metrics. A higher raw score alone is insufficient.

The desired progression is therefore:

```text
Research reliability rises as permanent evidence controls are added.
Candidate Strategy score may rise or fall.
Accepted Baseline changes only after a better Candidate passes its gates.
Overall readiness advances only when the next hard evidence gate passes.
```

## Required Before/After ledger

Every experiment summary must retain:

- experiment/candidate ID and RSCS schema version;
- immutable source hashes and cutoff;
- raw and effective mature sample;
- Target rate, Mean R, 95% CI, Profit Factor, normalized maximum drawdown, and
  longest loss sequence;
- chronological block and direction/regime results;
- cost-stress levels and results;
- all four scores, every component, every Gate, status, and score deltas from
  the named reference scorecard;
- explicit Validation/Test/Forward/Runtime/Deployment flags.

## Historical evidence ledger

| Stage | Mature Train | Target rate | Mean cost-aware R | Decision |
| --- | ---: | ---: | ---: | --- |
| original Objective contract | 229 | 22.71% | -0.161R | negative Baseline |
| minimum reclaim 0.10 ATR | 182 | 25.27% | -0.064R | quality improved; sample gate failed |
| CR-015 pre-Train augmentation | 233 | 25.32% | -0.078R | sample passed; ranker passed 1/4 folds |
| CR-016 continuation | 0 valid plans | — | — | Candidate rejected; Baseline unchanged |
| CR-017 reversal context | 0 valid plans | — | — | Candidate rejected; Baseline unchanged |
| IMP-080 current Target replay | 233 | 25.32% | -0.078R | formal RSCS-1.0 Baseline; Train NO-GO |
| IMP-082 effective-sample audit | 233 raw / 232 effective | 25.32% | -0.078R | G1 passed; Train remains NO-GO |
| IMP-083 Entry/Stop diagnostic | 232 effective | 25.43% | -0.074R; CI [-0.284,+0.138] | giveback diagnosed; no Candidate selected |
| IMP-084 causal M5 lifecycle | 232 Baseline / 230 Ratchet | 25.43% Baseline | Baseline -0.074R; Breakeven -0.079R; Ratchet -0.125R | both Candidates rejected; Baseline unchanged |
| IMP-085 lifecycle attribution | 232 Baseline / 230 Ratchet | unchanged | Breakeven Delta -1.084R; Ratchet Delta -7.032R | saved Stops outweighed by clipped Targets; no Candidate |
| IMP-086 canonical response attribution | 232 effective | unchanged | Baseline -0.074R; best support gain +0.007 | no canonical group passed the frozen confirmation gate; no Candidate |
| IMP-087 existing Entry geometry | 232 effective | unchanged | Baseline -0.074R; best support gain +0.0017 | existing geometry could not recall Target-first outcomes; no threshold/Candidate |
| IMP-088 trigger-event preparation | 232 outcome-blind requests | unchanged | no new outcome evidence yet | exporter compile-clean; formal score unchanged pending collection |

## Current formal Baseline

The IMP-083 structural Target Baseline, causally reconfirmed by IMP-084 M5
replay, produces:

| Score | Result |
| --- | ---: |
| Research Quality | 100.00 |
| Strategy Evidence | 20.00 |
| Operational Safety | 100.00 |
| Raw Overall | 60.00 |
| Hard-Gated Overall Readiness | **49.00** |

Status is `NO_GO_TRAIN`. G0 and G1 pass; G2-G8 remain false. The main missing
evidence, in priority order, is:

1. improve the Setup selection/Entry hypothesis on Train; the two frozen
   lifecycle-management Candidates did not create positive expectancy;
2. pass pre-registered expectancy, drawdown, and loss-tail gates;
3. pass temporal/direction stability on Train;
4. stable purged ranking, only after an earlier Train Candidate passes;
5. locked Validation, then approved Forward Shadow.

The scorecard Artifact is generated from
`training/config/research_scorecard_imp083_entry_stop_diagnostic.json`. Its current
output SHA-256 is
`C34059154453F9E400FB3A1B8620C178BBBB48CBAD0487A0EDC70C1ACE60E2DA`.
Deployment remains unauthorized.

IMP-084 companion scorecards preserve the Baseline score at `100/20/100`, raw
`60`, hard-gated Overall Readiness `49`. Breakeven and Ratchet each score
Strategy Evidence `18.75`, raw `59.38`, and hard-gated Overall Readiness `49`;
neither replaces the Baseline.

IMP-085 adds causal benefit/harm attribution without changing the Baseline
metrics or gates. Its score remains `100/20/100`, raw `60`, and hard-gated
Overall Readiness `49`; the score delta from IMP-084 is zero.

IMP-086 tests canonical Setup-response separability without changing the
Baseline. No group qualifies for confirmation, so its score remains
`100/20/100`, raw `60`, and hard-gated Overall Readiness `49`; every score
delta from IMP-085 is zero. The IMP-086 scorecard SHA-256 is
`9F549FC45543C7D3F7A6E7E75A53DDBD8E4D96680C4D5E5F925C80DD34E4BB8A`.

IMP-087 tests existing deterministic Entry geometry without changing the
Baseline or Feature Schema. No view qualifies for confirmation, so its score
remains `100/20/100`, raw `60`, and hard-gated Overall Readiness `49`; every
score delta from IMP-086 is zero. The IMP-087 scorecard SHA-256 is
`96244169C3AC4087E69C19C6D2F105B055AFF46B00D1C245A6941AC6C054A65C`.

IMP-088 preparation creates no Candidate and adds no outcome evidence to the
accepted Baseline. Its 232 requests are outcome-blind and the exporter is
compile-clean; the formal score remains the IMP-087 `100/20/100`, raw `60`,
hard-gated Overall Readiness `49` until the export is collected and validated.
