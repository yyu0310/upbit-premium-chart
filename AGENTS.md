# AGENTS.md

Context for AI coding assistants working in this repo.

## What this is

Two parts:

- `index.html` on `main`: a single static page that charts the BMT premium on Upbit over a base venue, Binance spot or MEXC spot, with Binance perp, MEXC spot and MEXC perp alongside. There's no build step and no backend. The only dependency is Lightweight Charts 5.0.8, loaded from jsDelivr with an SRI hash.
- `collect.py` on `main`: appends closed 1-minute candles for six sources, Upbit from its listing and Binance and MEXC from 14 days earlier, to `data/*.csv` and pushes them to the `data` branch. Standard library only, so it runs on the macOS system Python 3.9.

The `data` branch holds only the CSV files and a short README. It's kept apart from `main` so data commits don't trigger GitHub Pages builds.

## Data flow

1. The page looks up the latest `data` commit through the GitHub API, cached 60 seconds and limited to 60 calls an hour per IP, then loads the six CSV files from `raw.githubusercontent.com` at that commit. A raw URL with the branch name is cached for 5 minutes. GitHub Pages caches for 10 and ignores query strings.
2. It fills the minutes after the last CSV row: Upbit KRW-BMT and then KRW-USDT from REST, paged back to the last stored minute, and Binance spot and perp from REST klines. MEXC can't be filled, because its REST APIs send no CORS header.
3. Live updates come from the Upbit WebSocket `candle.1m`, the MEXC futures WebSocket `sub.kline`, and the MEXC spot WebSocket, which only pushes protobuf. Binance spot and perp are polled every 2 seconds.
4. Every source is a 1-minute map keyed by open time in unix seconds, aligned to one grid from two weeks before the listing, where a missing minute repeats the previous close. The page converts Upbit to USDT, aggregates to the chosen interval and draws.

## Constraints

- Upbit allows a web page about one request every 10 seconds, and its 429 reply has no CORS header, so the browser sees a network error. Keep the 10.5 second spacing and retry in `upbitGet`. A local origin such as `http://localhost` isn't limited, so test the pacing on the deployed page.
- MEXC spot protobuf: the wrapper's field 308 is the kline. Inside it, field 2 is the open time in seconds and fields 3, 4, 5 and 6 are open, close, high and low as decimal strings. `pbFields` reads only what's needed.
- MEXC spot REST klines ignore `startTime` unless `endTime` is also given, return at most 500 rows, and treat `endTime` as exclusive. `collect.py` walks 500-minute windows.
- Binance perp WebSocket was silent in testing, so Binance stays on REST polling.
- Keep the SRI hash when touching the Lightweight Charts script tag.
- Two weeks of 1m candles is about 20,000 points per series, so `schedule()` redraws at most once a second. A full 1m redraw measured 66 ms, 15m 11 ms.

## Using the data for backtests

The CSV files on the `data` branch are public and free to download. No account or key is needed.

- One file: `https://raw.githubusercontent.com/yyu0310/upbit-premium-chart/data/data/<name>.csv`
- All files: `git clone -b data --depth 1 https://github.com/yyu0310/upbit-premium-chart`
- pandas: `pd.read_csv(url)`, then `pd.to_datetime(df["time"], unit="s", utc=True)`

| `<name>` | Market | Quote | Starts (UTC) |
| --- | --- | --- | --- |
| `upbit_krw_bmt` | Upbit KRW-BMT | KRW | 2026-10-24 03:05 |
| `upbit_krw_usdt` | Upbit KRW-USDT | KRW | 2026-10-24 03:05 |
| `binance_spot` | Binance spot BMTUSDT | USDT | 2026-10-10 03:05 |
| `binance_perp` | Binance USDT perpetual BMTUSDT | USDT | 2026-10-10 03:05 |
| `mexc_spot` | MEXC spot BMTUSDT | USDT | 2026-10-10 03:05 |
| `mexc_perp` | MEXC USDT perpetual BMT_USDT | USDT | 2026-10-10 03:05 |

Things to know before backtesting:

