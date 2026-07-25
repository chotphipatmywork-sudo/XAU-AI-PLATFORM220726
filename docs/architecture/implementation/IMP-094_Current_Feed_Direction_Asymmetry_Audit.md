# IMP-094 Current-Feed Direction Asymmetry Audit

Version: 1.0.0

Date: 2026-07-24

Status: Completed; hypothesis not confirmed

Architecture Baseline: ABR-1.0

Related: IMP-089 through IMP-093

## Purpose

Repeated Train-only diagnostics show weaker BUY outcomes and occasionally
positive SELL outcomes. IMP-094 tests whether that observation is sufficiently
sampled and stable to be called a confirmed hypothesis. It does not create a
direction filter.

## Frozen confirmation contract

Each direction requires at least 40 mature records. SELL must be positive, BUY
must be negative, and the underlying candidate must already pass its complete
frozen Train gate. Failing any condition leaves the result hypothesis-only.

Validation/Test remain sealed. Runtime, Risk, Execution, minimum RR, and
Deployment remain unchanged. A historical direction result cannot authorize
SELL-only Runtime behavior; independent post-cutoff confirmation is required.

## Result

The baseline showed BUY `19 / -0.501R` versus SELL `12 / +0.119R`. M15 Stop 1
showed BUY `24 / -0.433R` versus SELL `18 / +0.309R`. Both observations failed
the minimum 40 records per direction and their underlying candidates failed
the complete Train gate.

M5 Stop 1 was the only candidate with at least 40 records in both directions
(BUY 109, SELL 79), but both directions remained negative and the candidate
failed its Train gate. Therefore no candidate confirmed direction asymmetry.

The SELL advantage remains a research hypothesis only. It must not become a
SELL-only filter or a Runtime change without independent post-cutoff evidence.

- Focused diagnostic test: passed.
- Direction filter created: false.
- Runtime change request authorized: false.
- Deployment: NO-GO.
- Source Stop replay SHA-256:
  `0D6AA7B95A9D154E760BC4167D7C99B50C7165BE85E35C5C113F6B454A5A2A45`
- Direction audit SHA-256:
  `5C01A76D69621988807A5688A49A0AC3F7FC57791F9D5160F04ED868B467E353`
