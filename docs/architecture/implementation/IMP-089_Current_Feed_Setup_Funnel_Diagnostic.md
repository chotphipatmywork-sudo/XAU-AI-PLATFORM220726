# IMP-089 Current-Feed Setup Funnel Diagnostic

Version: 1.0.0

Date: 2026-07-24

Status: Implemented and validated

Architecture Baseline: ABR-1.0

Related: IMP-076, IMP-079, IMP-088

## Purpose

The owner selected complete regeneration from the current `XAUUSD` broker feed
after IMP-088 proved that the preserved Setup Audit and the newly available M5
history were not parity-compatible. The complete `2020-01-01` through
`2026-06-30` real-tick run remained fail-closed and deployment-disabled, but
produced only 56 trainable structural plans. This diagnostic attributes that
sample shortage without changing Runtime, Risk, Entry, Target, minimum RR, or
the canonical AI Feature Schema.

## Frozen evidence and time boundary

The diagnostic accepts only Setup Audit SHA-256
`B6122AEA49F764055347B0459104DA53AD37EA815D2CC6568E4B0BC6885490F1`
with exact Setup Audit Schema 3.0.

Before opening Setup dispositions, the Train-only cutoff was preregistered as
`2024-07-01 00:00` exclusive. The reader stops at that timestamp. Later
evidence is not read for hypothesis selection; no Validation/Test file is
accepted by the tool.

## Measurements

The output reports the causal funnel:

`Observation -> POI -> Trigger -> Reversal Context -> Plan`

It also reports non-plan reason buckets and descriptive RR distribution among
trigger rows. It rejects chronological drift, causal-stage bypass, an accepted
plan below the frozen `2.0R` minimum, source-hash drift, or schema drift.

## Protected boundaries

- Feature Schema remains Trend, Volatility, Liquidity, and Session only.
- Brain does not approve Risk or execute.
- Risk remains the final permission gate.
- Validation/Test are not used for selection.
- No training, Runtime integration, order action, or deployment is possible.
- Status remains research `NO-GO`.

## Validation

`training/test_current_feed_setup_funnel.py` verifies cutoff sealing, funnel
counts, causal-stage ordering, the `2.0R` lock, and deployment locks. No MQL5
source is changed, so MetaEditor compilation is not required for IMP-089.

The focused test, Stage D Dataset regression, Objective Setup diagnostic
regression, and Python syntax validation passed. The Train-only result contains
104,891 observations, 7,431 confirmed POIs, 1,465 triggers, 597 reversal
contexts, and 31 accepted plans. Of the non-plan rows, 508 were rejected
because the nearest structural Target was below the frozen `2.0R` minimum.
Only 31 of 1,465 trigger rows had RR at or above `2.0R`; median trigger RR was
`0.0R` and the 75th percentile was `0.423R`.

The 31 mature Train-only outcomes contain 7 `TARGET_FIRST` and 24
`STOP_FIRST`, with mean cost-aware return `-0.120R`. Two of four descriptive
chronological blocks and one of two directions were positive; the effective
sample remains below 200.

Diagnostic SHA-256:
`9350F0FD457A5BB4E61CE8990A22ABB31AEEE25A1504DBC7DFD018360BDB75C0`.
Research scorecard input is
`training/config/research_scorecard_imp089_current_feed_funnel.json`.

The resulting scorecard is Research Quality `100.00`, Strategy Evidence
`19.82`, Operational Safety `100.00`, and hard-gated Overall Readiness `49.00`
with status `NO_GO_TRAIN`. Relative to IMP-087, Strategy Evidence changed by
`-0.18`; this is a new-feed baseline reset, not a Runtime candidate result.
