"""Append closed 1-minute BMT candles from six sources to CSV files, then commit and push them.
Upbit starts at its listing; Binance and MEXC start two weeks earlier.

Usage:
  python3 collect.py --repo DIR    collect into DIR/data, then commit and push DIR (a clone checked out on the `data` branch);
                                   run it every minute for the freshest data
  python3 collect.py --no-push     collect into ./data only
  python3 collect.py --selftest    offline checks

Each CSV is `time,open,high,low,close,volume,quote_volume`, time = candle open in unix seconds (UTC), oldest first.
volume is in BMT; quote_volume is in KRW for the two Upbit files and USDT for the others.
Only closed minutes are written. Upbit has no candle for a minute without trades; the others always do.
Standard library only, so it runs on the macOS system Python 3.9.
"""
import csv
import json
import os
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

LISTING = 1792811100          # 2026-10-24 03:05 UTC, first KRW-BMT candle on Upbit
PRE = LISTING - 14 * 86400    # Binance and MEXC start two weeks earlier to show the run-up to the listing
ROOT = Path(sys.argv[sys.argv.index("--repo") + 1]).resolve() if "--repo" in sys.argv else Path(__file__).resolve().parent
DATA = ROOT / "data"
UA = {"User-Agent": "upbit-premium-chart collector (+https://github.com/yyu0310/upbit-premium-chart)"}
SOURCES = ["upbit_krw_bmt", "upbit_krw_usdt", "binance_spot", "binance_perp", "mexc_spot", "mexc_perp"]


def log(msg):
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {msg}", flush=True)


def get(url):
    log(f"[GET] {url}")
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20) as r:
        return json.load(r)


# ---------- fetchers: each returns {open_time_sec: [o, h, l, c, volume, quote_volume]} for start <= t < end ----------

