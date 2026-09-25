"""FRED daily series (e.g. DGS10), cached as CSV."""
from __future__ import annotations

import os
import subprocess
from datetime import date

CACHE = os.environ.get("YAHOO_CACHE", "/tmp/yahoo_cache")


def series(sid: str) -> list[tuple[date, float]]:
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, f"fred_{sid}.csv")
    if not os.path.exists(path):
        r = subprocess.run(["curl", "-sS", "-m", "60", f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}"],
                           capture_output=True, text=True)
        if not r.stdout.startswith("observation_date"):
            raise RuntimeError(f"fred failed: {sid}")
        open(path, "w").write(r.stdout)
    out = []
    for line in open(path).read().splitlines()[1:]:
        d, v = line.split(",")
        if v not in ("", "."):
            out.append((date.fromisoformat(d), float(v)))
    return out