- Columns are `time,open,high,low,close,volume,quote_volume`. `time` is the candle's open in unix seconds, UTC.
- `volume` is in BMT. `quote_volume` is in the quote currency: KRW for the two Upbit files, USDT for the others. MEXC perp reports contracts, which `collect.py` converts to BMT with the contract size from the MEXC API, 10 BMT per contract when checked.
- 1-minute candles only. Only closed minutes are written. `collect.py` runs every minute, and a closed minute reached GitHub 27 to 88 seconds after it closed, 57 seconds at the median. A raw URL with the branch name can be 5 minutes older, so use `git pull` or a commit URL for the newest rows.
- Upbit has no row for a minute without trades, so fill or skip those minutes yourself. The Binance and MEXC files have one row per minute with no gaps, and a minute without trades has volume 0.
- Upbit prices are in Korean won. To get USDT, divide by the `upbit_krw_usdt` close of the same minute, or by a USD/KRW rate.
- The rows come from each exchange's public REST API through `collect.py`. They haven't been reconciled against official exchange history files.
- The MIT license covers the code. The market data belongs to the exchanges, so check their API terms before redistributing it or using it commercially.

## Live data for trading

Use the CSV files for backtests only. A trading program should connect to the exchanges directly from its own machine. GitHub adds at least a minute: rows are pushed once a minute, only after each minute closes, and the commit lookup is cached for 60 seconds.

Delays below were measured from Taiwan on 2026-10-25, as receive time minus the exchange's timestamp, with the local clock corrected by `sntp` to within about 0.3 seconds.

| Venue | Endpoint | Subscribe or request | Delay |
| --- | --- | --- | --- |
| Upbit KRW-BMT, KRW-USDT | `wss://api.upbit.com/websocket/v1` | `[{"ticket":"any"},{"type":"candle.1m","codes":["KRW-BMT","KRW-USDT"]}]`. Use `"type":"trade"` for every trade. Frames are binary UTF-8 JSON. Send the text `PING` every 60 seconds | Median about 0.4 s, 90% within 0.9 s |
| Binance spot BMTUSDT | `wss://stream.binance.com:9443/ws/bmtusdt@kline_1m` or `@trade` | None, the stream name is the subscription | About 0.1 s |
| Binance perp BMTUSDT | REST `https://fapi.binance.com/fapi/v1/klines?symbol=BMTUSDT&interval=1m&limit=2` | Poll. The futures WebSocket `wss://fstream.binance.com/ws/bmtusdt@kline_1m` and `@aggTrade` sent nothing in 30 seconds of testing | One request takes about 45 ms, so the delay is your poll interval |
| MEXC spot BMTUSDT | `wss://wbs-api.mexc.com/ws` | `{"method":"SUBSCRIPTION","params":["spot@public.kline.v3.api.pb@BMTUSDT@Min1"]}`. Frames are protobuf, see below. Send `{"method":"PING"}` every 20 seconds. The JSON channel on `wss://wbs.mexc.com/ws` replies "Blocked" | About 0.1 s |
| MEXC perp BMT_USDT | `wss://contract.mexc.com/edge` | `{"method":"sub.kline","param":{"symbol":"BMT_USDT","interval":"Min1"}}`. Messages with `channel` `push.kline` carry `data.t` in seconds, `o`, `h`, `l`, `c`, `q` in contracts and `a` in USDT. Send `{"method":"ping"}` every 15 seconds | About 0.1 s |

- MEXC spot protobuf: the wrapper's field 308 is the kline. Inside it, field 2 is the open time in seconds, fields 3, 4, 5 and 6 are open, close, high and low as decimal strings. `pbFields` in `index.html` is a 20-line decoder.
- MEXC perp volume is in contracts. Multiply by `contractSize` from `https://contract.mexc.com/api/v1/contract/detail?symbol=BMT_USDT`, 10 BMT when checked.
- Rate limits for REST: Upbit about 10 requests a second from a server but about one every 10 seconds from a web page, Binance 6,000 weight a minute per IP, MEXC 20 requests every 2 seconds.
- `socket()` in `index.html` shows a reconnect and heartbeat pattern that has run against all three WebSockets.

## Testing

- `python3 collect.py --selftest` runs offline checks. `python3 collect.py --no-push` writes `./data` without git.
- Page: serve the folder with `python3 -m http.server`. To test against local CSV files, set `RAW` to `"data/"` in a copy and remove the `latestData()` call. Open it in headless Chrome with `--remote-debugging-port`, then read `M`, which holds the bar map per source, and `#stat` through the DevTools protocol. Binance spot and perp gain one bar per minute. Upbit only gains a bar for a minute with trades.
