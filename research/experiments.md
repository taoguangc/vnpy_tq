# 策略实验日志（append-only）

> 格式见根目录 `program_trading.md` §7。禁止删除历史行；REVERT 实验保留记录。

| 日期 | 策略 | 品种 | 假设 ID | 改动摘要 | ΔPnL | Sharpe | RR | WR | 决策 | 备注 |
|------|------|------|---------|----------|------|--------|----|----|------|------|
| 2026-07-08 | pa_cta | rb | EXP-000 | baseline（CbC 入口验证） | — | -0.45 | 54 | 38.9% | BASE | 总PnL -43,543；direct script 与 -m 一致 |
| 2026-07-08 | pa_cta | rb | EXP-001 | 关闭 setup_risk_mult（H1：反向校准加码是病因） | -807 | -0.43 | 54 | 38.9% | REVERT | 总PnL -44,350；OPP02 多/空 PnL 一分不变(-19,765/-47,846) → **H1 证伪**。放大 OPP02 的是 ATR 高波动档 sizing_factor=1.5，非 _SETUP_RISK_MULT |
| 2026-07-08 | pa_cta | rb | EXP-002 | aff_gate_mode sizing→filter @0.25（H2：AFF filter 治 OPP02） | +31,426 | -0.86 | 3 | 0% | REVERT | 总PnL -12,117 但仅剩 3 笔全亏；靠停摆降亏非 edge 改善 |
| 2026-07-08 | pa_cta | rb | EXP-003 | AFF filter 阈值放宽 0.25→0.15 | — | -0.95 | 4 | 0% | REVERT | 总PnL -13,600；笔数仅 3→4 → alpha 分布病态偏低，**filter 是分布问题非阈值问题，H2 证伪** |
| 2026-07-08 | pa_cta | rb | EXP-004 | alwaysin_min_bars 4→6（H4：入场端加严 always_in） | +15,496 | -0.28 | 48 | 41.7% | HOLD | 总PnL -28,047，Sharpe 最优；OPP02 -67,611→-53,936 但 SHORT 胜率仍 20% → **部分有效：减少触发次数、未提升单笔质量，仍净负** |
| 2026-07-08 | pa_cta | rb | EXP-005 | 仅 OPP02 加 AFF alpha≥0.25 拒单门禁（H5） | +23,025 | -0.21 | 45 | 40.0% | HOLD | 总PnL -20,518；OPP02 -67,611→-7,065（SHORT 归零）。**未收敛到 +24,068：亏损迁移到 OPP19_OD_BREAKOUT_SHORT(-4,215→-36,555)** → setup 非独立可加，病根在 regime |
| 2026-07-08 | pa_cta | rb | EXP-006 | OPP02 + OPP19 突破 同时加 AFF alpha≥0.25 门禁（趋势延续族整体，H6） | +63,971 | +0.26 | 40 | 42.5% | KEEP（样本内） | 总PnL **+20,428（首次转正）**，PF 1.20，年化 +3.38%，回撤率 27%→14.6%。趋势延续族在低 alpha 震荡 regime 停摆、反转族照常盈利。**边界：纯样本内单品种 rb，泛化待验证** |
| 2026-07-08 | pa_cta | rb | EXP-007 | Setup AFF → 15m R²≥0.30 替代（方案 A，CHOP 关；always_in+Dual Core 保留） | -49,862 | -0.31 | 48 | 37.5% | REVERT | 总PnL **-29,434**（EXP-006 +20,428）。R² 门过松：OPP02 空 1→5 笔（-43k）、OPP19 OD_BREAKOUT_SHORT 重现（-9.8k）；AFF 拦住的低质量趋势延续未被 R² 识别。**保留 regime_gate.py 代码，profile 回 EXP-006** |
| 2026-07-08 | pa_cta | rb | EXP-008 | R²≥0.50 替代 Setup AFF（CHOP 关） | -10,104 | +0.14 | 45 | 42.2% | REVERT | 总PnL **+10,324**（较 EXP-007 改善但仍低于 EXP-006 -10.1k）。OPP02 空 3 笔/-12k、OD_BREAKOUT_SHORT 2 笔/-2.7k 仍漏网 |
| 2026-07-08 | pa_cta | rb | EXP-009 | R²≥0.40 + CHOP≤55 联合替代 Setup AFF | -20,667 | ~0 | 46 | 39.1% | REVERT | 总PnL **-239**（近零但劣于 EXP-006）。联合门未优于单 R²≥0.50 |
| 2026-07-08 | pa_cta | rb | EXP-010 | R²≥0.50 + CHOP≤61.8 联合替代 Setup AFF | -10,104 | +0.14 | 45 | 42.2% | REVERT | 与 EXP-008 **逐项相同** → CHOP≤61.8 本样本未产生额外拦截。**结论：R² 路线无法复现 EXP-006，维持 Setup AFF** |
| 2026-07-08 | pa_cta | rb | EXP-011 | 关 LATE Arm 硬拦（`late_phase_gate_enabled=False`，EXP-006 其余不变） | 0 | +0.26 | 40 | 42.5% | HOLD（无效应） | 与 EXP-006 **逐项相同**，LATE 拦截 0。**rb 3 年样本 trend_phase 未达 LATE 有效拦截条件**；profile 维持 LATE 开（ma 曾有 1 次拦截，零成本保留） |
| 2026-07-08 | pa_cta | rb | EXP-012 | Core OPP Purification：禁 OPP12/02/19 + OPP16_SHORT（保留 16_LONG/15/13/08） | +40,238 | +0.97 | 22 | 54.5% | HOLD（样本内） | 总PnL **+60,666**，PF **2.94**，MDD **-3.7%**（基线 +20,428 / 1.20 / -14.6%）。**事后剔除已知拖累 setup，同样本 in-sample**；22 RT 样本偏少。须 ma/ag/au 走查后再定是否写入 profile |
| 2026-07-08 | pa_cta | ma,ag,au | EXP-012x | 同上 Purify 跨品种验证（各 6 组计 1 轮） | — | — | — | — | **REVERT（跨品种）** | **rb 专用，不可推广**。ma +38,773→**-40,064**（禁 OPP16_SHORT 砍掉主利润源）；ag +36,099→-3,675；au +48,110→+11,959。Purify **仅 rb in-sample 成立** |
| 2026-07-08 | pa_cta | rb | EXP-013 | AFF Archetype Router v0（替代 Setup AFF；LOW_ALPHA/COMPRESSION/EXPANSION/EXHAUSTION 分档允许 OPP 族） | +12,089 | +0.49 | 29 | 48.3% | HOLD（样本内） | 总PnL **+32,518**（基线 +20,428），PF 1.47，MDD -9.7%，arch 拦截 538。**优于 EXP-006、弱于 EXP-012 Purify（+60,666）**；router+SetupAFF 结果相同。跨品种待验证 |
| 2026-07-08 | pa_cta | ma,ag,au | EXP-013x | 同上 Router v0 跨品种（各 baseline+router 计 1 轮） | — | — | — | — | **部分泛化** | ma +38,773→**+41,221**（Δ+2,448，PF 1.78，保留 OPP16_SHORT）；**ag +36,099→-33,901；au +48,110→+829**。较 EXP-012x Purify **ma 不崩**（Purify -40k），但 ag/au 仍失效。**CTA 化：Router 优于静态 Purify，v0 路由表仍须分品种调** |
| 2026-07-09 | pa_cta | rb | EXP-014 | Router v1 lane 矩阵（`aff_archetype_use_lane_matrix=True`） | 0 | +0.49 | 29 | 48.3% | **REVERT（无增量）** | 与 v0 **逐项相同**（538 arch_blk）。TREND/REVERSAL 分轨在本样本未产生差异 |
| 2026-07-09 | pa_cta | rb,hc,ma,ta | EXP-015 | Router v2 adaptive（always_in 顺势 + context-respect TREND bypass + EXPANSION OPP16多收紧） | — | — | — | — | **HOLD** | 对照组 **rb/hc/ma/ta(PTA)**。v1≡v0。rb v2 +31,046（Δ+10,617，略低于 v0 +32,518）；ma v2 +41,221（Δ+2,448）；**hc -24,026→-67,375（Router 恶化）**；**ta -93,953→-56,480（v2 减亏 +37,473，仍负）** |
| 2026-07-09 | pa_cta | hc | EXP-016 | hc 专项：Router v0 vs minimal（仅 LOW_ALPHA 拒 TREND）+ OPP 分解 | -43,349 | -0.65 | 33 | 30.3% | **Router 关（hc）** | baseline -24,026。**主因：Router 砍掉 OPP08_SHORT 3笔/+19,910**；OPP13 RANGE_FAIL_LOW 1→2 笔（-5k→-44k）。minimal≡v0（703 vs 689 blk）→ **恶化来自 COMPRESSION 等档误杀 OPP08，非 LOW_ALPHA 单层** |
| 2026-07-09 | pa_cta | hc | EXP-017 | hc 分档阈值调参 + LOW_ALPHA 归因 + v2 OPP08 context 豁免 | — | — | — | — | **HOLD** | **COMPRESSION/EXHAUSTION 阈值（0.85/1.0）对 hc 无效**（OPP08 仍 0）。**根因：OPP08 触发时 alpha≈0→LOW_ALPHA**（仅 alpha_low=0 可恢复 OPP08）。**v2 OPP08 在 STRONG_BULL/BEAR/CHANNEL 豁免 LOW_ALPHA**：hc -67,375→**-48,208**（OPP08 4笔/+19k），**仍劣 baseline -24,026**；rb v2 +32,771（略优于 v0） |
| 2026-07-09 | pa_cta | hc | EXP-018 | `SYMBOL_PROFILES["hc"]` 品种自适应 LOW 档（vol 936、仅降仓、Router 关；rb/ma HIGH/MID 不变） | +7,002 | — | 49 | — | **KEEP（hc profile）** | 基线 -24,026→**-17,024**（Δ+7,002）。**rb/ma adaptive_on≡off**（risk_mult=1.0）。**Router 关 + Setup AFF 保留** |

