"""Event calendars: FOMC scheduled decision days (federalreserve.gov) and Employment Situation days (BLS rule)."""
from __future__ import annotations

import json
import os
import re
import subprocess
import time
from datetime import date, timedelta

CACHE = os.environ.get("YAHOO_CACHE", "/tmp/yahoo_cache")
_FULL = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
         "November", "December"]
MONTHS = {m[:3]: i for i, m in enumerate(_FULL, 1)}
MON_RE = r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.?"


def _mon(tok):
    return MONTHS[tok[:3]]


def _get(url):
    for a in range(5):
        r = subprocess.run(["curl", "-sS", "-m", "30", "-A", "Mozilla/5.0", url], capture_output=True, text=True, errors="ignore")
        if r.returncode == 0 and len(r.stdout) > 10000:
            return r.stdout
        time.sleep(3 + 3 * a)
    raise RuntimeError(url)


def fomc_days(first_year=1994):
    path = os.path.join(CACHE, "fomc_days.json")
    if os.path.exists(path):
        return [date.fromisoformat(x) for x in json.load(open(path))]
    out = set()
    for y in range(first_year, 2021):
        html = _get(f"https://www.federalreserve.gov/monetarypolicy/fomchistorical{y}.htm")
        for h in re.findall(r"<h5[^>]*>(.*?)</h5>", html, re.S):
            t = re.sub(r"<[^>]+>", "", h).strip()
            if "Meeting" not in t or "unscheduled" in t.lower() or "Conference Call" in t:
                continue
            m = re.match(rf"({MON_RE})(?:/({MON_RE}))?\s+(\d+)(?:\s*-\s*(?:({MON_RE})\s+)?(\d+))?\s+Meeting\s*-\s*(\d{{4}})", t)
            if not m:
                continue
            mon1, mon1b, d1, mon2, d2, yy = m.groups()
            last_mon = mon2 or mon1b or mon1
            mon = _mon(last_mon) if d2 else _mon(mon1)
            out.add(date(int(yy), mon, int(d2 or d1)))
        time.sleep(0.5)
    html = _get("https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm")
    text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))
    parts = re.split(r"(\d{4}) FOMC Meetings", text)
    for i in range(1, len(parts) - 1, 2):
        yy, body = int(parts[i]), parts[i + 1]
        for m in re.finditer(rf"({MON_RE})(?:/({MON_RE}))?\s+(\d+)(?:-(\d+))?\*?\s+Statement", body):
            mon1, mon2, d1, d2 = m.groups()
            mon = _mon(mon2) if (mon2 and d2) else _mon(mon1)
            out.add(date(yy, mon, int(d2 or d1)))
    days = sorted(d for d in out if d <= date.today())
    json.dump([str(d) for d in days], open(path, "w"))
    return days


def employment_days(first_year=1994, last=date(2026, 9, 24)):
    """BLS rule: third Friday after the Saturday ending the week that contains the 12th (approximation)."""
    out = []
    y, m = first_year, 1
    while True:
        d12 = date(y, m, 12)
        sat = d12 + timedelta(days=(5 - d12.weekday()) % 7)
        fri = sat + timedelta(days=6)  # first Friday after that Saturday
        rel = fri + timedelta(days=14)
        if rel > last:
            break
        out.append(rel)
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out
