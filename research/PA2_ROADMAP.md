# PA2 — Quantified Brooks CTA（Program 2.0 → 3.0）

> Research Program 1.0 已于 2026-07-11 归档。Program 2.0 Event 线（006–008）于 **2026-07-12 归档**。当前执行 **Program 3.0**：可交易配置（pa_cta OPP + 品种菜单），不再开新 Event detector。

## 0. 研究纪律

- **3 个月内禁止**：新 1m/微观因子、S1/S2/S3 调参、tick-native 复活、**新 Event detector / 1m 因子**。
- **`research/event_engine/`**：代码保留作基础设施；**禁止再烧回测配额**（006–008 已 FAIL）。
- **Program 3.0 允许**：pa_cta 回测 EXP、Setup AFF OOS、lean 多品种扫描、分品种 Purification 菜单。
- **时间周期**：006A–008A 已证多周期 FP/BP/FB Base Edge ≈ 0；不再预设 15m > 5m 开新 Event 线。

## 1. 目标交易画像（Hypothesis，待验证）

| 维度 | 目标 |
|------|------|
| 平均盈利 | 10–20 tick / 笔 |
| 持仓 | 20–120 分钟 |
| 频率 | 0–3 笔 / 日 / 品种 |
| 成本 | net@2 或 net@3 gate 须明确标注 |

## 2. EXP 路线图

### EXP-006A — Timeframe Selection（**ARCHIVE 2026-07-12**）

**Setup**：First Pullback（与 `first_pullback` detector 同机械定义，仅改 K 线周期）

**周期**：3m / 5m / 10m / 15m / 30m（由 1m 或现有 parquet **重采样**，禁止偷看未来）

**输出表**：

| Timeframe | n | WR | PF | Avg f10 (tick) | net@3 | Sharpe* | 备注 |
|-----------|---|----|----|----------------|-------|---------|------|
| 3m | 905 | 44.2% | 1.16 | +0.56 | **-2.44** | — | FAIL |
| 5m | 526 | 44.9% | 1.04 | +0.18 | **-2.82** | — | FAIL；pa_cta Prior |
| 10m | 263 | 49.4% | 1.14 | +0.94 | **-2.06** | — | FAIL |
| 15m | 204 | 49.0% | 1.10 | +0.97 | **-2.03** | — | FAIL；Prior 未获 Evidence |
| 30m | 95 | 51.6% | 1.44 | **+4.80** | **+1.80** | — | **PASS**（rb 2024-01~2025-06 in-sample） |

**Gate**：单 TF 不宣布「最优」除非 **n≥30 & net@cost>0** 且跨品种/OOS 待第二轮回。→ **30m rb in-sample 过 gate；跨品种/OOS 未验**。

**实现路径**：`research/run_timeframe_study.py` → `EventStudyRunner` + `bars.resample_minutes()`。**已跑 rb**。

---

### EXP-006 — Quantified First Pullback

- **状态：FROZEN（2026-07-11）** — 简化单周期 FP 不可策略化；OOS 未复现；与 OPP02 空 0 笔 / 方向相反
- 实现保留：`first_pullback` detector、`run_expectancy_study.py`（归档参考）
- rb @30m in-sample 结果见 `experiments.md` EXP-006/006A/006B

### EXP-007 — Quantified Breakout Pullback（**ARCHIVE 2026-07-12**）

- 迁移 `E1_breakout_pullback_rb` → `research/event_engine/detectors/breakout_pullback.py`
- **EXP-007A**：`python -m research.run_bp_study --symbol rb`（3/5/10/15/30m）
- **EXP-007B**：`python -m research.run_opp08_is_oos --symbol rb` — rb：Event 全 FAIL；CTA OPP08 n=8 小样本正 PnL
- 对照 pa_cta OPP08/19 族（007B 已做 OPP08）

### EXP-008 — Failed Breakout @ 目标 TF（**ARCHIVE 2026-07-12**）

- 1m S3 已 FAIL（Program 1.0）；在 5m/15m/30m 等慢周期复检（非救 1m）
- **EXP-008A**：`python -m research.run_fb_study --symbol rb`（3/5/10/15/30m）
- **rb/hc/MA 已跑**（2024-01~2025-06）：**三品种五周期全 FAIL**；相对最优 net@3：rb 30m -0.73、hc 15m -1.12、MA 10m -3.20

### EXP-009 — Trade Management Lab（**暂停**，Program 3.0）

- 数据源：`pa_cta` round_trips / `_trade_log`
- **除非**某品种 lean 扫描 PROFIT 后再做 Exit 归因；hc 已证病根在 setup 非出场
- 对比：1R / 2R / ATR trailing / Time stop 对 **同一 Entry cohort** 的 PF 分解
- **CLI**：`python -m research.run_tm_lab --symbol rb`
- **rb 已跑**（2023-05-17~2026-05-16，37 笔 cohort）：ACTUAL PF=1.26 net=+23k；机械规则均劣于 ACTUAL
- **hc / MA 已跑**（同窗口）：hc ACTUAL 劣于 STOP_EOD（−4.7k vs +22.2k）；MA ACTUAL 略劣 STOP_EOD（+40.2k vs +48.9k）

## 3. Brooks Event Library Schema（PA2）

```python
event = {
    "symbol", "datetime", "setup",
    "trend_strength", "pullback_depth", "pullback_bars", "signal_bar_quality",
    "future_10", "future_20", "future_40", "mfe", "mae",
}
```

与 `EventRecord` 对齐；结构字段进 `features` / `extra`。

## 4. 与 pa_cta 关系

| 层 | 角色 |
|----|------|
| Event Engine | **ARCHIVE** — 006–008 FAIL；代码保留，禁烧配额 |
| pa_cta | 执行、Regime 门禁（Setup AFF）、分品种菜单 |
| 禁止 | 新 Event detector；复制 hc 禁单到 rb/MA |

## 5. Program 3.0 路线图（2026-07-12 起）

| Step | EXP | 内容 | 配额 |
|------|-----|------|------|
| 0 | — | 归档 Event 006–008 | 0 |
| 1 | 009F′ | hc profile 复核（disabled_setups） | 1 |
| 2 | **020** | rb Setup AFF 日历 IS/OOS 开 vs 关 | 1 |
| 3 | **021** | lean 多品种扫描（含 al/zn/y/p/l/FG） | 1 |
| 4 | **022** | 仅 PROFIT 品种 setup 归因 + Purification | 按品种 1 次 |

**成功标准**：hc 固化复核通过；rb OOS AFF 不劣于关；≥1 新品种 PROFIT；Purify ΔPnL>0。

## 6. Program 1.0 冻结摘要

```text
1m Structural Setup + Quality + State + Sizing → 不能创造 Economic Edge
Micro Alpha (tick-native) → DEAD_FACTOR
PA2 Event 006–008 (FP/BP/FB @ 多周期) → Base Edge ≈ 0 → ARCHIVE
```

代码保留于 `research/event_engine/`，**禁止再开新 detector 或烧配额**。
