# program_trading — 量化自治研究 Playbook

> 灵感来源：[karpathy/autoresearch](https://github.com/karpathy/autoresearch) 的「改代码 → 固定协议实验 → 单指标决策 → 保留/回滚」循环。  
> **权威规则仍以 `AGENTS.md` / `CLAUDE.md` / `docs/01_CONSTITUTION.md` 为准**；  
> 研究门禁见 `docs/06_RESEARCH_WORKFLOW.md`，回测见 `docs/04_BACKTEST_SPEC.md`。  
> 本文件只定义实验编排，不覆盖配额、宪章与编码底线。

---

## 1. 目标

在**可控、可审计**前提下，让 Agent 对策略做迭代实验：

1. 提出**单一、可检验**假设（一行话）。
2. 做**最小 diff** 改码。
3. 在**固定协议**下跑回测（含成本）。
4. 按**门禁**决定保留 / 回滚 / 待验证。
5. 追加写入 `research/experiments.md`。

**禁止** overnight 无监督连跑、网格搜索、或为凑年化擅自扩参。

---

## 2. 架构分层（类比 autoresearch）

| 层级 | autoresearch | vnpy_tq |
|------|--------------|---------|
| 固定层 | `prepare.py` | 回测引擎、`scripts/rollover_backtest_engine.py`、`scripts/tq_rollover_data.py`、`data/tq/`、`symbol_config` 引擎字段 |
| 可变层 | `train.py` | 策略逻辑与参数（见 §3 白名单） |
| 编排层 | `program.md` | **本文件** + `AGENTS.md` 回测配额 + `docs/06_RESEARCH_WORKFLOW.md` |
| 实验日志 | （终端 / commit） | `research/experiments.md` |

---

## 3. 策略包与可变范围

### 3.1 Brooks PA CTA（`strategies/pa_cta/`）

| 文件 | Agent 可否改 | 说明 |
|------|-------------|------|
| `strategy.py` | ✅ 有限 | OPP 逻辑、filter、出场；新增 OPP 须遵守 OPP 编号规则（`CLAUDE.md`） |
| `aff_gate.py`, `wedge.py`, `vsa.py`, `opp_tf.py` | ✅ | 与假设相关的子模块 |
| `symbol_config.py` | ⚠️ 仅验证通过后 | 用户确认采纳后才写入 `LEAN_PROFILES` / 品种参数 |
| `backtest.py`, `rollover_strategy.py` | ❌ | 除非排障入口/引擎对接 |
| `scripts/rollover_backtest_engine.py` | ❌ | 引擎 bug 须单独排障任务 |

**回测入口**（CbC，含换月成本）：

```powershell
Set-Location C:\projects\vnpy_tq; $env:PYTHONIOENCODING='utf-8'
.\.venv\Scripts\python.exe strategies\pa_cta\backtest.py --symbol rb
```

### 3.2 SMC Order Flow VWAP（`strategies/smc_orderflow_vwap/`）

| 文件 | Agent 可否改 | 说明 |
|------|-------------|------|
| `smc_orderflow_vwap_strategy.py` | ✅ | 信号、macro filter、出场 |
| `session_bar_generator.py` | ✅ | 会话 K 合成 |
| `run_backtest.py` | ❌ | 除非新增 `--compare-*` 对照开关 |

```powershell
Set-Location C:\projects\vnpy_tq; $env:PYTHONIOENCODING='utf-8'
.\.venv\Scripts\python.exe strategies\smc_orderflow_vwap\run_backtest.py --symbol rb
.\.venv\Scripts\python.exe strategies\smc_orderflow_vwap\run_backtest.py --symbol rb --compare-macro
```

---

## 4. 固定实验协议（每次必须相同）

除非假设**明确**要测区间/品种/成本，否则默认：

| 项 | 默认值 |
|----|--------|
| 品种 | 用户指定；未指定时 **rb** |
| 数据 | TQ CbC：`data/tq/{prefix}/` + `rollover_map.parquet` |
| 区间 | 策略 `backtest.py` / `run_backtest.py` 内建默认（勿擅自缩短凑指标） |
| 成本 | **含成本**（rate + slippage）；零成本须标注且不得与含成本结论混比 |
| 资金 | `200_000`（或 `symbol_config` 中 `risk_capital`） |
| 改动 | **一次实验只改一个变量**（一个 OPP 规则 / 一个参数 / 一个 filter） |

---

## 5. 实验循环

```
假设 → 最小 patch → 回测（用户说「跑回测」或探索任务已授权）
     → 提取指标 → 门禁判定 → git 保留或 revert → 写 experiments.md
     → 配额内则停止并等待用户确认
```

### 5.1 假设模板（写进日志首列）

```
[OPP13] rb：放宽 range_fail 的 min_atr 0.5→0.4，预期增加 2–5 笔且总 PnL 不降
```

### 5.2 单变更原则

- ❌ 同轮同时改 OPP02 filter + OPP15 止损逻辑  
- ✅ 先改 OPP13，跑 1 次；下一轮再动 OPP15  

### 5.2.1 pa_minimal CTA 冻结基线（OPP16_LONG_LAE）

对照与 ΔPnL 默认相对下列集合（代码：`MINIMAL_BASE_PROFILE` / `CTA_BASELINE_*`）：

| 项 | 值 |
|----|-----|
| 交易集 | **仅** `OPP16_5M_TWO_BAR_REV_LONG`（SHORT/PIN/1H 禁） |
| 出场 | `signal_invalid_defer_exit_enabled=True`；`signal_invalid_buffer_atr_mult=0.1` |
| 入场闸 | LAE-2a：`opp16_lae_r2_er_gate_enabled=True`（`fast_r2<0.5` 且 `slow_er<0.20`） |
| 量软仓 | `opp16_session_vol_soft_enabled=True`（sess%&lt;60 → risk×0.5；硬拒 floor 关） |
| 入场位 | EQ-A2：`opp16_ema_above_gate_enabled=True`（浅贴 EMA 有利侧 0～1ATR 拒；顺势可跳过） |
| 顺宽逆严 | `opp16_trend_asym_entry_enabled=True`（逆势须失败突破+收在 EMA 有利侧） |
| 空侧 DYN | `opp16_short_dyn_sizing_enabled=False`（代码保留；对照用 override） |
| 版本串 | `0.5.1_OPP16_LONG_LAE` |

**禁止**：未经用户确认，把多 OPP / OPP01·08·13 白名单或默认开空写入 `MINIMAL_BASE_PROFILE`。扩 OPP / 2WAY / DYN 只作 CLI override 对照，Δ 仍对上表基线。

### 5.2.2 亏损归因层级（单杠杆）

拆解亏损用于**找下一个可证伪假设**，不是逐项修到赚钱：

1. 交易集合（该不该交易该 setup）→ 2. 入场质量拒单 → 3. 风险手数 → 4. 出场/缓冲/滑点  

每轮流程：归因产出 **1** 个假设 → OFF/ON 或影子对照 → IS 选规则 / OOS 验证 → `KEEP` / `REVERT` / `HOLD`。  
禁止同轮并联修多个「根因」；症状标签（如 EARLY_FAIL）≠ 可修杠杆（见 LAE-1 REVERT）。

### 5.3 回测配额（摘自 AGENTS.md §5.1）

| 类型 | 上限 | 本 playbook |
|------|------|-------------|
| 探索/调参 | 3 次/对话 | 每次实验计 1 次；用尽**立即停止** |
| `--compare*` / `--compare-macro` | 1 次/命令 | 整命令计 1 次 |
| 排障 | 3 次 | 不得顺带调参 |

---

## 6. 指标与门禁

autoresearch 用单一 `val_bpb`；交易用**主指标 + 硬门禁**。

### 6.1 必录指标（每次实验）

- 总净盈亏、年化收益、Sharpe、最大回撤率  
- 交易次数 / round-trip 数、胜率  
- 总手续费 + 总滑点（含换月成本若有）  
- **策略特有**：pa_cta → OPP 贡献表 + 漏斗；SMC → 换月统计 + macro 层拦截  

### 6.2 主指标（相对基线 Δ）

探索阶段默认主指标：**Δ总净盈亏**（同品种、同区间、含成本）。

可选替代（须在假设中声明）：

- ΔSharpe（样本足够时，round-trip ≥ 30）  
- 单 OPP 的 ΔPnL（OPP 级诊断实验）  

### 6.3 硬门禁（任一触发 → 不得保留，除非用户特批）

| 门禁 | 条件 |
|------|------|
| 样本 | round-trip < 10 且 PnL 大幅变化 → 标「样本不足，未证实」 |
| 成本 | 毛利润 > 0 但净利润 < 0 且成本占比恶化 → 标「成本敏感」 |
| 回撤 | 最大回撤率比基线恶化 **> 5pp** |
| 笔数 | 交易次数变化 **> ±50%** 且无事先假设 → 标「分布漂移」 |
| 逻辑 | 怀疑 lookahead / 同 bar 撮合违规 → 先走 `quant-backtest-validation-tool`，不得保留 |

### 6.4 决策

| 结果 | 动作 |
|------|------|
| **KEEP** | 主指标改善且门禁通过；下轮可写入 `symbol_config`（须用户确认） |
| **REVERT** | 回滚代码；日志记原因 |
| **HOLD** | 指标混杂或样本不足；保留 diff 但不写入 profile，等用户决定 |

---

## 7. 实验日志

路径：**`research/experiments.md`**（append-only，禁止删历史行）。

每完成一次回测追加一行：

```markdown
| 日期 | 策略 | 品种 | 假设 ID | 改动摘要 | ΔPnL | Sharpe | RR | WR | 决策 | 备注 |
|------|------|------|---------|----------|------|--------|----|----|------|------|
| 2026-07-08 | pa_cta | rb | EXP-001 | baseline | — | -0.45 | 54 | 38.9% | BASE | CbC 入口验证 |
```

- **假设 ID**：`EXP-NNN` 递增；对照实验用同一 ID 后缀 `-A`/`-B`。  
- **BASE**：该品种当前 git 基线，新系列实验前先跑一行 BASE。

---

## 8. Agent 启动话术（复制即用）

```
请阅读 program_trading.md §5.2.1–5.2.2、research/RESEARCH_OPTIMIZATION_PROTOCOL.md 与 AGENTS.md §5。
策略包：strategies/pa_minimal/（对照基线 OPP16_LONG_LAE）
品种：rb,i,ma,ta（或用户指定）
任务：探索类，最多 3 轮回测。

1. 对照基线 = MINIMAL_BASE（OPP16 多 + LAE 开闸）；勿把扩 OPP 当默认。
2. 归因后提出 1 个最小假设（单变量）。
3. 改码 → 等我确认或直接跑回测（按任务类型）。
4. OFF/ON 或影子 → IS/OOS（若适用）→ KEEP/REVERT/HOLD，追加 experiments.md。
5. 输出 AGENTS.md 完整四段，然后停止。
```

---

## 9. 禁止清单

- 未经用户同意：参数扫描、多品种 `--all`、自动优化到目标年化  
- 一次 diff 改多个 OPP / 多个无关文件  
- 为 KEEP 擅自缩短回测区间、改 `--zero-cost` 冒充含成本结果  
- 修改 `data/tq/` 或 Parquet 源数据  
- 在根目录新建一次性回测脚本（用既有 `backtest.py` / `run_backtest.py`）  
- 配额用尽后继续回测  
- 将扩 OPP / 多 OPP 白名单未经确认写入 `MINIMAL_BASE_PROFILE`（对照只用 override）  
- 同轮用多条「亏损根因」并联改码（须遵守 §5.2.2：一轮一个杠杆）  

---

## 10. 与 autoresearch 的差异（必读）

| autoresearch | 本 playbook |
|--------------|-------------|
| 固定 5 分钟 GPU | 无统一时长；以**协议一致**为准 |
| 单文件 `train.py` | 多文件策略包；白名单内最小改 |
| 单一 val_bpb | 主指标 + 多维门禁 |
| Agent 可通宵 | **每 3 轮须用户确认** |

---

## 11. 相关 Skill

| 场景 | Skill |
|------|-------|
| 跑回测 | `vnpy-cta-backtest` |
| 结果可疑 | `quant-backtest-validation-tool` |
| 多品种泛化 | `vnpy-multi-symbol` |
| TQ 数据 | `vnpy-quant-python` §TQ 数据 / `tools/download_rb_monthly.py` |
