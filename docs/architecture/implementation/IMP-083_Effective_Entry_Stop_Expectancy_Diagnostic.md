# IMP-083 Effective Entry/Stop Expectancy Diagnostic

Version: 1.0.0

Date: 2026-07-22

Status: Completed; favorable-excursion giveback identified; NO-GO

Architecture Baseline: ABR-1.0

Related: RSCS-1.0, CR-013, IMP-079, IMP-080, IMP-082

## Purpose

Explain the negative current-strategy expectancy on the audited 232-record
Effective Train sample before proposing another strategy contract. Measure
cost-aware return uncertainty, drawdown/loss tails, and MFE/MAE path behavior
without selecting an Entry, Stop, Target, or Trade Lifecycle Candidate.

## Frozen diagnostic contract

- Train source SHA-256:
  `F31E6DED4E0AC3B20FDD7964D3E634902736C8AD3316AA15A4E63D5C3C7E9A7E`;
- Effective Sample audit SHA-256:
  `2646BBD8E881B6BB7F8621E27D1933BE1376711C75558E046B9EA964A1393414`;
- use only the maximum non-overlapping 232-record schedule from IMP-082;
- use cost-aware `plan_rr` for `TARGET_FIRST`, `-1R` for `STOP_FIRST`, and
  `0R` for `TIMEOUT`;
- independently validate Dataset `realized_r` as gross path R so Gross R and
  cost-aware R cannot be silently mixed;
- calculate a deterministic circular moving-block percentile interval with
  seed `20260722`, 10,000 samples, and block length `ceil(N^(1/3)) = 7`;
- describe fixed MFE thresholds `0.5R`, `1.0R`, and `2.0R`, plus winner MAE
  thresholds `0.5R` and `0.75R`;
- retain four chronological blocks and both pre-declared directions;
- do not select a threshold or Candidate after observing the result.

Validation/Test paths are forbidden inputs. The tool must fail on source/audit
hash drift, Effective Sample parity drift, invalid path metrics, or protected
state drift.

## Implementation

- `training/diagnose_entry_stop_expectancy.py` implements the strict
  Effective-Train diagnostic;
- `training/test_entry_stop_expectancy_diagnostic.py` covers cost-aware
  expectancy, loss-tail accounting, MFE thresholds, deterministic confidence
  bounds, evidence-hash drift, and Gross R integrity;
- `tools/diagnose_entry_stop_expectancy.ps1` is the path-with-spaces-safe entry
  point;
- `training/config/research_scorecard_imp083_entry_stop_diagnostic.json`
  records the resulting Baseline evidence without awarding unpassed gates.

## Effective-Train result

| Measure | Result |
| --- | ---: |
| Effective N | 232 |
| Target / Stop | 59 / 173 |
| Target rate | 25.43% |
| Mean cost-aware R | **-0.074R** |
| moving-block 95% CI | **[-0.284R, +0.138R]** |
| cumulative R | -17.176R |
| Profit Factor | 0.901 |
| maximum drawdown | 34.474R |
| longest loss sequence | 15 |

Both directions remained negative: BUY `-0.087R`, SELL `-0.060R`. Only the
third chronological block was positive (`+0.321R`); blocks 1, 2, and 4 were
`-0.054R`, `-0.472R`, and `-0.091R`.

## Entry/Stop path finding

Of the 173 `STOP_FIRST` outcomes:

- 116 had reached at least `+0.5R` MFE before Stop;
- 70 had reached at least `+1.0R` MFE before Stop;
- 36 had reached at least `+2.0R` MFE before Stop;
- only 57 failed before ever reaching `+0.5R` MFE.

The median losing-path MFE was `0.823R`. Therefore a large share of losses did
not simply move immediately in the wrong direction: they first moved
favorably and later returned to the structural Stop. This is evidence of
favorable-excursion giveback in the current accepted-plan lifecycle.

This finding does **not** authorize Breakeven, Trailing Stop, partial close, or
a closer Target. The Dataset records completed M15 bar excursions and cannot
prove intrabar order when a management threshold and adverse level occur in
the same bar. MFE/MAE are not broker fills and do not include management
slippage. A causal M5 or real-tick past-only lifecycle replay is required.

## RSCS-1.0 result

Research Quality remains `100.00`, Strategy Evidence `20.00`, Operational
Safety `100.00`, raw Overall `60.00`, and Hard-Gated Overall `49.00` with
`NO_GO_TRAIN`. IMP-083 changes unknown expectancy into measured negative,
uncertain expectancy; it correctly earns no extra score. G0 and G1 pass;
G2-G8 remain false.

The diagnostic SHA-256 is
`D9A2E303E4D509D6833F62198F21747C3AD0068CDD027449A7A8B660419D52FF`.
The Scorecard SHA-256 is
`C34059154453F9E400FB3A1B8620C178BBBB48CBAD0487A0EDC70C1ACE60E2DA`.

## Safety and validation

The focused test and complete Python regression passed `50/50`. The PowerShell
wrapper parsed and executed from the Workspace path containing a space. No
MQL5, Runtime, Risk, Execution, Feature Schema, or Label Schema file changed,
so the last verified Runtime compile remains `0 errors, 0 warnings`.

Validation, Test, Forward, Live Execution, and Deployment remained sealed and
unauthorized. Broker state was not touched.

## Next evidence

Pre-register a small Train-only lifecycle replay with unchanged Entry, initial
structural Stop, minimum `2.0R`, Risk, and position size. Candidate management
rules must use causal M5 or real-tick ordering, include spread/slippage stress,
and be rejected unless expectancy, every chronological block, both directions,
drawdown, and loss tail improve. Do not create a Runtime CR until that offline
Candidate passes its frozen Train gates.
