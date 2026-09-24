"""Phase 1 raw-edge studies. Each returns a Result with tables and (where it applies) a primary effect.

The primary effect is what the Gate 1 check in doc 00 compares against costs: the average gross
return per trade (in basis points of price) in the direction the hypothesis predicts, and the
share of calendar years in which it had that sign.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, time, timedelta
from typing import Optional

from . import stats as st
from .bars import Bar, by_date, timeframe, to_daily

BPS = 1e4


@dataclass
class Result:
    study: str
    title: str
    tables: list[tuple[str, list[dict]]] = field(default_factory=list)
    primary: Optional[dict] = None
    notes: list[str] = field(default_factory=list)


def _primary(label: str, dates, values_bps, sign: int = 1, baseline: Optional[dict] = None,
             effect: Optional[float] = None, t: Optional[float] = None) -> dict:
    frac, n_years = st.year_consistency(dates, values_bps, sign, baseline)
    return {
        "label": label,
        "n": len(values_bps),
        "effect_bps": st.mean(values_bps) if effect is None else effect,
        "t": st.tstat(values_bps) if t is None else t,
        "years_frac": frac,
        "n_years": n_years,
        "sign": sign,
    }


def _summary_row(name: str, dates, vals: list[float], extra: Optional[dict] = None) -> dict:
    frac, _ = st.year_consistency(dates, vals, 1)
    row = {"group": name, "n": len(vals), "mean_bps": st.mean(vals), "t": st.tstat(vals),
           "hit": st.mean([v > 0 for v in vals]) if vals else math.nan, "years_pos": frac}
    if extra:
        row.update(extra)
    return row


# --------------------------------------------------------------------------- profile

def profile(bars: list[Bar], slot_minutes: int = 60, weekday: bool = False) -> Result:
    """Mean return and volatility per time-of-day slot (Andersen & Bollerslev 1997; Ranaldo 2009)."""
    groups: dict[tuple, tuple[list, list]] = {}
    for a, b in zip(bars, bars[1:]):
        if b.ts - a.ts > timedelta(days=4) or a.c <= 0:
            continue
        minute = (b.ts.hour * 60 + b.ts.minute) // slot_minutes * slot_minutes
        key = (b.ts.weekday(), minute) if weekday else (minute,)
        dates, vals = groups.setdefault(key, ([], []))
        dates.append(b.ts.date())
        vals.append(math.log(b.c / a.c) * BPS)
    rows = []
    for key in sorted(groups):
        dates, vals = groups[key]
        m = st.mean(vals)
        frac, _ = st.year_consistency(dates, vals, 1 if m >= 0 else -1)
        label = f"{key[-1] // 60:02d}:{key[-1] % 60:02d}"
        if weekday:
            label = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][key[0]] + " " + label
        rows.append({"slot": label, "n": len(vals), "mean_bps": m, "t": st.tstat(vals),
                     "up": st.mean([v > 0 for v in vals]), "abs_bps": st.mean([abs(v) for v in vals]),
                     "years_same_sign": frac})
    sig = sum(abs(r["t"]) >= 2 for r in rows if r["t"] == r["t"])
    res = Result("profile", f"Time-of-day profile ({slot_minutes}-minute slots, returns stamped at bar open)")
    res.tables.append(("Per-slot returns (bps of price)", rows))
    res.notes.append(f"{sig} of {len(rows)} slots have |t| >= 2; about {0.05 * len(rows):.1f} would by chance. "
                     "Only slots with a mechanism (e.g. Ranaldo's home-session pattern) and stable yearly sign count.")
    return res


# --------------------------------------------------------------------------- variance ratio

def varratio(bars: list[Bar], horizons: tuple[int, ...] = (2, 4, 8, 16, 32)) -> Result:
    """Trend vs mean-reversion character by horizon (Lo & MacKinlay 1988)."""
    tf = timeframe(bars)
    rets, dates = [], []
    for a, b in zip(bars, bars[1:]):
        if a.c > 0 and b.ts - a.ts <= max(tf * 3, timedelta(days=4)):
            rets.append(math.log(b.c / a.c))
            dates.append(b.ts.date())
    rows = []
    for q in horizons:
        vr, z = st.variance_ratio(rets, q)
        reading = "trending" if z >= 2 else ("mean-reverting" if z <= -2 else "random-walk-like")
        rows.append({"q": q, "horizon": str(tf * q), "VR": vr, "z_robust": z, "reading": reading})
    ac = st.autocorr(rets, 1)
    by_year: dict[int, list[float]] = {}
    for d, r in zip(dates, rets):
        by_year.setdefault(d.year, []).append(r)
    yearly = [st.autocorr(v, 1) for v in by_year.values() if len(v) > 50]
    neg = st.mean([a < 0 for a in yearly]) if yearly else math.nan
    res = Result("varratio", f"Variance ratios on {tf} returns ({len(rets)} returns)")
    res.tables.append(("Variance ratio (VR > 1 trending, < 1 mean-reverting; z robust to heteroskedasticity)", rows))
    res.tables.append(("Lag-1 autocorrelation", [{"lag1_autocorr": ac, "years": len(yearly), "years_negative": neg}]))
    return res


# --------------------------------------------------------------------------- intraday momentum

def intraday_momentum(bars: list[Bar], open_t: time, close_t: time, first_min: int = 30,
                      last_min: int = 30, from_open: bool = False) -> Result:
    """Last-period return vs first-period / rest-of-day return (Gao et al. 2018; Baltussen et al. 2021)."""
    tf = timeframe(bars)
    tf_min = tf.total_seconds() / 60
    if first_min % tf_min or last_min % tf_min:
        raise ValueError(f"--first/--last must be multiples of the bar size ({tf_min:g} minutes)")
    days = by_date(bars)
    rec = {"date": [], "r1": [], "rest": [], "last": [], "rv": []}
    prev_close: Optional[float] = None
    skipped = 0
    for d in sorted(days):
        idx = {b.ts: b for b in days[d]}
        o_dt, c_dt = datetime.combine(d, open_t), datetime.combine(d, close_t)

        def end_price(t: datetime) -> Optional[float]:
            bar = idx.get(t - tf)
            return bar.c if bar else None

        first_bar = idx.get(o_dt)
        p_first = end_price(o_dt + timedelta(minutes=first_min))
        p_mid = end_price(c_dt - timedelta(minutes=last_min))
        p_close = end_price(c_dt)
        if None in (first_bar, p_first, p_mid, p_close):
            skipped += 1
            continue
        base = first_bar.o if from_open or prev_close is None else prev_close
        if prev_close is not None or from_open:
            session = [b for b in days[d] if o_dt <= b.ts < c_dt - timedelta(minutes=last_min)]
            rv = math.sqrt(sum(math.log(b.c / b.o) ** 2 for b in session if b.o > 0))
            rec["date"].append(d)
            rec["r1"].append(math.log(p_first / base) * BPS)
            rec["rest"].append(math.log(p_mid / base) * BPS)
            rec["last"].append(math.log(p_close / p_mid) * BPS)
            rec["rv"].append(rv)
        prev_close = p_close
    res = Result("intraday-momentum",
                 f"Intraday momentum, session {open_t:%H:%M}-{close_t:%H:%M}, first {first_min}m, last {last_min}m")
    n = len(rec["date"])
    if n < 50:
        res.notes.append(f"only {n} complete sessions (skipped {skipped}); check --open/--close and time zones")
        return res
    base_lbl = "session open" if from_open else "prior close"
    reg = []
    for name, x in ((f"first {first_min}m (from {base_lbl})", rec["r1"]), (f"rest of day (from {base_lbl})", rec["rest"])):
        o = st.ols(rec["last"], x)
        reg.append({"predictor": name, "n": o["n"], "beta": o["beta"], "t_hc": o["t"], "r2": o["r2"]})
    res.tables.append((f"Regression of the last-{last_min}m return on earlier returns", reg))
    timing = []
    signals = {}
    for name, x in (("sign(first period)", rec["r1"]), ("sign(rest of day)", rec["rest"])):
        vals = [(1 if s > 0 else -1 if s < 0 else 0) * l for s, l in zip(x, rec["last"])]
        signals[name] = vals
        timing.append(_summary_row(name, rec["date"], vals))
    res.tables.append((f"Timing strategy: trade the last {last_min}m in the signal's direction (bps per day)", timing))
    cuts = st.terciles(rec["rv"])
    cond = []
    for level in ("low", "mid", "high"):
        sel = [i for i, v in enumerate(rec["rv"]) if st.bucket3(v, cuts) == level]
        vals = [signals["sign(rest of day)"][i] for i in sel]
        cond.append(_summary_row(f"{level} intraday volatility", [rec["date"][i] for i in sel], vals))
    res.tables.append(("Mechanism check: timing return by same-day volatility tercile (should rise with volatility)", cond))
    res.primary = _primary("last-period timing, rest-of-day signal", rec["date"], signals["sign(rest of day)"])
    res.notes.append(f"{n} sessions used, {skipped} skipped (missing bars, holidays, half days).")
    return res


# --------------------------------------------------------------------------- range breakout

def _daily_atr(bars: list[Bar], n: int = 14) -> dict:
    daily = to_daily(bars)
    atr, out, prev = None, {}, None
    for b in daily:
        out[b.ts.date()] = atr  # ATR known before this day
        tr = b.h - b.l if prev is None else max(b.h, prev.c) - min(b.l, prev.c)
        atr = tr if atr is None else atr + (tr - atr) / n
        prev = b
    return out


def range_break(bars: list[Bar], range_start: time, range_end: time, exit_t: time,
                entry_end: Optional[time] = None, buffer: float = 0.0, stop: str = "opposite") -> Result:
    """Break of a time-window range (opening range, Asian range) held to a fixed exit time.

    Entry is a stop order at the range high/low (+ buffer x range width); gaps fill at the bar open.
    With stop="opposite" the stop is the other side of the range; if the entry bar also touches the
    stop, the trade is counted as stopped (conservative). Days whose first breakout bar touches both
    sides are skipped as ambiguous.
    """
    entry_end = entry_end or exit_t
    atr = _daily_atr(bars)
    trades = {"date": [], "dir": [], "bps": [], "R": [], "w_atr": []}
    ambiguous = no_break = 0
    for d, day in sorted(by_date(bars).items()):
        rng = [b for b in day if range_start <= b.ts.time() < range_end]
        if not rng:
            continue
        hi, lo = max(b.h for b in rng), min(b.l for b in rng)
        width = hi - lo
        if width <= 0:
            continue
        window = [b for b in day if range_end <= b.ts.time() < exit_t]
        if not window:
            continue
        up_lvl, dn_lvl = hi + buffer * width, lo - buffer * width
        entry = None
        for i, b in enumerate(window):
            if b.ts.time() >= entry_end:
                break
            up, dn = b.h >= up_lvl, b.l <= dn_lvl
            if up and dn:
                entry = "ambiguous"
                break
            if up:
                entry = (i, 1, max(up_lvl, b.o))
                break
            if dn:
                entry = (i, -1, min(dn_lvl, b.o))
                break
        if entry is None:
            no_break += 1
            continue
        if entry == "ambiguous":
            ambiguous += 1
            continue
        i, direction, px = entry
        exit_px = window[-1].c
        if stop == "opposite":
            stop_lvl = lo if direction == 1 else hi
            for j, b in enumerate(window[i:]):
                hit = b.l <= stop_lvl if direction == 1 else b.h >= stop_lvl
                if hit:
                    gap_px = min(stop_lvl, b.o) if direction == 1 else max(stop_lvl, b.o)
                    exit_px = stop_lvl if j == 0 else gap_px
                    break
        trades["date"].append(d)
        trades["dir"].append(direction)
        trades["bps"].append(direction * (exit_px - px) / px * BPS)
        trades["R"].append(direction * (exit_px - px) / width)
        a = atr.get(d)
        trades["w_atr"].append(width / a if a else math.nan)

    res = Result("range-break", f"Range {range_start:%H:%M}-{range_end:%H:%M} breakout, entries until "
                                f"{entry_end:%H:%M}, exit {exit_t:%H:%M}, stop={stop}, buffer={buffer:g}x range")
    n = len(trades["bps"])
    if n < 30:
        res.notes.append(f"only {n} trades; check the time windows and time zone")
        return res

    def rows_for(sel: list[int], name: str) -> dict:
        return _summary_row(name, [trades["date"][i] for i in sel], [trades["bps"][i] for i in sel],
                            {"mean_R": st.mean([trades["R"][i] for i in sel])})

    allsel = list(range(n))
    rows = [rows_for(allsel, "all breakouts"),
            rows_for([i for i in allsel if trades["dir"][i] == 1], "long (upside break)"),
            rows_for([i for i in allsel if trades["dir"][i] == -1], "short (downside break)")]
    res.tables.append(("Breakout trades (bps of price per trade, gross)", rows))
    valid = [i for i in allsel if trades["w_atr"][i] == trades["w_atr"][i]]
    if len(valid) >= 30:
        cuts = st.terciles([trades["w_atr"][i] for i in valid])
        rows = [rows_for([i for i in valid if st.bucket3(trades["w_atr"][i], cuts) == lv], f"{lv} range width / ATR")
                for lv in ("low", "mid", "high")]
        res.tables.append(("By range width relative to the prior 14-day ATR (Crabel: narrow ranges break better)", rows))
    res.primary = _primary("breakout trade return", trades["date"], trades["bps"])
    res.notes.append(f"{n} trades; {no_break} days without a break; {ambiguous} ambiguous days skipped.")
    return res


# --------------------------------------------------------------------------- daily studies

def _log_ret(a: float, b: float) -> float:
    return math.log(b / a) * BPS if a > 0 and b > 0 else 0.0


def ibs(daily: list[Bar], sma_len: int = 200, low: float = 0.2, nlow: int = 5) -> Result:
    """Next-day return by internal bar strength and after N-day lows, above/below the SMA (F2)."""
    closes = [b.c for b in daily]
    res = Result("ibs", f"IBS and N-day-low mean reversion (SMA {sma_len}, IBS < {low}, {nlow}-day low)")
    if len(daily) < sma_len + 50:
        res.notes.append("not enough daily bars")
        return res
    running = sum(closes[:sma_len])
    rec = []  # (date, ibs, up, next_bps, t)
    for t in range(sma_len, len(daily) - 1):
        running += closes[t] - closes[t - sma_len]
        sma = running / sma_len
        b = daily[t]
        if b.h <= b.l:
            continue
        rec.append((b.ts.date(), (b.c - b.l) / (b.h - b.l), b.c > sma, _log_ret(b.c, daily[t + 1].c), t))
    uncond = [r[3] for r in rec]
    yearly_base = st.yearly_means([r[0] for r in rec], uncond)
    rows = []
    edges = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0001]
    for regime, cond in (("all", lambda r: True), ("above SMA", lambda r: r[2]), ("below SMA", lambda r: not r[2])):
        for lo_e, hi_e in zip(edges, edges[1:]):
            vals = [r[3] for r in rec if cond(r) and lo_e <= r[1] < hi_e]
            rows.append({"regime": regime, "ibs": f"{lo_e:.1f}-{min(hi_e, 1):.1f}", "n": len(vals),
                         "next_day_bps": st.mean(vals), "t": st.tstat(vals)})
    res.tables.append((f"Next-day return by IBS bucket (unconditional mean {st.mean(uncond):.2f} bps)", rows))

    fwd_rows = []
    for h in (1, 3, 5):
        vals, dates = [], []
        for t in range(max(sma_len, nlow), len(daily) - h):
            window = closes[t - nlow:t]
            sma = sum(closes[t - sma_len + 1:t + 1]) / sma_len
            if closes[t] < min(window) and closes[t] > sma:
                vals.append(_log_ret(closes[t], closes[t + h]))
                dates.append(daily[t].ts.date())
        base = [_log_ret(closes[t], closes[t + h]) for t in range(sma_len, len(daily) - h)]
        fwd_rows.append({"hold_days": h, "n": len(vals), "mean_bps": st.mean(vals), "t_nw": st.nw_tstat(vals, h - 1),
                         "unconditional_bps": st.mean(base)})
    res.tables.append((f"{nlow}-day-low close above the SMA: forward returns", fwd_rows))

    sel = [r for r in rec if r[2] and r[1] < low]
    vals = [r[3] for r in sel]
    excess = [v - yearly_base[r[0].year] for v, r in zip(vals, sel)]
    res.primary = _primary(f"IBS < {low} above SMA, next-day excess return", [r[0] for r in sel], excess,
                           effect=st.mean(excess), t=st.tstat(excess))
    res.notes.append("Primary effect is the excess over the same year's average day, which removes equity drift.")
    return res


def tom(daily: list[Bar], before: int = 1, after: int = 3) -> Result:
    """Turn-of-month: last `before` and first `after` trading days vs the rest (McConnell & Xu 2008)."""
    months: dict[tuple, list[int]] = {}
    for i, b in enumerate(daily):
        months.setdefault((b.ts.year, b.ts.month), []).append(i)
    in_tom = set()
    for idxs in months.values():
        in_tom.update(idxs[:after])
        in_tom.update(idxs[-before:] if before else [])
    tom_d, tom_v, oth_d, oth_v = [], [], [], []
    for i in range(1, len(daily)):
        r = _log_ret(daily[i - 1].c, daily[i].c)
        if i in in_tom:
            tom_d.append(daily[i].ts.date())
            tom_v.append(r)
        else:
            oth_d.append(daily[i].ts.date())
            oth_v.append(r)
    res = Result("tom", f"Turn of month: last {before} + first {after} trading days")
    if len(tom_v) < 60:
        res.notes.append("not enough months")
        return res
    k = before + after
    diff = st.mean(tom_v) - st.mean(oth_v)
    res.tables.append(("Daily returns (bps)", [
        {"days": "turn of month", "n": len(tom_v), "mean_bps": st.mean(tom_v), "t": st.tstat(tom_v)},
        {"days": "other days", "n": len(oth_v), "mean_bps": st.mean(oth_v), "t": st.tstat(oth_v)},
        {"days": "difference", "n": len(tom_v), "mean_bps": diff, "t": st.welch_t(tom_v, oth_v)},
    ]))
    base = st.yearly_means(oth_d, oth_v)
    res.primary = _primary(f"TOM excess per {k}-day trade", tom_d, tom_v, 1, base, effect=diff * k,
                           t=st.welch_t(tom_v, oth_v))
    return res


def compression(daily: list[Bar], n: int = 7, atr_len: int = 20) -> Result:
    """Range expansion and next-day breakout after narrow-range (NR-n) days, with an ablation baseline (F4)."""
    res = Result("compression", f"NR{n} compression -> expansion and next-day breakout")
    if len(daily) < atr_len + n + 50:
        res.notes.append("not enough daily bars")
        return res
    atr = None
    groups = {True: {"d": [], "exp_atr": [], "exp_self": [], "brk": [], "brk_d": []},
              False: {"d": [], "exp_atr": [], "exp_self": [], "brk": [], "brk_d": []}}
    for t in range(1, len(daily) - 1):
        b, p, nx = daily[t], daily[t - 1], daily[t + 1]
        tr = max(b.h, p.c) - min(b.l, p.c)
        atr = tr if atr is None else atr + (tr - atr) / atr_len
        if t < max(atr_len, n) or b.h <= b.l:
            continue
        rng = b.h - b.l
        nr = all(rng <= daily[t - k].h - daily[t - k].l for k in range(1, n))
        g = groups[nr]
        g["d"].append(b.ts.date())
        g["exp_atr"].append((nx.h - nx.l) / atr)
        g["exp_self"].append((nx.h - nx.l) / rng)
        up, dn = nx.h > b.h, nx.l < b.l
        if up != dn:
            direction, px = (1, max(b.h, nx.o)) if up else (-1, min(b.l, nx.o))
            g["brk"].append(direction * (nx.c - px) / px * BPS)
            g["brk_d"].append(b.ts.date())
    rows = []
    for key, name in ((True, f"after NR{n} day"), (False, "after other days")):
        g = groups[key]
        rows.append({"group": name, "n": len(g["d"]), "next_range_atr": st.mean(g["exp_atr"]),
                     "next_range_vs_today": st.mean(g["exp_self"]), "breakouts": len(g["brk"]),
                     "breakout_bps": st.mean(g["brk"]), "t": st.tstat(g["brk"])})
    res.tables.append(("Next-day range and breakout of today's high/low (entry at the level, exit at close)", rows))
    ablation = st.welch_t(groups[True]["brk"], groups[False]["brk"])
    res.notes.append(f"Ablation: NR{n} breakouts minus other-day breakouts = "
                     f"{st.mean(groups[True]['brk']) - st.mean(groups[False]['brk']):.2f} bps (Welch t {ablation:.2f}). "
                     "If this isn't clearly positive, the compression filter adds nothing.")
    g = groups[True]
    res.primary = _primary(f"NR{n} next-day breakout return", g["brk_d"], g["brk"])
    return res


def breakout(daily: list[Bar], n: int = 55, horizons: tuple[int, ...] = (1, 5, 10, 20)) -> Result:
    """Forward returns after N-day closing-high/low breakouts, signed in the breakout direction (F1)."""
    closes = [b.c for b in daily]
    res = Result("breakout", f"{n}-day closing breakout, signed forward returns")
    if len(daily) < n + max(horizons) + 50:
        res.notes.append("not enough daily bars")
        return res
    rows, primary = [], None
    for h in horizons:
        signed, longs, shorts, dates = [], [], [], []
        for t in range(n, len(daily) - h):
            window = closes[t - n:t]
            r = _log_ret(closes[t], closes[t + h])
            if closes[t] > max(window):
                signed.append(r)
                longs.append(r)
                dates.append(daily[t].ts.date())
            elif closes[t] < min(window):
                signed.append(-r)
                shorts.append(-r)
                dates.append(daily[t].ts.date())
        base = [_log_ret(closes[t], closes[t + h]) for t in range(n, len(daily) - h)]
        rows.append({"hold_days": h, "signals": len(signed), "signed_bps": st.mean(signed),
                     "t_nw": st.nw_tstat(signed, max(h - 1, 0)), "long_bps": st.mean(longs),
                     "short_bps": st.mean(shorts), "unconditional_bps": st.mean(base)})
        if h == max(horizons):
            primary = _primary(f"{h}-day signed return after breakout", dates, signed,
                               t=st.nw_tstat(signed, max(h - 1, 0)))
    res.tables.append(("Forward returns after breakouts (short side sign-flipped so positive = trend continued)", rows))
    res.primary = primary
    res.notes.append("Signals on consecutive days overlap; the Newey-West t-stat only partly corrects for this.")
    return res
