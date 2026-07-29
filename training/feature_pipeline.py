"""Deterministic, causal, standard-library feature extraction."""
from __future__ import annotations
import csv, hashlib, json, math
from pathlib import Path
from statistics import mean, pstdev
from datetime import datetime, timezone

FEATURE_NAMES = ("return_1", "return_3", "candle_range", "candle_body", "upper_wick", "lower_wick", "body_ratio", "range_ratio", "rolling_mean", "rolling_std")
IDENTITY = ("record_id", "symbol", "timestamp")

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""): h.update(chunk)
    return h.hexdigest().upper()

def register_feature_schema(version="1.0.0"):
    return {"feature_schema_version": version, "feature_names": list(FEATURE_NAMES), "feature_count": len(FEATURE_NAMES)}

def _value(value, places=12):
    return "" if value is None else f"{value:.{places}f}"

def generate_features(source: Path, output: Path, manifest: Path, source_identity: str, source_hash: str, rolling_window=3):
    with source.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f); fields = reader.fieldnames or []; rows = list(reader)
    required = set(IDENTITY) | {"open", "high", "low", "close"}
    missing = required - set(fields)
    if missing: raise ValueError(f"missing source columns: {sorted(missing)}")
    rows.sort(key=lambda r: (r["timestamp"], r["record_id"]))
    out_fields = list(IDENTITY) + list(FEATURE_NAMES)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=out_fields, lineterminator="\n"); w.writeheader(); closes=[]
        for row in rows:
            o,h,l,c = [float(row[k]) for k in ("open","high","low","close")]; closes.append(c)
            rng=h-l; prev=closes[-2] if len(closes)>1 else None
            vals=[c/prev-1 if prev else None, c/closes[-4]-1 if len(closes)>3 else None, rng, c-o, h-max(o,c), min(o,c)-l, (c-o)/rng if rng else 0.0, rng/c if c else 0.0, mean(closes[-rolling_window:]) if len(closes)>=rolling_window else None, pstdev(closes[-rolling_window:]) if len(closes)>=rolling_window else None]
            w.writerow({**{k:row[k] for k in IDENTITY}, **dict(zip(FEATURE_NAMES, map(_value, vals)))})
    payload={"manifest_version":"1.0.0","research_track_id":"CONTROLLED_RESEARCH_REGENERATION","feature_schema_version":"1.0.0","feature_set_id":"FEATURE-FOUNDATION-001","source_dataset_identity":source_identity,"source_dataset_sha256":source_hash,"feature_dataset_identity":output.stem,"feature_dataset_sha256":sha256(output),"feature_names":list(FEATURE_NAMES),"feature_count":len(FEATURE_NAMES),"record_count":len(rows),"labels_generated":False,"encoding":"UTF-8","newline":"LF","generated_at_utc":datetime.now(timezone.utc).isoformat().replace("+00:00","Z")}
    manifest.parent.mkdir(parents=True, exist_ok=True); manifest.write_text(json.dumps(payload,sort_keys=True,indent=2)+"\n",encoding="utf-8")

def validate_features(dataset: Path, manifest: Path, rolling_window=3):
    errors=[]
    with dataset.open(newline="",encoding="utf-8-sig") as f: r=csv.DictReader(f); fields=r.fieldnames or []; rows=list(r)
    expected=list(IDENTITY)+list(FEATURE_NAMES)
    if fields != expected: errors.append("non-deterministic feature ordering or columns")
    if len({x.get("record_id") for x in rows}) != len(rows): errors.append("duplicate record_id")
    seen_by_symbol = {}
    for row in rows:
        index = seen_by_symbol.get(row.get("symbol", ""), 0)
        seen_by_symbol[row.get("symbol", "")] = index + 1
        for n in FEATURE_NAMES:
            try:
                raw = row[n]
                if raw == "":
                    allowed = ((n == "return_1" and index == 0) or
                               (n == "return_3" and index < 3) or
                               (n in ("rolling_mean", "rolling_std") and index < rolling_window))
                    if not allowed: errors.append("unexpected empty feature value")
                elif not math.isfinite(float(raw)):
                    errors.append("invalid or non-finite feature value")
            except (KeyError,TypeError,ValueError): errors.append("missing or non-numeric feature value")
    if not manifest.is_file(): errors.append("manifest missing")
    else:
        m=json.loads(manifest.read_text(encoding="utf-8"));
        if m.get("feature_dataset_sha256") != sha256(dataset): errors.append("manifest/hash mismatch")
        if m.get("feature_dataset_identity") != dataset.stem or m.get("research_track_id") != "CONTROLLED_RESEARCH_REGENERATION": errors.append("manifest identity mismatch")
        if m.get("record_count") != len(rows): errors.append("record accounting mismatch")
        if m.get("feature_names") != list(FEATURE_NAMES) or m.get("feature_count") != len(FEATURE_NAMES): errors.append("feature schema mismatch")
    return sorted(set(errors))
