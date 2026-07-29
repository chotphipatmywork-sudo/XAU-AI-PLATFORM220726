"""Offline inference-record boundary; consumes precomputed values only."""
from __future__ import annotations
import csv, hashlib, json
from pathlib import Path

FIELDS=("record_id","symbol","timestamp","inference_id","model_id","model_version","feature_set_version","configuration_version","output","confidence","status")

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest().upper()

def validate_records(path: Path) -> list[str]:
    with path.open(newline="",encoding="utf-8-sig") as f: r=csv.DictReader(f); fields=r.fieldnames or []; rows=list(r)
    errors=[]
    if fields != list(FIELDS): errors.append("inference schema or ordering mismatch")
    ids=[x.get("record_id","") for x in rows]
    if len(ids)!=len(set(ids)): errors.append("duplicate record_id")
    if any(not all(x.get(k) for k in FIELDS) for x in rows): errors.append("missing inference identity")
    for x in rows:
        try:
            if not 0.0 <= float(x["confidence"]) <= 1.0: errors.append("confidence out of range")
        except (ValueError,TypeError): errors.append("invalid confidence")
    if any((rows[i]["timestamp"],rows[i]["record_id"])>(rows[i+1]["timestamp"],rows[i+1]["record_id"]) for i in range(len(rows)-1)): errors.append("non-deterministic ordering")
    return sorted(set(errors))

def generate_manifest(records: Path, manifest: Path, parent_identities: dict) -> dict:
    errors=validate_records(records)
    if errors: raise ValueError("; ".join(errors))
    with records.open(newline="",encoding="utf-8-sig") as f: count=sum(1 for _ in csv.DictReader(f))
    data={"manifest_version":"1.0.0","inference_schema_version":"1.0.0","parent_identities":dict(sorted(parent_identities.items())),"inference_records_sha256":sha256(records),"record_count":count}
    manifest.write_text(json.dumps(data,sort_keys=True,indent=2)+"\n",encoding="utf-8"); return data

def validate_manifest(records: Path, manifest: Path, parents: dict) -> list[str]:
    if not manifest.is_file(): return ["manifest missing"]
    data=json.loads(manifest.read_text(encoding="utf-8")); errors=[]
    with records.open(newline="",encoding="utf-8-sig") as f: count=sum(1 for _ in csv.DictReader(f))
    if data.get("inference_records_sha256")!=sha256(records): errors.append("manifest/hash mismatch")
    if data.get("parent_identities")!=dict(sorted(parents.items())): errors.append("parent identity mismatch")
    if data.get("record_count")!=count: errors.append("record accounting mismatch")
    return errors
