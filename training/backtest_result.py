"""Offline closed-trade result and metric calculation."""
from __future__ import annotations
import csv, hashlib, json, math
from datetime import datetime
from pathlib import Path

TRADE_FIELDS = ("record_id", "decision_id", "symbol", "entry_timestamp", "exit_timestamp", "side", "entry_price", "exit_price", "quantity", "cost", "pnl", "exit_reason")

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""): h.update(chunk)
    return h.hexdigest().upper()

def _read(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f: return list(csv.DictReader(f))

def build_results(events: Path, output: Path, cost: float | None = None) -> None:
    if cost is None: raise ValueError("explicit cost required")
    rows = _read(events); open_rows = {}
    results = []
    for row in rows:
        rid = row.get("record_id", "")
        if row.get("event_type") == "ENTRY":
            if rid in open_rows: raise ValueError("duplicate entry")
            open_rows[rid] = row
        elif row.get("event_type") == "EXIT":
            entry = open_rows.pop(rid, None)
            if entry is None: raise ValueError("exit without entry")
            try:
                entry_time = datetime.fromisoformat(entry.get("timestamp", "").replace("Z", "+00:00")); exit_time = datetime.fromisoformat(row.get("timestamp", "").replace("Z", "+00:00"))
                if entry_time.tzinfo is None or exit_time.tzinfo is None: raise ValueError
            except ValueError: raise ValueError("invalid UTC timestamp")
            if exit_time < entry_time: raise ValueError("non-causal exit")
            try:
                ep, xp, qty, fee = float(entry["price"]), float(row["price"]), float(entry["quantity"]), float(cost)
                if not all(math.isfinite(v) for v in (ep, xp, qty, fee)) or qty <= 0: raise ValueError
            except (KeyError, TypeError, ValueError): raise ValueError("invalid trade values")
            gross = (xp - ep) * qty if entry.get("side") == "BUY" else (ep - xp) * qty
            results.append({"record_id": rid, "decision_id": entry.get("decision_id", ""), "symbol": entry.get("symbol", ""), "entry_timestamp": entry.get("timestamp", ""), "exit_timestamp": row.get("timestamp", ""), "side": entry.get("side", ""), "entry_price": entry.get("price", ""), "exit_price": row.get("price", ""), "quantity": entry.get("quantity", ""), "cost": f"{fee:.10f}", "pnl": f"{gross-fee:.10f}", "exit_reason": row.get("exit_reason", "")})
    if open_rows: raise ValueError("open trade without exit")
    results.sort(key=lambda r: (r["exit_timestamp"], r["record_id"]))
    with output.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(TRADE_FIELDS), lineterminator="\n"); w.writeheader(); w.writerows(results)

def metrics(results: Path) -> dict:
    rows = _read(results); pnls = [float(r["pnl"]) for r in rows]
    if any(not math.isfinite(v) for v in pnls): raise ValueError("non-finite pnl")
    wins = [v for v in pnls if v > 0]; losses = [v for v in pnls if v < 0]
    equity = peak = drawdown = 0.0
    for value in pnls:
        equity += value; peak = max(peak, equity); drawdown = max(drawdown, peak - equity)
    if not pnls or not losses: raise ValueError("undefined metric denominator")
    return {"trade_count": len(pnls), "net_pnl": f"{sum(pnls):.10f}", "win_rate": f"{len(wins)/len(pnls):.10f}", "profit_factor": f"{sum(wins)/abs(sum(losses)):.10f}", "max_drawdown": f"{drawdown:.10f}"}

def validate_results(results: Path) -> list[str]:
    rows = _read(results); errors = set(); ids = [row.get("record_id", "") for row in rows]
    if len(ids) != len(set(ids)): errors.add("duplicate trade record_id")
    for row in rows:
        if row.get("side") not in {"BUY", "SELL"}: errors.add("invalid side")
        if row.get("exit_reason") not in {"STOP", "TARGET", "TIMEOUT", "END_OF_DATA"}: errors.add("invalid exit reason")
        try:
            if not math.isfinite(float(row.get("pnl", "nan"))): errors.add("non-finite pnl")
        except ValueError: errors.add("invalid pnl")
    return sorted(errors)

REQUIRED_METADATA = ("cost_configuration_hash", "validation_report_id", "git_commit", "environment_id", "generation_command", "acceptance_status", "storage_location", "backup_status")

def generate_manifest(results: Path, manifest: Path, parent_identities: dict, metadata: dict | None = None) -> dict:
    result_errors = validate_results(results)
    if result_errors: raise ValueError("; ".join(result_errors))
    metadata = metadata or {}
    missing = [key for key in REQUIRED_METADATA if not metadata.get(key)]
    if missing: raise ValueError("missing manifest metadata: " + ", ".join(missing))
    data = {"manifest_version":"1.0.0", "result_schema_version":"1.0.0", "parent_identities":dict(sorted(parent_identities.items())), "results_sha256":sha256(results), "record_count":len(_read(results)), "metrics":metrics(results), **dict(sorted(metadata.items()))}
    manifest.write_text(json.dumps(data, sort_keys=True, indent=2, allow_nan=False)+"\n", encoding="utf-8"); return data

def validate_manifest(results: Path, manifest: Path, parent_identities: dict) -> list[str]:
    if not manifest.is_file(): return ["manifest missing"]
    data=json.loads(manifest.read_text(encoding="utf-8")); errors=[]
    if data.get("results_sha256") != sha256(results): errors.append("manifest/hash mismatch")
    if data.get("parent_identities") != dict(sorted(parent_identities.items())): errors.append("parent identity mismatch")
    if data.get("record_count") != len(_read(results)): errors.append("record accounting mismatch")
    return errors
