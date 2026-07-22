# XAU AI PLATFORM — Agent Working Rules

## Source of truth

Work only within this repository. Preserve the documented Architecture Baseline ABR-1.0 and treat the documents in `docs/project/` and `docs/architecture/adr/` as governing constraints.

## Protected runtime boundaries

The canonical business flow is:

`Market -> Brain -> AI Runtime -> Decision -> Risk -> Execution -> Trade Lifecycle`

- Brain provides market understanding; it must not approve risk or execute orders.
- Risk is the final permission gate before Execution.
- Execution receives only risk-approved decisions and must not bypass Risk.
- Do not introduce reverse or circular dependencies.
- A change to module boundaries, public contracts, runtime flow, or folder structure requires explicit user approval and corresponding documentation.

## AI learning rules

- The canonical AI feature set contains only Trend, Volatility, Liquidity, and Session.
- Keep features, labels, confidence, risk, and execution results as distinct data concepts.
- Live inference must remain independent from offline training and dataset generation.
- Historical labels use the approved 3-class, volatility-adjusted triple-barrier configuration: M15, 16 bars, and +/- 1.5 ATR(14). This was selected by the documented label calibration; any further change requires a new calibration and schema-version review.
- Historical dataset features must come from replayed Brain output; do not create a second incompatible feature definition.

## Implementation rules

- One class per `.mqh` file; name the file after its primary class.
- Include only necessary dependencies and follow the approved dependency direction.
- Add the standard project/file/layer/version/purpose header to each source file.
- Keep each class and function focused on a single responsibility.
- Do not add placeholders, dead code, or unrelated refactors.

## Validation and handoff

For every code change:

1. Update the applicable architecture or implementation document.
2. Add or update the focused test EA under `tests/`.
3. Check local include paths and dependency direction.
4. Compile the affected test in MetaEditor; report errors and warnings exactly.
5. Summarize modified files, validation result, known limitations, and the next phase.
