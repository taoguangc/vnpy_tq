---
name: quant-backtest-validation-tool
description: Audit vn.py CTA backtests in vnpy_quant for lookahead bias, Parquet data issues, cost/position sizing errors, and metric sanity. Use when backtest results look suspicious, zero trades, annual return jumps, comparing zero-cost vs含成本, or before trusting external tutorial claims.
tags: ['quant', 'backtest', 'validation', 'risk-check', 'futures', 'vnpy', 'parquet']
version: '1.1.0'
---

# 量化回测校验（vnpy_quant）

对 **策略代码 + 回测配置 + 统计结果** 做审计，输出问题清单与根因假设。**不自动改策略、不自动发起第二轮及以后回测**（流程约束见仓库根目录 `AGENTS.md` §5）。

## 何时必须使用本 skill

- 年化/回撤/夏普相对历史结论 **突变**（如 9%→90% 仅改仓位）
- `total_trade_count == 0` 或交易次数与信号逻辑明显不符
- 含成本由盈转亏，或 `--zero-cost` 与含成本差异过大
- 接入 CSDN/51CTO/TradingView 等 **外来代码或回测数字**
- 用户明确要求「查未来函数」「校验回测」「审计数据」

## 相关文件

| 用途 | 路径 |
|------|------|
| Round-trip 配对与胜率/盈亏比 | `scripts/backtest_trade_analysis.py` |
| Parquet 加载 | `scripts/parquet_data_loader.py` |
| 回测 SOP / 引擎参数 | `.agents/skills/vnpy-cta-backtest/SKILL.md` |
| 数据下载 | `.agents/skills/vnpy-quant-python/SKILL.md` §TQ 数据 |
| 流程与风控底线 | `AGENTS.md` + `AGENTS_DETAIL.md` |
| 外来代码检查表 | `AGENTS_DETAIL.md` §7 |

---

## 审计输出格式（必须）

用中文输出，结构固定为四块（与 `AGENTS.md` §5.2 **完整四段**同类结构，此处侧重**审计**而非改参）：

1. **审计结论**：通过 / 有条件通过 / 不通过（一句话）。
2. **发现项**：按严重程度列 `P0`（致命）/`P1`（重要）/`P2`（建议），每项写清「现象 → 可能根因 → 验证方式」。
3. **指标交叉核对**：引擎 `calculate_statistics` vs round-trip 汇总是否自洽（见下文 §5）。
4. **建议的下一步**：**仅 1 个**优先动作（或 2～3 个可选），并写明需用户确认后再改代码/再回测。

**禁止**：为「验证猜测」擅自再跑回测、参数扫描或 `diagnose_strategy.py` 网格（除非用户授权）。

---

## 1. 数据完整性

### 1.1 数据源与路径

- [ ] 数据来自 `data/tq/{prefix}/` TQ 分月 Parquet + CbC 拼接链路。
- [ ] `load_bar_data_from_parquet` 的 `symbol` **小写**（如 `rb888`），与 `vt_symbol`（如 `rb888.SHFE`）一致。
- [ ] 回测 `start`/`end` 落在 parquet 实际日期范围内；加载后 `len(engine.history_data)` 与区间匹配（非 0、非异常少）。
- [ ] 未在 Parquet 流程中误用 `engine.load_data()`（SQLite）。

### 1.2 时间与连续性

- [ ] 1m 序列无大面积断档（夜盘/午休除外）；注意节假日、主力 888 换月处的 **跳空** 是否被策略误读为信号。
- [ ] `datetime` 单调、无重复 bar；`ArrayManager` 在 `am.inited` 之前无交易逻辑。

### 1.3 连续合约

- [ ] 使用 CbC 分月拼接时，策略逻辑是否假设「物理主力」；换月跳空是否触发假突破/假止损。
- [ ] 样本区间是否覆盖至少 2 个主力周期（`AGENTS_DETAIL.md` §3）。

---

## 2. 未来函数与执行语义

### 2.1 指标与信号

- [ ] 无 `shift(-1)`、未来 bar 的 high/low/close 参与**当前** bar 信号。
- [ ] 多周期：`BarGenerator` 合成的大周期 bar 是否在 **周期结束** 后才用于决策（避免用未收盘 K 线）。
- [ ] `ArrayManager` 每 bar 先 `update_bar` 再算指标；RSI/ATR/SMA 窗口长度与 `load_bar` 天数一致。

### 2.2 vn.py `BacktestingEngine` 特性（本仓库默认）

- [ ] 同 bar 内：信号常基于 **当根收盘价**，成交也按当根 close（±滑点）——偏乐观；审计时若收益过高，标注「同 bar 成交偏差」。
- [ ] 停止单：触发价与 `slippage`（tick 数）是否与 `pricetick` 一致。
- [ ] 过滤条件（日盘 `day_session_only`、ATR 过滤等）是否在代码与 `add_strategy(setting)` 中 **同时生效**（避免参数写了但未传入）。

### 2.3 外来教程（扩展 `AGENTS_DETAIL.md` §7）

