"""Offline decision-record boundary; never grants Risk or Execution permission."""
from __future__ import annotations
import csv, hashlib, json
from pathlib import Path

FIELDS=("record_id","symbol","timestamp","ai_record_id","decision_id","decision","confidence","decision_configuration_version","status")

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest().upper()

def validate_records(path: Path) -> list[str]:
    with path.open(newline="",encoding="utf-8-sig") as f: r=csv.DictReader(f); fields=r.fieldnames or []; rows=list(r)
    errors=[]
    if fields != list(FIELDS): errors.append("decision schema or ordering mismatch")
    ids=[x.get("record_id","") for x in rows]
    if len(ids)!=len(set(ids)): errors.append("duplicate record_id")
    if any(not all(x.get(k) for k in FIELDS) for x in rows): errors.append("missing decision identity")
    for x in rows:
        try:
            confidence=float(x["confidence"])
            if not 0.0 <= confidence <= 1.0: errors.append("confidence out of range")
        except (ValueError,TypeError): errors.append("invalid confidence")
        if x["decision"] in ("RISK_APPROVED","EXECUTE","ORDER"): errors.append("prohibited decision status")
    if any((rows[i]["timestamp"],rows[i]["record_id"])>(rows[i+1]["timestamp"],rows[i+1]["record_id"]) for i in range(len(rows)-1)): errors.append("non-deterministic ordering")
    return sorted(set(errors))

def generate_manifest(records: Path, manifest: Path, parent_identities: dict) -> dict:
    errors=validate_records(records)
    if errors: raise ValueError("; ".join(errors))
    payload={"manifest_version":"1.0.0","decision_schema_version":"1.0.0","parent_identities":dict(sorted(parent_identities.items())),"decision_records_sha256":sha256(records),"record_count":len(open_records(records))}
    manifest.write_text(json.dumps(payload,sort_keys=True,indent=2)+"\n",encoding="utf-8"); return payload

def open_records(path):
    with path.open(newline="",encoding="utf-8-sig") as f: return list(csv.DictReader(f))

def validate_manifest(records: Path, manifest: Path, parent_identities: dict) -> list[str]:
    if not manifest.is_file(): return ["manifest missing"]
    data=json.loads(manifest.read_text(encoding="utf-8")); errors=[]
    if data.get("decision_records_sha256")!=sha256(records): errors.append("manifest/hash mismatch")
    if data.get("parent_identities")!=dict(sorted(parent_identities.items())): errors.append("parent identity mismatch")
    if data.get("record_count")!=len(open_records(records)): errors.append("record accounting mismatch")
    return errors
