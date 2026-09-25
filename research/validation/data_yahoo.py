"""Daily OHLC + adjusted close from Yahoo's chart API, cached as JSON."""
from __future__ import annotations

import json
import os
import subprocess
import time
import urllib.parse
from datetime import datetime, timezone

CACHE = os.environ.get("YAHOO_CACHE", "/tmp/yahoo_cache")


def daily(symbol: str):
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, symbol.replace("^", "_").replace("=", "_") + ".json")
    if not os.path.exists(path):
        url = ("https://query1.finance.yahoo.com/v8/finance/chart/" + urllib.parse.quote(symbol)
               + "?period1=0&period2=4102444800&interval=1d&events=div%2Csplit&includeAdjustedClose=true")
        for attempt in range(6):
            r = subprocess.run(["curl", "-sS", "-m", "60", "-A", "Mozilla/5.0", url], capture_output=True, text=True)
            try:
                data = json.loads(r.stdout)
                if data["chart"]["result"]:
                    break
            except Exception:
                pass
            time.sleep(2 + 3 * attempt)
        else:
            raise RuntimeError(f"yahoo failed: {symbol}")
        json.dump(data, open(path, "w"))
    data = json.load(open(path))["chart"]["result"][0]
    ts = data["timestamp"]
    q = data["indicators"]["quote"][0]
    adj = data["indicators"].get("adjclose", [{}])[0].get("adjclose") or q["close"]
    tz_off = data["meta"].get("gmtoffset", 0)
    rows = []
    for i, t in enumerate(ts):
        o, h, l, c, a = q["open"][i], q["high"][i], q["low"][i], q["close"][i], adj[i]
        if None in (o, h, l, c, a) or c <= 0:
            continue
        d = datetime.fromtimestamp(t + tz_off, tz=timezone.utc).date()
        rows.append({"date": d, "o": o, "h": h, "l": l, "c": c, "adj": a})
    # de-duplicate dates (keep last)
    out = {}
    for r in rows:
        out[r["date"]] = r
    return [out[d] for d in sorted(out)]
