# upbit-premium-chart

[English](README.md) | [繁體中文](README.zh-TW.md) | [简体中文](README.zh-CN.md)

A live chart of the BMT premium on Upbit over Binance and MEXC. BMT is the Bubblemaps token. Upbit quotes it in Korean won, so the page converts it to USDT and draws it next to Binance spot, the Binance USDT perpetual, MEXC spot and the MEXC USDT perpetual. Binance and MEXC start two weeks before BMT listed on Upbit, to show the run-up, and Upbit starts at its listing.

History is stored as CSV files on this repo's `data` branch, appended every minute by `collect.py`. The page reads those files first, so it opens in a second or two, then fetches the last few minutes live and keeps updating over WebSockets and polling. There's no backend and no API key in the page.

Live page: https://yyu0310.github.io/upbit-premium-chart/

![BMT on Upbit, Binance and MEXC from two weeks before the Upbit listing on 2026-10-24, 15-minute candles](docs/demo.png)

To run the page locally with an AI coding agent, paste this:

```
Clone https://github.com/yyu0310/upbit-premium-chart and serve the folder with any static file server, for example python3 -m http.server, then open index.html in a browser.
```

## What it shows

| Part | What it does |
| --- | --- |
| Show | Untick a venue to hide it in both panes, the header and the crosshair legend. The browser remembers the choice. |
| Top pane | Price in USDT for Upbit, Binance spot, Binance perp, MEXC spot and MEXC perp. The venue picked under Candles is drawn as candles, the others as close lines. An arrow marks the Upbit listing. |
| Bottom pane | Premium of every venue over the premium base, in percent. If the picked venue isn't the base, its premium is drawn as candles. |
| Premium base | Binance spot or MEXC spot. Use MEXC spot for a token Binance doesn't list. |
| Interval | 1m, 5m, 15m or 1h candles. 15m is the default. |
| KRW to USDT | Convert Upbit's won price with the USD/KRW exchange rate, or with Upbit's own KRW-USDT price minute by minute. The two differ because USDT itself trades at a premium in Korea. |
| Header numbers | Latest price for each venue, and its premium over the base. |
| Crosshair | Prices and premiums at the hovered candle. |

## Requirements

- A modern browser.
- Network access to `raw.githubusercontent.com`, `api.upbit.com`, `api.binance.com` or its mirror `data-api.binance.vision`, `fapi.binance.com`, `contract.mexc.com`, `wbs-api.mexc.com` and `open.er-api.com`.
- To run your own collector: Python 3.9 or later. It uses the standard library only.

## Quick start

Viewing the chart:
1. Clone the repo. An AI agent can do this.
2. Serve the folder with a static file server and open `index.html`. An AI agent can do this too.

Running your own collector is optional. The page reads this repo's `data` branch by default.
1. Clone the `data` branch into its own folder: `git clone -b data https://github.com/yyu0310/upbit-premium-chart data-clone`. An AI agent can do this.
2. Run `python3 collect.py --repo data-clone` on a schedule, every minute for example. With `--no-push` it only writes the CSV files.
3. To push, the clone needs write access to your fork. Create the deploy key or token yourself. Don't hand it to an AI agent.
4. Set `REPO` at the top of the script in `index.html` to your fork.

## Data sources

| Venue | History | Live updates | Live delay |
| --- | --- | --- | --- |
| Upbit KRW-BMT | CSV, then REST for the minutes after the last row | WebSocket `candle.1m` | About 0.4 s, 90% within 0.9 s |
| Upbit KRW-USDT | CSV, then REST for the minutes after the last row | WebSocket `candle.1m` | About 0.4 s |
| Binance spot BMTUSDT | CSV, then REST klines | REST poll every 2 seconds | Up to 2 s |
| Binance perp BMTUSDT | CSV, then REST klines | REST poll every 2 seconds | Up to 2 s |
| MEXC spot BMTUSDT | CSV only | WebSocket, protobuf frames | About 0.1 s |
| MEXC perp BMT_USDT | CSV only | WebSocket `sub.kline` | About 0.1 s |
| USD/KRW | `open.er-api.com`, loaded once | None. The source updates once a day | |

Live delays were measured from Taiwan on 2026-10-25, as receive time minus the exchange's timestamp, with the clock corrected to within about 0.3 seconds. A Binance request takes about 45 ms, so its delay is the 2-second poll.

CSV delay: a closed minute reached GitHub 27 to 88 seconds after it closed, 57 seconds at the median, measured over 4 minutes. The page adds up to 60 seconds for the commit lookup. A raw URL with the branch name adds up to 5 minutes of cache, so use `git pull` or a commit URL for the newest rows.

Use the CSV files for backtests. For live trading, connect to the exchanges directly from your own machine. AGENTS.md lists the endpoints, messages and measured delays.

Each CSV is `time,open,high,low,close,volume,quote_volume`, where `time` is the candle's open in unix seconds, UTC. `volume` is in BMT. `quote_volume` is in KRW for the two Upbit files and USDT for the others. Only closed minutes are written.

Premium = venue price / base price - 1.

## Limitations

- MEXC's REST APIs send no CORS header, so the page can't fetch the minutes between the last CSV row and the moment it opens. MEXC repeats its last stored close across those minutes until its WebSocket sends a new candle. The gap is usually 1 to 3 minutes.
- If the collector stops, the CSV files go stale. Upbit and Binance then fetch more history live and the MEXC gap grows.
- Binance and MEXC start at 2026-10-10 03:05 UTC, 14 days before the Upbit listing. Upbit starts at 2026-10-24 03:05 UTC. Times on the axis are local time.
- The chart redraws at most once a second. Two weeks of 1-minute candles is about 20,000 points per venue.
- Upbit only sends a candle for a minute with trades. A minute without trades repeats the previous close as a flat bar. Binance and MEXC always send a bar.
- For Upbit converted with KRW-USDT, the high and low use the KRW-USDT close of the same minute, so they are approximate.
- Upbit allows a web page about one request every 10 seconds, so the minutes after the last CSV row can take 10 to 20 seconds to appear. Live Upbit updates start immediately over the WebSocket.
- Right after the page opens, the Upbit status dot can turn red for a few seconds and then go green on its own. The first WebSocket connection seems to hit the same limit and reconnects 3 seconds later. Data isn't affected.
- Binance blocks some regions. If the base venue is unreachable, nothing is drawn, so switch the base. If another venue is unreachable, only that venue stays empty.
- Keep the tab in the foreground. Browsers slow timers in background tabs.
- Charts use [Lightweight Charts](https://github.com/tradingview/lightweight-charts) 5.0.8 from jsDelivr, pinned with a Subresource Integrity hash.

Nothing here is financial advice.

## License

MIT