## 2026-07-08 OPP02 病灶排查 备注

**病灶定位**：OPP02（EMA 回调，多+空）在 rb/TQ-CbC 3 年区间净亏 -67,611，其余 10 个 setup 合计 **+24,068**。OPP02 是趋势延续型入场，对「是否真趋势」高度敏感。

**③ 数据源差异（未在本仓库核实）**：用户提供的 pa_lean 基线里 OPP02 为正贡献（约 +50,750），但那份是 **RQ 888 后复权连续**；本轮是 **TQ 分月 raw CbC（无复权）**。两者连合约构造方法都不同，OPP02 正负反转不能仅归因于「换了一段行情」。pa_lean 数字无法在此仓库验证，标记为待核实。

**AFF alpha 定义**（`aff_gate.py`，供后续复用）：`alpha_strength = env_score(ER) × compression_score`，0~1。
- `compression_score`：ATR 在近 200 根最低 20% 分位(0.6) + 布林带宽最低 20%(0.3) + NR7(0.1)。
- `env_score`：由 20 周期 Efficiency Ratio(净位移/路径波动) 分档，ER<0.20→0，ER≥0.35→1.0。
- 因两因子**相乘**，alpha 高只在「低波动 且 高效率」（收敛后顺滑推进）时出现，是**偏窄口径**的优质趋势探测器。rb 趋势多伴随高波动（ATR 不低），故 alpha 普遍偏低 → 全局 filter 会拍死整条策略（EXP-002/003 已证）。结论：AFF 适合 **sizing 降仓**，不适合 rb 的**全局硬门禁**。

