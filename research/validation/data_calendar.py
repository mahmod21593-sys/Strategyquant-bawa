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


def treasury_auctions(original_term: str = "10-Year", start: int = 1980, end: int = 2026) -> list[date]:
    """Auction dates of nominal Treasury notes with this original term (new issues and reopenings; TIPS excluded),
    from the TreasuryDirect securities API. Cached."""
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, "treasury_notes.json")
    if not os.path.exists(path):
        rows = []
        for y in range(start, end + 1):
            url = (f"https://www.treasurydirect.gov/TA_WS/securities/search?format=json&type=Note"
                   f"&startDate={y}-01-01&endDate={y}-12-31")
            rows += json.loads(_get_json(url))
        json.dump(rows, open(path, "w"))
    rows = json.load(open(path))
    out = {date.fromisoformat(r["auctionDate"][:10]) for r in rows
           if r.get("originalSecurityTerm") == original_term and r.get("tips") != "Yes" and r.get("type") == "Note"}
    return sorted(out)


def _get_json(url):
    for a in range(5):
        r = subprocess.run(["curl", "-sS", "-m", "60", url], capture_output=True, text=True, errors="ignore")
        if r.returncode == 0 and r.stdout.strip().startswith("["):
            return r.stdout
        time.sleep(3 + 3 * a)
    raise RuntimeError(url)


def japan_holidays(first_year=2003, last_year=2026):
    """Japanese national holidays (python `holidays`) plus the bank holidays Dec 31 and Jan 2-3 (A33)."""
    import holidays
    out = set(holidays.Japan(years=range(first_year, last_year + 1)))
    for y in range(first_year, last_year + 1):
        out |= {date(y, 12, 31), date(y, 1, 2), date(y, 1, 3)}
    return out


def gotobi_days(first_year=2003, last_year=2026):
    """{Tokyo business day: 'ME' (month's last business day) or '510' (other Gotobi day)} (A33).
    Gotobi = the 5th, 10th, 15th, 20th, 25th and 30th, each moved to the preceding business day if needed."""
    hol = japan_holidays(first_year, last_year)

    def bd(d):
        return d.weekday() < 5 and d not in hol

    def prev_bd(d):
        while not bd(d):
            d -= timedelta(days=1)
        return d
    out = {}
    for y in range(first_year, last_year + 1):
        for m in range(1, 13):
            nxt = date(y + (m == 12), m % 12 + 1, 1)
            out[prev_bd(nxt - timedelta(days=1))] = "ME"
            for k in (5, 10, 15, 20, 25, 30):
                try:
                    g = prev_bd(date(y, m, k))
                except ValueError:
                    continue
                out.setdefault(g, "510")
    return out


def boj_days():
    """BoJ decision days from the statement file dates on the BoJ's past-meetings page (A33); the extraordinary
    2020-05-22 meeting is excluded."""
    path = os.path.join(CACHE, "boj_days.json")
    if os.path.exists(path):
        return [date.fromisoformat(x) for x in json.load(open(path))]
    out = set()
    for url in ("https://www.boj.or.jp/en/mopo/mpmsche_minu/past.htm", "https://www.boj.or.jp/en/mopo/mpmsche_minu/index.htm"):
        html = _get(url)
        for row in re.findall(r"<tr>(.*?)</tr>", html, re.S):
            td = re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)
            if not td:
                continue
            m = re.search(r"mpmdeci/(?:mpr|state)_\d{4}/k(\d{2})(\d{2})(\d{2})[a-z]?\.(?:pdf|htm)", td[0])
            if m:
                out.add(date(2000 + int(m.group(1)), int(m.group(2)), int(m.group(3))))
    out.discard(date(2020, 5, 22))
    days = sorted(d for d in out if d <= date.today())
    json.dump([str(d) for d in days], open(path, "w"))
    return days
