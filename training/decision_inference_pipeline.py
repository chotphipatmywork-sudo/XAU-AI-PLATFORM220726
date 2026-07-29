"""Offline deterministic join of validated decision and inference evidence."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

FIELDS = (
    "record_id", "symbol", "timestamp", "inference_id", "decision_id",
    "model_id", "model_version", "configuration_version", "output",
    "confidence", "decision", "status",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _read(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def validate_records(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        rows = list(reader)
    errors: set[str] = set()
    if fields != list(FIELDS):
        errors.add("integration schema or ordering mismatch")
    ids = [row.get("record_id", "") for row in rows]
    if any(not value for value in ids):
        errors.add("missing record identity")
    if len(ids) != len(set(ids)):
        errors.add("duplicate record_id")
    for row in rows:
        if any(not row.get(field) for field in FIELDS):
            errors.add("missing integration identity")
        try:
            confidence = float(row.get("confidence", ""))
            if not 0.0 <= confidence <= 1.0:
                errors.add("confidence out of range")
        except (TypeError, ValueError):
            errors.add("invalid confidence")
        if row.get("status") in {"RISK_APPROVED", "EXECUTE", "ORDER"}:
            errors.add("prohibited decision status")
    if any((rows[i]["timestamp"], rows[i]["record_id"]) >
           (rows[i + 1]["timestamp"], rows[i + 1]["record_id"])
           for i in range(len(rows) - 1)):
        errors.add("non-deterministic ordering")
    return sorted(errors)


def integrate(decisions: Path, inferences: Path, output: Path) -> None:
    drows, irows = _read(decisions), _read(inferences)
    dmap, imap = {}, {}
    for row in drows:
        if row.get("record_id") in dmap:
            raise ValueError("duplicate decision record_id")
        dmap[row.get("record_id", "")] = row
    for row in irows:
        if row.get("record_id") in imap:
            raise ValueError("duplicate inference record_id")
        imap[row.get("record_id", "")] = row
    if set(dmap) != set(imap):
        raise ValueError("integration join mismatch")
    rows = []
    for record_id in sorted(dmap, key=lambda value: (dmap[value].get("timestamp", ""), value)):
        decision, inference = dmap[record_id], imap[record_id]
        if decision.get("symbol") != inference.get("symbol") or decision.get("timestamp") != inference.get("timestamp"):
            raise ValueError("parent chronology mismatch")
        rows.append({field: (decision if field in {"decision_id", "decision"} else inference).get(field, "") for field in FIELDS})
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(FIELDS), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def generate_manifest(records: Path, manifest: Path, parent_identities: dict) -> dict:
    errors = validate_records(records)
    if errors:
        raise ValueError("; ".join(errors))
    payload = {
        "manifest_version": "1.0.0",
        "integration_schema_version": "1.0.0",
        "parent_identities": dict(sorted(parent_identities.items())),
        "integration_records_sha256": sha256(records),
        "record_count": len(_read(records)),
    }
    manifest.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return payload


def validate_manifest(records: Path, manifest: Path, parent_identities: dict) -> list[str]:
    if not manifest.is_file():
        return ["manifest missing"]
    data = json.loads(manifest.read_text(encoding="utf-8"))
    errors = []
    if data.get("integration_records_sha256") != sha256(records):
        errors.append("manifest/hash mismatch")
    if data.get("parent_identities") != dict(sorted(parent_identities.items())):
        errors.append("parent identity mismatch")
    if data.get("record_count") != len(_read(records)):
        errors.append("record accounting mismatch")
    return errors
