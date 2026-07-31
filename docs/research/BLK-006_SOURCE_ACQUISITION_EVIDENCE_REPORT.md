# BLK-006 Source Acquisition Evidence Report

Version: 1.0.0

Status: Accepted — BLK-006 acquisition-stage closure

Document Type: Factual Acquisition Evidence Report

Architecture Baseline: ABR-1.0

## Purpose

Record factual evidence for the manually completed MT5 source acquisition under the approved OEG-001 scope.

## Governance Context

- OEG-001: GO WITH CONDITIONS
- BLK-005: CLOSED
- BLK-006 readiness: READY WITH CONDITIONS
- BLK-007: APPROVED WITH CONDITIONS

This report records acquisition only. It does not validate, manifest, hash, freeze, replay, backtest, or generate datasets.

## Approved Source Identity

- Provider: Vantage Markets
- Symbol: `XAUUSD`
- Timeframe: `M15`
- Proposed coverage: `2021-07-01 00:00:00 UTC` through `2026-06-30 23:59:59 UTC`
- Source ID: `SRC-XAUUSD-M15-VANTAGE-202107-202606-V1`

## Acquisition Environment

- Acquisition platform: MetaTrader 5
- Broker: Vantage Markets
- Account server: `VantageMarkets-Demo`
- Account type: Demo
- Symbol origin: Native server-provided `XAUUSD`; custom symbol: No
- Source timezone: SATISFIED — Vantage MetaTrader GMT+2 standard-time and GMT+3 daylight-saving conventions are recorded below
- Price convention: SATISFIED — artifact-specific Bid-based convention established below
- MT5 terminal version/build: Pending factual confirmation
- Acquisition operator: Project Owner and Acquisition Operator; relationship: PERFORMED EXPORT
- Export method: Native MetaTrader 5 Bars Export
- Acquisition timestamp: Approximate operator recollection; see acquisition record below

## Acquisition Procedure and OHLC Provenance

Evidence classification: DIRECT OPERATOR RECOLLECTION, corroborated by a DIRECT AUTHORIZED TECHNICAL OBSERVATION.

Procedure:

1. Open `View → Symbols → Bars`.
2. Select `XAUUSD` and `M15`.
3. Enter the requested From and To timestamps.
4. Click `Request` and wait for Bars data.
5. Click `Export`.
6. Enter the canonical filename and save directly as CSV using default MT5 settings.

Requested export range: `2021-07-01 00:00:00` through `2026-06-30 00:00:00`. This is not asserted as actual artifact coverage; actual coverage remains determined from the canonical CSV.

Export method: Native MetaTrader 5 Bars Export. External script, EA, indicator, third-party exporter, and intermediate conversion: None.

Original filename: `SRC-XAUUSD-M15-VANTAGE-202107-202606-V1.csv`.

