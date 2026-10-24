# upbit-premium-chart

[English](README.md) | [繁體中文](README.zh-TW.md) | [简体中文](README.zh-CN.md)

即時顯示 BMT 在 Upbit 相對幣安與 MEXC 的溢價。BMT 是 Bubblemaps 的代幣。Upbit 用韓元報價，頁面會換算成 USDT，跟幣安現貨、幣安 USDT 永續合約、MEXC 現貨、MEXC USDT 永續合約畫在一起，從 BMT 在 Upbit 上市那一分鐘畫到現在。

歷史資料以 CSV 存在這個 repo 的 `data` 分支，`collect.py` 每 5 分鐘補一次。頁面先讀這些檔，一兩秒就能打開，再即時補上最後幾分鐘，之後透過 WebSocket 與輪詢持續更新。頁面沒有後端，也不含任何 API 金鑰。

線上頁面：https://yyu0310.github.io/upbit-premium-chart/

![2026-10-24 Upbit 上市以來，BMT 在 Upbit、幣安、MEXC 的 5 分 K](docs/demo.png)

想在本機跑，把下面這段貼給 AI coding agent：

```
Clone https://github.com/yyu0310/upbit-premium-chart ，用任何靜態檔案伺服器開這個資料夾，例如 python3 -m http.server，再用瀏覽器打開 index.html。
```

## 畫面內容

| 區塊 | 功能 |
| --- | --- |
| 上圖 | Upbit、幣安現貨、幣安合約、MEXC 現貨、MEXC 合約的 USDT 價格。Candles 選哪家，哪家畫成 K 線，其他畫收盤線。 |
| 下圖 | 各家相對溢價基準的溢價百分比。選中的那家不是基準時，它的溢價畫成 K 線。 |
| Premium base | 溢價基準，可選幣安現貨或 MEXC 現貨。幣安沒上的幣改用 MEXC 現貨。 |
| Interval | 1 分、5 分、15 分、1 小時 K 線。 |
| KRW to USDT | Upbit 韓元價的換算方式：USD/KRW 匯率，或 Upbit 自己的 KRW-USDT 逐分鐘價格。USDT 在韓國本身有溢價，所以兩種算法結果不同。 |
| 右上數字 | 各家最新價格，以及相對基準的溢價。 |
| 十字線 | 游標所在那根 K 線的各家價格與溢價。 |

## 需求

- 新版瀏覽器。
- 網路連得到 `raw.githubusercontent.com`、`api.upbit.com`、`api.binance.com` 或它的鏡像 `data-api.binance.vision`、`fapi.binance.com`、`contract.mexc.com`、`wbs-api.mexc.com`、`open.er-api.com`。
- 想自己跑資料收集程式：Python 3.9 以上，只用標準函式庫。

## 快速開始

看圖：
1. Clone 這個 repo。AI agent 可以代勞。
2. 用靜態檔案伺服器開資料夾，打開 `index.html`。AI agent 也可以代勞。

自己跑資料收集程式是選用的，頁面預設讀這個 repo 的 `data` 分支。
1. 把 `data` 分支 clone 到獨立資料夾：`git clone -b data https://github.com/yyu0310/upbit-premium-chart data-clone`。AI agent 可以代勞。
2. 定時跑 `python3 collect.py --repo data-clone`，例如每 5 分鐘。加 `--no-push` 只寫 CSV、不推。
3. 要推的話，這份 clone 需要你 fork 的寫入權限。deploy key 或 token 請自己建立，不要交給 AI agent。
4. 把 `index.html` 程式開頭的 `RAW` 改成指向你 fork 的 `data` 分支。

## 資料來源

| 交易所 | 歷史 | 即時更新 |
| --- | --- | --- |
| Upbit KRW-BMT | CSV，最後一列之後用 REST 補 | WebSocket `candle.1m` |
| Upbit KRW-USDT | CSV，最後一列之後用 REST 補 | WebSocket `candle.1m` |
| 幣安現貨 BMTUSDT | CSV，再用 REST K 線補 | REST 每 2 秒輪詢 |
| 幣安合約 BMTUSDT | CSV，再用 REST K 線補 | REST 每 2 秒輪詢 |
| MEXC 現貨 BMTUSDT | 只有 CSV | WebSocket，protobuf 格式 |
| MEXC 合約 BMT_USDT | 只有 CSV | WebSocket `sub.kline` |
| USD/KRW | `open.er-api.com`，載入時抓一次 | 不更新，來源每天只更新一次 |

每個 CSV 的欄位是 `time,open,high,low,close`，`time` 是 K 線開盤時間，單位是 UTC 的 unix 秒。只寫已收盤的分鐘。

溢價 = 該交易所價格 / 基準價格 - 1。

## 限制

- MEXC 的 REST API 沒有 CORS 標頭，頁面抓不到 CSV 最後一列到打開頁面之間的那幾分鐘。這段 MEXC 用最後存下的收盤價補平線，等 WebSocket 推新 K 線才接上。空檔通常不到 10 分鐘：CSV 每 5 分鐘更新，`raw.githubusercontent.com` 再快取 5 分鐘。
- 資料收集程式停掉的話，CSV 就不會更新。Upbit 和幣安會改用 REST 抓比較長的一段，MEXC 的空檔會變長。
- 圖從 2026-10-24 UTC 03:05 開始，也就是 BMT 在 Upbit 上市的時間。時間軸是本地時間。
- Upbit 只有有成交的分鐘才有 K 線，沒成交的分鐘用上一根收盤補一根平線。幣安和 MEXC 每分鐘都有。
- 用 KRW-USDT 換算時，Upbit 的高低點用同一分鐘的 KRW-USDT 收盤價當分母，是近似值。
- 網頁打 Upbit 大約每 10 秒只能 1 次，所以 CSV 最後一列之後的 Upbit K 線要 10 到 20 秒才會出現。Upbit 的即時更新走 WebSocket，一打開就有。
- 剛打開頁面時，Upbit 的狀態燈可能紅幾秒，接著自己變綠。看起來是第一次 WebSocket 連線也被同一個限流擋下，3 秒後自動重連。資料不受影響。
- 幣安在部分地區被封鎖。連不到溢價基準時整張圖都不會畫，請切換基準。連不到其他交易所時，只有那家是空的。
- 分頁請保持在前景，瀏覽器會降低背景分頁的計時器頻率。
- 圖表用 jsDelivr 上的 [Lightweight Charts](https://github.com/tradingview/lightweight-charts) 5.0.8，並以 Subresource Integrity 雜湊鎖定版本。

本頁內容不構成投資建議。

## 授權

MIT
