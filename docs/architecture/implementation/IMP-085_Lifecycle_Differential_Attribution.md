# IMP-085 Lifecycle Differential Attribution

Version: 1.1.0

Date: 2026-07-23

Status: Completed; management benefit/harm attributed; no Candidate selected;
NO-GO

Architecture Baseline: ABR-1.0

Related: RSCS-1.0, IMP-082, IMP-083, IMP-084

## Purpose

Explain why the two IMP-084 causal M5 lifecycle Candidates underperformed the
unchanged Baseline. Decompose paired return changes into management benefit,
management harm, unchanged outcomes, and ambiguity without proposing another
Stop rule or selecting a post-hoc subgroup.

This is a Train-only diagnostic. It cannot open Validation/Test, change Entry,
initial Stop, Target, Risk, Runtime, or authorize Forward/Deployment.

## Frozen evidence

- lifecycle request SHA-256:
  `42FB2CA1EA960ADB902D868E06E134D95D9229DEB5B38E01BA6DD8FA19CBAD10`;
- request manifest SHA-256:
  `2FE5B5E6FB9EC63796E1F230FFDE1D3539EF70C29D9FBF3B3E779A3273BDD220`;
- causal M5 export SHA-256:
  `AF4C0031F9EDEB58F4FFB7B4F86044938FA992DABD8A804AFEB7BB9090693758`;
- IMP-084 replay SHA-256:
  `97675D0EBDF8ED85A88E6B118A9412F2513477E85DD6C84B38FFE309362D2630`;
- Candidates and costs remain exactly those pre-registered in IMP-084;
- paired attribution uses only Candidate-effective records; ambiguity remains
  quarantined and receives no invented return.

## Frozen attribution categories

Each Candidate result is paired with the same request's Baseline result and
assigned exactly one category:

1. `TARGET_PRESERVED`: Baseline and Candidate both reach Target; Delta R is
   zero.
2. `TARGET_CLIPPED_BY_MANAGEMENT`: a Baseline Target becomes a managed Stop;
   Delta R must be negative.
3. `STOP_LOSS_IMPROVED_BY_MANAGEMENT`: a Baseline initial Stop becomes a
   managed Stop; Delta R must be positive.
4. `STOP_UNCHANGED`: both variants reach the initial Stop; Delta R is zero.
5. `AMBIGUOUS_QUARANTINE`: Candidate active-Stop and Target collide in one M5
   bar; Delta R is unknown and excluded.

Any other transition, non-zero Delta for an unchanged category, wrong Delta
sign, unresolved path, source-hash drift, report mismatch, or protected-state
drift fails closed.

## Frozen outputs

For each Candidate at `1.00x`, `1.25x`, and `1.50x`, report:

- category and outcome counts;
- paired Baseline/Candidate cumulative and Mean R;
- positive, negative, net, and Mean Delta R;
- positive/negative/zero paired-record counts;
- benefit-to-harm R ratio;
- the same decomposition for both directions and four chronological blocks.

Subgroup results are explanatory only. They cannot become Runtime filters or
new Candidates without a separately pre-registered confirmation contract.

## Safety and validation plan

The implementation is Python-only and reuses the strict request/path readers
and causal simulator validated in IMP-084. A focused synthetic test must cover
every category, paired accounting, ambiguity exclusion, Delta-sign enforcement,
and invalid-transition rejection. Complete Python regression follows. No MQL5
file changes, so no new MetaEditor target is affected; the last verified
IMP-084 compile remains `0 errors, 0 warnings`.

## Completed result

The diagnostic passed exact request/export/replay hash parity and accounted for
all 232 requests. Its SHA-256 is
`67DD536BC9C56C3E971EF4E349872AB6C59AE335AF39BE479BB27E811005CA52`.

