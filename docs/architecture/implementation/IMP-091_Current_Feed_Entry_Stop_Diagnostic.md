# IMP-091 Current-Feed Entry/Stop Path Diagnostic

Version: 1.0.0

Date: 2026-07-24

Status: Completed; lifecycle evidence required

Architecture Baseline: ABR-1.0

Related: IMP-083, IMP-089, IMP-090

## Purpose

IMP-090 found no current, M5, or M15 structural Target candidate that passed
the Train-only gate. IMP-091 therefore measures whether current Entry/Stop
geometry, rather than Target selection alone, explains the negative result.
It is descriptive and cannot select or integrate an Entry or Stop candidate.

## Frozen inputs and bins

The diagnostic reuses the 597 hash-locked IMP-090 requests/export and exact
current-feed Setup Audit and Decision hashes. It reads only observations and
outcomes known before `2024-07-01 00:00`.

Before execution, these fixed buckets were registered:

- gross reward/risk: `<0.5`, `0.5–1.0`, `1.0–2.0`, `>=2.0`;
- structural Stop distance in reconstructed ATR: `<0.5`, `0.5–1.0`,
  `1.0–1.5`, `>=1.5`;
- trigger engulfment ATR: `<0.25`, `0.25–0.5`, `0.5–1.0`, `>=1.0`;
- reclaim ATR: `<0.10`, `0.10–0.25`, `0.25–0.50`, `>=0.50`.

The tool also counts stopped paths that first achieved at least `0.5R` or
`1.0R` MFE. Same-bar Target/Stop collisions remain ambiguous.

## Protected boundaries

- Observations below `2.0R` are diagnostic counterfactuals, not authorized
  trades and do not weaken the minimum RR gate.
- Validation/Test are not used.
- No candidate, model, Runtime, Risk, Execution, or Deployment change occurs.
- ABR-1.0 and the canonical Feature Schema remain unchanged.

## Validation

The focused test verifies bucket boundaries, path accounting, candidate locks,
and Deployment false. No MQL5 source changes, so MetaEditor compilation is not
required.

## Train-only result

Of 597 requests, 574 had known Entry/cost geometry. Eighteen M15 paths were
ambiguous, leaving 556 descriptive paths:

- 303 `TARGET_FIRST`, 253 `STOP_FIRST`;
- gross mean return `+0.025R`;
- 100 stopped paths first reached at least `+0.5R`;
- 28 stopped paths first reached at least `+1.0R`.

The payoff relationship is adverse. Rows below `0.5R` gross reward/risk have
an 80.95% Target rate but only `+0.042R` mean return. Rows at or above the
frozen `2.0R` have a 25.35% Target rate and `-0.107R` mean return. Thus simply
enforcing higher structural payoff removes the high-hit-rate portion without
creating positive expectancy.

Stop distance `0.5–1.0 ATR` and trigger engulfment below `0.25 ATR` are
descriptively positive, but neither is authorized as a filter or Stop
candidate because the complete result is positive in only two of four
chronological blocks. Current M15 evidence also cannot establish intrabar
profit-giveback ordering.

The next admissible evidence step is a current-feed causal M5 lifecycle replay
for the same frozen contexts. Breakeven, ratchet, or trailing behavior must not
be selected before that evidence is collected.

Diagnostic SHA-256:
`12D5D6820C0D9CEC5F23CE426AA99736436D470B839B10DC5474C4985543C76D`.
Three relevant regressions and Python syntax validation passed. The IMP-089
scorecard remains the accepted baseline and status remains `NO_GO_TRAIN`.
