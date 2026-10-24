# upbit-premium-chart

[English](README.md) | [繁體中文](README.zh-TW.md) | [简体中文](README.zh-CN.md)

即時顯示 BMT 在 Upbit 相對幣安的溢價。BMT 是 Bubblemaps 的代幣。Upbit 的 BMT 用韓元報價，頁面會換算成 USDT，跟幣安現貨、幣安 USDT 永續合約畫在一起。沒有後端，也不用 API 金鑰。瀏覽器直接呼叫交易所 API，分頁開著圖就會持續更新。

線上頁面：https://yyu0310.github.io/upbit-premium-chart/

![2026-10-24 BMT 在 Upbit 上市當天，Upbit 相對幣安現貨的溢價](docs/demo.png)

想在本機跑，把下面這段貼給 AI coding agent：

```
Clone https://github.com/yyu0310/upbit-premium-chart ，用任何靜態檔案伺服器開這個資料夾，例如 python3 -m http.server，再用瀏覽器打開 index.html。
```

## 畫面內容

| 區塊 | 功能 |
| --- | --- |
| 上圖 | Upbit、幣安現貨、幣安合約的 USDT 價格。Candles 選哪家，哪家畫成 K 線，另外兩家畫收盤線。 |
| 下圖 | Upbit 與幣安合約相對幣安現貨的溢價百分比。選中的那家畫成溢價 K 線。 |
| Interval | 1 分、5 分、15 分 K 線。 |
| KRW to USDT | Upbit 韓元價的換算方式：USD/KRW 匯率，或 Upbit 自己的 KRW-USDT 逐分鐘價格。USDT 在韓國本身有溢價，所以兩種算法結果不同。 |
| 右上數字 | 各家最新價格與溢價。 |
| 十字線 | 游標所在那根 K 線的各家價格與溢價。 |

## 需求

- 新版瀏覽器。
- 網路連得到 `api.upbit.com`、`api.binance.com` 或它的鏡像 `data-api.binance.vision`、`fapi.binance.com`、`open.er-api.com`。

## 快速開始

AI agent 可以代勞的：
1. Clone 這個 repo。
2. 用靜態檔案伺服器開資料夾，打開 `index.html`。

你自己要做的：沒有了。不需要帳號、金鑰或任何設定。

## 資料來源

| 交易所 | 歷史，從本地時間午夜起 | 即時更新 |
| --- | --- | --- |
| Upbit KRW-BMT 與 KRW-USDT | REST 1 分鐘 K 線，每次 200 根 | WebSocket `candle.1m` |
| 幣安現貨 BMTUSDT | REST 1 分鐘 K 線 | REST 每 2 秒輪詢 |
| 幣安合約 BMTUSDT | REST 1 分鐘 K 線 | REST 每 2 秒輪詢 |
| USD/KRW | `open.er-api.com`，載入時抓一次 | 不更新，來源每天只更新一次 |

溢價 = 該交易所價格 / 幣安現貨價格 - 1。

## 限制

- 沒有 MEXC。MEXC 合約 REST API 沒有 CORS 標頭，瀏覽器讀不到歷史資料。
- 只看今天，從本地時間午夜開始，時間軸是本地時間。
- BMT 在 2026-10-24 UTC 03:05 於 Upbit 上市，之前 Upbit 沒有資料。
- Upbit 只有有成交的分鐘才有 K 線，沒成交的分鐘用上一根收盤補一根平線。幣安每分鐘都有。
- 用 KRW-USDT 換算時，Upbit 的高低點用同一分鐘的 KRW-USDT 收盤價當分母，是近似值。
- 網頁打 Upbit 大約每 10 秒只能 1 次。圖會先畫出幣安，Upbit 的舊 K 線每次補 200 根，慢慢補上。Upbit 的即時更新走 WebSocket，一打開就有。
- 幣安在部分地區被封鎖。你的網路連不到某個 API 時，那家就會是空的。
- 分頁請保持在前景，瀏覽器會降低背景分頁的計時器頻率。
- 圖表用 jsDelivr 上的 [Lightweight Charts](https://github.com/tradingview/lightweight-charts) 5.0.8，並以 Subresource Integrity 雜湊鎖定版本。

本頁內容不構成投資建議。

## 授權

MIT
