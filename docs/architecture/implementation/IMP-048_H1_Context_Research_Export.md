# IMP-048 H1 Context Research Export

Status: Implemented and executed; research-only output complete.

## Purpose

`CHistoricalH1ContextExporter` creates an auxiliary research CSV from the already validated canonical Dataset. It replays the existing Brain on the most recent fully closed H1 bar and writes five Trend/Volatility values keyed by Dataset ID and Timestamp.

The exporter does not change Feature Schema 4.0 or any live Runtime contract. The auxiliary file is not accepted by the model trainer until a separate research diagnostic joins and validates every timestamp.

## Timing contract

The canonical historical M15 feature row represents the completed M15 bar. Its observation time is therefore `M15 open + 15 minutes`. An H1 bar is eligible only when `H1 open + 60 minutes <= observation time`. This prevents the exporter from reading a partially formed higher-timeframe bar.

## Files

- `core/ai/HistoricalH1ContextExporter.mqh`
- `tests/TestHistoricalH1ContextExporter.mq5`
- output: `XAU_AI_H1_CONTEXT_RESEARCH.csv` under `MQL5/Files`

## Safety

- The canonical dataset is opened read-only.
- The auxiliary output is replaced on each research run.
- Any missing H1 mapping, invalid Brain result, out-of-range value, or write failure terminates the export with `-1`.
- The Test EA calls `ExpertRemove()` after success or failure.
- No model, probability, decision, risk, or execution code is invoked.

## Local validation

`TestHistoricalH1ContextExporter.mq5` compiled with `0 errors / 0 warnings` in 1,925 ms. Runtime execution then used the broker's H1 history and the validated canonical Dataset under `MQL5/Files`.

For the configured terminal, `tools/sync_h1_research_to_mt5.ps1` copies only the exporter and focused EA into the MT5 project copy, clears a file-level Read-only attribute when necessary, and verifies SHA-256 equality. It does not copy or modify the canonical Dataset.

## Runtime result

The XAUUSD M15 run passed closed-H1 timing, exported all 6,675 canonical records, and called `ExpertRemove()` at `2026.07.16 09:29:41.692`. The CSV contains 6,676 lines including its header, is 720,256 bytes, and has SHA-256 `34816A67072ED2C33FE86503A8174DAC7327DF2E0ACC514733B47A718A101D22`.
