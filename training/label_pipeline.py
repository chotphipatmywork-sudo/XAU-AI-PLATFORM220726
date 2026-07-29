"""Contract-driven, deterministic label record handling (offline only)."""
from __future__ import annotations
import csv, hashlib, json, math
from pathlib import Path
from datetime import datetime, timezone

IDENTITY = ("record_id", "symbol", "timestamp")

def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()

def register_label_schema(version: str, label_set_id: str, allowed_values: list[str]) -> dict:
    if not version or not label_set_id or not allowed_values:
        raise ValueError("label schema identity and allowed values are required")
    if len(set(allowed_values)) != len(allowed_values):
        raise ValueError("allowed values must be unique")
    return {"label_schema_version": version, "label_set_id": label_set_id, "allowed_values": list(allowed_values)}

def generate_labels(source: Path, output: Path, manifest: Path, schema: dict,
                    label_column: str, source_identity: str, source_hash: str) -> None:
    with source.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle); fields = reader.fieldnames or []; rows = list(reader)
    required = set(IDENTITY) | {label_column}
    missing = required - set(fields)
    if missing:
        raise ValueError(f"missing source columns: {sorted(missing)}")
    rows.sort(key=lambda row: (row["timestamp"], row["record_id"]))
    output_fields = list(IDENTITY) + ["label", "missing_reason"]
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=output_fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            value = row[label_column]
            if value == "":
                writer.writerow({**{key: row[key] for key in IDENTITY}, "label": "", "missing_reason": "SOURCE_MISSING"})
            elif value not in schema["allowed_values"]:
                raise ValueError(f"label value outside schema: {value}")
            else:
                writer.writerow({**{key: row[key] for key in IDENTITY}, "label": value, "missing_reason": ""})
    payload = {"manifest_version": "1.0.0", "research_track_id": "CONTROLLED_RESEARCH_REGENERATION", "label_schema_version": schema["label_schema_version"], "label_set_id": schema["label_set_id"], "source_dataset_identity": source_identity, "source_dataset_sha256": source_hash, "label_dataset_identity": output.stem, "label_dataset_sha256": sha256(output), "record_count": len(rows), "labels_generated": True, "encoding": "UTF-8", "newline": "LF", "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")}
    manifest.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def validate_labels(dataset: Path, manifest: Path, schema: dict) -> list[str]:
    errors = []
    expected = list(IDENTITY) + ["label", "missing_reason"]
    with dataset.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle); fields = reader.fieldnames or []; rows = list(reader)
    if fields != expected:
        errors.append("schema or column ordering mismatch")
    ids = [row.get("record_id", "") for row in rows]
    if len(ids) != len(set(ids)):
        errors.append("duplicate record_id")
    if any(not row.get(key, "") for row in rows for key in IDENTITY):
        errors.append("missing identity value")
    for row in rows:
        value = row.get("label", "")
        reason = row.get("missing_reason", "")
        if value == "":
            if reason != "SOURCE_MISSING": errors.append("missing label reason")
        elif value not in schema["allowed_values"]:
            errors.append("label value outside schema")
        elif reason: errors.append("unexpected missing reason")
    if not manifest.is_file():
        errors.append("manifest missing")
    else:
        data = json.loads(manifest.read_text(encoding="utf-8"))
        if data.get("label_dataset_sha256") != sha256(dataset): errors.append("manifest/hash mismatch")
        if data.get("label_schema_version") != schema["label_schema_version"]: errors.append("manifest schema mismatch")
        if data.get("label_dataset_identity") != dataset.stem or data.get("research_track_id") != "CONTROLLED_RESEARCH_REGENERATION": errors.append("manifest identity mismatch")
        if data.get("record_count") != len(rows): errors.append("record accounting mismatch")
        if data.get("label_set_id") != schema["label_set_id"]: errors.append("label identity mismatch")
    return sorted(set(errors))
