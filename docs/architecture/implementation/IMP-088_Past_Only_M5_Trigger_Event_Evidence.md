# IMP-088 Past-Only M5 Trigger Event Evidence

Version: 1.2.0

Date: 2026-07-23

Status: Implemented and compile-clean; MT5 collection pending

Architecture Baseline: ABR-1.0

Related: ADR-006, IMP-079, IMP-084, IMP-087

## Approval and purpose

The user explicitly approved the next evidence-collection step after IMP-087.
Collect missing M5 trigger-event detail for the 232 hash-sealed Effective Train
Setups before any new strategy hypothesis is selected. This change creates an
offline tester-only Artifact contract; it does not change the canonical
Feature Schema, Setup decision, Trade Plan, Risk, Execution, lifecycle, or
Runtime flow.

## Frozen source contract

The request builder must reuse the complete IMP-087 strict join and verify:

- augmented Train SHA-256
  `F31E6DED4E0AC3B20FDD7964D3E634902736C8AD3316AA15A4E63D5C3C7E9A7E`;
- Effective Sample audit SHA-256
  `2646BBD8E881B6BB7F8621E27D1933BE1376711C75558E046B9EA964A1393414`;
- pre-Train Setup Audit SHA-256
  `A406B7EDADA6CACB5691487341294E5F950FF262D1CE8AE26EF958843338B8B8`;
- main Train Setup Audit SHA-256
  `A8463D7F118CB52A7B514099FF8B8839F3C2401ECA5A66F50376C4D87C1C9F7A`;
- Past-only Target manifest SHA-256
  `2D6A559F03245D40C0CB84ACAC1CC1C97D6F2017875ED3DF513D5C54F9C4C6BF`;
- IMP-086 SHA-256
  `A281F29D0CD25E9DCE894BF03F486BA6F7426014DF4F1BFD31DFA29BAA0DBC27`;
- IMP-087 SHA-256
  `40B1A1D46F7C20A960C22AD60FC4B4FEF612DAAA569BCDBE823AACB5FA60E039`.

Requests contain no outcome label. They retain only exact observation time,
direction, trigger/context M5 opens, Entry, POI, Stop, Target, expected
sweep/reclaim evidence, point size, a fixed 64-bar lookback, and
`deployment_authorized=false`.

## Causal exporter semantics

For each request, the isolated exporter must:

1. prove trigger open plus one completed M5 period equals observation time;
2. prove context and trigger bars are contiguous and fully closed;
3. replay the existing Brain at the historical trigger shift to obtain the
   same M5 ATR rather than defining a second ATR;
4. recompute confirmed swing structure and require exact POI/Target parity;
5. require Entry to equal trigger close within half a symbol point;
6. recompute sweep penetration and reclaim distance and require parity with
   the frozen Setup Audit;
7. read only trigger and older M5 bars.

The output contains raw trigger/context OHLC and these derived observations:

- trigger range, body, direction-aligned body, upper wick, and lower wick in
  M5 ATR units;
- trigger close location within its bar and context close location;
- context body and direction-aligned context body in ATR units;
- direction-aligned trigger follow-through from context close in ATR units;
- Entry drift from trigger close in ATR units;
- exact POI and Target structural-level ages in M5 bars;
- age of the most recent prior POI touch and prior POI-touch count over the
  frozen 64-bar lookback;
- explicit known-time, parity, and deployment flags.

All values are observations, not canonical AI features. Missing history,
non-finite values, invalid geometry, parity drift, ambiguous structural level,
or output failure deletes the partial export and fails closed.

## Protected boundaries

- the exporter is only callable from a focused research EA;
- request/output files live in MT5 `MQL5/Files` and project research output;
- no order function, Risk permission, Runtime provider, or live inference path
  is added;
- no outcome is used during evidence calculation;
- Validation/Test/Forward remain sealed;
- Deployment remains false and status remains NO-GO.

## Validation plan

Add focused Python tests for request chronology, exact 232-record contract,
outcome-label exclusion, and manifest locks. Add focused MQL5 tests for timing,
BUY/SELL geometry, bar-shape math, directional sweep/reclaim, and level-age
lookup. Sync only the new research source/test, compile the test EA in
MetaEditor, and require exactly `0 errors, 0 warnings` before collection.

After the user runs the exporter once, a strict collector will hash and
validate the export before any outcome attribution contract is written.

## Implementation evidence

The strict request builder produced exactly 232 chronological requests from
`2020.03.20 22:45` through `2025.07.15 09:30`. The request header contains no
Outcome field and the manifest confirms all protected flags false.

- request SHA-256:
  `79EC9BA7C7517406A3BBF419EF6D27D68358757E8BE7682972740E510B371882`;
- request manifest SHA-256:
  `5ADBBA1835D4B6FDF8D6C09CD5876878D87C98AB236FFB0B072D5295B1479870`;
- exporter source SHA-256:
  `BF0219B29866F18EE2D49A8673C9A0B261BD0EDFF3558815CFB77267FA8D21F4`;
- focused test EA SHA-256:
  `44D406111AE5E5E067B6205EF57A81F7B4A27BA9F9BBAC12C848D31297F7EDD9`.

The request was hash-verified after copying to the selected MT5 Terminal
`MQL5/Files`. The new exporter and test EA were hash-verified after targeted
sync into `MQL5/Experts/XAU-AI-PLATFORM`.

MetaEditor compiled `TestPastOnlyTriggerEventExporter.mq5` with exactly
`0 errors, 0 warnings`. Compile-log SHA-256 is
`0FFC1C6C9E4842C8710138C767E0BB8BDC731A3131D385FCED851E794A641EEC`.
The complete Python regression passed `57/57`.

No formal RSCS score changes at preparation time because no new evidence row
has been collected or joined to an outcome. The accepted Baseline remains
`100/20/100`, raw `60`, hard-gated Overall Readiness `49`, and
`NO_GO_TRAIN`.

## Collection handoff

Keep Algo Trading disabled. Attach `TestPastOnlyTriggerEventExporter` once to
an XAUUSD chart. The EA performs only file-based offline research, prints
synthetic contract checks, exports all requests, then calls `ExpertRemove()`.
Success requires `Past-only trigger-event records written: 232`.

After that message, run `tools/collect_trigger_event_research.ps1`. The
collector copies the Artifact by hash and validates all 232 rows before any
next attribution stage. A partial or malformed export is rejected.

## Broker-symbol suffix remediation

The first collection attempt on broker chart `XAUUSD.sc` failed closed at the
first request with MT5 error `4301` because the request correctly retained the
canonical symbol `XAUUSD`, while market history is registered under the broker
symbol `XAUUSD.sc`. No partial export survived and records written was `-1`.

Version 1.2 separates symbol roles without weakening identity checks:

- request `symbol` remains canonical `XAUUSD`;
- historical data uses the EA chart `_Symbol` by default, or explicit
  `DataSymbol` input;
- the broker symbol must begin with the canonical symbol;
- broker point size must exactly match the frozen request point size;
- export schema 1.1 records both `symbol` and `data_symbol` for provenance.

The remediated source/test were re-synced and recompiled with `0 errors, 0
warnings`; focused validation and the combined Python regression passed
`57/57`. Runtime, Risk, request hashes, and all NO-GO locks remain unchanged.
