"""SEC EDGAR 8-K Item 2.02 (Results of Operations) filings, cached. Times are the EDGAR acceptance time (UTC)."""
from __future__ import annotations

import json
import os
import subprocess
import time
from datetime import datetime, timezone

CACHE = os.environ.get("EDGAR_CACHE", "/tmp/edgar_cache")
UA = "strategyquant-research contact@example.org"  # SEC asks for a descriptive User-Agent


def _get(url, path):
    if not os.path.exists(path):
        os.makedirs(CACHE, exist_ok=True)
        for attempt in range(6):
            r = subprocess.run(["curl", "-sS", "-m", "60", "-A", UA, "-o", path, "-w", "%{http_code}", url], capture_output=True, text=True)
            if r.stdout.strip() == "200":
                break
            time.sleep(1 + 2 * attempt)
        else:
            raise RuntimeError(f"edgar failed: {url}")
        time.sleep(0.2)  # stay well under the SEC's 10 requests per second
    return json.load(open(path))


def earnings_filings(cik: int) -> list:
    """[(acceptance datetime UTC, form, items)] for 8-K filings that include Item 2.02."""
    base = f"CIK{cik:010d}"
    d = _get(f"https://data.sec.gov/submissions/{base}.json", os.path.join(CACHE, f"{base}.json"))
    blocks = [d["filings"]["recent"]]
    for f in d["filings"].get("files", []):
        blocks.append(_get(f"https://data.sec.gov/submissions/{f['name']}", os.path.join(CACHE, f["name"])))
    out = []
    for b in blocks:
        for form, items, acc in zip(b["form"], b["items"], b["acceptanceDateTime"]):
            if form in ("8-K", "8-K/A") and "2.02" in (items or "") and form == "8-K":
                out.append(datetime.strptime(acc[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc))
    return sorted(set(out))
