"""A49 cost procedure: each stock's median Dukascopy ask - bid over session minutes (09:30-16:00 NY) in the 30,000-candle
page starting 2025-03-03, in bps of mid, plus 1 bp commission allowance -> results/round35_costs.json (A49), round37_costs.json (A51)"""
import json
import os
import subprocess
from datetime import datetime, timezone

import numpy as np

from data_duka_chart import UA
from data_histdata import NY

STOCKS = {"AAPL": "AAPL.US/USD", "AMZN": "AMZN.US/USD", "MSFT": "MSFT.US/USD", "NVDA": "NVDA.US/USD", "TSLA": "TSLA.US/USD",
          "META": "FB.US/USD", "GOOGL": "GOOGL.US/USD", "JPM": "JPM.US/USD", "V": "V.US/USD", "AMD": "AMD.US/USD",
          "AVGO": "AVGO.US/USD", "NFLX": "NFLX.US/USD"}
TS = int(datetime(2025, 3, 3, tzinfo=timezone.utc).timestamp() * 1000)


def page(ins, side):
    u = (f"https://freeserv.dukascopy.com/2.0/?path=chart/json3&instrument={ins}&offer_side={side}&interval=1MIN&splits=true"
         f"&stocks=true&limit=30000&time_direction=N&timestamp={TS}&jsonp=_cb")
    for _ in range(6):
        s = subprocess.run(["curl", "-sS", "-m", "120", "-A", UA, "-H", "Referer: https://freeserv.dukascopy.com/2.0/?path=chart/index", u],
                           capture_output=True, text=True).stdout
        try:
            rows = json.loads(s[s.find("(") + 1:s.rfind(")")])
            if rows and rows[0]:
                return {r[0]: r for r in rows}
        except ValueError:
            pass
    raise RuntimeError(ins + side)


def main(stocks=STOCKS, name="round35_costs.json"):
    out = {}
    for sym, ins in stocks.items():
        b, a = page(ins, "B"), page(ins, "A")
        sp = []
        for t in sorted(set(a) & set(b)):
            lt = datetime.fromtimestamp(t / 1000, timezone.utc).astimezone(NY)
            if 570 <= lt.hour * 60 + lt.minute < 960:
                ca, cb = a[t][4], b[t][4]
                sp.append((ca - cb) / ((ca + cb) / 2) * 1e4)
        med = float(np.median(sp))
        out[sym] = {"session_minutes": len(sp), "median_spread_bps": med, "cost_per_entry_bps": med + 1.0}
        print(sym, out[sym], flush=True)
    json.dump(out, open(os.path.join(os.path.dirname(__file__), "results", name), "w"), indent=1)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2:  # python3 measure_stock_costs.py round37_costs.json BA AMGN ...
        main({t: f"{t}.US/USD" for t in sys.argv[2:]}, sys.argv[1])
    else:
        main()