- [ ] `from vnpy_ctastrategy import ...`，非 `vnpy.app.cta_strategy`。
- [ ] 动态手数：`手数 ≈ risk_money / (ATR × contract_size)`，且 `contract_size == engine.size`。
- [ ] 外网年化/回撤数字：**未在本仓库含成本复现前不得引用**。

---

## 3. 成本、仓位与风控

### 3.1 引擎成本参数

- [ ] `rate`、`slippage` 与报告中的 `total_commission`、`total_slippage` 非零（含成本回测）。
- [ ] 零成本对照（`--zero-cost`）须在报告中 **单独标注**，不与含成本结论混谈。
- [ ] 毛利润拆解：`gross ≈ total_net_pnl + commission + slippage`（逻辑一致即可，允许四舍五入误差）。

### 3.2 仓位与乘数

- [ ] `engine.set_parameters(size=...)` 与品种一致（RB/HC/i 等常见为 10；以交易所规则为准）。
- [ ] 策略内 `contract_size` / 名义风险计算与 `size` 一致。
- [ ] `max(1, int(...))` 是否在高波动时仍强制 1 手，导致风险上限失效。
- [ ] 单笔亏损是否可能超过资金 1%（抽查最大亏损 round-trip 的 `capital_pct`）。

### 3.3 止损与平仓

- [ ] 除均线/指标反向信号外，是否存在 **独立止损**（ATR、固定比例、时间平仓如 14:50）。
- [ ] 平仓方向与持仓一致（多仓 `sell`、空仓 `cover`）；`cancel_all` 与挂单逻辑无死锁。

---

## 4. 风险指标与结果合理性

### 4.1 引擎统计字段

核对 `engine.calculate_statistics()` 至少包含：

`annual_return`、`total_net_pnl`、`max_drawdown`、`max_ddpercent`、`total_trade_count`、`sharpe_ratio`、`total_commission`、`total_slippage`。

### 4.2 异常模式（红旗）

| 现象 | 常见根因 |
|------|----------|
| 交易次数不变，年化暴增 | 仅改手数/乘数错误、零成本、或 `size` 设错 |
| 交易次数为 0 | parquet 路径/区间、`min_atr_pct` 过高、日盘过滤、未 `am.inited` |
| 胜率很高但年化很差 | 成本吞噬、盈亏比极差、单笔大亏 |
| 含成本巨亏、零成本大赚 | 正常；应优化信号而非先砍 `slippage` |
| 夏普 >3 且 1min 高频 | 过拟合、同 bar 成交、样本过短 |

### 4.3 样本与结论

- [ ] 是否单年、单品种、仅多头/仅日盘；结论是否过度外推。
- [ ] 与用户/外网历史结论对比时，区间、品种、成本设置是否一致。

---

## 5. Round-trip 交叉核对（推荐）

在策略 `run_parquet_backtest()` 或审计脚本中，用 `scripts/backtest_trade_analysis.py`：

```python
from scripts.backtest_trade_analysis import pair_round_trips, summarize_round_trips

round_trips = pair_round_trips(
    engine.get_all_trades(),
    size=engine.size,
    rate=rate,           # 与 set_parameters 一致
    slippage=slippage,
    capital=engine.capital,
)
summary = summarize_round_trips(round_trips)
# summary: win_rate, payoff_ratio, profit_factor, total, wins, losses
```

核对项：

- [ ] `summary["total"]` 与 `total_trade_count` 量级合理（一笔 round-trip 对应开平，与成交笔数关系因策略而异，但不应差一个数量级而无解释）。
- [ ] `win_rate`、`payoff_ratio` 与策略 `on_stop` 或打印的胜率是否接近。
- [ ] 回测结束仍有持仓时，用 `snapshot_open_position_at_end` 解释 `total_net_pnl` 与已平仓 round-trip 之和的差异。

---

## 6. Agent 行为边界

| 允许 | 禁止 |
|------|------|
| 读代码、读 parquet 元数据、读已有回测日志 | 未经用户确认的第二轮回测 |
| 输出审计报告与 1 条下一步建议 | 自动 `optimize` / 网格 / 改参连跑 |
| 建议用户跑 `--zero-cost` 做 **一次** 对照（须用户确认） | 为通过审计而降低 `slippage` 或扩大样本「刷指标」 |

回测执行细节与命令见 **vnpy-cta-backtest** skill；数据问题先查 **vnpy-quant-python** §TQ 数据。

---

## 7. 快速检查清单（复制用）

```
[ ] Parquet 路径 + 区间 + symbol 小写
[ ] 含成本 rate/slippage/size/pricetick
[ ] ArrayManager update_bar + inited
[ ] 无未来数据 / 多周期收盘
[ ] 动态手数含 contract_size
[ ] 独立止损或时间平仓
[ ] 引擎 stats 与 round_trips 大致自洽
[ ] 结论标注样本局限；外网数字已复现
[ ] 仅输出审计，未擅自再回测
```
