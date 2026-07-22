# IMP-006 Historical Labeling

Status: Implemented; pending MetaEditor compilation validation.

The training target is a three-class, volatility-adjusted triple-barrier label with a 16-bar horizon and 1.5 ATR(14) barriers for M15. The original 1.0 ATR baseline was calibrated against 3,278 historical bars and produced only 2.04% HOLD labels. The selected 1.5 ATR candidate produced 10.57% HOLD labels while retaining BUY and SELL coverage.

| Event | Label |
| --- | --- |
| Upper barrier reached first | BUY (+1) |
| Lower barrier reached first | SELL (-1) |
| Neither barrier reached within horizon | HOLD (0) |

Bars that reach both barriers inside one candle are excluded because M15 OHLC data cannot establish intrabar ordering. `CLabelGenerator` consumes only historical bars and ATR; it has no live inference, risk, or execution dependency.

IMP-064 corrected tail handling so a label is emitted only when all sixteen
future M15 bars are present. Shortened end-of-array horizons are excluded and
must never be treated as the approved Label Schema 1.1.0 target.
