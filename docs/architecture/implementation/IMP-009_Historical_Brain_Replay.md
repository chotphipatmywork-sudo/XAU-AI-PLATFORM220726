# IMP-009 Historical Brain Replay

Status: Implemented; Session parity correction pending MetaEditor validation.

`CHistoricalBrainReplay` evaluates the existing Brain analyzers at a requested MQL5 bar shift. The new `Shift` field in indicator and Brain contexts is a backward-compatible extension: live callers keep the default value of zero.

The provider manager adds the configured base shift to EMA and ATR requests, so an analysis at historical shift `N` uses indicators available at that bar and its preceding bars, not data from later bars.

The replay output is intended for `CHistoricalDatasetBuilder`. It does not access AI inference, Risk, Execution, or Trade Lifecycle.

IMP-067 corrects the replay observation contract so Session is evaluated at the
completed bar time (`bar open + timeframe duration`), matching Runtime Brain.
The Dataset record timestamp remains the bar-open identity. This calculation
does not read a later bar or any future price.