| Candidate / cost | Paired N | Saved Stops | Clipped Targets | Ambiguous | Benefit R | Harm R | Net Delta R | Mean Delta R |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Breakeven 1.00x | 232 | 42 | 17 | 0 | +42.000 | -43.084 | **-1.084** | -0.0047 |
| Breakeven 1.25x | 232 | 42 | 18 | 0 | +42.000 | -42.624 | **-0.624** | -0.0027 |
| Breakeven 1.50x | 232 | 42 | 19 | 0 | +42.000 | -43.492 | **-1.492** | -0.0064 |
| Ratchet 1.00x | 230 | 42 | 22 | 2 | +47.953 | -54.984 | **-7.032** | -0.0306 |
| Ratchet 1.25x | 230 | 42 | 23 | 2 | +47.052 | -54.267 | **-7.215** | -0.0314 |
| Ratchet 1.50x | 230 | 42 | 24 | 2 | +46.001 | -55.044 | **-9.043** | -0.0393 |

At primary cost Breakeven improved 42 losing paths by approximately `+1R`
each, but each of its 17 clipped Targets lost about `2.53R` relative to
Baseline. Its benefit-to-harm ratio was `0.975`, so the rule was close to
balanced but still negative. Ratchet increased average benefit per saved Stop,
but clipped 22 Targets; its benefit-to-harm ratio fell to `0.872`. All cost
levels remained net negative.

## Direction and temporal attribution at 1.00x

| Candidate / group | Saved | Clipped | Net Delta R | Mean Delta R |
| --- | ---: | ---: | ---: | ---: |
| Breakeven BUY | 22 | 8 | +0.802 | +0.0066 |
| Breakeven SELL | 20 | 9 | -1.886 | -0.0171 |
| Ratchet BUY | 22 | 11 | -4.865 | -0.0402 |
| Ratchet SELL | 20 | 11 | -2.167 | -0.0199 |
| Breakeven block 1 | 15 | 5 | +2.885 | +0.0497 |
| Breakeven block 2 | 12 | 2 | +7.390 | +0.1274 |
| Breakeven block 3 | 7 | 7 | -11.231 | -0.1936 |
| Breakeven block 4 | 8 | 3 | -0.128 | -0.0022 |
| Ratchet block 1 | 15 | 7 | +1.508 | +0.0260 |
| Ratchet block 2 | 12 | 2 | +9.493 | +0.1637 |
| Ratchet block 3 | 7 | 8 | -13.292 | -0.2332 |
| Ratchet block 4 | 8 | 5 | -4.742 | -0.0832 |

The management effect is non-stationary: it helped during chronological blocks
1-2 but removed substantial value from the only strong Baseline period, block
3. Breakeven was slightly positive for BUY and negative for SELL; Ratchet was
negative in both directions. Chronological block and direction observations
were discovered after the Candidate result and therefore cannot be converted
into filters, thresholds, or a Runtime rule.

## Interpretation and decision

The causal finding is not that lifecycle management never helps. It helps many
individual losing paths, but the saved loss size is smaller than the value
destroyed when relatively few high-value winners are clipped. Uniform
management is therefore poorly matched to the varying quality of accepted
Setups and cannot repair the Baseline's negative selection expectancy.

Both IMP-084 management Candidates remain rejected. No further Breakeven,
Ratchet, Trailing, partial-close, or Stop-threshold search is authorized from
this evidence. The next research priority moves upstream to Train-only Setup
selection/Entry attribution using only the canonical Trend, Volatility,
Liquidity, and Session features. That diagnostic must remain descriptive and
cannot select a threshold without a separately pre-registered confirmation
contract.

## Score and validation

IMP-085 changes explanation, not strategy performance. RSCS-1.0 therefore
remains Research Quality `100.00`, Strategy Evidence `20.00`, Operational
Safety `100.00`, raw Overall `60.00`, and Hard-Gated Overall Readiness `49.00`
with `NO_GO_TRAIN`. The score delta from the IMP-084 Baseline is zero. The
Scorecard SHA-256 is
`7A79D16527848669E3E4CC4DCD6903B52537D370FF4F06324E8431B5684A6C07`.

The focused attribution test passed and complete Python regression passed
`53/53`. No MQL5 source changed; the last affected MetaEditor compile remains
IMP-084 `0 errors, 0 warnings`. Validation/Test/Forward remain sealed, broker
state is unchanged, and Runtime Change Request, Live Execution, and Deployment
remain unauthorized.
