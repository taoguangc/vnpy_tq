---
name: vnpy-cta-backtest
description: Run vn.py CTA Parquet backtests in vnpy_quant. Use for BacktestingEngine, run_parquet_backtest, SYMBOL_PROFILES, --symbol, --zero-cost, --compare, pair_round_trips, or AGENTS.md §5 workflow.
version: '1.3.0'
---

# vn.py CTA Parquet 回测

**路径**：Parquet → `load_bar_data_from_parquet` → `engine.history_data` → `run_backtesting()`。**禁止** Parquet 流程中 `engine.load_data()`（SQLite）。

**流程**：`AGENTS.md` §5（探索 3 次 / 排障 3 次）。**审计**（结果可疑时）：`quant-backtest-validation-tool`。**编码/风控**：`AGENTS.md` §2、`AGENTS_DETAIL.md` §4。

## 关键路径

| 用途 | 路径 |
|------|------|
| 通用入口 | `scripts/run_backtest_parquet.py` |
| Parquet 加载 | `scripts/parquet_data_loader.py` |
| Round-trip | `scripts/backtest_trade_analysis.py` |
| 品种 size/slippage | `scripts/symbol_profiles.md` |
| 回测模板 | `strategies/pac_pullback_strategy.py` |
| 参数扫描（须授权） | `scripts/diagnose_strategy.py` |
| 数据 | `data/tq/{prefix}/` 分月 Parquet + CbC 拼接 |

## 默认常量

| 项 | 值 |
|----|-----|
| 区间 | `2023-05-17` → `2026-05-16` |
| capital | `200_000` |
| rate | `0.00003` |
| interval | `Interval.MINUTE` |

## 运行命令

```powershell
.\.venv\Scripts\python.exe strategies\pac_pullback_strategy.py --symbol i888
.\.venv\Scripts\python.exe strategies\<策略>.py --symbol i888 --zero-cost
.\.venv\Scripts\python.exe scripts\run_backtest_parquet.py
```

终端只取末尾指标表；`--compare` / `--all` 整命令计 1 轮回测（`AGENTS.md` §5.1）。

## SOP（6 步）

1. 确认 parquet 存在
2. `set_parameters`（区间、成本、size、pricetick——见 `symbol_profiles.md`）
3. `history_data = load_bar_data_from_parquet(...)`
4. `add_strategy(Class, setting)`（过滤/日盘参数必须传入）
5. `run_backtesting` → `calculate_result` → `calculate_statistics`
6. 可选 `pair_round_trips` 核对胜率/盈亏比

代码模板：Grep `run_parquet_backtest` in `strategies/pac_pullback_strategy.py`，勿在 skill 内重复贴大段示例。

## 成本与排查

1. `gross ≈ net + commission + slippage`
2. `--zero-cost` 须标注「零成本，不可与实盘混比」
3. 交易过少：parquet 区间、`min_atr_pct`、日盘过滤、`setting` 未传入
4. 勿擅自降低 `slippage`
5. `diagnose_strategy.py` 须用户授权（`AGENTS.md` §5.3）

## 常见错误

| 现象 | 原因 |
|------|------|
| 无成交/数据为 0 | parquet 缺失、symbol 大小写、区间超范围 |
| 年化异常跳变 | `size` 错、动态手数未乘 `contract_size`、零成本当含成本 |
| 与历史不一致 | 区间/品种/成本/`day_session_only` 与 setting 不一致 |
| 极慢 | 误用 SQLite `load_data()` |
| 指标 NaN | 未 `update_bar` / 未 `inited` |
| 过滤无效 | `add_strategy` 未传过滤参数 |

数据下载：`tools/download_rb_monthly.py`、`scripts/download_new_symbols_1m.py`（见 `vnpy-quant-python`）。`scripts/` 约定：`vnpy-quant-python`。
