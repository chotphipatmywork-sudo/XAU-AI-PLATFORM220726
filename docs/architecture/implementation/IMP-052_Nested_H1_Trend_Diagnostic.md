# IMP-052 Nested H1 Trend Diagnostic

Status: Implemented and evaluated; H1 Trend rejected.

## Purpose

IMP-051 found that the three closed-H1 Trend fields improved the weakest aggregate gate and three of four fold-level weakest gates, while H1 Volatility degraded the method. Because that decomposition followed inspection of the complete H1 result, `training/nested_h1_trend_diagnostic.py` registers the exact Baseline-versus-H1-Trend boundary and requires Inner selection before every unseen Outer period.

Model, raw probabilities, argmax policy, four Outer folds, three Inner folds, and the 16-record purge remain fixed. Validation and Test are not accepted. The shared nested runner is also used by IMP-050 to prevent method drift.

`training/test_nested_h1_trend_diagnostic.py` freezes the two feature-set names. Existing H1 join, group-width, nested-selection, and purge tests cover the remaining shared behavior.

This result remains development evidence because the research path was chosen after inspecting current Train periods. Even a favorable result requires fresh temporal evidence before a Feature Contract change.

## Result

Inner selection chose Baseline before Outer folds 1, 2, and 4 and H1 Trend only before fold 3. The complete Train Inner selection chose H1 Trend, but that late-history preference did not generalize across past Outer histories.

Aggregate Outer Accuracy was `0.4510`, Macro F1 `0.4127`, SELL precision `0.5000`, SELL recall `0.5563`, BUY precision `0.4027`, and BUY recall `0.3503`. No Outer fold passed the complete gate. H1 Trend is rejected for the canonical Feature Contract, and Validation/Test remain unread.