Initial export directory: `C:\Users\poowa\Documents\Codex\XAU-AI-PLATFORM-replacement-artifacts\`.

Final canonical directory: `C:\Users\poowa\Documents\Codex\XAU-AI-PLATFORM-replacement-artifacts\source\raw\`.

Post-export handling: Single export; no rename, filtering, merge, editor resave, manual editing, or OHLC recalculation. File move only.

OHLC source linkage: `MT5 View → Symbols → Bars → Native Bars Request → Native MT5 Export → Automatic Open/High/Low/Close generation → Canonical CSV`.

Open, High, Low, and Close were generated automatically by MT5. No manual mapping or calculation occurred. CopyRates was not the acquisition method and is not required for this native export linkage.

Approximate export time: `2026-07-29 21:25` Thailand time (`2026-07-29 14:25 UTC`), based on direct operator recollection. No contemporaneous system timestamp is asserted.

## Authorized Technical Observation

Observation type: NEW AUTHORIZED TECHNICAL OBSERVATION

Observation UTC: `2026-07-30 03:04:53 UTC`

Observed environment: `VantageMarkets-Demo`, Vantage Markets (Pty) Ltd, demo account, native `XAUUSD`, custom symbol `false`, chart mode `SYMBOL_CHART_MODE_BID` (value `0`), calculation mode `SYMBOL_CALC_MODE_CFDLEVERAGE` (value `4`).

Integrity controls: no trade operation, export operation, symbol-property modification, or source-artifact modification was performed.

The observation occurred after export and does not prove chart mode at the precise export instant or historical chart-mode continuity throughout July 2021–June 2026. It was performed on the same identified server, account type, native symbol, and acquisition environment and was accepted as sufficient for export applicability under the approved reassessment.

## External Timezone Evidence Adoption

Adoption status: APPROVED FOR ADOPTION

Approval authority: Project Owner

Adoption date UTC: `2026-07-29`

Evidence authority: Vantage Markets

Approved evidence:

- *The Ultimate Gold Trading — Terms and Conditions* ([Vantage Markets](https://www.vantagemarkets.com/en/promotions/the-ultimate-gold-trading-tnc/))
- *Trade USOIL on MT4 & MT5 in South Africa* ([Vantage Markets](https://www.vantagemarkets.com/en-za/academy/how-to-trade-usoil-on-mt4-and-mt5-in-south-africa/))

Evidence access date UTC: `2026-07-29`

Approved technical facts:

- Vantage MetaTrader server time uses GMT+2 as standard time.
- Vantage MetaTrader server time may use GMT+3 during daylight-saving adjustment.
- When the applicable offset is GMT+2, UTC timestamp = source server timestamp - 02:00.
- When the applicable offset is GMT+3, UTC timestamp = source server timestamp - 03:00.

Evidence limitations:

- Historical daylight-saving transition dates are not inferred.
- The applicable offset for individual source records is not established.
- The exact export server or account identifier is not established.
- Timezone-dependent coverage is not fully resolved.

Repository recording is authorized for this report only. BLK-006 closure authorization is not granted by this adoption decision.

## External Price Convention Evidence Adoption

Adoption status: APPROVED FOR ADOPTION

Approval authority: Project Owner

Adoption date UTC: `2026-07-29`

Evidence classification: External authoritative platform evidence

Evidence authority: MetaQuotes Ltd

Approved evidence:

1. *Price Data in the Trading Platform* — [MetaTrader 5 Help](https://www.metatrader5.com/en/terminal/help/trading_advanced/price_data)
2. *View and Configure Charts* — [MetaTrader 5 Help](https://www.metatrader5.com/en/terminal/help/charts_analysis/charts)
3. *Symbol Properties — ENUM_SYMBOL_CHART_MODE* — [MQL5 Reference](https://www.mql5.com/en/docs/constants/environment_state/marketinfoconstants)
4. *CopyRates* — [MQL5 Reference](https://www.mql5.com/en/docs/series/copyrates)
5. *MqlRates* — [MQL5 Reference](https://www.mql5.com/en/docs/constants/structures/mqlrates)

Approved general technical facts:

- MetaTrader 5 OTC charts and OTC M1 bars are based on Bid prices.
- Higher-timeframe bars are constructed from underlying M1 bars.
- MetaTrader 5 supports symbol-specific Bid and Last chart modes.
- `SYMBOL_CHART_MODE_BID` means chart bars are based on Bid prices.
- `SYMBOL_CHART_MODE_LAST` means chart bars are based on Last prices.
- `CopyRates` retrieves historical bar data represented by `MqlRates` structures.
- `MqlRates` contains time, open, high, low, close, volume, and spread-related fields.

Adoption scope: General MetaTrader 5 chart-price and historical-bar semantics only.

Artifact-specific applicability is established by the approved operator record and authorized observation recorded in this report. The canonical CSV used native MT5 Bars Export, not CopyRates; the observed native symbol used `SYMBOL_CHART_MODE_BID`; no price-side transformation occurred; and raw OHLC preservation is established. Exact chart mode at the export instant and historical continuity remain limitations.

Price Convention blocker status: CLOSED.

## Raw Artifact Identity

- Raw file path: `C:\Users\poowa\Documents\Codex\XAU-AI-PLATFORM-replacement-artifacts\source\raw\SRC-XAUUSD-M15-VANTAGE-202107-202606-V1.csv`
- File size: `7393765` bytes
- Total line count: `117997`
- Header line count: `1`
- Data record count: `117996`
- CreationTimeUtc: `2026-07-29 14:23:27`
- LastWriteTimeUtc: `2026-07-29 14:23:28`

No SHA-256 value is recorded by this report.

## Backup Evidence Recording

Source artifact: `C:\Users\poowa\Documents\Codex\XAU-AI-PLATFORM-replacement-artifacts\source\raw\SRC-XAUUSD-M15-VANTAGE-202107-202606-V1.csv`

Backup destination artifact: `D:\XAU-AI-BACKUP\SRC-XAUUSD-M15-VANTAGE-202107-202606-V1.csv`

Filename verification:

- Source filename: `SRC-XAUUSD-M15-VANTAGE-202107-202606-V1.csv`
- Destination filename: `SRC-XAUUSD-M15-VANTAGE-202107-202606-V1.csv`
- Filename match: CONFIRMED

File-size verification:

- Source size: `7,393,765` bytes
- Destination size: `7,393,765` bytes
- File-size match: CONFIRMED

File-count verification:

- Source file count: `1`
- Destination file count: `1`
- File-count match: CONFIRMED

Filesystem timestamp evidence was observed during the prior read-only verification. These timestamps are filesystem metadata only; they are not export timestamps, acquisition timestamps, backup-verification activity timestamps, or proof of exact copy time.

Copy completion: CONFIRMED.

Evidence basis: Project Owner factual confirmation that the approved artifact was copied, corroborated by read-only filesystem observation of destination existence, matching filename, matching byte size, and matching file count.

Backup verification result: PASS.

Backup verification activity timestamp: NOT RECORDED. This is NOT NORMATIVELY REQUIRED for BLK-006 acquisition closure.

Backup operator identity: NOT RECORDED. This is NOT AUTOMATICALLY REQUIRED for BLK-006 acquisition closure.

Backup hash: NOT GENERATED — DEFERRED BY CURRENT SCOPE.

Source manifest: NOT GENERATED — DEFERRED TO MANIFEST PHASE.

Backup evidence recording: COMPLETE.

## Export Schema

The export schema is:

```text
<DATE> <TIME> <OPEN> <HIGH> <LOW> <CLOSE> <TICKVOL> <VOL> <SPREAD>
```

The file uses MT5 whitespace/tab-delimited bars with a `.csv` extension. Exported values are OHLC, tick volume, real volume, and spread.

## Record Reconciliation

The reported MT5 line count reconciles as:

```text
117996 data bars + 1 header = 117997 total lines
```

This is a factual count reconciliation only and is not a market-data quality validation.

## Actual Coverage

- Actual first record: `2021.07.01 01:00:00`
- Actual last record: `2026.06.29 23:45:00`

## Coverage Deviation

- Requested start: `2021-07-01 00:00:00 UTC`
- Actual first record: `2021.07.01 01:00:00`
- Requested end: `2026-06-30 23:59:59 UTC`
- Actual last record: `2026.06.29 23:45:00`

The adopted evidence defines the applicable GMT+2 and GMT+3 conversion rules, but does not establish which offset applies to individual source records or provide historical daylight-saving transition dates. The difference remains **TIMEZONE-DEPENDENT COVERAGE: UNRESOLVED**. Historical daylight-saving transition dates have not been established, the applicable GMT+2 or GMT+3 offset has not been assigned to individual records, and complete-period historical continuity has not been independently established. It is not classified as invalid data by this report.

## Pending Metadata

- Exact broker/server/feed identifier
- Timezone-dependent coverage and historical per-record offset applicability
- MT5 terminal version/build

Approved backup destination status: CREATED at `D:\XAU-AI-BACKUP`.

## Execution Constraints

The artifact may proceed only through the separately approved acquisition evidence and validation gates. Source Identity changes require Project Owner approval. Runtime, Risk, Execution, Live Trading, and Production activities remain outside scope.

## Prohibited Activities

This report does not authorize SHA-256 calculation, manifest generation, market-data validation, source freeze, replay, backtest, dataset generation, model training, or Runtime/Risk/Execution changes.

## Readiness Conclusion

- Acquisition execution: COMPLETED
- Raw artifact: EXISTS
- Record reconciliation: PASS for reported MT5 line count
- BLK-006 final acceptance: APPROVED
- Backup requirement: SATISFIED and recorded
- Source timezone metadata: RESOLVED
- UTC conversion rule: RESOLVED
- Timezone-dependent coverage: UNRESOLVED
- Price convention: RESOLVED
- Export/Acquisition Method: RESOLVED
- OHLC source linkage: RESOLVED
- Price-side transformation: NO TRANSFORMATION ESTABLISHED
- Raw OHLC preservation: ESTABLISHED

## BLK-006 Final Acceptance Readiness Review

### Result

FAIL

### Review Findings

- Governance compliance: PASS
- Raw artifact identity: PASS
- File size and timestamps: PASS
- Record reconciliation: PASS
- Coverage assessment: PASS (timezone/session deviation deferred)
- External timezone evidence adoption: COMPLETE
- Operator factual evidence: ADMISSIBLE
- Authorized technical observation: VALID
- Export/Acquisition Method: RESOLVED
- Artifact-specific Price Convention: RESOLVED
- Backup requirement: SATISFIED and recorded
- Timezone-dependent coverage: DEFERRED TO VALIDATION PHASE
- MT5 terminal version/build: OPTIONAL SUPPORTING METADATA
- Chain-of-custody completion: DEFERRED TO MANIFEST OR FREEZE PHASE
- Remaining mandatory evidence blockers: NONE
- Source timezone normative compliance: SATISFIED
- UTC conversion compliance: SATISFIED
- Exact export server/account identity: NOT NORMATIVELY REQUIRED for closing this specific metadata blocker
- Source timezone metadata blocker: CLOSED
- Timezone-dependent coverage: UNRESOLVED
- Chain of Custody: PARTIAL
- Evidence completeness: PARTIAL
- Operational metadata: PENDING
- Independent backup: PASS and recorded

Approved backup destination: CREATED

Backup copy: CONFIRMED

Backup verification: PASS

Backup evidence: COMPLETE

### Final Acceptance Recommendation

Project Owner Final Acceptance: APPROVED for BLK-006 acquisition-stage closure on `2026-07-30` UTC.

The acceptance applies only to the recorded acquisition evidence, accepted limitations, deferred items, and authorization boundaries. It does not authorize hashing, manifest generation, source freeze, or resolution of timezone-dependent coverage.

### Remaining Required Actions

#### Operational Metadata

- MT5 Version / Build

#### Independent Backup

Status: **COMPLETE**

The approved source artifact was copied to:

`D:\XAU-AI-BACKUP\SRC-XAUUSD-M15-VANTAGE-202107-202606-V1.csv`

The backup verification result is **PASS**. Source and destination records have matching filenames, byte sizes, and file counts. Copy completion is confirmed, backup evidence recording is complete, and the Backup Close-Out Blocker is closed.

No further BLK-006 acquisition-stage backup action is required.

Hash generation, manifest generation, chain-of-custody completion, immutable source freeze, and long-term audit controls remain deferred to their approved later phases.

#### Deferred Validation

- Resolve coverage deviation during the approved validation phase.

#### Governance

Status: **COMPLETE**

Project Owner Final Acceptance was approved and recorded on `2026-07-30`.

The BLK-006 acquisition evidence package was accepted, and acquisition-stage closure was approved.

No further BLK-006 acquisition-stage approval action remains.

### Blocker Disposition

- Export/Acquisition Method Requirement: SATISFIED
- Export/Acquisition Method Blocker: CLOSED
- Artifact-Specific Price Convention: SATISFIED
- Price Convention Blocker: CLOSED
- Source Timezone Metadata: RESOLVED
- UTC Conversion Rule: RESOLVED
- Export/Acquisition Method Blocker: CLOSED
- Price Convention Blocker: CLOSED
- Backup Close-Out Blocker: CLOSED
- Timezone-Dependent Coverage: UNRESOLVED
- Source Timezone Blocker: CLOSED
- Final Governance Action: PROJECT OWNER FINAL ACCEPTANCE — APPROVED AND RECORDED
- Git Close-Out: PENDING
- Other deferred items: UNAFFECTED

### Recommendation

ACCEPTED FOR ACQUISITION-STAGE CLOSURE

### Reason

Project Owner Final Acceptance has been recorded. BLK-006 acquisition-stage closure is approved; later validation, manifest, chain-of-custody, and freeze phases remain separate.

### Scope Statement

This review was performed strictly within the approved governance scope.

No technical validation beyond the approved scope was performed.

### Reassessment Traceability

This disposition was recorded from the approved BLK-006 Source Timezone Post-Adoption Closure Reassessment and the approved BLK-006 Operator and Technical Observation Integration Reassessment. No separate reassessment artifact is asserted.

## BLK-006 Project Owner Final Acceptance

Decision: APPROVED

Approval authority: Project Owner

Approval date UTC: `2026-07-30`

Accepted scope: BLK-006 Source Acquisition Evidence package for acquisition-stage closure.

Accepted findings:

- Canonical artifact identity is consistent.
- Source Timezone metadata and UTC conversion requirements are satisfied.
- Export/Acquisition Method and OHLC source linkage are satisfied.
- Artifact-specific Price Convention is satisfied.
- No price-side transformation is established and raw OHLC preservation is established.
- Backup copy completion is confirmed, verification is PASS, and evidence recording is complete.
- Remaining mandatory acquisition-evidence blockers: NONE.

Accepted deferred items and preserved limitations:

- Timezone-dependent coverage, historical DST determination, and per-record offset assignment.
- Hash, manifest, chain-of-custody, immutable freeze, and long-term audit controls.
- Exact MT5 terminal version/build and other optional metadata.
- Exact historical timezone applicability, exact export-instant chart mode, historical chart-mode continuity, and independent OTC classification.

Closure decision: BLK-006 acquisition evidence ACCEPTED; APPROVED FOR CANONICAL CLOSURE RECORDING.

BLK-006 current status: CLOSED for acquisition stage.

This approval does not authorize source modification, hashing, manifest generation, source freeze, timezone-dependent coverage resolution, commit, or push.

## References

OEG-001, BLK-005, BLK-006, BLK-007, BSA-001, BSV-001, BSM-001, BFP-001, and ABR-1.0.
