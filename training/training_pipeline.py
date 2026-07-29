"""Offline deterministic training-dataset assembly; no model training."""
from __future__ import annotations
import csv, hashlib, json
from pathlib import Path
from datetime import datetime, timezone

IDENTITY = ("record_id", "symbol", "timestamp")

def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""): digest.update(chunk)
    return digest.hexdigest().upper()

def _read(path):
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames or [], list(reader)

def assemble_dataset(features: Path, labels: Path, output: Path, manifest: Path,
                     train_end: str, validation_end: str):
    feature_fields, feature_rows = _read(features); label_fields, label_rows = _read(labels)
    for fields, name in ((feature_fields, "features"), (label_fields, "labels")):
        if any(key not in fields for key in IDENTITY): raise ValueError(f"{name} identity schema mismatch")
    if len({r["record_id"] for r in feature_rows}) != len(feature_rows): raise ValueError("duplicate feature IDs")
    if len({r["record_id"] for r in label_rows}) != len(label_rows): raise ValueError("duplicate label IDs")
    labels_by_id = {r["record_id"]: r for r in label_rows}
    if any(r["record_id"] not in labels_by_id for r in feature_rows): raise ValueError("missing label join")
    feature_only = [k for k in feature_fields if k not in IDENTITY]
    label_only = [k for k in label_fields if k not in IDENTITY]
    fields = list(IDENTITY) + feature_only + label_only
    rows = []
    for row in feature_rows:
        label = labels_by_id[row["record_id"]]
        if any(row[k] != label[k] for k in ("symbol", "timestamp")): raise ValueError("identity mismatch")
        rows.append({**{k: row[k] for k in IDENTITY}, **{k: row[k] for k in feature_only}, **{k: label[k] for k in label_only}})
    rows.sort(key=lambda r: (r["timestamp"], r["record_id"]))
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n"); writer.writeheader(); writer.writerows(rows)
    partitions = {"train": 0, "validation": 0, "test": 0}
    for row in rows:
        partitions["train" if row["timestamp"] < train_end else "validation" if row["timestamp"] < validation_end else "test"] += 1
    payload = {"manifest_version": "1.0.0", "research_track_id": "CONTROLLED_RESEARCH_REGENERATION", "dataset_schema_version": "1.0.0", "dataset_identity": output.stem, "feature_dataset_identity": features.stem, "label_dataset_identity": labels.stem, "feature_dataset_sha256": sha256(features), "label_dataset_sha256": sha256(labels), "training_dataset_sha256": sha256(output), "record_count": len(rows), "partition_counts": partitions, "train_end_exclusive": train_end, "validation_end_exclusive": validation_end, "encoding": "UTF-8", "newline": "LF", "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")}
    manifest.parent.mkdir(parents=True, exist_ok=True); manifest.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def validate_dataset(dataset: Path, manifest: Path, train_end: str, validation_end: str):
    errors=[]; fields, rows = _read(dataset)
    expected_identity = list(IDENTITY)
    if fields[:3] != expected_identity: errors.append("identity ordering mismatch")
    if len({r.get("record_id") for r in rows}) != len(rows): errors.append("duplicate IDs")
    if any(not all(r.get(k) for k in IDENTITY) for r in rows): errors.append("missing identity")
    if any((rows[i]["timestamp"], rows[i]["record_id"]) > (rows[i+1]["timestamp"], rows[i+1]["record_id"]) for i in range(len(rows)-1)): errors.append("non-deterministic ordering")
    if not manifest.is_file(): errors.append("manifest missing")
    else:
        data=json.loads(manifest.read_text(encoding="utf-8"));
        if data.get("training_dataset_sha256") != sha256(dataset): errors.append("manifest/hash mismatch")
        if data.get("train_end_exclusive") != train_end or data.get("validation_end_exclusive") != validation_end: errors.append("partition boundary mismatch")
        if data.get("dataset_identity") != dataset.stem or data.get("research_track_id") != "CONTROLLED_RESEARCH_REGENERATION": errors.append("manifest identity mismatch")
        if data.get("record_count") != len(rows): errors.append("record accounting mismatch")
        expected_counts = {"train": 0, "validation": 0, "test": 0}
        for row in rows:
            expected_counts["train" if row["timestamp"] < train_end else "validation" if row["timestamp"] < validation_end else "test"] += 1
        if data.get("partition_counts") != expected_counts: errors.append("partition accounting mismatch")
    return sorted(set(errors))
