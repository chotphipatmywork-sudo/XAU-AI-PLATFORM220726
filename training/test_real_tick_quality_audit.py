"""XAU AI PLATFORM | Offline Test | Version 1.0.0."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from audit_real_tick_quality import audit


def main() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        log = root / "tester.log"
        exclusions = root / "quality.json"
        log.write_text(
            "XAUUSD : 2025.11.19 23:59 - all the real ticks discarded within a day\n"
            "XAUUSD : 2026.05.01 23:59 - real ticks absent for 31 minutes\n"
            "XAUUSD : 2021.07.01 00:00 - 2026.06.30 00:00 "
            "real ticks absent for 10 minutes\n",
            encoding="utf-8",
        )
        exclusions.write_text(json.dumps({"excluded_dates": [
            {"date": "2025-11-19"}, {"date": "2026-05-01"}
        ]}), encoding="utf-8")
        report = audit(log, exclusions)
        if not report["all_warned_dates_quarantined"]:
            raise AssertionError("Covered real-tick warning dates were rejected")
        exclusions.write_text(json.dumps({"excluded_dates": [
            {"date": "2025-11-19"}
        ]}), encoding="utf-8")
        report = audit(log, exclusions)
        if report["missing_exclusion_dates"] != ["2026-05-01"]:
            raise AssertionError("Missing real-tick exclusion was not detected")
    print("Real-tick quality warning audit test passed")


if __name__ == "__main__":
    main()
