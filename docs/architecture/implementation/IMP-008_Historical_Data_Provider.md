# IMP-008 Historical Data Provider

Status: Implemented; pending MetaEditor compilation validation.

`CHistoricalDataProvider` belongs to the Data layer and loads MQL5 historical rates and ATR values for a bounded time range. It performs retrieval only: no Brain analysis, feature construction, labeling, training, risk evaluation, or order activity.

The caller must verify that rates and ATR arrays are aligned before passing them to a replay or dataset workflow. This avoids hidden assumptions about missing history or indicator warm-up periods.

`tests/TestHistoricalDataProvider.mq5` is the focused compile and smoke-test entry point.
