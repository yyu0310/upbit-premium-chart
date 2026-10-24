# AGENTS.md

Context for AI coding assistants working in this repo.

## What this is

A single static page, `index.html`, that charts the BMT premium on Upbit over Binance spot, with Binance perp alongside. There's no build step and no backend. The only dependency is Lightweight Charts 5.0.8, loaded from jsDelivr with an SRI hash.

## Data flow

1. On load, the page fetches today's 1-minute candles from local midnight. Upbit KRW-BMT and KRW-USDT come from REST at 200 candles per page, newest first, paged with an exclusive `to`. Binance spot and perp come from REST klines, and USD/KRW from `open.er-api.com`.
2. Live updates come from the Upbit WebSocket `candle.1m` for both Upbit markets. Binance spot and perp are polled every 2 seconds.
3. Every source is stored as a 1-minute map keyed by open time in unix seconds and aligned to one minute grid, where a missing minute repeats the previous close. The page converts Upbit to USDT, aggregates to the chosen interval and draws.

## Constraints

- Everything runs in the browser, so every endpoint must send CORS headers or be a WebSocket. MEXC futures REST doesn't, which is why MEXC isn't included.
- Upbit throttles browser requests. Keep the 429 backoff in `getJson`.
- Binance perp WebSocket was silent in testing, so Binance stays on REST polling.
- Keep the SRI hash when touching the Lightweight Charts script tag.

## Testing

Serve the folder with `python3 -m http.server` and open it in headless Chrome with `--remote-debugging-port`. Read `M`, which holds the bar count per source, and `#stat` through the DevTools protocol. Each source should gain one bar per minute.
