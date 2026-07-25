# IMP-090 Current-Feed Past-Only Structural Target Ladder

Version: 1.0.0

Date: 2026-07-24

Status: Completed; no Target candidate passed

Architecture Baseline: ABR-1.0

Related: IMP-080, IMP-089

## Purpose and frozen scope

IMP-089 found 597 reversal-confirmed contexts before the preregistered
`2024-07-01 00:00` Train cutoff, but only 31 accepted plans. The dominant
post-context rejection was a nearest structural Target below the frozen
`2.0R` minimum. IMP-090 collects outcome-blind, past-only M5/M15 structural
Target ladders for those contexts from the same current `XAUUSD` feed.

The builder accepts only Setup Audit SHA-256
`B6122AEA49F764055347B0459104DA53AD37EA815D2CC6568E4B0BC6885490F1`
and exact Setup Audit Schema 3.0. It stops before the Train cutoff and includes
no Outcome label.

## Contract

- All requests must have POI, trigger, and reversal context confirmed.
- Trigger M5 timing must end exactly at the observation timestamp.
- Existing Entry/cost evidence is retained when available; otherwise the
  exporter derives Entry from the completed trigger close.
- Structural Stop/current Target and `2.0R` remain frozen.
- The exporter reads only trigger and older M5/M15 bars and returns up to three
  confirmed past-only structural Targets per timeframe.
- Validation/Test, Training, Runtime, Risk, Execution, and Deployment remain
  unchanged and unauthorized.

## Validation

Focused Python tests cover cutoff sealing, causal gates, known/unknown Entry,
Outcome exclusion, and the `2.0R` lock. The focused MQL5 EA verifies trigger
timing and Target-ladder ordering. MetaEditor must report exactly `0 errors,
0 warnings` before collection.

The hash-locked builder produced exactly 597 chronological requests: 574 with
known Entry/cost parity evidence and 23 whose Entry must be derived from the
completed trigger close. The request contains no Outcome label.

- request SHA-256:
  `9BBD853742D16A015C6D3179B86986A3A209646A228E593DBBC98E8BDD715C0C`;
- exporter SHA-256:
  `BC029DAF920591A5D923AA9A562452D316308465ABFC89BB4D4AE85888C20B44`;
- focused EA SHA-256:
  `28D733D8C42FBD1CEFB11830E08B99424B8653909D71253D4C7898516961AC19`;
- compile-log SHA-256:
  `E8672A23857D2B006D95D49F16D11AF7CB9261A4F30A4A35361DC68AD787E720`.

MetaEditor reported exactly `0 errors, 0 warnings`. Three relevant Python
regressions and syntax validation passed. The request was copied to the
selected MT5 Terminal `MQL5/Files` and verified by SHA-256.

The owner ran the focused exporter on `XAUUSD,M15`; all 597 requests were
written and the EA removed itself. Export SHA-256:
`E930FFEEB5AF464DBCFD7FFD531D264AA9ED7D326CDAAD07ED2487CC72E7E2FA`.
The strict current-feed collector validates exact request/export parity and
replays all candidates only against the hash-locked current-feed Decision path.

## Train-only result

No current, M5, or M15 Target candidate passed the fixed Train gate.

| Candidate | Mature | Target rate | Mean cost-aware R |
|---|---:|---:|---:|
| Current Target | 31 | 22.58% | -0.261R |
| M5 Target 1 | 3 | 33.33% | +0.405R |
| M5 Target 2 | 21 | 28.57% | -0.047R |
| M5 Target 3 | 52 | 26.92% | -0.023R |
| M15 Target 1 | 69 | 18.84% | -0.268R |
| M15 Target 2 | 109 | 21.10% | -0.187R |
| M15 Target 3 | 129 | 17.83% | -0.273R |

M5 Target 1 has only three mature records and fails sample and chronological
stability requirements. M5 Target 3 is descriptively closest to zero but
remains negative, directionally inconsistent, and negative in three of four
chronological blocks. M15 Target 3 improves sample coverage but remains
materially negative. No candidate is eligible for a Runtime Change Request.

Replay report SHA-256:
`79F323552BA0452AC14A8CC957BD6ADA76E81C2A806A7789D492933D98F2D4A0`.
Three relevant regressions and Python syntax validation passed. The accepted
IMP-089 scorecard remains unchanged at `100.00 / 19.82 / 100.00`, hard-gated
Overall Readiness `49.00`, status `NO_GO_TRAIN`.
