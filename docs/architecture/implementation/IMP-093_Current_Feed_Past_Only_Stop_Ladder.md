# IMP-093 Current-Feed Past-Only Structural Stop Ladder

Version: 1.0.0

Date: 2026-07-24

Status: Completed; all Train-only candidates rejected

Architecture Baseline: ABR-1.0

Related: IMP-091, IMP-092

## Purpose

Target substitution and lifecycle management did not pass. IMP-093 therefore
collects outcome-blind same-side confirmed pivot Stops from M5 and M15 for the
same 597 current-feed Train contexts. It reuses the hash-locked IMP-090 request
without reading Outcome labels.

## Frozen contract

Candidates are Current Stop and up to three nearest past-only same-side pivot
Stops per M5/M15 timeframe. BUY uses confirmed lows below Entry; SELL uses
confirmed highs above Entry. Entry, current Target, cost, and the `2.0R`
minimum remain frozen. Candidate feasibility and outcomes are evaluated only
after export.

Validation/Test, Runtime, Risk, Execution, and Deployment remain unchanged and
unauthorized. Missing history, Entry parity drift, malformed geometry, or file
failure deletes partial output and fails closed.

## Validation evidence

- The focused EA validates synthetic BUY and SELL Stop ordering before export.
- MetaEditor compile result: `0 errors, 0 warnings`.
- Exporter SHA-256:
  `A9697D93462C21D69BFC9A5FBCD62F7203697C29D1A165D8F4D5D6087125C41F`
- Focused EA SHA-256:
  `8328E30146EBC6AFEF8F143DAF6C7D52BEC568F440C96C88A6B9C7C9664A9E7F`
- Compile log SHA-256:
  `BA83192F8C97127408591824FAD243F43C951D5DC29596354F4A08F832C5E523`

The first compile attempt failed closed with `101 errors, 18 warnings`
because `input` was used as an identifier although it is an MQL5 keyword.
The identifier was corrected and the focused BUY/SELL ladder checks were
added before the successful compile above.

The first terminal self-test then returned false for both directions because
its synthetic arrays contained only five bars while the frozen ladder
requires 67 bars. No research export was attempted. The fixture now derives
its size from `RequiredBars()`, retains three isolated pivots per direction,
and the corrected EA was synced and compiled again at `0 errors, 0 warnings`.

## Collection handoff

Attach `TestCurrentFeedStructuralStopExporter` to an `XAUUSD,M15` chart.
Keep Algo Trading disabled. The expected completion message is:

`Current-feed structural Stop records written: 597`

This collection is offline research only and does not authorize a Runtime
candidate, Forward test, Live Execution, or Deployment.

## Collection and replay result

MT5 wrote all `597` records after both focused ladder checks returned `true`.
The export passed exact schema, request coverage, chronology, baseline parity,
cost, minimum-RR, causal-time, ladder-order, and Deployment-lock validation.

| Stop candidate | Mature | Target first | Mean cost-aware R | Result |
|---|---:|---:|---:|---|
| Current Stop | 31 | 7 | -0.261 | Reject |
| M5 Stop 1 | 188 | 24 | -0.464 | Reject |
| M5 Stop 2 | 65 | 12 | -0.350 | Reject |
| M5 Stop 3 | 25 | 4 | -0.449 | Reject |
| M15 Stop 1 | 42 | 10 | -0.115 | Reject |
| M15 Stop 2 | 8 | 2 | -0.136 | Reject |
| M15 Stop 3 | 4 | 2 | +0.552 | Reject: insufficient sample |

No candidate passed the frozen Train gate. The positive M15 Stop 3 result has
only four mature records and cannot authorize a Candidate. M15 Stop 1 reduced
the observed loss magnitude but remained negative and too small. Therefore no
Runtime change request, Forward test, or Deployment is authorized.

Evidence:

- Export SHA-256:
  `FB6E0073BDF0FD89E4B09324B6C092F0812DBA7D243608063B61E4F167627C75`
- Replay report SHA-256:
  `0D6AA7B95A9D154E760BC4167D7C99B50C7165BE85E35C5C113F6B454A5A2A45`
- Request SHA-256:
  `9BBD853742D16A015C6D3179B86986A3A209646A228E593DBBC98E8BDD715C0C`
- Decision path SHA-256:
  `A20A7B5F1399541C271D46999433B8C69B650D27F48DC3480B59E15E9C4022EC`
- Focused Python regressions: request, Target replay, and Stop replay all
  passed.
