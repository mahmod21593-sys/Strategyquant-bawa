"""HistData integrity audit (round 21, A35a): transient spike bars.

A bar is a spike if any of its open/high/low/close is more than `lim` (1% FX, 2% metals and indices) away from the
median close of the two bars before and the two after, while those neighbours agree with each other (within lim / 2).

    python3 data_audit.py   -> results/data_audit_spikes.json   ({symbol: [[file date, file minute, o, h, l, c], ...]})
"""
from __future__ import annotations

import glob
import json
import os
from datetime import date

import numpy as np

from data_histdata import available_years
from data_minutes import _file_year

OUT = os.path.join(os.path.dirname(__file__), "results")
CACHE = os.environ.get("HISTDATA_CACHE", "/tmp/histdata_cache")
WIDE = ("XAU", "XAG", "SPX", "NSX", "GRX", "UKX", "FRX", "JPX", "AUX", "HKX", "ETX", "WTI", "BCO")


def spike_mask(x, lim):
    c = x[:, 3]
    n = len(c)
    pad = np.r_[np.full(2, c[0]), c, np.full(2, c[-1])]
    nb = np.stack([pad[0:n], pad[1:n + 1], pad[3:n + 3], pad[4:n + 4]], 1)
    med = np.median(nb, 1)
    agree = (nb.max(1) / nb.min(1) - 1) < lim / 2
    dev = np.max(np.abs(x / med[:, None] - 1), 1)
    return agree & (dev > lim)


def main():
    syms = sorted({os.path.basename(p).split("_")[0] for p in glob.glob(os.path.join(CACHE, "*_M1_*.zip"))})
    res = {}
    for s in syms:
        lim = 0.02 if s.startswith(WIDE) else 0.01
        rows = []
        for y in available_years(s, range(2000, 2027)):
            t, x = _file_year(s, y)
            m = spike_mask(x, lim)
            for i in np.nonzero(m)[0]:
                d = date.fromordinal(int(t[i] // 1440) + date(1970, 1, 1).toordinal())
                rows.append([str(d), int(t[i] % 1440), *[float(v) for v in x[i]]])
        res[s] = rows
        print(s, len(rows), rows[:3], flush=True)
    json.dump(res, open(os.path.join(OUT, "data_audit_spikes.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