def upbit(market, start, end):
    out, to = {}, ""
    while True:
        rows = get(f"https://api.upbit.com/v1/candles/minutes/1?market={market}&count=200{to}")
        for c in rows:
            t = int(datetime.fromisoformat(c["candle_date_time_utc"]).replace(tzinfo=timezone.utc).timestamp())
            if start <= t < end:
                out[t] = [c["opening_price"], c["high_price"], c["low_price"], c["trade_price"],
                          c["candle_acc_trade_volume"], c["candle_acc_trade_price"]]
        if len(rows) < 200 or rows[-1]["candle_date_time_utc"] <= datetime.fromtimestamp(start, timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"):
            return out
        to = f"&to={rows[-1]['candle_date_time_utc']}Z"   # newest first, `to` is exclusive
        time.sleep(0.15)                                   # about 10 requests a second without an Origin header


def binance(url, limit, start, end):
    out, t = {}, start
    while t < end:
        rows = get(f"{url}&startTime={t * 1000}&limit={limit}")
        for k in rows:
            if k[0] // 1000 < end:
                out[k[0] // 1000] = [float(x) for x in k[1:6]] + [float(k[7])]   # o h l c, base volume, quote volume
        if len(rows) < limit:
            return out
        t = rows[-1][0] // 1000 + 60
    return out


def mexc_spot(start, end):
    # MEXC spot ignores startTime unless endTime is also given, and returns at most 500 rows; endTime is exclusive
    out, t = {}, start
    while t < end:
        stop = min(end, t + 500 * 60)
        rows = get(f"https://api.mexc.com/api/v3/klines?symbol=BMTUSDT&interval=1m&startTime={t * 1000}&endTime={stop * 1000}&limit=500")
        for k in rows:
            if start <= k[0] // 1000 < end:
                out[k[0] // 1000] = [float(x) for x in k[1:6]] + [float(k[7])]   # o h l c, base volume, quote volume
        t = stop
    return out


def mexc_perp(start, end):
    # vol is in contracts; contractSize (BMT per contract, 10 when checked) is read each run in case MEXC changes it
    size = get("https://contract.mexc.com/api/v1/contract/detail?symbol=BMT_USDT")["data"]["contractSize"]
    out, t = {}, start
    while t < end:
        stop = min(end, t + 2000 * 60)
        d = get(f"https://contract.mexc.com/api/v1/contract/kline/BMT_USDT?interval=Min1&start={t}&end={stop}")
        if not d.get("success"):
            raise RuntimeError(f"MEXC perp error: {d}")
        d = d["data"]
        for i, ts in enumerate(d["time"]):
            if start <= ts < end:
                out[ts] = [d["open"][i], d["high"][i], d["low"][i], d["close"][i], d["vol"][i] * size, d["amount"][i]]
        t = stop
    return out


FETCH = {
    "upbit_krw_bmt": lambda s, e: upbit("KRW-BMT", s, e),
    "upbit_krw_usdt": lambda s, e: upbit("KRW-USDT", s, e),
    "binance_spot": lambda s, e: binance("https://api.binance.com/api/v3/klines?symbol=BMTUSDT&interval=1m", 1000, s, e),
    "binance_perp": lambda s, e: binance("https://fapi.binance.com/fapi/v1/klines?symbol=BMTUSDT&interval=1m", 1500, s, e),
    "mexc_spot": mexc_spot,
    "mexc_perp": mexc_perp,
}


# ---------- CSV ----------

def last_time(path):
    """Open time of the last row, or None for a missing or empty file."""
    if not path.exists():
        return None
    last = None
    with path.open(encoding="utf-8") as f:
        for row in csv.reader(f):
            if row and row[0] != "time":
                last = int(row[0])
    return last


def fmt(x):
    s = repr(float(x))
    return s[:-2] if s.endswith(".0") else s


def append(path, bars):
    new = not path.exists()
    with path.open("a", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["time", "open", "high", "low", "close", "volume", "quote_volume"])
        for t in sorted(bars):
            w.writerow([t] + [fmt(v) for v in bars[t]])


def collect():
    DATA.mkdir(exist_ok=True)
    end = int(time.time()) // 60 * 60          # start of the current, still open minute
    failed = []
    for name in SOURCES:
        path = DATA / f"{name}.csv"
        last = last_time(path)
        start = (LISTING if name.startswith("upbit") else PRE) if last is None else last + 60
        if start >= end:
            log(f"[{name}] up to date (last {last})")
            continue
        try:
            bars = FETCH[name](start, end)
        except Exception as e:                  # one source failing must not stop the others
            log(f"[{name}] FAILED: {e!r}")
            failed.append(name)
            continue
        append(path, bars)
        log(f"[{name}] {start} -> {end}: +{len(bars)} bars, last now {max(bars) if bars else last}")
    return failed


def git(*args):
    log(f"[git] {' '.join(args)}")
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True).stdout


def push():
    if not git("status", "--porcelain", "data").strip():
        log("[git] nothing new")
        return
    git("add", "data")
    git("-c", "user.name=upbit-premium-chart bot", "-c", "user.email=bot@upbit-premium-chart.invalid",
        "commit", "-q", "-m", f"data: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC")
    git("push", "-q", "origin", "HEAD:data")
    log("[git] pushed")
    if datetime.now().minute == 0:
        git("gc", "--quiet")   # one commit a minute leaves many loose objects; pack them hourly


def selftest():
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "x.csv"
        assert last_time(p) is None
        append(p, {120: [1, 2, 0.5, 1.5, 10, 15], 60: ["0.0381", "0.039", "0.038", "0.0385", "12245.9", "471.84252"]})
        assert p.read_text().splitlines() == ["time,open,high,low,close,volume,quote_volume",
                                              "60,0.0381,0.039,0.038,0.0385,12245.9,471.84252", "120,1,2,0.5,1.5,10,15"], p.read_text()
        assert last_time(p) == 120
        append(p, {180: [55.4, 55.8, 55.4, 55.5, 519723.15861122, 26697274.98927121]})
        assert last_time(p) == 180 and p.read_text().count("time,") == 1
    assert fmt(1340.0) == "1340" and fmt("0.04133") == "0.04133" and fmt(1e-05) == "1e-05"
    print("selftest OK")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
        sys.exit(0)
    bad = collect()
    if "--no-push" not in sys.argv:
        push()
    sys.exit(1 if bad else 0)