**H5 结论（EXP-005 已测）**：仅门 OPP02（alpha≥0.25 拒单）后 OPP02 近乎清空，但总盈亏只到 -20,518、未收敛到 +24,068——**亏损迁移到 OPP19_OD_BREAKOUT_SHORT**。证明各 setup 通过共享持仓/状态**相互影响，非独立可加**。

**H6 结论（EXP-006 已测，KEEP-样本内）**：把 alpha≥0.25 门禁扩展到整个**趋势延续族**（OPP02 EMA 回调 + OPP19 开盘突破 breakout，不含 OD_REV 逆势）后策略**首次转正 +20,428**，PF 1.20，Sharpe +0.26。核心洞察：**病根是 regime——这段 rb/TQ-CbC 数据被 AFF 普遍判为低 alpha（震荡/假趋势），所有趋势延续型入场在此都送人头**；门禁让趋势延续族在低 alpha 时停摆、反转/区间族（OPP16/15/13）照常盈利，与市场结构自洽。

**KEEP 边界（必须复核后才可推广）**：EXP-006 为**纯样本内、单品种 rb、单区间**，alpha 阈值 0.25 沿用未重新拟合。门禁逻辑理论上可泛化（真趋势数据 alpha 升高会自动放行趋势延续族），但**未验证**；下一步须跨品种/走查确认不会在真正趋势品种上误杀利润源。已固化进 rb SYMBOL_PROFILES（`opp02_aff_gate_enabled` / `opp19_breakout_aff_gate_enabled` = True），标注样本内。

