# upbit-premium-chart

[English](README.md) | [繁體中文](README.zh-TW.md) | [简体中文](README.zh-CN.md)

A live chart of the BMT premium on Upbit over Binance. BMT is the Bubblemaps token. Upbit quotes it in Korean won, so the page converts it to USDT and draws it next to Binance spot and the Binance USDT perpetual. There's no backend and no API key. The browser calls the exchanges directly and the chart keeps updating while the tab is open.

Live page: https://yyu0310.github.io/upbit-premium-chart/

![Upbit premium over Binance spot on 2026-10-24, the day BMT listed on Upbit](docs/demo.png)

To run it locally with an AI coding agent, paste this:

```
Clone https://github.com/yyu0310/upbit-premium-chart and serve the folder with any static file server, for example python3 -m http.server, then open index.html in a browser.
```

## What it shows

| Part | What it does |
| --- | --- |
| Top pane | Price in USDT for Upbit, Binance spot and Binance perp. The venue picked under Candles is drawn as candles, the other two as close lines. |
| Bottom pane | Premium of Upbit and of Binance perp over Binance spot, in percent. The picked venue is drawn as premium candles. |
| Interval | 1m, 5m or 15m candles. |
| KRW to USDT | Convert Upbit's won price with the USD/KRW exchange rate, or with Upbit's own KRW-USDT price minute by minute. The two differ because USDT itself trades at a premium in Korea. |
| Header numbers | Latest price and premium for each venue. |
| Crosshair | Prices and premiums at the hovered candle. |

## Requirements

- A modern browser.
- Network access to `api.upbit.com`, `api.binance.com` or its mirror `data-api.binance.vision`, `fapi.binance.com` and `open.er-api.com`.

## Quick start

What an AI agent can do for you:
1. Clone the repo.
2. Serve the folder with a static file server and open `index.html`.

What you do yourself: nothing else. There are no accounts, keys or settings.

## Data sources

| Venue | History from local midnight | Live updates |
| --- | --- | --- |
| Upbit KRW-BMT and KRW-USDT | REST 1-minute candles, 200 per request | WebSocket `candle.1m` |
| Binance spot BMTUSDT | REST 1-minute klines | REST poll every 2 seconds |
| Binance perp BMTUSDT | REST 1-minute klines | REST poll every 2 seconds |
| USD/KRW | `open.er-api.com`, loaded once | None. The source updates once a day |

Premium = venue price / Binance spot price - 1.

## Limitations

- MEXC is not included. Its futures REST API sends no CORS header, so a browser can't read its history.
- The chart covers today only, from local midnight. Times on the axis are local time.
- BMT listed on Upbit on 2026-10-24 at 03:05 UTC, so Upbit has no data before that.
- Upbit only sends a candle for a minute with trades. A minute without trades repeats the previous close as a flat bar. Binance always sends a bar.
- For Upbit converted with KRW-USDT, the high and low use the KRW-USDT close of the same minute, so they are approximate.
- Upbit allows a web page about one request every 10 seconds. The chart draws Binance right away, and older Upbit candles fill in one page of 200 at a time. Live Upbit updates start immediately over the WebSocket.
- Binance blocks some regions. If an API is unreachable from your network, that venue stays empty.
- Keep the tab in the foreground. Browsers slow timers in background tabs.
- Charts use [Lightweight Charts](https://github.com/tradingview/lightweight-charts) 5.0.8 from jsDelivr, pinned with a Subresource Integrity hash.

Nothing here is financial advice.

## License

MIT
