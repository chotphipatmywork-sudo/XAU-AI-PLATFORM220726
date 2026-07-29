"""Offline source registration and label/feature-free dataset pipeline."""

from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Iterable


REQUIRED_COLUMNS = ("record_id", "symbol", "timestamp")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


@dataclass(frozen=True)
class SourceRegistration:
    source_id: str
    source_version: str
    path: str
    schema_version: str
    provider: str
    symbol: str
    timeframe: str
    timezone: str
    record_count: int
    byte_size: int
    sha256: str


def register_source(path: Path, *, source_id: str, source_version: str,
                    schema_version: str, provider: str, symbol: str,
                    timeframe: str, timezone: str) -> SourceRegistration:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open(newline="", encoding="utf-8-sig") as stream:
        count = sum(1 for _ in csv.DictReader(stream))
    return SourceRegistration(source_id, source_version, str(path), schema_version,
                              provider, symbol, timeframe, timezone, count,
                              path.stat().st_size, sha256(path))


def write_source_manifest(registration: SourceRegistration, manifest: Path) -> None:
    """Persist the immutable registration record for later approval."""
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps(asdict(registration), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_dataset(source: Path, output: Path, manifest: Path,
                  registration: SourceRegistration) -> None:
    with source.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        missing = [name for name in REQUIRED_COLUMNS if name not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"missing required columns: {missing}")
        rows = list(reader)
    rows.sort(key=lambda row: (row["timestamp"], row["record_id"]))
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=reader.fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    payload = {"identity": asdict(registration), "dataset_path": str(output),
               "dataset_sha256": sha256(output), "manifest_version": "1.0.0",
               "generated_at": datetime.now().isoformat(timespec="seconds"),
               "labels_generated": False, "features_generated": False}
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def validate_dataset(dataset: Path, manifest: Path) -> list[str]:
    errors: list[str] = []
    with dataset.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        if any(name not in (reader.fieldnames or []) for name in REQUIRED_COLUMNS):
            errors.append("required columns missing")
        rows = list(reader)
    ids = [row.get("record_id", "") for row in rows]
    if any(not value for value in ids):
        errors.append("missing record identity")
    if len(ids) != len(set(ids)):
        errors.append("duplicate record identity")
    ordering = [(row.get("timestamp", ""), row.get("record_id", "")) for row in rows]
    if ordering != sorted(ordering):
        errors.append("record ordering is not deterministic")
    if any(not row.get("timestamp", "") or not row.get("symbol", "") for row in rows):
        errors.append("required value missing")
    if not manifest.is_file():
        errors.append("manifest missing")
    else:
        payload = json.loads(manifest.read_text(encoding="utf-8"))
        for field in ("identity", "dataset_path", "dataset_sha256", "manifest_version"):
            if field not in payload:
                errors.append(f"manifest field missing: {field}")
    return errors