---

## 机制说明（Arm 五道通用门禁）

> 代码：`strategies/pa_cta/strategy.py`（`_arm_pending_confirm` / `_arm_fast_track`）。  
> 执行点：OPP 信号触发后、进入 `PENDING_CONFIRM` / `FAST_TRACK_ARMED` **之前**。  
> 顺序固定，任一拦截 → **不 arm**（本次机会作废）。

```
LATE → AFF → Dual Core → VSA → TF Arm
```

**Lane（Dual Core 分支）**：TREND = OPP02/08/19；REVERSAL = OPP12/13/15/16/17。

| 门禁 | 周期 | 核心量 | Arm 动作 | rb 默认 |
|------|------|--------|----------|---------|
| **LATE** | 15m | `trend_phase`, `trend_direction` | 拒单 | 开 |
| **AFF** | 15m | `alpha = env×comp` | filter 拒单 / sizing 只缩仓 | 开 sizing |
| **Dual Core** | 1m | `vwap_regime`, lane, context | 拒单 | 开 |
| **VSA** | 5m | `vol_pct`, 棒形 | 拒单 | 开 |
| **TF Arm** | arm 时 | 状态机 + TF 优先级 | 拒单/排队反向平仓 | 开 |

### 1. LATE 软禁

- **阶段**：15m `always_in` 连续 ≥4 根同侧 EMA20 + 斜率一致 → `EARLY`(<8) / `MATURE`(8–19) / `LATE`(≥20 且 ATR 收缩<0.7×入场 ATR **或** 回调计数≥3)。
- **拦截**：`trend_phase=="LATE"` 时 — OPP15 **一律拒**；OPP13/08/02/12/19 **顺趋势**拒（`WIDE_RANGE` 豁免 OPP13/08/02/19）。

### 2. AFF 全局

- **公式**（`aff_gate.py`，15m）：`alpha = env_score(ER) × compression_score`；compression = 0.6×低 ATR 分位 + 0.3×低 BB 宽 + 0.1×NR7；ER 20 周期分档 0~1.0。
- **rb**：`mode=sizing`，Arm **不拒单**；定仓乘子 alpha≥0.50→1.2，≥0.25→1.0，(0,0.25)→0.85，=0→0.7。
- **filter 模式**：`alpha < 0.25` → Arm 拒单（EXP-002/003 证伪全局 filter 于 rb）。

### 3. VWAP Dual Core

- **Regime**（1m）：日内 VWAP + 30 根斜率/穿越计数 → `CHOP` / `TREND_UP` / `TREND_DOWN`（CHOP：穿越≥4 或斜率/位置未达趋势带）。
- **TREND lane 拒**：CHOP+区间 context；逆 regime；多且 close<VWAP-deadband / 空且 close>VWAP+deadband。
- **REVERSAL lane 拒**：强趋势且 |close−VWAP|/ATR>1.2；CHOP+STRONG_BULL/BEAR context。

### 4. VSA 量价熔断

- **5m 信号棒**：`vol_pct`（近 40 根分位）+ spread/body/close_pos。
- **多拒**：无量阳线（vol≤35%）或放量弱收（vol≥70% 且 close_pos≤0.40 或 body 极短）；**空对称**。

### 5. TF Arm 跨周期

- **持仓反向新信号**：排队 TF 反向平仓，本次不 arm。
- **已有 pending**：`opp_tf.py` 优先级 D>1H>15M>5M；低周期不可覆盖高周期 arm。

### Setup 专属门禁（不在 Arm 五道内）

- `opp02_aff_gate_enabled` / `opp19_breakout_aff_gate_enabled`：信号函数内 `alpha<0.25` **硬拒**（EXP-006，仅趋势延续族；不含 OPP19 OD_REV）。
- 更上游：`always_in`、`disabled_setups`、`rb_min_atr` 等属信号/定仓，非 Arm 层。

