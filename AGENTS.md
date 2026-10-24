# AGENTS.md

Context for AI coding assistants working in this repo.

## What this is

Two parts:

- `index.html` on `main`: a single static page that charts the BMT premium on Upbit over a base venue, Binance spot or MEXC spot, with Binance perp, MEXC spot and MEXC perp alongside. There's no build step and no backend. The only dependency is Lightweight Charts 5.0.8, loaded from jsDelivr with an SRI hash.
- `collect.py` on `main`: appends closed 1-minute candles for six sources to `data/*.csv` and pushes them to the `data` branch. Standard library only, so it runs on the macOS system Python 3.9.

The `data` branch holds only the CSV files and a short README. It's kept apart from `main` so data commits don't trigger GitHub Pages builds.

## Data flow

1. The page loads the six CSV files from `raw.githubusercontent.com`, which caches for 5 minutes and sends CORS headers. GitHub Pages caches for 10 and ignores query strings.
2. It fills the minutes after the last CSV row: Upbit KRW-BMT and then KRW-USDT from REST, paged back to the last stored minute, and Binance spot and perp from REST klines. MEXC can't be filled, because its REST APIs send no CORS header.
3. Live updates come from the Upbit WebSocket `candle.1m`, the MEXC futures WebSocket `sub.kline`, and the MEXC spot WebSocket, which only pushes protobuf. Binance spot and perp are polled every 2 seconds.
4. Every source is a 1-minute map keyed by open time in unix seconds, aligned to one grid from the listing minute, where a missing minute repeats the previous close. The page converts Upbit to USDT, aggregates to the chosen interval and draws.

## Constraints

- Upbit allows a web page about one request every 10 seconds, and its 429 reply has no CORS header, so the browser sees a network error. Keep the 10.5 second spacing and retry in `upbitGet`. A local origin such as `http://localhost` isn't limited, so test the pacing on the deployed page.
- MEXC spot protobuf: the wrapper's field 308 is the kline. Inside it, field 2 is the open time in seconds and fields 3, 4, 5 and 6 are open, close, high and low as decimal strings. `pbFields` reads only what's needed.
- MEXC spot REST klines ignore `startTime` unless `endTime` is also given, return at most 500 rows, and treat `endTime` as exclusive. `collect.py` walks 500-minute windows.
- Binance perp WebSocket was silent in testing, so Binance stays on REST polling.
- Keep the SRI hash when touching the Lightweight Charts script tag.

## Testing

- `python3 collect.py --selftest` runs offline checks. `python3 collect.py --no-push` writes `./data` without git.
- Page: serve the folder with `python3 -m http.server`. To test against local CSV files, change `RAW` to `"data/"` in a copy. Open it in headless Chrome with `--remote-debugging-port`, then read `M`, which holds the bar map per source, and `#stat` through the DevTools protocol. Binance spot and perp gain one bar per minute. Upbit only gains a bar for a minute with trades.
