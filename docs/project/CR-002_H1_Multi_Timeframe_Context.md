# CR-002 Proposed H1 Multi-timeframe Market Context

Version: 0.1.0

Date: 2026-07-16

Status: Research evaluated and rejected; no Feature Contract change

Architecture Baseline: ABR-1.0

Related Phase: Model Training and Deployment

## Problem

Feature Schema 4.0 passed its data and implementation gates but failed temporal model generalization. The nested Train-only process passed no Outer fold, and BUY precision/recall were materially below contract. Additional model and threshold search against inspected periods would introduce selection bias rather than new market information.

The M15 label horizon spans 16 bars, or four hours. Current features describe only the M15 Brain state and may omit the higher-timeframe direction and volatility regime governing that horizon.

## Proposed research boundary

Before changing the canonical feature tensor, export five past-only values from the existing Brain analyzers on H1:

1. H1 Trend Regime
2. H1 Trend Momentum
3. H1 Trend Slope
4. H1 Volatility Regime
5. H1 Volatility Change

The research file is auxiliary and keyed by the existing validated Dataset ID and Timestamp. It does not modify Feature Schema 4.0, the canonical CSV, live inference, Decision, Risk, Execution, or Trade Lifecycle.

## Leakage control

For an M15 record, observation time is the close of that M15 bar. Only an H1 bar whose close time is less than or equal to that observation time may be used. A currently forming H1 bar is forbidden. Historical and future live inference must use this same closed-bar rule.

## Feasibility

- Brain Trend and Volatility analyzers already accept arbitrary timeframe and historical shift.
- Historical Brain replay can analyze H1 without a second feature definition.
- `CTrendContext` already reserves higher-timeframe fields, although they are currently unused.
- A cache can reuse one closed H1 analysis across the corresponding M15 records.

## Potential approved implementation

If Train-only research shows stable improvement and the project owner explicitly approves the breaking change, append the five values within the existing Trend and Volatility groups and increment the Feature Schema MAJOR version. Historical replay and live Brain projection must remain identical. Schema 4.0 data and artifacts would become incompatible.

## Required evidence

1. Auxiliary exporter compiles with zero errors and warnings.
2. Closed-H1 timing test passes.
3. Auxiliary rows match all Train timestamps with no duplicates or missing values.
4. Fixed-method controlled comparison improves the weakest gate without reading Validation/Test.
5. Nested feature-set selection retains H1 context before unseen Outer periods.
6. Only then may Architecture, Interface, and Version approval be requested for a canonical schema change.

## Rollback

Delete the auxiliary research file and research-only exporter/test. Feature Schema 4.0 and all Runtime modules remain unchanged.

## Approval record

- Research-only diagnostic: Allowed under the active Model Training investigation
- Canonical Feature Contract change: Pending explicit project-owner approval
- Deployment approval: Not requested

## Research result

The auxiliary exporter wrote all 6,675 Dataset rows and passed the closed-bar timing contract. Strict ID/Timestamp joining covered all 4,656 Train records without reading Validation or Test.

The complete five-field H1 set improved aggregate BUY recall but reduced Accuracy, Macro F1, and SELL precision. Nested selection retained the complete set before three of four Outer periods but produced no passing fold and underperformed the fixed Schema 4.0 Baseline overall.

Exploratory ownership decomposition found that H1 Trend alone improved the weakest gate in three inspected folds, while H1 Volatility degraded the method. The registered nested Baseline-versus-H1-Trend confirmation then selected H1 Trend before only one of four unseen Outer periods. Aggregate Accuracy was `0.4510`, Macro F1 `0.4127`, BUY precision `0.4027`, and BUY recall `0.3503`; no Outer fold passed the complete gate.

## Decision

Reject CR-002 as a canonical Feature Schema change. Keep Schema 4.0 unchanged, do not add H1 fields to live Brain projection or historical training rows, and do not deploy any H1 research artifact. The auxiliary CSV may be retained only as reproducibility evidence.