### 五道消融摘要（2026-07-08，含成本，关 Gate vs baseline ΔPnL）

| Gate | rb | ma | hc | ta | 泛化 |
|------|-----|-----|-----|-----|------|
| Dual Core | −80,885 | −39,098 | −55,177 | **+7,587** | 3/4 正向；ta 例外 |
| VSA | −28,315 | −45,710 | −12,168 | −37,427 | 4/4 正向 |
| AFF sizing | −4,533 | +2,715* | +821 | −21,496 | 不一致（*ma PnL↑但 DD 恶化） |
| LATE / TF Arm | 0 | 0 | 0 | 0 | 本样本未触发有效拦截 |

> rb baseline（EXP-006）：+20,428，40 RT，Dual Core 拦截 69，VSA 拦截 31。

---

## Regime 架构整理（2026-07-08，rb 实证优先级）

> 目标：减少「多层 regime 重复感」，按**实测贡献**排序，明确保留/可简化项。

### 分层职责（保留，不合并为单一指标）

| 层 | 周期 | 职责 | rb 实测 |
|----|------|------|---------|
| **market_context** | 15m | Brooks 结构路由（哪些 OPP 可扫） | 核心，非纯门禁 |
| **always_in + trend_phase** | 15m | 方向偏性 + 趋势年龄 | OPP02 前提；LATE Arm **rb 未触发** |
| **Setup AFF** | 15m | OPP02/19 突破硬拒（α<0.25） | **EXP-006 主因**（+20,428） |
| **Dual Core** | 1m VWAP | Arm 硬拦（lane×regime） | **最强**（关则 −80,885） |
| **VSA** | 5m | 量价假突破熔断 | 强（关则 −28,315） |
| **AFF sizing** | 15m | 全局定仓缩放 | modest +4,533 |
| **LATE / TF Arm** | 15m / arm | Arm 软禁 / 周期冲突 | **rb 零拦截**（EXP-011 证实） |

### 15m 重叠与结论

- **context / always_in / AFF** 在「趋势 vs 震荡」上有概念重叠，但实测 **Setup AFF 不可替代**（R² 路线 EXP-007~010 均劣于 EXP-006）。
- **Dual Core** 与 15m 正交互补（1m 日内执行 vs 15m 结构），非重复。
- **LATE**：rb 上可关可留（EXP-011 无差异）；**建议 profile 保持开启**（ma 消融有 1 次拦截，零成本）。

### 当前 rb profile 定稿（EXP-006 + EXP-011 确认）

| 开关 | 状态 | 说明 |
|------|------|------|
| Setup AFF（OPP02/19 突破） | **开** | KEEP |
| 全局 AFF sizing | **开** | 保留 modest 正贡献 |
| Dual Core + VSA | **开** | 核心 Arm 门禁 |
| LATE Arm | **开** | rb 无效应；跨品种保留 |
| R² Setup 门 | **关** | EXP-007~010 REVERT |

---

## 下一阶段研究路线（2026-07-08，用户定稿）

> 评价：rb +20,428 不是失败样本，而是 **有 Alpha、可解释、可扩展** 的验证点；下一阶段 KPI 从「rb 还能赚多少」转为 **5~10 品种能否复制结构**（CTA 化）。

### 优先级 A：Exit Attribution（先于 Purification）

**OPP16 LONG（rb EXP-006，7 笔 +34,821）出场归因（已跑 `_trade_log` 对齐）：**

| exit_reason | 笔数 | 净盈亏 | 备注 |
|-------------|------|--------|------|
| PROFIT_PROTECT_1440 | 3 | +24,278 | 含最大单笔 +20,226（持 5.6h） |
| EOD_FLAT | 3 | +12,014 | 14:55 强平 |
| CHANDELIER_STOP | 1 | -1,471 | 唯一亏损 |
| MM_HALF / MM_RUNNER | **0** | — | **本样本未触发 MM 路径** |

**待验证假设（非结论）：**

- OPP16 多 **不是**「MM runner 不足」——盈利单主要死在 **14:40 PROFIT_PROTECT** 与 **EOD_FLAT**，非 MM 半仓/余仓逻辑。
- OPP16 **空**（8 笔 -8,639）拖累来自 **2 笔 STOP_LOSS**（-16,933），不是出场过早。
- Exit 优化应优先量化：**PROFIT_PROTECT / EOD 是否截断右尾**（需 MFE/MAE 或零成本对照），而非先调 runner 参数。

