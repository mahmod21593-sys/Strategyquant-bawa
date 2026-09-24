import tempfile
import unittest
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from edgelab.bars import Bar, convert, load_bars, parse_tz, timeframe, to_daily


def write(tmp, name, text):
    p = Path(tmp) / name
    p.write_text(text, encoding="utf-8")
    return p


class Loading(unittest.TestCase):
    def test_mt5_tab_export(self):
        text = ("<DATE>\t<TIME>\t<OPEN>\t<HIGH>\t<LOW>\t<CLOSE>\t<TICKVOL>\t<VOL>\t<SPREAD>\n"
                "2024.01.02\t09:30:00\t1.1000\t1.1010\t1.0990\t1.1005\t100\t0\t2\n"
                "2024.01.02\t09:35:00\t1.1005\t1.1020\t1.1000\t1.1015\t100\t0\t2\n")
        with tempfile.TemporaryDirectory() as d:
            bars = load_bars(write(d, "eurusd.csv", text))
        self.assertEqual(bars[0].ts, datetime(2024, 1, 2, 9, 30))
        self.assertEqual(bars[1].c, 1.1015)
        self.assertEqual(timeframe(bars), timedelta(minutes=5))

    def test_dukascopy_export(self):
        text = ("Gmt time,Open,High,Low,Close,Volume\n"
                "02.01.2024 09:30:00.000,1.1,1.2,1.0,1.15,10\n"
                "02.01.2024 09:31:00.000,1.15,1.2,1.1,1.12,10\n")
        with tempfile.TemporaryDirectory() as d:
            bars = load_bars(write(d, "duka.csv", text))
        self.assertEqual(bars[1].ts, datetime(2024, 1, 2, 9, 31))

    def test_headerless_and_compact_time(self):
        text = "20240102,093000,10,11,9,10.5,1\n20240102,093500,10.5,11,10,10.8,1\n"
        with tempfile.TemporaryDirectory() as d:
            bars = load_bars(write(d, "x.csv", text))
        self.assertEqual(bars[0].ts, datetime(2024, 1, 2, 9, 30))
        self.assertEqual(bars[1].h, 11.0)

    def test_semicolon_decimal_comma(self):
        text = "Date;Open;High;Low;Close\n2024-01-02 09:30;1,5;1,6;1,4;1,55\n2024-01-02 09:35;1,55;1,6;1,5;1,58\n"
        with tempfile.TemporaryDirectory() as d:
            bars = load_bars(write(d, "x.csv", text))
        self.assertEqual(bars[0].c, 1.55)


class TimeZones(unittest.TestCase):
    def test_nyclose_tracks_new_york_dst(self):
        ny = parse_tz("America/New_York")
        srv = parse_tz("NYCLOSE")
        for day in (date(2024, 1, 2), date(2024, 7, 1)):
            bar = Bar(datetime.combine(day, datetime.min.time()) + timedelta(hours=16, minutes=30), 1, 1, 1, 1)
            self.assertEqual(convert([bar], srv, ny)[0].ts.time().strftime("%H:%M"), "09:30")

    def test_fixed_offset_does_not_track_dst(self):
        ny = parse_tz("America/New_York")
        utc2 = parse_tz("UTC+2")
        summer = convert([Bar(datetime(2024, 7, 1, 15, 30), 1, 1, 1, 1)], utc2, ny)[0].ts
        winter = convert([Bar(datetime(2024, 1, 2, 15, 30), 1, 1, 1, 1)], utc2, ny)[0].ts
        self.assertEqual((summer.hour, summer.minute), (9, 30))
        self.assertEqual((winter.hour, winter.minute), (8, 30))

    def test_conversion_into_nyclose(self):
        ny, srv = ZoneInfo("America/New_York"), parse_tz("NYCLOSE")
        # The week US DST has started but Europe's hasn't: New York 09:30 is still server 16:30.
        out = convert([Bar(datetime(2024, 3, 11, 9, 30), 1, 1, 1, 1)], ny, srv)[0].ts
        self.assertEqual(out, datetime(2024, 3, 11, 16, 30))

    def test_offset_parsing(self):
        self.assertEqual(parse_tz("UTC-5").utcoffset(None), timedelta(hours=-5))
        self.assertEqual(parse_tz("GMT+0530").utcoffset(None), timedelta(hours=5, minutes=30))


class Daily(unittest.TestCase):
    def test_aggregation_with_day_start(self):
        bars = [Bar(datetime(2024, 1, 2, 22), 1, 2, 0.5, 1.5), Bar(datetime(2024, 1, 3, 1), 1.5, 3, 1.4, 2.5),
                Bar(datetime(2024, 1, 3, 23), 2.5, 2.6, 2.4, 2.45)]
        d = to_daily(bars, day_start_hour=22)
        self.assertEqual([b.ts.date() for b in d], [date(2024, 1, 2), date(2024, 1, 3)])
        self.assertEqual((d[0].o, d[0].h, d[0].l, d[0].c), (1, 3, 0.5, 2.5))


if __name__ == "__main__":
    unittest.main()
