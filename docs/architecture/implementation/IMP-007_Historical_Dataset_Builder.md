# IMP-007 Historical Dataset Builder

Status: Feature Schema 3.0.0 implemented; local MetaEditor compilation passed.

## Purpose

`CHistoricalDatasetBuilder` persists replayed Brain analysis with labels generated from historical M15 bars. It accepts aligned `MqlRates`, `CBrainAnalysisResult`, and ATR arrays ordered from oldest to newest.

## Feature Contract (Schema 3.0.0)

The builder uses `CBrainFeatureAdapter`, which maps the canonical Brain outputs without deriving a second, incompatible feature definition:

| AI feature | Brain output |
| --- | --- |
| Trend regime | ATR-normalized EMA 50/200 regime component, clamped to 0..100 |
| Trend momentum | ATR-normalized EMA 50 movement over 16 completed bars, clamped to 0..100 |
| Trend slope | ATR-normalized current EMA 50 slope component, clamped to 0..100 |
| Volatility regime | Current ATR divided by the preceding 16-value ATR average, mapped around neutral 50 |
| Volatility change | Existing short ATR-change confidence mapped around neutral 50 |
| Liquidity activity | Existing `Liquidity.Score` |
| Liquidity range position | Close position inside the preceding 10-bar high/low range, 0..100 |
| Liquidity sweep direction | Buy-side sweep `0`, no/double sweep `50`, sell-side sweep `100` |
| Session Asia/London/New York | Three-field one-hot encoding using `100/0/0`, `0/100/0`, or `0/0/100` |

The canonical feature groups remain Trend, Volatility, Liquidity, and Session. Schema 3.0.0 contains eleven model dimensions because the approved groups are expanded without adding any new group. Existing runtime Trend, Volatility confidence, Liquidity score, Decision, label generation, Risk, and Execution behavior remain unchanged.

## Boundary

The component requires historical replay to supply one Brain result and ATR value per bar. It has no dependency on live execution, risk approval, or trading decisions.
