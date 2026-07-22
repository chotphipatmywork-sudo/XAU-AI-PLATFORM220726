# IMP-064 Full Label Horizon Enforcement

Status: Focused runtime passed; awaiting corrected Dataset evidence.

Related: Label Schema 1.1.0, IMP-006, IMP-022, Phase 7 closure

## Defect

`CLabelGenerator` previously shortened its future window at the end of a loaded
historical array by using the final available bar. Up to the final fifteen
eligible feature rows could therefore receive a target based on fewer than the
approved sixteen future M15 bars.

This was not look-ahead leakage, but it violated the fixed target definition
and changed the probability of HOLD near the Dataset boundary.

## Correction

The generator now requires:

`entry_index + HorizonBars < ArraySize(bars)`

If the complete future horizon is unavailable, label generation returns
`false` and Dataset generation excludes the row. The approved M15, 16-bar,
plus/minus 1.5 ATR(14), BUY/HOLD/SELL configuration is unchanged; Label Schema
remains 1.1.0 because the implementation is being corrected to its existing
contract rather than defining a new target.

## Focused validation

`tests/TestLabelGenerator.mq5` verifies:

- exactly sixteen future bars can generate BUY;
- a fifteen-bar future tail is rejected;
- a late entry with a shortened horizon is rejected;
- the complete full-horizon contract passes.

`tests/TestHistoricalDatasetBuilder.mq5` and
`tests/TestHistoricalDatasetOrchestrator.mq5` are recompiled to verify the
dependent Dataset path.

## Required evidence

1. MetaEditor compilation: zero errors and zero warnings for all three targets.
2. Focused runtime messages: every horizon assertion is `true`.
3. Regenerate the canonical historical Dataset without append mode.
4. Repeat Dataset, Split, Partition, and Readiness validation.
5. Do not reuse model evidence generated from the pre-correction Dataset.

Validation and Test remain protected. Deployment and live execution remain
unauthorized.

## Compile evidence

- workspace/MT5 SHA-256 verification: both synchronized files match;
- `tests/TestLabelGenerator.mq5`: 0 errors, 0 warnings;
- `tests/TestHistoricalDatasetBuilder.mq5`: 0 errors, 0 warnings;
- `tests/TestHistoricalDatasetOrchestrator.mq5`: 0 errors, 0 warnings.

## Focused runtime evidence

- exact 16-bar horizon BUY valid: true;
- truncated horizon rejected: true;
- late-entry shortened horizon rejected: true;
- complete full-horizon contract valid: true.
