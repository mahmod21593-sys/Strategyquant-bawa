# SQX build aids for the three confirmed edges

Hand these to whoever builds the StrategyQuant X strategies, together with
[../../evidence/edges/SQX_build_matrix.md](../../evidence/edges/SQX_build_matrix.md), the full specification.

| File | Use |
|---|---|
| `rev_variants_shortlist.csv` | **REV** (index reversal): the 110 variants on US500, US100 and JP225 that were positive under all three SQX builds and robust in family A (tier 1–2), with the signal, exit and filter written out. Research numbers are for build (c): M5 chart, decision at 15:55 NY, cash-session D1 bars. Pick 10–20 per market, de-duplicated at correlation 0.6. The "Close > SMA(200)" filter is excluded because it is the worst in every build. |
| `gotobi_calendar_2003_2030.csv` | **GT** (Tokyo fix): every Gotobi day 2003–2030 in Tokyo dates. `gotobi_5_10` = the 5th/10th/15th/20th/25th/30th, moved back to the previous Tokyo business day; `month_end` = the month's last Tokyo business day. Holidays: Japanese national holidays (python `holidays`, current law) plus Dec 31 and Jan 2–3. Re-check 2027–2030 against the official calendar each year, since Japanese holidays can be changed by law. |

Codes in the shortlist: K2–K5 = k down closes in a row; R5/R10/R20 = RSI(2) below the level;
I10/I25 = IBS below 0.10/0.25; L5/L10 = close at the lowest close of N sessions; D15 = a day's return below
−1.5 × its 20-day standard deviation. Exits: X1 = next session's 15:55; X3 = hold 3 sessions; XU = first up
close, max 5 sessions. Filters: F0 = none; DN = close below SMA(200) of D1.

N3 (US100 momentum) needs no data file: the rule is fully specified in the build matrix, section 2.
