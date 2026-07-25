# IMP-080 Past-Only Multilevel Structural Target Replay

Version: 1.2.0

Date: 2026-07-22

Status: Completed; all Target-only candidates rejected; NO-GO

Architecture Baseline: ABR-1.0

Related: CR-013, CR-015, CR-016, CR-017, IMP-056, IMP-075, IMP-079

## Purpose

Measure whether confirmed structural Target alternatives can resolve the broad
Target-room constraint found by IMP-079 before proposing another Runtime Change
Request. This is an isolated offline research exporter and Train-only replay.
It is not a Runtime strategy contract.

## Frozen source boundary

The request builder accepts only the eight frozen sources and SHA-256 values
used by IMP-079. It stops strictly before Validation start
`2025-07-16 03:00`, applies both approved real-tick exclusion manifests, and
exports only quality-admissible sweep/reclaim triggers. Validation and Test
partition files are forbidden inputs.

Each request preserves source, observation, symbol, direction, M5 trigger-bar
open, raw structural Stop, raw current Target, and the V1 plan values when they
are calculable. Missing Entry/cost evidence remains explicitly unknown; it may
not be invented by Python.

## Past-only evidence contract

The isolated MQL5 exporter must:

- load Entry from the exact completed M5 trigger bar recorded by the audit;
- require `entry_bar_open + 5 minutes == observation_time`;
- verify the derived Entry against the audit Entry when the latter is known;
- use confirmed pivots with frozen `left=2`, `right=2`, and `lookback=64`;
- start pivot search at index 2 of arrays whose index 0 is the latest completed
  bar, so both right-side confirmation bars were known at observation;
- build independent M5 and M15 ladders from confirmed swing highs for BUY and
  confirmed swing lows for SELL;
- retain at most the three spatially nearest unique levels in the reward
  direction, ordered from nearest to farther from Entry;
- fail closed on missing history, timestamp mismatch, schema mismatch, parity
  mismatch, invalid direction, or malformed evidence;
- write `known_time_valid=true` only after all checks pass.

The current V1 Target remains a baseline field. The exporter does not change
the canonical swing engine, Runtime Target, minimum RR, Risk, or Execution.

## Train-only replay contract

The replay may evaluate the baseline current Target and the six frozen ladder
slots against the same structural Stop and cost evidence. RR and counterfactual
outcomes are calculable only when Entry, Stop, Target, and cost are known. The
existing 64-M15-bar maturity horizon and same-bar ambiguous-outcome quarantine
remain unchanged.

Candidate reporting must include coverage, cost-aware `2.0R` reachability,
Target-first/Stop-first/timeout counts, mean cost-aware R, BUY/SELL results,
four chronological blocks, and a comparison with the current Target. A Target
source cannot be proposed for Runtime unless it passes all frozen Train gates:

- at least 200 mature Train records;
- positive mean cost-aware R;
- no chronological block with non-positive mean cost-aware R;
- no use of Validation or Test for selection;
- unchanged minimum `2.0R`, structural Stop, cost model, and Safety Locks.

Passing Train is necessary but not sufficient. It would authorize only a new
documented Runtime CR proposal, never Deployment or Live Execution.

## Protected boundaries

- no connection from the exporter or replay to Brain, AI Runtime, Decision,
  Risk, Execution, or Trade Lifecycle;
- no change to Feature Schema 4.0 or Label Schema 1.1;
- no model training, threshold tuning, Forward test, or broker mutation;
- no automatic attachment to a live chart and no order API calls;
- `deployment_authorized=false` and project status remain NO-GO.

## Validation plan

1. Add focused Python tests for hash/cutoff/exclusion/request schema behavior.
2. Add a focused MQL5 test for pivot confirmation, spatial ordering, exact
   trigger-bar timing, malformed input, and non-deployable output.
3. Compile the focused exporter test in MetaEditor with exactly
   `0 errors, 0 warnings`.
4. Run the complete Python regression.
5. Collect the MT5 export manually in research mode, then run the sealed
   Train-only replay. No Runtime test or Forward run is authorized here.

