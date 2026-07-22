# IMP-022 Label Calibration

Status: Implemented; pending MetaEditor compilation validation.

`CLabelCalibrator` evaluates the existing leakage-safe triple-barrier generator without writing a dataset or changing the active label configuration. The focused EA loads historical M15 bars and ATR(14), then reports BUY/HOLD/SELL distribution for the 1.00, 1.25, and 1.50 ATR barrier candidates at the approved 16-bar horizon.

The calibration objective is to find a candidate with sufficient HOLD representation for reliable three-class training while retaining enough BUY and SELL samples. A working target is 10% to 25% HOLD, subject to future walk-forward analysis. The test only measures label distribution; it does not claim predictive performance or approve a new configuration.

Calibration result: 1.50 ATR was selected. On 3,278 loaded M15 bars it produced 1,298 BUY, 346 HOLD, and 1,629 SELL labels (10.57% HOLD), compared with 2.04% HOLD at 1.00 ATR. Label Schema 1.1.0 therefore sets the active default to 16 bars and ±1.5 ATR(14).

`tests/TestLabelCalibration.mq5` remains read-only with respect to dataset CSV files.
