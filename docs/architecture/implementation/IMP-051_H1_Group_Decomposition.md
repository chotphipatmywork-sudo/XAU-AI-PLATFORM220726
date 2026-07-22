# IMP-051 H1 Group Decomposition

Status: Implemented and evaluated; H1 Trend selected for nested confirmation.

## Purpose

The complete five-field H1 context failed nested confirmation. This bounded exploratory diagnostic separates the existing Brain ownership groups to determine whether H1 Trend and H1 Volatility interfere when combined.

The four fixed sets are Schema 4.0 Baseline, Baseline plus three H1 Trend values, Baseline plus two H1 Volatility values, and Baseline plus all five values. Model, raw probabilities, argmax policy, four Train folds, and 16-record purge are unchanged.

## Interpretation limit

These Outer periods have already been inspected for the complete H1 set. This decomposition is research evidence only. A winning subgroup cannot authorize Schema 5.0 or deployment; it must first pass a separately registered nested comparison and later fresh-period evaluation.

`training/test_h1_group_diagnostic.py` verifies the exact group names, order, and feature widths.

## Result

H1 Trend ranked first with Accuracy `0.4579`, Macro F1 `0.4132`, BUY precision `0.4192`, BUY recall `0.4078`, and weakest-gate ratio `0.8384`. It improved the weakest gate in three of four folds. H1 Volatility ranked below Baseline, and combining it with H1 Trend reduced the full H1 result.

No set passed a complete fold or stable gate. IMP-052 therefore registers only Baseline versus the three-field H1 Trend subgroup for nested confirmation; this exploratory result cannot approve Schema 5.0.
