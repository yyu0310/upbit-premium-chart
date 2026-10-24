# upbit-premium-chart

[English](README.md) | [繁體中文](README.zh-TW.md) | [简体中文](README.zh-CN.md)

实时显示 BMT 在 Upbit 相对币安的溢价。BMT 是 Bubblemaps 的代币。Upbit 的 BMT 用韩元报价，页面会换算成 USDT，和币安现货、币安 USDT 永续合约画在一起。没有后端，也不用 API 密钥。浏览器直接调用交易所 API，页面开着图表就会持续更新。

在线页面：https://yyu0310.github.io/upbit-premium-chart/

![2026-10-24 BMT 在 Upbit 上线当天，Upbit 相对币安现货的溢价](docs/demo.png)

想在本地运行，把下面这段贴给 AI coding agent：

```
Clone https://github.com/yyu0310/upbit-premium-chart ，用任何静态文件服务器打开这个文件夹，例如 python3 -m http.server，再用浏览器打开 index.html。
```

## 页面内容

| 区块 | 功能 |
| --- | --- |
| 上图 | Upbit、币安现货、币安合约的 USDT 价格。Candles 选哪家，哪家画成 K 线，另外两家画收盘线。 |
| 下图 | Upbit 与币安合约相对币安现货的溢价百分比。选中的那家画成溢价 K 线。 |
| Interval | 1 分、5 分、15 分 K 线。 |
| KRW to USDT | Upbit 韩元价的换算方式：USD/KRW 汇率，或 Upbit 自己的 KRW-USDT 逐分钟价格。USDT 在韩国本身有溢价，所以两种算法结果不同。 |
| 右上数字 | 各家最新价格与溢价。 |
| 十字线 | 光标所在那根 K 线的各家价格与溢价。 |

## 需求

- 新版浏览器。
- 网络能访问 `api.upbit.com`、`api.binance.com` 或它的镜像 `data-api.binance.vision`、`fapi.binance.com`、`open.er-api.com`。

## 快速开始

AI agent 可以代劳的：
1. Clone 这个 repo。
2. 用静态文件服务器打开文件夹，打开 `index.html`。

你自己要做的：没有了。不需要账号、密钥或任何设置。

## 数据来源

| 交易所 | 历史，从本地时间午夜起 | 实时更新 |
| --- | --- | --- |
| Upbit KRW-BMT 与 KRW-USDT | REST 1 分钟 K 线，每次 200 根 | WebSocket `candle.1m` |
| 币安现货 BMTUSDT | REST 1 分钟 K 线 | REST 每 2 秒轮询 |
| 币安合约 BMTUSDT | REST 1 分钟 K 线 | REST 每 2 秒轮询 |
| USD/KRW | `open.er-api.com`，加载时获取一次 | 不更新，来源每天只更新一次 |

溢价 = 该交易所价格 / 币安现货价格 - 1。

## 限制

- 没有 MEXC。MEXC 合约 REST API 没有 CORS 头，浏览器读不到历史数据。
- 只看今天，从本地时间午夜开始，时间轴是本地时间。
- BMT 在 2026-10-24 UTC 03:05 于 Upbit 上线，之前 Upbit 没有数据。
- Upbit 只有有成交的分钟才有 K 线，没成交的分钟用上一根收盘补一根平线。币安每分钟都有。
- 用 KRW-USDT 换算时，Upbit 的高低点用同一分钟的 KRW-USDT 收盘价当分母，是近似值。
- Upbit 会对浏览器请求限流。页面会退避重试，但连续刷新时加载可能变慢。
- 币安在部分地区被封锁。你的网络访问不到某个 API 时，那家就会是空的。
- 页面请保持在前台，浏览器会降低后台页面的计时器频率。
- 图表用 jsDelivr 上的 [Lightweight Charts](https://github.com/tradingview/lightweight-charts) 5.0.8，并以 Subresource Integrity 哈希锁定版本。

本页内容不构成投资建议。

## 许可

MIT
