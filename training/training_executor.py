"""Metadata-only training executor; no machine-learning execution."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

STATES=("CREATED","RUNNING","COMPLETED","FAILED","CANCELLED")
TRANSITIONS={"CREATED":{"RUNNING","CANCELLED"},"RUNNING":{"COMPLETED","FAILED","CANCELLED"},"COMPLETED":set(),"FAILED":set(),"CANCELLED":set()}

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest().upper()

def create_execution(history: Path, execution_id: str, training_session_id: str, configuration_hash: str) -> dict:
    record={"execution_id":execution_id,"training_session_id":training_session_id,"state":"CREATED","configuration_sha256":configuration_hash,"metrics":{},"checkpoint":None}
    history.parent.mkdir(parents=True,exist_ok=True)
    with history.open("a",encoding="utf-8",newline="\n") as f: f.write(json.dumps(record,sort_keys=True,separators=(",",":"))+"\n")
    return record

def transition_execution(history: Path, execution_id: str, state: str, metrics=None, checkpoint=None) -> dict:
    if state not in STATES: raise ValueError("invalid execution state")
    with history.open(encoding="utf-8") as f: records=[json.loads(x) for x in f if x.strip()]
    matches=[x for x in records if x["execution_id"]==execution_id]
    if not matches: raise ValueError("execution not found")
    current=matches[-1]["state"]
    if state not in TRANSITIONS[current]: raise ValueError("invalid execution transition")
    updated=dict(matches[-1]); updated["state"]=state
    if metrics is not None: updated["metrics"]=dict(sorted(metrics.items()))
    if checkpoint is not None: updated["checkpoint"]=dict(sorted(checkpoint.items()))
    with history.open("a",encoding="utf-8",newline="\n") as f: f.write(json.dumps(updated,sort_keys=True,separators=(",",":"))+"\n")
    return updated

def write_manifest(history: Path, manifest: Path, execution_id: str) -> None:
    records=[json.loads(x) for x in history.read_text(encoding="utf-8").splitlines() if x.strip()]; selected=[x for x in records if x["execution_id"]==execution_id]
    if not selected: raise ValueError("execution not found")
    latest=selected[-1]
    manifest.write_text(json.dumps({"manifest_version":"1.0.0","execution_id":execution_id,"training_session_id":latest["training_session_id"],"state":latest["state"],"history_count":len(selected),"metrics":latest["metrics"],"checkpoint":latest["checkpoint"]},sort_keys=True,indent=2)+"\n",encoding="utf-8")

def validate_manifest(history: Path, manifest: Path, execution_id: str) -> list[str]:
    if not manifest.is_file(): return ["manifest missing"]
    data=json.loads(manifest.read_text(encoding="utf-8")); records=[json.loads(x) for x in history.read_text(encoding="utf-8").splitlines() if x.strip()]; selected=[x for x in records if x["execution_id"]==execution_id]
    if not selected: return ["execution not found"]
    latest=selected[-1]; errors=[]
    if data.get("state")!=latest["state"] or data.get("training_session_id")!=latest["training_session_id"]: errors.append("manifest identity mismatch")
    if data.get("history_count")!=len(selected): errors.append("history accounting mismatch")
    if data.get("metrics")!=latest["metrics"] or data.get("checkpoint")!=latest["checkpoint"]: errors.append("execution metadata mismatch")
    return errors
