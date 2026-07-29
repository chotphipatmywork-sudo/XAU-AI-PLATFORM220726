"""Metadata-only training artifact registry preparation."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest().upper()

def validate_artifact(record: dict) -> list[str]:
    required=("artifact_id","artifact_version","training_session_id","execution_id","evaluation_id","model_registry_id","status")
    errors=[f"missing {k}" for k in required if not record.get(k)]
    if record.get("status") not in ("DRAFT","PROMOTION_REQUESTED","APPROVED","REJECTED"): errors.append("invalid artifact status")
    if record.get("artifact_path"): errors.append("artifact files are prohibited")
    return errors

def register_artifact(history: Path, record: dict) -> dict:
    errors=validate_artifact(record)
    if errors: raise ValueError("; ".join(errors))
    existing=[]
    if history.is_file():
        with history.open(encoding="utf-8") as f: existing=[json.loads(x) for x in f if x.strip()]
    if any(x.get("artifact_id")==record["artifact_id"] and x.get("artifact_version")==record["artifact_version"] and x.get("status")==record["status"] for x in existing): raise ValueError("duplicate artifact record")
    history.parent.mkdir(parents=True,exist_ok=True)
    with history.open("a",encoding="utf-8",newline="\n") as f: f.write(json.dumps(record,sort_keys=True,separators=(",",":"))+"\n")
    return record

def request_promotion(history: Path, artifact_id: str, artifact_version: str, approver_role: str) -> dict:
    with history.open(encoding="utf-8") as f: records=[json.loads(x) for x in f if x.strip()]
    matches=[x for x in records if x.get("artifact_id")==artifact_id and x.get("artifact_version")==artifact_version]
    if not matches: raise ValueError("artifact not found")
    if matches[-1]["status"] != "DRAFT": raise ValueError("promotion requires DRAFT artifact")
    record=dict(matches[-1]); record.update({"status":"PROMOTION_REQUESTED","approver_role":approver_role})
    return register_artifact(history,record)

def write_manifest(history: Path, manifest: Path) -> None:
    manifest.write_text(json.dumps({"manifest_version":"1.0.0","registry_identity":history.stem,"registry_sha256":sha256(history),"record_count":len([x for x in history.read_text(encoding="utf-8").splitlines() if x.strip()])},sort_keys=True,indent=2)+"\n",encoding="utf-8")

def validate_manifest(history: Path, manifest: Path) -> list[str]:
    if not manifest.is_file(): return ["manifest missing"]
    data=json.loads(manifest.read_text(encoding="utf-8")); lines=[x for x in history.read_text(encoding="utf-8").splitlines() if x.strip()]; errors=[]
    if data.get("registry_sha256") != sha256(history): errors.append("manifest/hash mismatch")
    if data.get("record_count") != len(lines): errors.append("record accounting mismatch")
    return errors
