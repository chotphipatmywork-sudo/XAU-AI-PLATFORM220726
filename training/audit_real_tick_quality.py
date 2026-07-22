"""XAU AI PLATFORM | Offline Audit | Version 1.0.0.

Verify that every date warned by an MT5 real-tick log is quarantined.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


WARNING_PATTERN = re.compile(
    r"XAUUSD\s*:\s*(\d{4}\.\d{2}\.\d{2})\s+\d{2}:\d{2}\s+-\s+"
    r"(?:real ticks (?:absent|discarded|mismatched)|all the real ticks discarded)",
    re.IGNORECASE,
)


def read_log(path: Path) -> str:
    data = path.read_bytes()
    if data.startswith(b"\xff\xfe") or data[:200].count(b"\x00") > 20:
        return data.decode("utf-16", errors="replace")
    return data.decode("utf-8-sig", errors="replace")


def audit(log_path: Path, exclusion_path: Path) -> dict[str, object]:
    payload = json.loads(exclusion_path.read_text(encoding="utf-8-sig"))
    configured = {
        entry["date"] for entry in payload.get("excluded_dates", [])
        if isinstance(entry, dict) and isinstance(entry.get("date"), str)
    }
    warned = {
        match.group(1).replace(".", "-")
        for match in WARNING_PATTERN.finditer(read_log(log_path))
    }
    missing = sorted(warned - configured)
    return {
        "audit_stage": "mt5_real_tick_warning_coverage",
        "log_file": str(log_path),
        "quality_exclusion_file": str(exclusion_path),
        "warned_dates": sorted(warned),
        "configured_exclusion_dates": sorted(configured),
        "missing_exclusion_dates": missing,
        "all_warned_dates_quarantined": not missing,
        "deployment_authorized": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", required=True, type=Path)
    parser.add_argument("--quality-exclusions", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    arguments = parser.parse_args()
    report = audit(arguments.log, arguments.quality_exclusions)
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not report["all_warned_dates_quarantined"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
