---
name: vnpy-rqdata-data-pipeline
description: Download Chinese futures history from RQData (米筐) and prepare Parquet/CSV for vn.py backtests in vnpy-futures. Use when running download_rqdata_batch.py, rqdatac, MA888/RB888 continuous contracts, data/raw/rq parquet files, or fixing BarData load errors.
---

# RQData → Parquet/CSV → vn.py 回测数据

本仓库数据母版在 **`data/raw/rq/`**（Parquet）；回测直接读 Parquet，不依赖 SQLite 导入。

## 项目文件

| 用途 | 路径 |
|------|------|
| 批量下载 | `scripts/download_rqdata_batch.py` |
| 连接测试 | `scripts/test_rqdata.py` |
| 米筐账号 | `configs/rq_config.py`（`RQ_USER`, `RQ_PWD`） |
| 原始数据 | `data/raw/rq/{SYMBOL}_1m.parquet` |
| vn.py 风格 CSV | `data/csv/{symbol}_1m.csv` |
| 回测加载 | `scripts/parquet_data_loader.py` |

## 下载 SOP

### 1. 配置品种与区间

编辑 `scripts/download_rqdata_batch.py`：

```python
START_DATE = "2015-01-01"
END_DATE = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")
FREQUENCY = "1m"
SYMBOLS = ["MA888"]   # 米筐连续合约：RB888, MA888, M888 ...
```

新品种必须在 `EXCHANGE_MAP` 中补前缀 → 交易所，例如 `"MA": "CZCE"`、`"M": "DCE"`。

### 2. 运行下载

```powershell
.\.venv\Scripts\python.exe scripts\download_rqdata_batch.py
```

### 3. 检查输出

成功时应生成：

- `data/raw/rq/MA888_1m.parquet` — **回测用这个**
- `data/csv/ma888_1m.csv` — 备份/人工查看；当前 Parquet 回测不读 CSV

### 4. 常见失败

| 错误 | 处理 |
|------|------|
| `Quota exceeded` | 米筐额度用尽，稍后重试或换账号/套餐 |
| `返回空数据` | 合约代码错、无权限、日期区间无数据 |
| KeyError on `EXCHANGE_MAP` | 新品种未加映射 |

测试连接：

```powershell
.\.venv\Scripts\python.exe scripts\test_rqdata.py
```

## 合约与路径命名

| 米筐 order_book_id | parquet 文件名 | 回测 symbol | 示例 exchange |
|--------------------|----------------|-------------|---------------|
| `RB888` | `RB888_1m.parquet` | `rb888` | `SHFE` |
| `MA888` | `MA888_1m.parquet` | `ma888` | `CZCE` |
| `M888` | `M888_1m.parquet` | `m888` | `DCE` |

规则：

- 米筐用**大写** + `888` 连续合约。
- Parquet 文件名：`{SYMBOL}_1m.parquet`（大写）。
- `load_bar_data_from_parquet` 的 `symbol` 参数用**小写**。
- `vt_symbol` = `{symbol}.{EXCHANGE.value}`，如 `ma888.CZCE`。

## Parquet 结构（RQData）

`read_parquet` 后通常为 MultiIndex：`order_book_id`, `datetime`。列含 `open`, `high`, `low`, `close`, `volume`, `open_interest`, `total_turnover` 等。

`parquet_data_loader.py` 会 `reset_index()`，按 `start`/`end` 过滤，再转为 `BarData`：

```python
BarData(
    gateway_name="PARQUET",
    symbol=symbol,           # 小写
    exchange=exchange,
    datetime=...,
    interval=Interval.MINUTE,
    open_price=row.open,
    high_price=row.high,
    low_price=row.low,
    close_price=row.close,
    volume=row.volume,
    turnover=row.total_turnover,
    open_interest=row.open_interest,
)
```

## 接入回测

在 `scripts/run_backtest_parquet.py` 中：

```python
PARQUET_FILE = ROOT / "data" / "raw" / "rq" / "MA888_1m.parquet"
SYMBOL = "ma888"
EXCHANGE = Exchange.CZCE

engine.history_data = load_bar_data_from_parquet(
    PARQUET_FILE, SYMBOL, EXCHANGE, Interval.MINUTE, START, END
)
```

**不要**下载后只留 CSV 却走 `engine.load_data()`，除非另行实现 CSV→SQLite 导入。

## 数据流总览

```
米筐 RQData (rq.get_price)
    ↓
data/raw/rq/{SYMBOL}_1m.parquet   ← 母版，可重复转换
data/csv/{symbol}_1m.csv          ← 可选副本
    ↓
parquet_data_loader.load_bar_data_from_parquet
    ↓
list[BarData] → engine.history_data
    ↓
BacktestingEngine.run_backtesting()
```

## 增量更新

脚本当前为**全量重下**覆盖 parquet/csv。增量更新需自行改 `END_DATE` 或扩展脚本（未实现前不要假设支持增量）。

## 其他数据源

本仓库回测栈为 **vn.py + Parquet**（母版 `data/raw/rq/`）。第三方 H5/CSV 等不能直接被 `BacktestingEngine` 消费；若必须导入，需按上文字段转为 `BarData`，或优先走本仓库 RQData 下载链路。
