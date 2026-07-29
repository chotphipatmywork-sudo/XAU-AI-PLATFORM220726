"""Offline deterministic evaluation of precomputed predictions."""
from __future__ import annotations
import csv, hashlib, json
from pathlib import Path
from datetime import datetime, timezone

IDENTITY = ("record_id", "symbol", "timestamp")

def sha256(path: Path) -> str:
    digest=hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""): digest.update(chunk)
    return digest.hexdigest().upper()

def validate_input(path: Path):
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader=csv.DictReader(handle); fields=reader.fieldnames or []; rows=list(reader)
    expected=list(IDENTITY)+["actual","predicted"]
    errors=[]
    if fields != expected: errors.append("evaluation schema or ordering mismatch")
    ids=[r.get("record_id", "") for r in rows]
    if len(ids) != len(set(ids)): errors.append("duplicate record_id")
    if any(not all(r.get(k) for k in IDENTITY) for r in rows): errors.append("missing identity")
    if any((rows[i]["timestamp"],rows[i]["record_id"]) > (rows[i+1]["timestamp"],rows[i+1]["record_id"]) for i in range(len(rows)-1)): errors.append("non-deterministic ordering")
    if any(not r.get("actual") or not r.get("predicted") for r in rows): errors.append("missing prediction value")
    return errors, rows

def evaluate(input_path: Path, manifest: Path, dataset_identity: str, model_identity: str):
    errors, rows=validate_input(input_path)
    if errors: raise ValueError("; ".join(sorted(set(errors))))
    correct=sum(r["actual"] == r["predicted"] for r in rows)
    accuracy=correct/len(rows) if rows else 0.0
    payload={"manifest_version":"1.0.0","evaluation_schema_version":"1.0.0","evaluation_id":manifest.stem,"dataset_identity":dataset_identity,"model_identity":model_identity,"input_sha256":sha256(input_path),"record_count":len(rows),"metrics":{"accuracy":accuracy,"correct_count":correct},"generated_at_utc":datetime.now(timezone.utc).isoformat().replace("+00:00","Z")}
    manifest.write_text(json.dumps(payload,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    return payload

def validate_manifest(input_path: Path, manifest: Path, dataset_identity: str, model_identity: str):
    errors=[]
    if not manifest.is_file(): return ["manifest missing"]
    data=json.loads(manifest.read_text(encoding="utf-8"))
    if data.get("input_sha256") != sha256(input_path): errors.append("manifest/hash mismatch")
    if data.get("dataset_identity") != dataset_identity or data.get("model_identity") != model_identity: errors.append("manifest identity mismatch")
    if data.get("record_count") != len(validate_input(input_path)[1]): errors.append("record accounting mismatch")
    if "accuracy" not in data.get("metrics", {}): errors.append("accuracy missing")
    return sorted(set(errors))
