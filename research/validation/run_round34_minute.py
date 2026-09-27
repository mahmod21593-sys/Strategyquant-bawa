"""Minute-exact SQX-native N3 grid (round 11 R3 logic) on arbitrary local minute bars; the reference for the
round-34 calibration gate (PREREGISTRATION.md A48a)."""
from __future__ import annotations

import numpy as np

from data_minutes import H, L, O, day_of, group, price_at


def r3_grid(t, x, cost, start=570, end=960):
    """{'{base}|k{kk}|{mode}': {date: (net pnl, entries)}}; session start to end (local minutes; default 09:30-16:00),
    exit one minute before the end."""
    day, mod = t // 1440, t % 1440
    ins = (mod >= start) & (mod < end)
    keys, _, sh, sl, _, cnt, st = group(day[ins], x[ins])
    xi, mi = x[ins], mod[ins]
    po, pc, pf = price_at(day, mod, x, start, prefer_open=True), price_at(day, mod, x, end), price_at(day, mod, x, end - 1)
    valid = [i for i, k in enumerate(keys.tolist()) if cnt[i] >= 300 * (end - start) / 390 and k in po and k in pc and k in pf and day_of(k).weekday() < 5]
    tr, info, prev = {}, [], None
    for i in valid:
        if prev is not None:
            pcl = pc[int(keys[prev])]
            tr[i] = max(sh[i], pcl) - min(sl[i], pcl)
            info.append((i, prev))
        prev = i
    out = {f"{b}|k{kk}|{m}": {} for b in ("range", "atr14") for kk in (0.3, 0.5, 0.7) for m in ("flat", "reverse")}
    trs = []
    for i, pv in info:
        k = int(keys[i])
        d = day_of(k)
        trs.append(tr[i])
        width = {"range": sh[pv] - sl[pv], "atr14": float(np.mean(trs[-15:-1])) if len(trs) > 14 else None}
        rows = slice(st[i], st[i] + cnt[i])
        m_, xx = mi[rows], xi[rows]
        e = m_ < end - 1
        oo, hh, ll = xx[e, O], xx[e, H], xx[e, L]
        o0, exit_px = po[k], pf[k]
        for base in ("range", "atr14"):
            w = width[base]
            if not w:
                continue
            for kk in (0.3, 0.5, 0.7):
                U, D = o0 + kk * w, o0 - kk * w
                upt, dnt = hh >= U, ll <= D
                for mode in ("flat", "reverse"):
                    pnl, entries, pos, px, j0 = 0.0, 0, 0, None, 0
                    while True:
                        if pos == 0:
                            cand = np.nonzero(upt[j0:] | dnt[j0:])[0]
                            if not len(cand):
                                break
                            j = j0 + int(cand[0])
                            go_long = upt[j] and (not dnt[j] or U - oo[j] <= oo[j] - D)
                            pos, px = (1, max(U, oo[j])) if go_long else (-1, min(D, oo[j]))
                        else:
                            if mode == "flat":
                                break
                            cand = np.nonzero(dnt[j0:] if pos == 1 else upt[j0:])[0]
                            if not len(cand):
                                break
                            j = j0 + int(cand[0])
                            npx = min(D, oo[j]) if pos == 1 else max(U, oo[j])
                            pnl += pos * (npx / px - 1)
                            pos, px = -pos, npx
                        entries += 1
                        j0 = j + 1
                    if pos != 0:
                        pnl += pos * (exit_px / px - 1)
                    out[f"{base}|k{kk}|{mode}"][d] = (pnl - entries * cost / 1e4, entries)
    return out
