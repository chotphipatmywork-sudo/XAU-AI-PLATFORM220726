# IMP-095 Current-Feed Joint Geometry Frontier

Version: 1.0.0

Date: 2026-07-24

Status: Completed; no combination passed the Train gate

Architecture Baseline: ABR-1.0

Related: IMP-090 through IMP-094

## Purpose and frozen contract

IMP-095 combines the seven preregistered Stop choices with the seven
preregistered Target choices, producing a fixed 49-combination frontier before
outcome replay. Entry, cost, 64-bar horizon, and minimum `2.0R` remain frozen.

Every combination must pass the existing full Train gate. Descriptive ranking
cannot select a candidate. Validation/Test remain sealed and no new parameter
search is allowed after viewing outcomes.

Runtime, Risk, Execution, Forward testing, Live Execution, and Deployment
remain unchanged and unauthorized.

## Result

All 49 preregistered combinations were replayed. None passed the full Train
gate.

The strongest non-trivial descriptive result was:

`M5 Stop 2 + M15 Target 1`

- Mature records: 76 (required: 200)
- Target/Stop first: 21/55
- Mean cost-aware return: `+0.263R`
- BUY: 38 records, `+0.131R`
- SELL: 38 records, `+0.396R`
- Four chronological blocks:
  `+0.741R`, `+0.023R`, `+0.265R`, `+0.025R`
- Train gate: failed

Although its directions and chronological blocks were positive, it was found
inside a 49-combination descriptive frontier and has only 76 mature records.
It is therefore a research lead, not a confirmed Candidate. It cannot be used
to open Validation/Test or authorize Runtime/Forward/Deployment.

The other positive descriptive combinations had 66 or fewer mature records.
No post-outcome parameter expansion is allowed.

- Focused joint-geometry test: passed.
- MQL5 compile: not required; no MQL5 source or Runtime file changed.
- Frontier combinations: 49.
- Train-gate passing combinations: 0.
- Joint frontier SHA-256:
  `3F0EDEEDBCFB284E72F8A7284B59B8947F016F278F704DABFDB7E70FA34733CE`
- Deployment: NO-GO.
