"""Offline AI-record boundary validation; no inference or model execution."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

REQUIRED=("record_id","symbol","timestamp","research_track_id","dataset_identity","feature_set_version","label_set_version","training_session_id","execution_id","evaluation_id","model_id","ai_configuration_version","output_status")

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest().upper()

def validate_records(path: Path) -> list[str]:
    import csv
    with path.open(newline="",encoding="utf-8-sig") as f:
        r=csv.DictReader(f); fields=r.fieldnames or []; rows=list(r)
    errors=[]
    if fields != list(REQUIRED): errors.append("AI schema or ordering mismatch")
    ids=[x.get("record_id","") for x in rows]
    if len(ids)!=len(set(ids)): errors.append("duplicate record_id")
    if any(not all(x.get(k) for k in REQUIRED) for x in rows): errors.append("missing AI identity")
    if any((rows[i]["timestamp"],rows[i]["record_id"])>(rows[i+1]["timestamp"],rows[i+1]["record_id"]) for i in range(len(rows)-1)): errors.append("non-deterministic ordering")
    return sorted(set(errors))

def generate_manifest(records: Path, manifest: Path, parent_identities: dict, ai_configuration_version: str) -> dict:
    errors=validate_records(records)
    if errors: raise ValueError("; ".join(errors))
    payload={"manifest_version":"1.0.0","ai_schema_version":"1.0.0","ai_configuration_version":ai_configuration_version,"parent_identities":dict(sorted(parent_identities.items())),"ai_records_sha256":sha256(records),"record_count":len(open_records(records)),"encoding":"UTF-8","newline":"LF"}
    manifest.write_text(json.dumps(payload,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    return payload

def validate_manifest(records: Path, manifest: Path, parent_identities: dict) -> list[str]:
    if not manifest.is_file(): return ["manifest missing"]
    data=json.loads(manifest.read_text(encoding="utf-8")); errors=[]
    if data.get("ai_records_sha256")!=sha256(records): errors.append("manifest/hash mismatch")
    if data.get("parent_identities")!=dict(sorted(parent_identities.items())): errors.append("parent identity mismatch")
    if data.get("record_count") != len(open_records(records)): errors.append("record accounting mismatch")
    return sorted(set(errors))

def open_records(path: Path) -> list[dict]:
    import csv
    with path.open(newline="",encoding="utf-8-sig") as f: return list(csv.DictReader(f))
