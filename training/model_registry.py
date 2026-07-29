"""Offline append-only model registry metadata; never loads model artifacts."""
from __future__ import annotations
import json, re, hashlib
from pathlib import Path

STATUSES = ("DRAFT", "CANDIDATE", "APPROVED", "DEPRECATED", "RETIRED")
TRANSITIONS = {"DRAFT": {"CANDIDATE"}, "CANDIDATE": {"APPROVED", "DRAFT"}, "APPROVED": {"DEPRECATED"}, "DEPRECATED": {"RETIRED"}, "RETIRED": set()}
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest().upper()

def validate_version(version: str) -> bool:
    return bool(SEMVER.fullmatch(version or ""))

def validate_model(record: dict) -> list[str]:
    errors=[]
    for key in ("model_id", "model_version", "training_run_id", "evaluation_id", "dataset_identity", "feature_schema_version", "label_schema_version", "status"):
        if not record.get(key): errors.append(f"missing {key}")
    if record.get("status") not in STATUSES: errors.append("invalid status")
    if record.get("model_version") and not validate_version(record["model_version"]): errors.append("invalid semantic version")
    if "artifact_path" in record and record["artifact_path"]: errors.append("model artifact metadata must not imply loading")
    return errors

def register_model(registry: Path, record: dict) -> dict:
    errors=validate_model(record)
    if errors: raise ValueError("; ".join(errors))
    existing=[]
    if registry.is_file():
        with registry.open(encoding="utf-8") as f: existing=[json.loads(line) for line in f if line.strip()]
    if any(x.get("model_id")==record["model_id"] and x.get("model_version")==record["model_version"] for x in existing): raise ValueError("duplicate model identity")
    registry.parent.mkdir(parents=True, exist_ok=True)
    with registry.open("a", encoding="utf-8", newline="\n") as f: f.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
    return record

def transition_model(registry: Path, model_id: str, version: str, new_status: str) -> dict:
    with registry.open(encoding="utf-8") as f: records=[json.loads(line) for line in f if line.strip()]
    matches=[r for r in records if r.get("model_id")==model_id and r.get("model_version")==version]
    if not matches: raise ValueError("model identity not found")
    current=matches[-1].get("status")
    if new_status not in TRANSITIONS.get(current, set()): raise ValueError("invalid lifecycle transition")
    updated=dict(matches[-1]); updated["status"]=new_status
    with registry.open("a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(updated, sort_keys=True, separators=(",", ":")) + "\n")
    return updated

def validate_registry(registry: Path, manifest: Path) -> list[str]:
    errors=[]; records=[]
    if not registry.is_file(): return ["registry missing"]
    with registry.open(encoding="utf-8") as f: records=[json.loads(line) for line in f if line.strip()]
    seen=set()
    for record in records:
        errors.extend(validate_model(record)); key=(record.get("model_id"),record.get("model_version"))
        fingerprint=(key, record.get("status"))
        if fingerprint in seen: errors.append("duplicate model identity")
        seen.add(fingerprint)
    if not manifest.is_file(): errors.append("registry manifest missing")
    else:
        data=json.loads(manifest.read_text(encoding="utf-8"))
        if data.get("registry_sha256") != sha256(registry): errors.append("registry manifest hash mismatch")
        if data.get("record_count") != len(records): errors.append("registry accounting mismatch")
    return sorted(set(errors))

def write_manifest(registry: Path, manifest: Path) -> None:
    records=registry.read_text(encoding="utf-8").splitlines() if registry.is_file() else []
    manifest.write_text(json.dumps({"manifest_version":"1.0.0","registry_identity":registry.stem,"registry_sha256":sha256(registry),"record_count":len([x for x in records if x.strip()]),"statuses":list(STATUSES)},sort_keys=True,indent=2)+"\n",encoding="utf-8")
