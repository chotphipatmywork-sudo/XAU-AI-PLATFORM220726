# IMP-049 H1 Context Controlled Diagnostic

Status: Implemented and evaluated; mixed aggregate result, nested confirmation required.

## Purpose

`training/h1_context_diagnostic.py` compares the strict twelve-field Schema 4.0 Train tensor with the same tensor plus five closed-H1 Brain values. It is a pre-contract research diagnostic and cannot modify the canonical schema.

## Input validation

- The canonical Train reader remains strict Schema 4.0.
- The auxiliary header must exactly match the seven-field research contract.
- Rows join by both Dataset ID and Timestamp.
- Duplicate keys, missing Train keys, non-numeric values, and values outside `0..100` are rejected.
- Extra auxiliary rows are allowed because the auxiliary file covers the complete pre-split Dataset while the diagnostic consumes only Train.

## Method

The comparison fixes `random_forest_depth_10_hold_2`, raw probabilities, and argmax. It uses four expanding Train-only folds and purges 16 records before every evaluation period. Selection follows the established stable-gate and weakest-gate ordering. Validation and Test are not accepted as inputs.

## Validation

`training/test_h1_context_diagnostic.py` verifies the exact auxiliary header, five-field append order, strict missing-key rejection, and weakest-gate selection behavior.

The diagnostic output is association evidence only. A favorable result must undergo nested feature-set selection before CR-002 can request canonical Feature Schema approval.

## Result

The auxiliary file contained all 6,675 canonical Dataset rows, and all 4,656 Train keys joined exactly. H1 context raised aggregate BUY recall from `0.3373` to `0.3883` and the weakest-gate ratio from `0.8026` to `0.8109`, but reduced Accuracy from `0.4549` to `0.4377`, Macro F1 from `0.4236` to `0.3805`, and SELL precision from `0.5058` to `0.4876`. No fold passed the complete gate.

H1 improved the fold-level weakest gate in two periods and degraded it in two. This inspected mixed result is insufficient for CR-002 approval; IMP-050 performs nested feature-set selection before unseen Outer periods.
