# IMP-011 Liquidity Engine

Status: Implemented; pending MetaEditor compilation validation.

The Liquidity Engine evaluates each bar against the preceding ten bars only. The context supplies the maximum reference high, minimum reference low, and average tick volume of that historical window.

The result provides a 0-100 score from relative tick volume, marks liquidity near reference highs/lows, and detects a sweep only when price breaks a reference level then closes back inside it. A confirmed sweep receives the highest score.

This is analysis data only. It does not approve risk, issue a trade decision, or execute orders.