## Implementation and validation status

The isolated implementation consists of:

- `training/build_past_only_target_requests.py` and its focused test;
- `core/ai/PastOnlyStructuralTargetExporter.mqh`;
- `tests/TestPastOnlyStructuralTargetExporter.mq5`;
- `training/replay_past_only_targets.py` and its focused test;
- prepare, sync/compile, and collect/replay PowerShell entry points under
  `tools/`.

The request build verified all eight IMP-079 frozen hashes and produced 1,777
quality-admissible Train-only requests: 1,739 retain known Entry/cost evidence
and 38 preserve unknown Entry/cost explicitly. The request artifact SHA-256 is
`97660767EBD11904A4FD554F9811D17E45FD88898537709686F2F331D95566C5`.
Validation/Test usage, Runtime changes, and Deployment authorization are all
false in its manifest.

The focused MetaEditor target compiled `1/1` with exactly
`0 errors, 0 warnings`. Both new Python focused tests passed, followed by the
complete Python regression at `47/47`.

The first normal-chart collection attempt failed closed before writing any
records because the Terminal had no M5 cache for the first retained request at
`2020-03-18 12:30`. Inspection confirmed that annual XAUUSD history files for
2020 onward exist locally, while Terminal `MaxBars` was only `100000` and the
M5 cache was absent. Exporter version 1.1 adds bounded `CopyRates` prefetch and
reports `TERMINAL_MAXBARS` on failure. Collection therefore requires the user
to set MT5 `Max bars in chart` to `Unlimited` and restart the Terminal; this is
a data-availability setting only and does not enable Algo Trading.

## Train-only replay result

After changing Terminal Max Bars to Unlimited, the exporter wrote all 1,777
requests. The MT5 and Workspace copies have identical size (`446709` bytes)
and SHA-256
`CE6D17AEEC65B78E84789E64FC4C4BA683186FDC43F45E816DFCEC02F817F456`.
The replay report SHA-256 is
`80D0D66DFBEFAF38A3A8C14C0D874E84CE1874E9B12D595DACD0DEA4E7B85ED1`.

| Candidate | Mature | Target-first | Mean cost-aware R | Train gate |
| --- | ---: | ---: | ---: | --- |
| current Target | 233 | 25.32% | -0.078R | fail |
| M5 target 1 | 55 | 29.09% | +0.104R | fail |
| M5 target 2 | 157 | 27.39% | -0.005R | fail |
| M5 target 3 | 265 | 21.51% | -0.193R | fail |
| M15 target 1 | 281 | 21.35% | -0.178R | fail |
| M15 target 2 | 445 | 21.35% | -0.130R | fail |
| M15 target 3 | 464 | 18.97% | -0.191R | fail |

The current Target exactly reproduced the frozen 233-record baseline and its
`-0.078R` expectancy, establishing replay parity. M5 target 1 was the only
positive aggregate alternative, but it had only 55 mature records, SELL mean
was `-0.315R`, and chronological blocks 2 and 4 were negative. M5 target 2 was
nearly flat but remained below the 200-record gate and had three non-positive
chronological blocks. Every alternative with at least 200 mature records had
negative aggregate expectancy.

Farther M5/M15 levels increased the number of triggers capable of satisfying
the unchanged cost-aware `2.0R`, but Target-first probability declined to
approximately 19-22%. Structural Target distance alone therefore does not
resolve the weak setup expectancy. No candidate passed; Runtime candidate
proposal readiness, Runtime CR authorization, and Deployment authorization
remain false. Validation and Test were not opened.

## Conclusion

Do not issue another Target-source Runtime CR. The next bounded offline
question is whether Entry/Stop placement can distinguish setups that achieve
positive maximum favorable excursion before structural Stop. That diagnostic
must use the same frozen Train sources and may inspect direction/session only
as hypotheses; it may not create a Runtime filter, reduce minimum RR, open
Validation/Test, or compensate through Risk changes.