### Exit Attribution 实测（rb EXP-006，2026-07-08）

> MFE/MAE = 持仓期 high/low since entry × 乘数（**元/手**）；capture = 净盈亏 / (MFE×手数)；left表 = MFE 毛额 − 实际毛盈亏。

**OPP16 LONG（7 笔 +34,821）**

| exit_reason | n | 净PnL | 盈利单 capture（逐笔） |
|-------------|---|-------|------------------------|
| PROFIT_PROTECT_1440 | 3 | +24,278 | 85%（+20k 单）/ 45%（+6.6k，left +6,650）/ 亏损单 |
| EOD_FLAT | 3 | +12,014 | 75% / 37% / 34%（left +1.4~1.8k/手） |
| CHANDELIER_STOP | 1 | -1,471 | 亏损，left +6,650（曾浮盈后回吐） |

**OPP15 WEDGE（7 笔 +15,923）**

| exit_reason | n | 净PnL | 备注 |
|-------------|---|-------|------|
| EOD_FLAT | 4 | +27,351 | capture 51%~97%；楔形赢家走 EOD |
| PROFIT_PROTECT_1440 | 2 | -5,400 | 两笔均亏，MFE 仅 +20~30 元/手 → **入场错非出场早** |
| STOP_LOSS | 1 | -6,028 | MAE +120 元/手，left +5,950 |

**OPP16/15 盈利单 capture 中位数：60%（n=12）**

**已证实结论：**

1. **MM runner 不是当前瓶颈**——OPP16/15 样本 **零** MM_HALF / MM_RUNNER 出场。
2. **「太早止盈」仅部分成立**：EOD_FLAT 稳定吃掉 +1.4~8.4k 右尾（left表）；PROFIT_PROTECT 对大赢家可 capture 85%，但对 +6.6k 单仅 45%（left +6,650）。
3. **OPP15 亏损**来自 **STOP + 假楔形 PROFIT_PROTECT**，不是盈利单被截断。
4. **OPP16 空**亏损来自 **STOP_LOSS**（MAE 大），Purification 关 OPP16_SHORT 仍合理。

**待验证（需 EXP，非本报告）：** 延后/取消 PROFIT_PROTECT 或 EOD 对照 → 右尾 vs DD 权衡。

### 优先级 B：EXP-012 Core OPP Purification（rb）

**假设**：关闭拖累 setup，保留反转/区间核心，Sharpe/PF/DD 是否提升。

| 关闭 | 保留 |
|------|------|
| OPP12 / OPP16_SHORT / OPP19（全） / OPP02 | OPP16_LONG / OPP15 / OPP13 / OPP08 |

**实现注意**：`pa_cta` 尚无 `disabled_setups` 列表，需加 per-OPP 开关或 setup 前缀硬禁。**静态加总不可代替回测**（setup 非独立可加，EXP-005 已证）。

**主指标**：Sharpe、PF、最大回撤率（非总 PnL 最大化）。

### 优先级 C：EXP-013 AFF Archetype Router（架构升级）

**现状**：Setup AFF = 二元开/关（α<0.25 拒趋势延续）。

**目标**：用 `alpha_strength` × `compression_score` × `ER` 分档 **路由允许哪些 OPP**：

| AFF 状态 | 允许 OPP（草案） |
|----------|------------------|
| Compression | OPP15 / OPP16 |
| Expansion | OPP08 |
| Exhaustion | OPP13 |
| Low Alpha | 趋势延续全关 |

**边界**：须单变量消融 + 跨品种验证；不可在 rb 上拟合表格后直接推广。

### 优先级 D：多品种 CTA 化（主 KPI）

| 品种 | 总净盈亏（最新 profile，含成本） | 档 |
|------|----------------------------------|-----|
| rb | +20,428 | PROFIT |
| ma | +38,773 | PROFIT |
| ag | +36,099 | PROFIT |
| au | +48,110 | PROFIT |
| hc / ta | 负 | 结构未复制 |

**目标**：5~10 品种上 **OPP 盈亏结构**（Core 反转 vs 趋势延续）与 rb/ma 同型，而非逐品种追 PnL。
