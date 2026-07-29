"""Offline training-session metadata engine; never trains or loads models."""
from __future__ import annotations
import hashlib, json, re
from pathlib import Path

STATES=("CREATED","READY","RUNNING","COMPLETED","FAILED","CANCELLED")
TRANSITIONS={"CREATED":{"READY","CANCELLED"},"READY":{"RUNNING","CANCELLED"},"RUNNING":{"COMPLETED","FAILED","CANCELLED"},"COMPLETED":set(),"FAILED":set(),"CANCELLED":set()}
SEMVER=re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")

def config_hash(configuration: dict) -> str:
    data=json.dumps(configuration,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(data).hexdigest().upper()

def validate_configuration(configuration: dict) -> list[str]:
    errors=[]
    for key in ("dataset_identity","feature_schema_version","label_schema_version","configuration_version"):
        if not configuration.get(key): errors.append(f"missing {key}")
    if configuration.get("configuration_version") and not SEMVER.fullmatch(configuration["configuration_version"]): errors.append("invalid configuration version")
    if configuration.get("model_training", False): errors.append("model training is prohibited")
    return errors

def create_session(history: Path, training_session_id: str, training_job_id: str, configuration: dict) -> dict:
    errors=validate_configuration(configuration)
    if errors: raise ValueError("; ".join(errors))
    record={"training_session_id":training_session_id,"training_job_id":training_job_id,"state":"CREATED","configuration":configuration,"configuration_sha256":config_hash(configuration)}
    history.parent.mkdir(parents=True,exist_ok=True)
    with history.open("a",encoding="utf-8",newline="\n") as handle: handle.write(json.dumps(record,sort_keys=True,separators=(",",":"))+"\n")
    return record

def transition_session(history: Path, training_session_id: str, new_state: str) -> dict:
    if new_state not in STATES: raise ValueError("invalid state")
    with history.open(encoding="utf-8") as handle: records=[json.loads(line) for line in handle if line.strip()]
    matches=[r for r in records if r["training_session_id"]==training_session_id]
    if not matches: raise ValueError("session not found")
    current=matches[-1]["state"]
    if new_state not in TRANSITIONS[current]: raise ValueError("invalid lifecycle transition")
    updated=dict(matches[-1]); updated["state"]=new_state
    with history.open("a",encoding="utf-8",newline="\n") as handle: handle.write(json.dumps(updated,sort_keys=True,separators=(",",":"))+"\n")
    return updated

def write_manifest(history: Path, manifest: Path, training_session_id: str) -> None:
    records=[json.loads(line) for line in history.read_text(encoding="utf-8").splitlines() if line.strip()]
    selected=[r for r in records if r["training_session_id"]==training_session_id]
    if not selected: raise ValueError("session not found")
    latest=selected[-1]
    payload={"manifest_version":"1.0.0","training_session_id":training_session_id,"training_job_id":latest["training_job_id"],"state":latest["state"],"configuration_sha256":latest["configuration_sha256"],"history_count":len(selected)}
    manifest.write_text(json.dumps(payload,sort_keys=True,indent=2)+"\n",encoding="utf-8")

def validate_manifest(history: Path, manifest: Path, training_session_id: str) -> list[str]:
    errors=[]
    if not manifest.is_file(): return ["manifest missing"]
    data=json.loads(manifest.read_text(encoding="utf-8")); records=[json.loads(line) for line in history.read_text(encoding="utf-8").splitlines() if line.strip()]; selected=[r for r in records if r["training_session_id"]==training_session_id]
    if not selected: return ["session not found"]
    latest=selected[-1]
    if data.get("state")!=latest["state"] or data.get("training_job_id")!=latest["training_job_id"]: errors.append("manifest identity mismatch")
    if data.get("configuration_sha256")!=latest["configuration_sha256"]: errors.append("configuration hash mismatch")
    if data.get("history_count")!=len(selected): errors.append("history accounting mismatch")
    return errors
