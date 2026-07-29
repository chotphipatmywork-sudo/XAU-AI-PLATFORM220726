"""Offline causal backtest evidence generator; never sends orders."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

FIELDS = ("record_id", "symbol", "timestamp", "decision_id", "event_id", "event_type", "side", "price", "quantity", "status")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _read(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def validate_events(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields, rows = reader.fieldnames or [], list(reader)
    errors = set()
    if fields != list(FIELDS): errors.add("backtest schema or ordering mismatch")
    ids = [row.get("event_id", "") for row in rows]
    if len(ids) != len(set(ids)): errors.add("duplicate event_id")
    for row in rows:
        if any(not row.get(field) for field in FIELDS): errors.add("missing event field")
        try:
            if float(row.get("price", "")) <= 0 or float(row.get("quantity", "")) <= 0: errors.add("invalid price or quantity")
        except (TypeError, ValueError): errors.add("invalid price or quantity")
    if any((rows[i]["timestamp"], rows[i]["event_id"]) > (rows[i + 1]["timestamp"], rows[i + 1]["event_id"]) for i in range(len(rows) - 1)):
        errors.add("non-deterministic ordering")
    return sorted(errors)


def run_backtest(decisions: Path, bars: Path, output: Path) -> None:
    decisions_rows, bars_rows = _read(decisions), _read(bars)
    bar_map = {(row.get("symbol"), row.get("timestamp")): row for row in bars_rows}
    events = []
    for decision in decisions_rows:
        key = (decision.get("symbol"), decision.get("timestamp"))
        bar = bar_map.get(key)
        if bar is None: raise ValueError("missing causal bar")
        side = decision.get("side", "")
        if side not in {"BUY", "SELL"}: raise ValueError("invalid side")
        price = bar.get("ask") if side == "BUY" else bar.get("bid")
        events.append({"record_id": decision.get("record_id", ""), "symbol": decision.get("symbol", ""), "timestamp": decision.get("timestamp", ""), "decision_id": decision.get("decision_id", ""), "event_id": "entry-" + decision.get("record_id", ""), "event_type": "ENTRY", "side": side, "price": price or "", "quantity": decision.get("quantity", "1"), "status": "RESEARCH_ONLY"})
    events.sort(key=lambda row: (row["timestamp"], row["event_id"]))
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(FIELDS), lineterminator="\n")
        writer.writeheader(); writer.writerows(events)


def generate_manifest(events: Path, manifest: Path, input_identities: dict) -> dict:
    errors = validate_events(events)
    if errors: raise ValueError("; ".join(errors))
    payload = {"manifest_version": "1.0.0", "backtest_schema_version": "1.0.0", "input_identities": dict(sorted(input_identities.items())), "events_sha256": sha256(events), "record_count": len(_read(events))}
    manifest.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return payload


def validate_manifest(events: Path, manifest: Path, input_identities: dict) -> list[str]:
    if not manifest.is_file(): return ["manifest missing"]
    data = json.loads(manifest.read_text(encoding="utf-8")); errors = []
    if data.get("events_sha256") != sha256(events): errors.append("manifest/hash mismatch")
    if data.get("input_identities") != dict(sorted(input_identities.items())): errors.append("input identity mismatch")
    if data.get("record_count") != len(_read(events)): errors.append("record accounting mismatch")
    return errors
