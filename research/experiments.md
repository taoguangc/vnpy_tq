# 策略实验日志（append-only）

> 格式见根目录 `program_trading.md` §7。禁止删除历史行；REVERT 实验保留记录。

| 日期 | 策略 | 品种 | 假设 ID | 改动摘要 | ΔPnL | Sharpe | RR | WR | 决策 | 备注 |
|------|------|------|---------|----------|------|--------|----|----|------|------|
| 2026-07-12 | pa_cta | multi | **EXP-029** | Phase-4 软收缩：分层 Bayes risk_mult 替代小样本硬禁 | **待跑** | — | — | — | **PENDING** | 样本不足→0.5；OOS 负期望才禁候选；`setup_shrinkage_enabled` 默认关 |
| 2026-07-12 | pa_cta | rb | **EXP-028** | Phase-3 两族出场：`exit_families.py` + TM Lab `--v3` 固定 cohort 重放 | **待跑** | — | — | — | **PENDING** | 趋势延续 OPP02/08/19 breakout vs 反转 OPP12/13/15/16/19 rev；`exit_family_v3_enabled` 默认关；禁止出场改入场集合 |
| 2026-07-12 | pa_cta | rb | **EXP-026D** | 单变量关 Fast Lane 追踪（`fast_lane_trail_enabled=False`） | **0** | 0.14 | 39 | 43.6% | **HOLD（无效应）** | 与 026B **逐项相同** +9,647；入场 arm 不变，仅持仓期改走慢车道；本样本追踪路径无边际 PnL |
| 2026-07-12 | pa_cta | rb | **EXP-026C** | 单变量关 MM（half+runner=False）vs 026B | **0** | 0.14 | 39 | 43.6% | **HOLD（无效应）** | 与 026B **逐项相同** +9,647；rb 样本 MM 路径未贡献/减损 PnL（与旧归因「零 MM 出场」一致） |
| 2026-07-12 | pa_cta | rb | **EXP-026B** | Phase-1 硬不变量：拆分 stop_price/source/pending_exit/remaining；未成交不清 stop | +3.2k* | 0.14 | 39 | 43.6% | **KEEP（执行基线）** | *相对 EXP-026 +6.5k；最终 **+9,647** / MDD -12.2% / 最长 5.6h / 换月 0。**新 TQ_EXEC_BASELINE_RB**；旧出场统计仅作参考 |
| 2026-07-12 | pa_cta | rb | **EXP-026** | 出场执行真实性修复（噪声窗风控/MM 分批/Fast Lane/pending 撤单重挂） | −13.9k* | 0.10 | 39 | 43.6% | **KEEP（执行层）** | *相对 EXP-006/TM **+20k~+23k** 旧基线；修复后 **+6,497**。**已被 026B 基线取代** |
| 2026-07-12 | pa_cta | ag,au,ma | **EXP-025** | generic_base：IS 归因选菜单 → OOS 验证 | 见备注 | — | — | — | **SKIP/REVERT** | ag/au：IS 无净亏前缀 **SKIP**；ma 禁 OPP02/13/16：IS +38k / **OOS -50k REVERT**。**无 KEEP-OOS；不写 profile** |
| 2026-07-12 | pa_cta | 20品种 | **EXP-024** | GENERIC_BASE 扫描（无 profile/AFF/禁单） | — | — | — | — | **HOLD** | **PROFIT=0**；MARGINAL=**ag/au/ma**；LOSS=12（含 rb **-90k**/hc -95k）；BLOWUP=al/zn/y/p/l；fg 未爆仓仍 LOSS。**Base OPP 单独为负** |
| 2026-07-12 | pa_cta | hc,rb,au,ma,j | **EXP-023** | 菜单日历 IS/OOS Base vs Menu（单变量 disabled_setups） | 见备注 | — | — | — | **HOLD/REVERT** | OOS：hc +7.0k HOLD(6→1)；rb 0 **REVERT** 撤 OPP12_；au +27.9k HOLD(极端)；ma +8.1k HOLD；j +9.2k HOLD(IS异向+PF劣)。**无 KEEP-OOS** |
| 2026-07-12 | event_engine | — | **Program3.0** | PA2 Event 006–008 **ARCHIVE**；转向可交易配置 | — | — | — | — | **ARCHIVE** | 006A–008A 全 FAIL；`event_engine/` 禁烧配额；见 PA2_ROADMAP §5 |
| 2026-07-12 | pa_cta | au,ma,j,rb | **EXP-022** | MARGINAL 品种 setup Purification → profile | +28k/+19k/+5k/+10k | — | — | — | **KEEP** | au/ma/j 新 profile；rb +OPP12_；ag 无净亏前缀 SKIP |
| 2026-07-12 | pa_cta | 20品种 | **EXP-021** | lean 通用 rb profile 多品种扫描 | — | — | — | — | **HOLD** | **PROFIT=0**；MARGINAL=au/ma/ag/hc/rb/j；**新品种 al/zn/y/p/l/fg 全 LOSS**（al/zn/y/p 爆仓式过频） |
| 2026-07-12 | pa_cta | rb | **EXP-020** | Setup AFF 日历 IS/OOS 开 vs 关 | IS +67k | — | 37/4 | — | **HOLD（rb 样本内）** | IS AFF开优于关；**OOS AFF开 -8.7k vs 关 -5.2k FAIL** → AFF 不得跨品种铁律 |
| 2026-07-12 | pa_cta | hc | **EXP-009F″** | profile 固化复核（disabled_setups 注入） | +32.2k | 0.54 | 26 | 42.3% | **KEEP** | 与 009F′ 同向（PF 1.73）；OPP13/15/19空 已禁 |
| 2026-07-11 | event_engine | rb,hc,MA | **EXP-008A** | Failed Breakout @ 3/5/10/15/30m 跨品种 | — | — | — | — | **HOLD** | **三品种五周期全 FAIL**；相对最优 net@3：rb 30m **-0.73**、hc 15m -1.12、MA 10m -3.20；1m 基线 -3.19 未救 |
| 2026-07-11 | event_engine | ma,hc | **EXP-007A** | Breakout Pullback @ 3/5/10/15/30m 跨品种 | — | — | — | — | **HOLD** | **三品种五周期全 FAIL**；相对最优：rb 5m -2.47 / hc 3m -2.74 / MA 10m -2.89 |
| 2026-07-11 | event_engine | rb | **EXP-007B** | OPP08 vs Event BP@5m IS/OOS 对照 | — | — | 8 | 37.5% | **HOLD** | CTA OPP08 FULL +10.9k avg **+3.91t**（**n=8**）；Event BP **-2.74t**（n=1192）**同向负**；CTA IS +7.47t n=3 — **样本过小，CTA≠Event 集合** |
| 2026-07-11 | event_engine | rb | **EXP-007A** | Breakout Pullback @ 3/5/10/15/30m（2024-01~2025-06） | — | — | 116 | 47.4% | **HOLD** | **五周期全 FAIL**；5m 最优 net@3=-2.47（pa_cta OPP08 Prior）；1m legacy E1 亦 STOP |
| 2026-07-11 | event_engine | — | **EXP-006** | 简化 First Pullback **FROZEN** | — | — | — | — | **ARCHIVE** | OOS 未复现；OPP02 空 0 笔；counterfactual 净亏；Event PASS 不可策略化 |
| 2026-07-11 | event_engine | rb | **EXP-006B** | pa_cta OPP02 SHORT vs Event SHORT IS/OOS 对照 | — | — | 0* | — | **HOLD** | *production profile **0 笔** OPP02 空（AFF 拒）；counterfactual AFF 关：12 笔 net **-14.2k** avg **-3.39t**；**与 Event IS +7.0t 不同向** → gap 在 MTF+门禁+样本定义 |
| 2026-07-11 | event_engine | rb | **EXP-006** | SHORT-only @30m 扩窗复验（2023~2025 vs IS 2024-01~2025-06） | — | — | 103 | 51.5% | **HOLD** | FULL SHORT net@3=**+0.16** 边际 PASS；**IS +7.00 PASS**；OOS-PRE -6.64 / OOS-POST -16.18 **均 FAIL** → edge 未 OOS 复现 |
| 2026-07-11 | event_engine | rb | **EXP-006** | FP Expectancy Surface @30m（trend_leg×pullback×body） | — | — | 95 | 51.6% | **HOLD** | ALL net@3=+1.80 PASS；**SHORT +7.95 PASS / LONG -6.65 FAIL**；无 2D 格 n≥30 过 gate；edge 集中在空侧+强信号体 |
| 2026-07-11 | event_engine | ma,hc | **EXP-006A** | First Pullback @ 3/5/10/15/30m 跨品种（2024-01~2025-06） | — | — | — | — | **HOLD** | **MA/hc 全 TF FAIL**；MA 最优 15m net@3=-1.74；hc 最优 10m net@3=-1.61 |
| 2026-07-11 | event_engine | — | **Program1.0** | 1m S1/S2/S3 + Q/State/Sizing 大规模筛选 **FROZEN** | — | — | — | — | **ARCHIVE** | Base Edge≈0；负×放大已证实；→ **PA2** |
| 2026-07-11 | event_engine | rb | **Phase5** | Adaptive Sizing（quality×state×allow） | — | — | — | — | **HOLD** | 2024H1：S2 ru=55.5 w_net=-4.05 vs ALL -3.23 **lift 负**；S1 active=0（全 SKIP） |
| 2026-07-11 | event_engine | rb | **Phase4** | Market State 四态 + Setup 允许矩阵 | — | — | — | — | **HOLD** | 2024H1：矩阵全 FAIL；S3 CLIMAX ALLOWED net=-4.47 **劣于** DENIED -2.82；**v0 路由待校准** |
| 2026-07-11 | event_engine | rb | **Phase3** | Quality Score v0（S1/S2/S3 加权分档 FULL/HALF/SKIP） | — | — | — | — | **HOLD** | 2024H1：S3 HALF f10=+1.13 net@3=-1.87 vs ALL -3.19；S1 全 SKIP；**v0 权重未校准** |
| 2026-07-11 | event_engine | rb | **Phase2** | Setup Library：S1 Compression + S2 First Pullback 迁入 | — | — | 37/739* | — | **HOLD** | *2024H1；S1 f10=+0.84 net@3=-2.16 n=37；S2 f10=-0.23 net@3=-3.23 n=739；均未过 gate |
| 2026-07-11 | event_engine | rb | **Phase1** | 统一 Event Research Framework + S3 Failed Breakout 迁移 | — | — | 643* | — | **HOLD** | *2024H1 窗口；与 legacy E1 f5/f10/f20/MFE/MAE max_diff=0；新增 f40/f80 + AFF features；`research/event_engine/` |
| 2026-07-11 | tick_native | rb | P2 | delta_div × AFF compression 条件 Alpha（Last Chance） | — | — | 19 | WR 74% | **REJECTED** | COMP≥0.6 h=10 f10=+1.84 net@2=**-0.16** n=19；**无 n≥30 & net@2>0** → DEAD_FACTOR |
| 2026-07-11 | tick_native | rb | P3 | delta_div 收盘软禁 × pa_cta 追空 attribution（post-hoc） | 0 | 0.32 | 37 | — | **INOPERATIVE** | overlap=0；追空+收盘窗 cohort=0；S2 收盘空4笔零命中。**Architecture Mismatch**，非 Bad Code |
| 2026-07-11 | tick_native | rb,ma,ta | E4/P1 | full horizon expectancy curve（h=5..120） | — | — | — | — | **REJECTED** | 全品种 net@2 全负；rb 峰值 h=10 +1.45t/-0.55；ma h≥20 转负；**拉长持有期不救 edge** |
| 2026-07-11 | tick_native | ta | E3-30s | TA 收盘段 30s 执行对照（pricetick=2） | — | — | 1409 | WR 51% | **STOP** | market_close f10=+0.68 net@2=**-1.32**；confirm/stop/ask 更差 |
| 2026-07-11 | tick_native | ma,ta | Ladder | MA/TA tick-native 四周期对照 | — | — | — | — | **STOP** | MA 全样本60s +0.51/-1.49；TA 120s +1.30/-0.70；**三品种无 net@2>0** |
| 2026-07-10 | tick_native | rb | E3-60s | 60s 收盘段 delta_div_short 执行对照 | — | — | 240 | WR 55% | **STOP** | market_close f10=+1.45 net@2=**-0.55**（较30s -1.03 改善）；ask/confirm/stop 更差；**仍无 net@2>0** |
| 2026-07-10 | tick_native | rb | Ladder | 15/30/60/120s delta_div 四周期对照 | — | — | — | — | **HOLD** | 全样本 f10 15s 最优(+0.43)；**收盘段 60s 最优** f10=+1.45 net@2=-0.55 n=240；无 segment net@2>0 |
| 2026-07-10 | tick_native | rb | E3 | 收盘段 delta_div_short 执行对照（market/stop/confirm） | — | — | 344 | WR 50% | **STOP** | **market_close 最优** f10=+0.97t net=-2.03t（@3t）；ask/stop/confirm 更差；@2t net=-1.03t 仍负。**执行优化无法过成本线** |
| 2026-07-10 | tick_native | rb | E1 | Tick 原生 30s（delta 背离 / spread 宽 / exhaustion） | — | — | 48805 | — | **STOP** | 最优 delta_div_short f10=+0.40t net=-2.60t；时段最佳 14:30–15:00 f10=+0.97t net=-2.03t；**无 type 过成本 gate**。raw edge 强于 1m PA，仍不足策略化 |
| 2026-07-10 | tick_micro | rb | E2 | 时段分层（09/10:30/13:30/14:30/夜盘 × 微观子集） | — | — | 9286 | — | **STOP** | **无 segment net>0**（n≥30）；最优 failed_breakout_up\|high_abs **09:00–10:30** f10=+0.57t net=-2.42t n=40；13:xx 单段 f10 高但 n<30 未过 gate |
| 2026-07-10 | tick_micro | rb | E1 | 形态+Delta/1档盘口 Event Study | — | — | 9286 | — | **HOLD** | 假突破上 f10=-0.08t；high_absorption 子集 f10=+0.22t 仍 net=-2.78t；顺势突破亦负。待 MA tick 复跑 |
| 2026-07-10 | brooks_bp | rb | E1 | Breakout Pullback Continuation（顺势） | — | — | 1111 | WR 39% | **STOP** | ALL f10=**-0.43t** net=-3.43t；MFE/MAE=0.91；Long -0.27t / Short -0.57t；N 足但 edge 负。**RB 1m 顺势 BP 亦无 Alpha** |
| 2026-07-10 | brooks_h2l2 | rb | E1 | H2/L2 Second Entry Event Study | — | — | 92 | WR 29% | **STOP** | ALL f10=-1.13t；N<300 |
| 2026-07-10 | brooks_fade | rb | **归档** | E1+E2 Failed Breakout Fade 全线 STOP | — | — | — | — | **STOP** | 两层独立否定；Range≈Trend；不调参 |
| 2026-07-10 | brooks_fade | rb | E2 | Context Filter（ADX+EMA20/20 slope，RANGE 双条件） | — | — | 1388 | Range WR 48% | **STOP** | Range n=54 f10=-0.19t；Trend f10=-0.14t |
| 2026-07-10 | brooks_fade | rb | E1 | Failed Breakout Event Study（纯统计，无交易） | — | — | 1388 | — | **STOP** | avg f10 -0.09t；MFE<MAE |
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

## 2026-07-12 EXP-026 — 出场执行真实性修复（rb production profile）

**动机**：入场/出场架构审计发现 P0 执行语义与代码意图不一致；须先修执行再谈 alpha 优化。

**代码范围**（`strategies/pa_cta/strategy.py` + `rollover_strategy.py`）：

1. **噪声窗仍执行持仓风控**（9:00–9:05 / 13:00–13:05 / 21:00–21:05 有仓时跑止损+MM+TF 反向）
2. **同 bar 止损优先**：`_manage_stop_loss` 触发后立即 return，不继续 MM
3. **MM 真实分批**：半仓 `pos//2`、Runner 按 `_calc_mm_runner_exit_volumes()` 手数平仓
4. **Fast Lane 持久化**：`active_entry_lane` 不受 `_reset_machine()` 清除
5. **stop reason 仅在止损线实际移动时更新**（`_tighten_stop_long/short`）
6. **pending 撤单重挂**：限价平仓未成交时 `cancel_all` 后重挂；EOD 前清 `_exit_order_pending`；换月平旧后清 pending

**回测**（rb，TQ CbC，2023-05-17→2026-05-16，含成本，production profile）：

| 阶段 | 总净盈亏 | 年化 | Sharpe | RT | WR | 最长持有 | 换月持仓 |
|------|----------|------|--------|-----|-----|----------|----------|
| 旧基线 EXP-006 / TM ACTUAL | ~+20k~+23k | ~3% | ~0.26 | ~37–40 | ~43% | 日内 | — |
| 修复初版（pending 未修） | **+156,652** | 25.9% | 0.66 | 33 | 45% | **2070h** | 3 |
| **EXP-026 最终** | **+6,497** | 1.1% | 0.10 | 39 | 43.6% | **5.6h** | 0 |

**发现**：

1. 初版 +15 万为 **伪收益**：`_exit_order_pending` 在 vnpy 下一根 K 才撮合的限价单上卡死；EOD `cancel_all` 后无法再平 → 隔夜至换月（942h / 2070h 持仓）。
2. pending 修复后持仓恢复日内、换月 0 → **执行层修复通过**。
3. 相对旧 +20k **PnL 下降 ~14k**：主因真实 MM 分批 + Fast Lane 追踪生效；旧数字建立在「MM 名义半仓实为全平 + 追踪失效 + EOD 偶发失效」之上，**不可直接比策略 alpha**。
4. OPP 结构变化：OPP02 多 1 笔由 +58k→**-7k**（旧版长持隔夜单消失）；OPP16 空 7→8 笔、净 +77k→**-8.6k**；OPP13 由 -12k→**+9.7k**。

**决策**：**KEEP（执行层）** — 代码语义与 Brooks PA 设计一致；随后由 **EXP-026B** 固化硬不变量并重立 `TQ_EXEC_BASELINE_RB`。

## 2026-07-12 EXP-026B — Phase-1 硬不变量状态拆分

**范围**：只修执行语义，不寻找 alpha。

**四个硬不变量**：

1. 持仓时任何时段都必须检查止损（含噪声窗）
2. 同 bar 止损与目标同时触发，只允许止损单（止损触发后 return，挡 MM）
3. 半仓必须真实按指定 `volume` 平仓
4. 平仓单未成交前，**不清空** `stop_price`/`stop_source`，不重复下全平单（STOP/EOD/TF 可撤单升级）

**状态拆分**：

| 字段 | 含义 |
|------|------|
| `stop_price` | 当前逻辑止损价（原 `signal_stop_loss`） |
| `stop_source` | 止损来源（INITIAL/BREAKEVEN/CHANDELIER/…）；止损成交归因用此 |
| `pending_exit_order` | 未成交平仓单 `{kind, reason, volume, price, is_full, side}` |
| `remaining_position` | 预期剩余仓位（签手数）；成交后与 `pos` 同步 |

**回测**（rb production，含成本，2023-05-17→2026-05-16）：

| 版本 | 总净盈亏 | Sharpe | RT | 最长持有 | 换月 |
|------|----------|--------|-----|----------|------|
| 旧 EXP-006 参考 | ~+20k | ~0.26 | ~40 | 日内 | — |
| EXP-026 | +6,497 | 0.10 | 39 | 5.6h | 0 |
| **EXP-026B（现行基线）** | **+9,647** | **0.14** | **39** | **5.6h** | **0** |

**决策**：**KEEP** — `TQ_EXEC_BASELINE_RB = {rt:39, wr:43.6, pnl:9647, sharpe:0.14, pf:1.10}`。此前出场统计仅作旧版本参考。

**下一步（默认 1 项）**：在 026B 基线上做出场单变量消融（关 MM / 关 Fast Lane），仍不扩参找 alpha；或先 hc 同语义复跑。

**等待确认**：选 (A) EXP-026C MM 关消融，或 (B) hc 执行基线复跑。→ **已执行 A**。

## 2026-07-12 EXP-026C — MM 单变量消融（rb）

**假设**：在 026B 硬不变量基线上，关闭 MM 半仓/Runner 是否改变 PnL（边际贡献归因）。

**改动**：`mm_half_close_enabled=False` + `mm_runner_enabled=False`（仅 overrides，不改 profile）。

| 版本 | 总净盈亏 | Sharpe | RT | WR | MDD% | 最长持有 |
|------|----------|--------|-----|-----|------|----------|
| 026B（MM 开） | **+9,647** | 0.14 | 39 | 43.6% | -12.24% | 5.6h |
| **026C（MM 关）** | **+9,647** | 0.14 | 39 | 43.6% | -12.24% | 5.6h |

**发现**：ΔPnL=**0**，OPP 表与漏斗亦相同 → 本样本 **MM 路径未触发有效减仓**（或触发后对最终净值无净影响）。与历史「OPP16/15 零 MM 出场」归因一致。

**决策**：**HOLD（无效应）** — 保留 MM 代码与默认开（语义正确、零成本保留）；**不以关 MM 作为增益手段**。不改 `TQ_EXEC_BASELINE_RB`。

**下一步（默认 1 项）**：EXP-026D 关 Fast Lane 追踪（或强制全部 PENDING_CONFIRM）单变量消融；或 hc 执行基线复跑。

**等待确认**：选 (D) Fast Lane 关，或 (B) hc 复跑。→ **已执行 D**。

## 2026-07-12 EXP-026D — Fast Lane 追踪单变量消融（rb）

**假设**：关持仓期 Fast Lane 追踪（改走慢车道 PP/Chandelier），对 026B 基线 PnL 是否有边际影响。

**改动**：新增参数 `fast_lane_trail_enabled`（默认 True）；本轮 overrides=`False`。**入场 FAST_TRACK arm 不变**，只改 `_is_fast_lane_setup()` 门控。

| 版本 | 总净盈亏 | Sharpe | RT | WR | MDD% |
|------|----------|--------|-----|-----|------|
| 026B（Fast Lane 追踪开） | **+9,647** | 0.14 | 39 | 43.6% | -12.24% |
| **026D（追踪关）** | **+9,647** | 0.14 | 39 | 43.6% | -12.24% |

**发现**：ΔPnL=**0**，OPP/漏斗相同 → 本样本 Fast Lane 追踪与慢车道路径在净值上**不可区分**（或追踪几乎未改变止损线至成交）。与 026C（MM）同属「管理层开关无效应」。

**决策**：**HOLD（无效应）** — 保留 `fast_lane_trail_enabled=True` 默认；不改基线。026C+026D 合计表明：rb 上复杂出场层的可观测边际贡献集中在 **止损线移动以外的路径**（BE/PP/EOD/初始止损），MM 与 Fast Trail 对本窗口无增量。

**下一步（默认 1 项）**：hc 执行基线复跑（验证硬不变量跨品种）；或单变量关 PROFIT_PROTECT / EOD 做管理层归因（注意与旧 EXP-009C/D 语义不同，须以 026B 为对照）。

**等待确认**：选 (B) hc 复跑，或 (E) 关 PROFIT_PROTECT，或 (F) 关 EOD。

---

## 2026-07-12 EXP-028 — Phase-3 两族出场（固定 cohort，不改入场）

**动机**：禁止「每品种 × 每 setup 一套出场」；先收敛为 **两族**，在**固定入场 cohort** 上分解 Entry vs Management，出场变化**不得**改变入场集合（026B 硬约束）。

### 两族定义（`strategies/pa_cta/exit_families.py`）

| 族 | Setup | 出场要点 |
|----|-------|----------|
| **CONTINUATION** 趋势延续 | OPP02 / OPP08 / OPP19 **OD_BREAKOUT** | 结构初始止损；保本 ≥2.5×ATR（不宜过早）；1R 平半 + runner；runner Chandelier；禁 PP@14:40；保留右尾 |
| **REVERSAL** 反转/区间 | OPP12 / OPP13 / OPP15 / OPP16 / OPP19 **OD_REV** | 结构失效止损；1R 平约 2/3；无 runner；90min 时间止损；PP@14:40；禁长周期 Chandelier 拖尾 |

OPP19 按子类型拆分（breakout→延续，rev→反转），**不按** `OPP19_` 前缀一刀切。

### 对照方法（禁止出场反改入场）

1. **首选**：`python -m research.run_tm_lab --symbol rb --v3` — 冻结 026B `_trade_log` cohort，重放 `FAMILY_ASSIGNED` / `FAMILY_CONTINUATION` / `FAMILY_REVERSAL` vs `ACTUAL`。
2. **次选**：`exit_family_v3_enabled=True` 单变量 live 确认（仅出场路由变，入场逻辑/门禁不动）。
3. **禁止**：改 filter、改 arm 条件、改 disabled_setups 同时测出场。

### 实现状态

| 组件 | 路径 | 状态 |
|------|------|------|
| 族路由表 | `exit_families.py` | ✅ |
| Cohort 重放 | `trade_management_lab.py` + `run_tm_lab --v3` | ✅ 待跑 |
| Live 开关 | `exit_family_v3_enabled=False`（默认关） | ✅ |

**下一步**：跑 rb `--v3` 一轮（计 1 次探索配额）；若 `FAMILY_ASSIGNED` 劣于 ACTUAL 则 HOLD，优于则再开 live 确认。

**等待确认**：是否授权跑 rb EXP-028 cohort 对照。

---

## 2026-07-12 EXP-029 — Phase-4 软收缩（替代硬禁菜单）

**动机**：EXP-022/023 基于 3–10 笔 setup 净亏直接写 `disabled_setups`，OOS 常 REVERT 或 n 坍塌（hc 6→1）。**「未知」≠「应禁」**。

### 决策层级（禁止跳级）

| 层级 | 条件 | 动作 |
|------|------|------|
| 1 样本不足 | n < 10（可调） | **risk_mult = 0.5**，仍允许入场 |
| 2 收缩估计 | IS 分层 Bayes → class → global | mult ∈ [0.5, 1.0] 按 shrunk R 渐升 |
| 3 跨类/跨品种有效 | 同类 OPP 前缀 pooled n 足够 | 向 1.0 抬升 |
| 4 硬禁候选 | **仅 OOS** avg R ≤ -0.2 且 n ≥ 15 | 标记 `DISABLE_CANDIDATE`；默认**仍不禁** |
| 5 硬禁执行 | 用户确认 + `setup_shrinkage_hard_disable=True` | mult=0 才走 `_setup_disabled` |

### 实现

| 组件 | 路径 |
|------|------|
| 收缩核心 | `strategies/pa_cta/setup_shrinkage.py` |
| 估计 CLI | `python -m research.run_setup_shrinkage --symbols rb,hc,au,ma` |
| 策略开关 | `setup_shrinkage_enabled=False`（默认关） |
| profile 注入 | `setup_shrinkage_overrides="OPP13=0.50,OPP15=0.50"` |

**与硬禁关系**：Phase-4 启用后应**清空或保留注释** profile 内小样本 `disabled_setups`；rb888 经多轮回测证实的硬禁可保留并标注 `# rb888 特定`。

**对照**：
```powershell
python -m research.run_setup_shrinkage --symbol hc --compare-menu
```

**下一步**：跑 multi-symbol 估计表 → 对比 hc 硬禁菜单 vs 软收缩（1 轮探索配额）。

**等待确认**：是否授权跑 EXP-029 估计 + hc 对照。

## 2026-07-08 OPP02 病灶排查 备注

**病灶定位**：OPP02（EMA 回调，多+空）在 rb/TQ-CbC 3 年区间净亏 -67,611，其余 10 个 setup 合计 **+24,068**。OPP02 是趋势延续型入场，对「是否真趋势」高度敏感。

**③ 数据源差异（未在本仓库核实）**：用户提供的 pa_lean 基线里 OPP02 为正贡献（约 +50,750），但那份是 **外部后复权连续合约**；本轮是 **TQ 分月 raw CbC（无复权）**。两者连合约构造方法都不同，OPP02 正负反转不能仅归因于「换了一段行情」。pa_lean 数字无法在此仓库验证，标记为待核实。

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

---

## 2026-07-11 delta_div_short 归档（DEAD_FACTOR）

> 脚本：`experiments/E1_tick_native_micro.py`（E1/Ladder）、`E3_tick_execution.py`、`E4_expectancy_curve.py`、`P3_regime_filter_attribution.py`、`P2_conditional_alpha.py`  
> 样本：2025-01 ~ 2026-06（P3 用 pa_cta 全区间 2023-05 ~ 2026-05）；成本 gate：**net@2 > 0** 且 **n ≥ 30**（@3 tick 主报告，@2 tick gate）

### 研究树（终态）

```text
delta_div_short
├── Entry Alpha (E1/Ladder)     REJECTED   — 三品种无 net@2>0
├── Execution (E3)                REJECTED   — Execution Loss << Cost Drag
├── Horizon Extension (E4/P1)   REJECTED   — 全 horizon net@2 均负
├── PA Filter (P3)                INOPERATIVE — overlap=0，Architecture Mismatch
├── Conditional Alpha (P2)        REJECTED   — COMP≥0.6 最优仍 net@2<0 或 n<30
└── STATUS                        DEAD_FACTOR → Archive（停止消耗配额）
```

### 已证实（跨实验一致）

1. **Weak Statistical Alpha，Non-tradable Economic Edge**：WR ~51%、f10 可为正，但量级 **0.7~1.5 tick**，低于 **2 tick** 往返成本。
2. **Execution 不能救场**（E3）：TA market_close 最优；confirm 降 fill；stop/ask 更差。`net@2 ≈ f10 - 2`。
3. **拉长持有期不能放大 edge**（E4）：rb 峰值 h=10；ma h≥20 系统性反向；TA h=120→0。
4. **PA Filter 从未被调用**（P3）：非「filter 无效」，是 **condition overlap=0**（tick 30/60s × 收盘 micro vs 5m PA × 14:45 关窗）。TREND 追空在 14:30–14:44 **0 笔**。
5. **Compression 条件不足以复活**（P2）：rb COMP≥0.6 改善 f10（1.46→1.84）但 **n=19**，h=10 net@2=**-0.16**；未过 Last Chance gate。

### 三品种 Ladder 收盘段对照（delta_div_short，最优 bar）

| 品种 | bar | n | f10 (tick) | net@2 |
|------|-----|---|------------|-------|
| rb | 60s | 240 | +1.45 | -0.55 |
| ma | 60s | 310 | +0.27 | -1.73 |
| ta | 30s | 463* | +0.79 | -1.21 |

\*TA E4 用 pricetick=2 重检测；E3 tick=1 时 n=1409，结论同为 Cost/Edge>2。

### P3 结论表述（精确）

| 标签 | 含义 |
|------|------|
| **INOPERATIVE** | Filter 逻辑未错，但 **零 temporal overlap** → 等价 dead code |
| **Architecture Mismatch** | Micro Reversal Process（tick-native）≠ 5m Structural Trend（pa_cta Core OPP） |
| **Event Day ≠ Trade Day** | 微观事件日与 PA 入场日/时段常错开 |

### Kill Rule（已执行）

P2 为 Last Chance；失败后 **不再**对 delta_div_short 做：execution 优化、horizon 扩展、单品种扩参、pa_cta filter 入策略（除非先改架构：tick arm → 5m execute，属 **New Strategy Research**）。

### 代码修复（保留，供其他品种 tick 加载）

- `scripts/tq_tick_loader.py`：CZCE tick 小写文件名 + manifest/3→4 位 yymm 映射。
- `experiments/E3_tick_execution.py`：`--symbol` + 自动 pricetick。

### 产出路径

| 文件 | 内容 |
|------|------|
| `experiments/output/tick_native_ladder_summary_{rb,ma,ta}.csv` | Ladder |
| `experiments/output/expectancy_curve_summary.csv` | E4 全 horizon |
| `experiments/output/e3_execution_summary_ta_30s.csv` | E3 TA |
| `experiments/output/p3_filter_scopes_rb.csv` | P3 overlap |
| `experiments/output/p2_conditional_alpha_rb.csv` | P2 分层 |

---

## 2026-07-11 Event Research Framework — Phase 1

**目标**：Alpha Research → System Research 基础设施；统一 `EventRecord` + `EventStudyRunner.run(setup)`。

**包结构**：

```text
research/event_engine/
├── schema.py      EventRecord, f5/f10/f20/f40/f80, MFE/MAE
├── bars.py        TQ CbC 1m 加载
├── forwards.py    统一 forward 标注
├── features.py    15m AFF snapshot（可选）
├── summary.py     gate: n≥30 & net@cost h=10>0
├── runner.py      EventStudyRunner
└── detectors/
    └── failed_breakout.py   S3（首 migrator）
```

**CLI**：

```powershell
python -m research.run_event_study failed_breakout --symbol rb [--round2] [--legacy-output]
```

**输出**：`research/output/events_{setup}_{symbol}.csv`、`summary_{setup}_{symbol}.csv`；`--legacy-output` 同步写 `experiments/output/failed_breakout_events.csv`。

**已证实**：2024-01~05 rb 643 事件，legacy E1 同窗口 **direction/f5/f10/f20/mfe/mae max_diff=0**。

**待验证**：全样本 TQ CbC 跑通耗时（~5min+，Python 逐 bar 检测）；~~Phase 2 迁入 S1/S2~~ **Phase 2 已完成（见下）**。

---

## 2026-07-11 Event Research — Phase 2 Setup Library

**目标**：S1/S2/S3 三 setup 全部接入 `EventStudyRunner`；冻结 tick/delta/footprint。

| Setup | detector | 机械定义（摘要） | 2024H1 rb |
|-------|----------|------------------|------------|
| **S1** | `compression_breakout` | 前根 ATR 低分位 + 前根窄区间 → 当前 K 实体突破 10-bar 高低 | n=37, f10=**+0.84t**, net@3=**-2.16**, MFE>MAE |
| **S2** | `first_pullback` | BrooksScalp v0.1 FSM：趋势腿→EMA 回调→信号 K | n=739, f10=-0.23t, net@3=-3.23 |
| **S3** | `failed_breakout` | Phase 1 已迁移 | n=643, f10=-0.19t, net@3=-3.19 |

**CLI**：

```powershell
python -m research.run_event_study compression_breakout --symbol rb
python -m research.run_event_study first_pullback --symbol rb
python -m research.run_event_study failed_breakout --symbol rb   # 或 S1/S2/S3 别名
```

**已证实**：三 setup 均可产出统一 CSV；S1/S2/S3 在 2024H1 rb **均未过** economic gate（n≥30 & net@cost h=10>0）。

**待验证假设**：S1 全样本 f10/MFE 分布；S1 在 Phase 4 **COMPRESSION** 态路由后是否改善（当前仅 raw event study）。

---

## 2026-07-11 Event Research — Phase 3 Quality Score Engine

**目标**：`score = Σ w·feature` → **FULL / HALF / SKIP** 分档（0.8 / 0.6 阈值），检验高分 cohort 是否 lift net@h10。

**模块**：

```text
research/event_engine/quality_score.py   # S1/S2/S3 权重 profile + score_events
research/event_engine/quality_report.py  # 分层汇总 + lift 报告
research/run_quality_study.py            # CLI（自动 --quality）
```

**v0 权重（未拟合，路线图占位）**：

| Setup | 主成分 |
|-------|--------|
| S1 | compression 0.35 + narrow_range 0.25 + er 0.20 + body/session |
| S2 | trend_leg 0.35 + env 0.25 + shallow_pullback 0.20 + alpha/body |
| S3 | climax 0.35 + wick 0.25 + compression/breakout/session |

**CLI**：

```powershell
python -m research.run_quality_study compression_breakout --symbol rb
python -m research.run_event_study failed_breakout --symbol rb --quality
```

**输出**：`events_scored_{setup}_{symbol}.csv`（含 `quality_score`, `size_bucket`, `q_*` 分量）、`quality_{setup}_{symbol}.csv`

**2024H1 rb 验证（已证实）**：

| Setup | ALL net@3 | Q_HALF/FULL | 结论 |
|-------|-----------|-------------|------|
| S1 | -2.16 (n=37) | 全 SKIP（score<0.6） | v0 阈值过高 / 样本少 |
| S2 | -3.23 | FULL **更差**（lift 负） | v0 权重与 edge **反向** |
| S3 | -3.19 | HALF+FULL n=97, net **-1.95** | 有 lift，仍 **未过 gate** |

**下一步（Phase 4）**：4 态 market state（TREND/RANGE/COMPRESSION/CLIMAX）× setup 允许矩阵；Quality Score 须在 state 内分档再评估（禁止全样本拟合权重）。

---

## 2026-07-11 Event Research — Phase 4 Market State

**目标**：15m AFF 派生四态 + Setup 允许矩阵（S1→COMPRESSION, S2→TREND, S3→CLIMAX）。

**分类 v0（互斥优先级）**：

1. `compression_score >= 0.6` → **COMPRESSION**
2. `climax_atr >= 2.0`（15m |close-EMA20|/ATR）→ **CLIMAX**
3. `env_score >= 0.75` 或 `er >= 0.35` → **TREND**
4. 其余 → **RANGE**

**模块**：`market_state.py`、`state_report.py`、`run_state_study.py`

**CLI**：

```powershell
python -m research.run_state_study compression_breakout --symbol rb
python -m research.run_state_study S3 --symbol rb --quality   # ALLOWED cohort 上 Quality
```

**输出**：`state_{setup}_{symbol}.csv`、`events_state_{setup}_{symbol}.csv`

**2024H1 rb（已证实，矩阵修复后）**：

| Setup | ALLOWED n | ALLOWED net@3 | DENIED net@3 | Matrix |
|-------|-----------|---------------|--------------|--------|
| S1 | 7 (COMPRESSION) | -2.57 | **-2.07** | FAIL |
| S2 | 130 (TREND) | -3.66 | -3.13 | FAIL |
| S3 | 141 (CLIMAX) | **-4.47** | -2.82 | FAIL |

**结论**：v0 状态路由在本窗口 **未 lift**（S3 ALLOWED 劣于 DENIED）；分类阈值与 pa_cta Router 对齐前 **不得写入策略**。

**下一步（Phase 5）**：Adaptive Sizing（`risk = base × setup_quality × market_state`）— 须在 state 内校准后再 AB。

---

## 2026-07-11 Event Research — Phase 5 Adaptive Sizing

**公式（研究层 v0）**：

```text
size_mult = 0                         if setup_allowed=0
          = bucket_mult × state_mult  otherwise
bucket: FULL=1.0, HALF=0.5, SKIP=0
state:  TREND/COMPRESSION/CLIMAX=1.0, RANGE=0.75
weighted_net_h10 = Σ(f10 × size_mult) / Σ(size_mult) - cost
```

**模块**：`adaptive_sizing.py`、`run_sizing_study.py`（自动启用 State + Quality）

**CLI**：

```powershell
python -m research.run_sizing_study first_pullback --symbol rb
```

**输出**：`sizing_{setup}_{symbol}.csv`、`events_sized_{setup}_{symbol}.csv`

**2024H1 rb（已证实）**：

| Setup | ALL net@3 | SIZED w_net@3 | risk_units | lift |
|-------|-----------|---------------|------------|------|
| S1 | -2.16 | n/a (active=0) | 0 | — |
| S2 | -3.23 | **-4.05** | 55.5 | **负** |
| S3 | -3.19 | **-3.59** | 17.0 | **负** |

**结论**：v0 叠加 Quality+State 过滤后 **未改善** economic gate；S1 在 COMPRESSION+Quality 下 **无可交易事件**（全 SKIP）。

**System Research 栈（Phase 1–5）**：框架完备；**S1/S2/S3 1m event 层无 economic edge** → 见下 **Program 1.0 归档** 与 **PA2**。

---

## 2026-07-11 Research Program 1.0 — **COMPLETED / FROZEN**

> **正式发布**：1m 结构化 Alpha 大规模筛选完成；错误方向已排除。Framework 代码保留，**禁止**再对 S1/S2/S3 做 Quality/State/Sizing 调参。

### 冻结结论（已证实，跨 Phase 1–5 + tick-native 一致）

```text
Base Edge ≈ 0（1m S1/S2/S3，rb 2024H1 及更宽样本）
→ Quality / State / Sizing 只能排序或放大已有信号
→ 负 × 过滤/加权 ≈ 更负或不变（S2 ALL -3.23 → SIZED -4.05）
```

| 层级 | 能否创造 Alpha | 本仓库证据 |
|------|----------------|------------|
| Base Setup（1m） | **否** | S1/S2/S3 gate 全 FAIL |
| Quality Score | **否**（仅排序） | S3 HALF lift 仍 net<0 |
| Market State | **否**（仅过滤） | S3 CLIMAX ALLOWED **劣于** DENIED |
| Adaptive Sizing | **否**（仅放大） | S2/S3 weighted net **更负** |
| Tick 微观（delta/footprint） | **否** | DEAD_FACTOR 2026-07-11 |

**正确堆叠顺序（不可反）**：`Base Alpha → State → Quality → Sizing`

### 归档方向（STOP，勿再消耗配额）

- 1m Setup Library 优化 / 扩参
- tick-native、delta_div、footprint、1m quantified scalping
- ML 救负 Alpha、预测未来数分钟方向
- Quality/State/Sizing v0 调参

### 保留资产

- `research/event_engine/` — 新 Brooks **15m/5m** Event 研究入口
- `pa_cta` EXP-006 rb profile — **唯一 in-sample 转正** CTA 路径
- tick parquet — 冻结，不删

---

## PA2 — Quantified Brooks CTA（Program 2.0）

> 细则：`research/PA2_ROADMAP.md`

**KPI（未来 3 个月）**：**不再发现新 1m/微观因子**；集中 EXP-006 系列。

**时间周期**：`15m` 为 **Prior**（pa_cta 架构 + 成本结构），**非 Evidence**。须 **EXP-006A** 数据驱动选 TF。

**交易画像目标（待验证）**：avg 10–20 tick / 笔；持仓 20–120 min；0–3 笔/日。

| EXP | 主题 | 优先级 |
|-----|------|--------|
| **006A** | Timeframe Selection（FP @ 3/5/10/15/30m） | ⭐⭐⭐⭐⭐ 先做 |
| **006** | Quantified First Pullback | ⭐⭐⭐⭐⭐ |
| **007** | Quantified Breakout Pullback | ⭐⭐⭐⭐⭐ |
| **008** | Failed Breakout（15m 层复检） | ⭐⭐⭐⭐ |
| **009** | Trade Management Lab（1R/2R/ATR trail/Time） | ⭐⭐⭐⭐⭐ |

**Brooks Event Library（PA2 Phase 1）**：FP、BP、Wedge Reversal、Failed Breakout、Final Flag — 统一 `EventRecord` schema（已有 f5–f80 + MFE/MAE + 结构特征）。

**Phase 2 目标**：Expectancy Surface（Trend Strength × Pullback Depth × …），非「有没有信号」。

**Phase 3 目标**：Trade Management Attribution — Entry PF vs Management PF 分离（pa_cta `_trade_log` / round_trips 已有基础）。

---

## 2026-07-11 EXP-006A — First Pullback 多周期对照（rb）

**窗口**：2024-01-01 ~ 2025-06-30 | **数据源**：TQ CbC rb 分月 1m 拼接（122,190 bars）  
**Setup**：`first_pullback` detector（BrooksScalp v0.1 FSM，仅改重采样周期）  
**Forward**：f10 = 10 bars @ 各 TF（wall-clock 见下表）| **成本**：net@3 = f10 − 3 tick  
**Gate**：n≥30 & net@3>0  
**输出**：`research/output/exp006a_timeframe_first_pullback_rb.csv`

| TF | n | WR | PF | avg f10 | net@3 | net@2 | MFE | MAE | wall h10 | Gate |
|----|---|-----|-----|---------|-------|-------|-----|-----|----------|------|
| 3m | 905 | 44.2% | 1.16 | +0.56 | **-2.44** | -1.44 | 11.7 | 10.8 | 30 min | FAIL |
| 5m | 526 | 44.9% | 1.04 | +0.18 | **-2.82** | -1.82 | 14.7 | 14.9 | 50 min | FAIL |
| 10m | 263 | 49.4% | 1.14 | +0.94 | **-2.06** | -1.06 | 22.1 | 20.5 | 100 min | FAIL |
| 15m | 204 | 49.0% | 1.10 | +0.97 | **-2.03** | -1.03 | 31.5 | 26.1 | 150 min | FAIL |
| **30m** | **95** | **51.6%** | **1.44** | **+4.80** | **+1.80** | +2.80 | 43.6 | 34.4 | 300 min | **PASS** |

**已证实**：

1. 五周期中仅 **30m** 过 gate（n=95, net@3=+1.80）；3/5/10/15m 虽 gross f10 为正或近零，扣 3 tick 后全负。
2. f10 随周期单调改善（3m +0.56 → 30m +4.80）；MFE/MAE 同步放大，30m PF=1.44。
3. **15m Prior 未被本实验支持**：15m（net@3=-2.03）劣于 10m（-2.06）且远劣 30m（+1.80）；5m（pa_cta 信号层 Prior）net@3=-2.82 最差档之一。
4. 30m 样本 n=95 刚过 gate 下限，**统计置信度有限**。

**待验证假设**：

- 30m edge 在 ma/hc 或 2023/2025H2 OOS 是否复现。
- 30m f10=10 bars = 300 min 持仓与 PA2 目标画像（20–120 min）**不完全对齐**——可能需 EXP-009 管理层或更短 forward horizon 复检。
- Event 层 PASS ≠ CTA 可交易（无 always_in / AFF / 多 OPP 干扰）。

**下一步（默认 1 项）**：在 **30m** 上启动 **EXP-006** Expectancy Surface（trend_strength × pullback_depth × …），或先跑 ma/hc 006A 对照再定 TF。

**等待确认**：是否 (A) 直接 EXP-006 @30m，(B) 先补 ma/hc 006A，(C) 仍用 15m/5m 对齐 pa_cta 架构做 EXP-006（与 Event 层结论冲突需明示）。→ **已执行 B（006A 跨品种）+ EXP-006 @30m 分层**。

---

## 2026-07-11 EXP-006 — First Pullback Expectancy Surface（rb @30m）

**窗口**：2024-01-01 ~ 2025-06-30 | **TF**：30m（006A rb 唯一过 gate 周期）  
**CLI**：`python -m research.run_expectancy_study --symbol rb --timeframe 30`  
**输出**：`research/output/exp006_first_pullback_rb_30m_summary.csv` / `_surface.csv`

### 1D 分层（节选）

| Segment | n | WR | f10 | net@3 | Gate |
|---------|---|-----|-----|-------|------|
| **ALL** | 95 | 51.6% | +4.80 | **+1.80** | **PASS** |
| LONG | 40 | 42.5% | -3.65 | **-6.65** | FAIL |
| **SHORT** | 55 | 58.2% | +10.95 | **+7.95** | **PASS** |
| TL weak | 37 | 51.4% | +7.22 | +4.22 | PASS |
| PD mid | 27 | 63.0% | +13.96 | +10.96 | FAIL（n<30） |
| SignalBody Q3 | 22 | 54.5% | +13.23 | +10.23 | FAIL（n<30） |

### 2D Surface（TrendLeg × PullbackDepth）

- **无单元格**同时满足 n≥30 & net@3>0。
- 最高 net@3 格：TL weak × PD mid（n=9, +28.44）— **样本过小，待验证假设**。

**已证实**：

1. rb 30m ALL edge **几乎全部来自 SHORT**（+7.95）；LONG 子集 net@3=-6.65，与 rb 品种偏空/趋势结构一致。
2. 分层 **有 lift**（SHORT vs ALL +6.15 tick），说明简化 FP 内 **存在可分离子 cohort**，非纯噪声。
3. 无 2D 格过 gate → **不能**用固定 trend_leg×pullback 阈值宣布「最优格」；须 OOS 或扩大窗口复验。

**待验证假设**：

- SHORT-only FP @30m 在 2023 / 2025H2 是否仍 PASS。
- 是否应对 LONG 路径硬禁或转 MTF（15m always_in）后再测。

**下一步（默认 1 项）**：SHORT-only cohort 扩大样本（延长窗口或加 hc/MA @30m 006 分层），或对照 pa_cta OPP02 空侧 round_trips。→ **已执行扩窗（A）**。

---

## 2026-07-11 EXP-006A — SHORT-only 扩窗复验（rb @30m）

**窗口**：FULL 2023-01-01 ~ 2025-12-31 | **IN-SAMPLE** 2024-01-01 ~ 2025-06-30（子窗口切片）  
**CLI**：`python -m research.run_expectancy_study --direction short --start 2023-01-01 --end 2025-12-31 --is-start 2024-01-01 --is-end 2025-06-30`

| Cohort | n | WR | f10 | net@3 | Gate |
|--------|---|-----|-----|-------|------|
| **FULL SHORT** | 103 | 51.5% | +3.16 | **+0.16** | **PASS**（边际） |
| **IN-SAMPLE** | 59 | 57.6% | +10.00 | **+7.00** | **PASS** |
| OOS-PRE（2023） | 33 | 45.5% | -3.64 | **-6.64** | FAIL |
| OOS-POST（2025H2） | 11 | 36.4% | -13.18 | **-16.18** | FAIL |

**已证实**：

1. 扩窗 FULL SHORT **勉强过 gate**（+0.16），但 **OOS 两段均 FAIL** → 先前 IS 的 +7.95 **未外推**。
2. IN-SAMPLE SHORT net@3=+7.00，与首轮 EXP-006（+7.95, n=55）**方向一致**（n 略增至 59，因扩窗加载影响 FSM 边界）。
3. OOS-POST 仅 n=11，统计力不足，但 f10 大幅为负，**不能忽略**。

**待验证假设**：

- IS edge 是否 rb 2024-H1 行情特异（空头趋势段）而非 setup 通用 alpha。
- pa_cta OPP02 空侧（含 15m always_in）是否在 OOS 仍盈利——若 CTA 正、Event 负，则 **gap 在 MTF/regime 层**。

**下一步（默认 1 项）**：对照 **pa_cta OPP02 SHORT round_trips** 按同窗口 IS/OOS 切分（选项 B），或冻结 Event 层简化 FP 路径。→ **已执行（B）**。

---

## 2026-07-11 EXP-006B — pa_cta OPP02 SHORT vs Event SHORT @30m

**窗口**：2023-01-01 ~ 2025-12-31 | **IN-SAMPLE**：2024-01-01 ~ 2025-06-30  
**CLI**：`python -m research.run_opp02_is_oos --symbol rb` / `--no-opp02-aff-gate`

### Production profile（rb EXP-006 KEEP，AFF 开）

| Cohort | OPP02 SHORT n | net PnL |
|--------|---------------|---------|
| FULL / IS / OOS | **0** | 0 |

AFF alpha≥0.25 拒空侧 OPP02；同窗仅 1 笔 OPP02 多。

### Counterfactual（AFF 关，非 production）

| Cohort | n | WR | avg tick | net PnL | Gate |
|--------|---|-----|----------|---------|------|
| FULL | 12 | 50.0% | -3.39 | -14,234 | FAIL |
| IN-SAMPLE | 3 | 0.0% | -18.20 | -19,106 | FAIL |
| OOS-PRE | 9 | 66.7% | +1.55 | +4,872 | FAIL（n<30） |

### Event vs CTA（同窗口）

| Cohort | Event net@3 | CTA avg tick（AFF 关） |
|--------|-------------|------------------------|
| IN-SAMPLE | **+7.00** PASS | **-18.20**（n=3） |
| OOS-PRE | -6.64 FAIL | +1.55（n=9） |

**已证实**：Production CTA OPP02 空 **0 笔**，与 Event 59 IS 事件 **非同一集合**；AFF 关 counterfactual 全窗 **净亏**，与 Event IS **方向相反** → gap 在 **MTF + regime 门禁 + 样本定义**，Event PASS **不可直接策略化**。

**下一步（默认 1 项）**：冻结 Event 层简化 FP；转 EXP-007 BP 或 pa_cta 全策略 IS/OOS。→ **已执行（D：FP FROZEN + EXP-007A）**。

---

## 2026-07-11 EXP-007A — Breakout Pullback 多周期对照（rb）

**窗口**：2024-01-01 ~ 2025-06-30 | **Setup**：`breakout_pullback`（自 `E1_breakout_pullback_rb` 迁入）  
**CLI**：`python -m research.run_bp_study --symbol rb`  
**输出**：`research/output/exp006a_timeframe_breakout_pullback_rb.csv`

| TF | n | WR | PF | avg f10 | net@3 | Gate |
|----|---|-----|-----|---------|-------|------|
| 3m | 829 | 45.4% | 1.03 | +0.11 | -2.89 | FAIL |
| **5m** | 562 | 49.5% | 1.11 | +0.53 | **-2.47** | FAIL |
| 10m | 317 | 45.4% | 0.86 | -1.26 | -4.26 | FAIL |
| 15m | 225 | 46.7% | 0.99 | -0.08 | -3.08 | FAIL |
| 30m | 116 | 47.4% | 0.75 | -3.32 | -6.32 | FAIL |

**已证实**：rb 五周期 **全 FAIL**；相对最优为 **5m**（net@3=-2.47），与 pa_cta OPP08 信号层 Prior 一致但 Event 层仍无 edge。与 2026-07-10 legacy E1（1m ALL f10=-0.43t）**同向负期望**。

**下一步（默认 1 项）**：EXP-007B 对照 pa_cta OPP08 round_trips（同窗 IS/OOS），或 ma/hc 007A 跨品种。→ **已执行 007B**。

---

## 2026-07-11 EXP-007B — OPP08 vs Event BP @5m IS/OOS（rb）

**窗口**：FULL 2023-01-01 ~ 2025-12-31 | IN-SAMPLE 2024-01-01 ~ 2025-06-30  
**CLI**：`python -m research.run_opp08_is_oos --symbol rb`

### 对照（ALL）

| Cohort | Event n | Event net@3 | Event Gate | CTA n | CTA avg tick | CTA net PnL | CTA Gate |
|--------|---------|-------------|------------|-------|--------------|-------------|----------|
| FULL | 1192 | **-2.74** | FAIL | 8 | **+3.91** | +10,935 | FAIL（n<30） |
| IN-SAMPLE | 562 | **-2.47** | FAIL | 3 | **+7.47** | +7,840 | FAIL（n=3） |
| OOS-PRE | 449 | -3.27 | FAIL | 5 | +1.77 | +3,094 | FAIL |
| OOS-POST | 181 | -2.27 | FAIL | 0 | — | 0 | FAIL |

**已证实**：

1. **Event BP @5m 全 cohort FAIL**（扩窗 FULL net@3=-2.74），与 007A 同向。
2. **CTA OPP08 同窗 net PnL 为正**（FULL +10.9k，IS +7.8k），但 **n=8/3 远小于 gate**——不能宣布 CTA edge，只能标「小样本正 PnL vs Event 大样本负 tick」。
3. 与 EXP-006B 镜像：**CTA 成交集 ⊂ 漏斗后子集**，Event 机械 BP 触发远多（1192 vs 8）→ **两者不可直接比 WR/期望**。

**待验证假设**：OPP08 正 PnL 是否在默认 3 年全窗（2023-05~2026-05）仍成立且 n 更大。

**下一步（默认 1 项）**：ma/hc **007A** 跨品种，或 **EXP-008** Failed Breakout @5m/15m。→ **已执行 007A 跨品种（C）**。

---

## 2026-07-11 EXP-007A — Breakout Pullback 跨品种（rb / hc / MA）

**窗口**：2024-01-01 ~ 2025-06-30 | **成本**：net@3 = f10 − 3 tick

| 品种 | 3m | 5m | 10m | 15m | 30m | 相对最优 TF |
|------|-----|-----|------|------|------|-------------|
| **rb** | -2.89 | **-2.47** | -4.26 | -3.08 | -6.32 | **5m** |
| **hc** | **-2.74** | -2.80 | -3.08 | -2.77 | -5.15 | **3m** |
| **MA** | -3.51 | -3.28 | **-2.89** | -3.49 | -3.78 | **10m** |

（表中为 net@3；**三品种五周期全部 FAIL gate**）

**已证实**：

1. BP 机械定义在 rb/hc/MA **均无 economic edge**（与 rb legacy E1 STOP 一致）。
2. **无跨品种统一最优 TF**（rb→5m、hc→3m、MA→10m），与 FP 007A 结论类似。
3. pa_cta OPP08（5m 信号层）在 Event 层 **5m 亦 FAIL**——Prior 架构不能从 Event 层获 Evidence 支持。

**下一步（默认 1 项）**：**EXP-008** Failed Breakout @5m/15m，或冻结 Event 层 BP 路径。→ **已执行 EXP-008A（E）**。

---

## 2026-07-11 EXP-008A — Failed Breakout 跨品种（rb / hc / MA）

**窗口**：2024-01-01 ~ 2025-06-30 | **Setup**：`failed_breakout` (S3 Fade) | **CLI**：`python -m research.run_fb_study`

| 品种 | 3m | 5m | 10m | 15m | 30m | 相对最优 TF | 1m 基线* |
|------|-----|-----|------|------|------|-------------|----------|
| **rb** | -3.06 | -3.85 | -4.17 | -4.17 | **-0.73** | **30m** | net@3≈-3.19 |
| **hc** | -3.35 | -3.63 | -2.92 | **-1.12** | -2.34 | **15m** | — |
| **MA** | -3.44 | -3.79 | **-3.20** | -5.04 | -4.30 | **10m** | — |

*Program 1.0 rb 1m S3 net@3=-3.19（2024H1）。表中为 net@3；**全部 FAIL gate**。

**已证实**：

1. 慢周期 **未救** S3：rb 30m 最优仍 net@3=-0.73（f10=+2.27 但扛不住 3 tick）；**无品种过 gate**。
2. hc 15m 略好（-1.12）仍 FAIL；MA 全档更差。
3. 与 Phase 4 结论一致：S3→CLIMAX 路由无法在 Event 层创造 edge。

**下一步（默认 1 项）**：归档 Event 层 S1/S2/S3 多周期路径；转 **EXP-009** Trade Management Lab（pa_cta round_trips）或暂停 Event 筛选线。→ **已执行 EXP-009**。

---

## 2026-07-11 EXP-009 — Trade Management Lab（pa_cta rb）

**窗口**：2023-05-17 ~ 2026-05-16 | **品种**：rb EXP-006 profile（含成本）  
**CLI**：`python -m research.run_tm_lab --symbol rb`  
**方法**：同一 37 笔 Entry cohort；1m bar 重放出厂规则 vs 机械出场（initial_stop 来自 `_entry_snapshot`）  
**输出**：`research/output/exp009_tm_lab_rb_summary.csv` / `_by_setup.csv`

| Rule | n | WR | PF | Net PnL | Δ vs ACTUAL |
|------|---|-----|-----|---------|-------------|
| **ACTUAL**（production） | 37 | 43.2% | **1.26** | **+23,086** | — |
| STOP_EOD（仅初始止损 + 14:55 强平） | 37 | 43.2% | 1.10 | +9,404 | -13,682 |
| FIXED_2R | 37 | 43.2% | 0.98 | -1,586 | -24,673 |
| ATR_TRAIL（Chandelier 2.5×ATR5） | 37 | 43.2% | 0.91 | -9,691 | -32,777 |
| TIME_120 | 37 | 37.8% | 0.74 | -25,824 | -48,911 |
| FIXED_1R | 37 | 45.9% | 0.69 | -30,009 | -53,095 |

**Entry vs Management 分解**：

| 指标 | 值 | 说明 |
|------|-----|------|
| Entry 代理 (FIXED_1R) PF | **0.69** | **与假设「Entry PF ~1.2」不符** |
| Production PF | **1.26** | 含 MM / Chandelier / PROFIT_PROTECT / EOD |
| STOP_EOD PF | 1.10 | 最接近「纯入场+硬止损」代理 |
| Management 增值（ACTUAL − STOP_EOD） | **+13,682** | production 管理层相对「仅止损+EOD」有净贡献 |

**已证实**：

1. **机械 1R/2R/120min/ATR trail 均劣于 production**；最佳机械规则 STOP_EOD 仍少赚 ~14k。
2. **入场 cohort 在 FIXED_1R 下 PF<1**——edge 主要来自 **非对称出场栈**（Chandelier、PROFIT_PROTECT、EOD 选择性截断/放右尾），非「固定 R 倍数止盈」。
3. 与 Exit Attribution（OPP16/15）一致：盈利路径依赖 **PROFIT_PROTECT + EOD**，非 MM runner。

**待验证假设**：

- hc/MA 同法复检；IS/OOS 分段（2024-01~2025-06）是否同样「ACTUAL > 机械规则」。
- 简化出场（如弱化 PROFIT_PROTECT）须单变量 EXP，不可从本表直接推断 DD 变化。

**下一步（默认 1 项）**：归档 Event 层多周期 S1/S2/S3/BP/FB 路径；pa_cta 侧重 Exit 单变量消融（PROFIT_PROTECT / EOD 对照）或 hc 跨品种 TM Lab。

**等待确认**：是否 (A) hc TM Lab，(B) PROFIT_PROTECT 消融回测，(C) 暂停 PA2 Event 线、冻结 Program 2.0 筛选结论。→ **已执行 A（hc + MA）**。

---

## 2026-07-11 EXP-009B — Trade Management Lab 跨品种（hc / MA）

**窗口**：2023-05-17 ~ 2026-05-16 | **含成本** | **CLI**：`python -m research.run_tm_lab --symbol hc|MA`

| 品种 | cohort n | ACTUAL PF | ACTUAL Net | 最佳机械规则 | 最佳机械 Net | ACTUAL vs 最佳机械 |
|------|----------|-----------|------------|--------------|-------------|-------------------|
| **rb** | 37 | **1.26** | **+23,086** | STOP_EOD (PF 1.10) | +9,404 | **ACTUAL 优 +13,682** |
| **hc** | 48 | 0.95 | -4,774 | **STOP_EOD (PF 1.21)** | **+22,221** | **ACTUAL 劣 −26,995** |
| **MA** | 20 | 1.72 | +40,209 | **STOP_EOD (PF 1.72)** | **+48,857** | **ACTUAL 劣 −8,648** |

### 分规则 Net PnL（Δ vs ACTUAL）

| Rule | rb | hc | MA |
|------|-----|-----|-----|
| ACTUAL | +23,086 | −4,774 | +40,209 |
| STOP_EOD | +9,404 (−13.7k) | **+22,221 (+27.0k)** | **+48,857 (+8.6k)** |
| FIXED_2R | −1,586 | +10,045 (+14.8k) | +15,367 (−24.8k) |
| ATR_TRAIL | −9,691 | +5,384 (+10.2k) | −38,652 (−78.9k) |
| FIXED_1R | −30,009 | −33,904 | +5,946 (−34.3k) |
| TIME_120 | −25,824 | −19,775 | −20,223 |

**已证实**：

1. **管理层增值非跨品种稳定**：rb 上 production 优于一切机械规则；**hc / MA 上 STOP_EOD（仅初始止损 + 14:55 强平）净优于 ACTUAL**。
2. hc ACTUAL 净亏（−4.7k）而 STOP_EOD 净赚（+22.2k）——当前 Chandelier / PROFIT_PROTECT / MM 栈在 hc **整体减损**（与 hc profile 低流动性 + OPP 构成相关，待 setup 级分解）。
3. Entry 代理 FIXED_1R：rb/hc PF<1；MA PF=1.11（唯一接近「Entry ~1.2」），但 ACTUAL 相对 FIXED_1R 仍 +34k——MA 上复杂出场对 FIXED_1R 有增也有损，相对 STOP_EOD 则偏负。
4. MA 样本 n=20，STOP_EOD vs ACTUAL 同 PF=1.72 但 Net 差 +8.6k——差异来自 **出场时机** 而非胜率结构。

**待验证假设**：

- hc 上 setup 级（OPP08/16/19）何者被 PROFIT_PROTECT/EOD 伤害最大（读 `exp009_tm_lab_hc_by_setup.csv`）。
- hc 是否应试验 **简化出场 profile**（弱化 PROFIT_PROTECT / 提前 EOD 逻辑）——须单变量 EXP，不可直接改 production。

**下一步（默认 1 项）**：hc **PROFIT_PROTECT 消融** 或 hc setup 级 TM 分解报告；或归档 PA2 Event 线。

**等待确认**：是否 (B) hc PROFIT_PROTECT 消融，(C) 冻结 Event 线，或 (D) hc setup 级 TM 细读。→ **已执行 B**。

---

## 2026-07-11 EXP-009C — hc PROFIT_PROTECT_1440 单变量消融

**窗口**：2023-05-17 ~ 2026-05-16 | **含成本** | **单变量**：`profit_protect_enabled=False`  
**CLI**：`python -m research.run_profit_protect_ablation --symbol hc`  
**实现**：`strategies/pa_cta/strategy.py` 新增 `profit_protect_enabled`（默认 True）

| 版本 | 总净盈亏 | Sharpe | 笔数 | WR | PF | maxDD% |
|------|----------|--------|------|-----|-----|--------|
| 基线（PROFIT_PROTECT 开） | **−4,774** | −0.07 | 48 | 35.4% | **0.95** | **−14.98%** |
| 消融（PROFIT_PROTECT 关） | −20,624 | −0.29 | 48 | 35.4% | 0.79 | −21.11% |
| **Δ（关 − 开）** | **−15,850** | — | 0 | — | — | +6.13pp 更差 |

### exit_reason 迁移（关键）

| exit_reason | 基线 n / net | 消融 n / net |
|-------------|-------------|-------------|
| PROFIT_PROTECT_1440 | **19 / −19,078** | 0 / 0 |
| EOD_FLAT | 7 / **+22,173** | **23 / −13,167** |
| CHANDELIER_STOP | 10 / +25,958 | 12 / +30,736 |
| STOP_LOSS | 6 / −29,821 | 7 / −34,187 |

### OPP19 SHORT（TM Lab 重点怀疑对象）

| | n | net | PF |
|---|-----|-----|-----|
| 基线 | 7 | −4,460 | 0.26 |
| 消融 | 7 | −3,810 | 0.29 |
| Δ | — | **+650** | — |

**已证实**：

1. **关 PROFIT_PROTECT 整体劣化 hc**（−15.9k），与 TM Lab「STOP_EOD 优于 ACTUAL」**不矛盾**——TM Lab 是 bar 重放 + 固定初始止损；本 EXP 是 **全栈联动**（出场路径迁移至 EOD/Chandelier/STOP）。
2. 关 PP 后 **19 笔 PROFIT_PROTECT 消失**，但 **EOD 笔数 7→23** 且 EOD 净盈亏 **+22k→−13k**——主要损伤来自 **EOD 承接路径变劣**，非 OPP19 空单独主导。
3. OPP19 空略改善（+650），**不足以**抵消 EOD 迁移损失 → **不可**对 hc 单独关 PP。

**结论**：**REVERT / KEEP** production `profit_protect_enabled=True`（全品种默认）；hc 优化须另寻单变量（EOD 逻辑 / Chandelier 参数 / setup 过滤），非 PP 一刀切。

**待验证假设**：hc 上弱化 PP **且** 同步约束 EOD 出场（双变量）——须用户授权，非本 EXP 范围。

**下一步（默认 1 项）**：归档 PA2 Event 线；或 hc **EOD 出场**单变量消融；或 (D) setup 级 TM 细读。

**等待确认**：是否 (C) 冻结 Event 线，(E) hc EOD 消融，或 (D) setup 细读。→ **已执行 E**。

---

## 2026-07-11 EXP-009D — hc EOD_FLAT（14:55 强平）单变量消融

**窗口**：2023-05-17 ~ 2026-05-16 | **含成本** | **单变量**：`eod_flat_enabled=False`  
**CLI**：`python -m research.run_eod_flat_ablation --symbol hc`  
**实现**：`strategies/pa_cta/strategy.py` 新增 `eod_flat_enabled`（默认 True）

| 版本 | 总净盈亏 | Sharpe | 笔数 | WR | PF | maxDD% |
|------|----------|--------|------|-----|-----|--------|
| 基线（EOD 强平 开） | **−4,774** | −0.07 | 48 | 35.4% | **0.95** | **−14.98%** |
| 消融（EOD 强平 关） | −11,537 | −0.18 | 47 | 31.9% | 0.88 | −16.23% |
| **Δ（关 − 开）** | **−6,763** | — | −1 | — | — | 更差 |

### exit_reason 迁移

| exit_reason | 基线 n / net | 消融 n / net |
|-------------|-------------|-------------|
| **EOD_FLAT** | **7 / +22,173** | **0 / 0** |
| PROFIT_PROTECT_1440 | 19 / −19,078 | 25 / −48 |
| CHANDELIER_STOP | 10 / +25,958 | 9 / +25,413 |
| STOP_LOSS | 6 / −29,821 | 7 / −32,830 |

### setup Δ Top（关 − 开）

| Setup | Δ net |
|-------|-------|
| OPP19_LONG | −3,269 |
| OPP16_SHORT | −2,920 |
| OPP15_WEDGE | −593 |

**已证实**：

1. **关 EOD 强平劣化 hc（−6.8k）**——基线 7 笔 EOD 贡献 **+22k** 净盈亏，关后该路径消失且 PP/STOP 未能替代。
2. 结合 EXP-009C：**hc 上 PP 与 EOD 均不可单独关闭**；两者共同构成 production 出场栈，单变量消融均劣于基线。
3. TM Lab「STOP_EOD 优于 ACTUAL（+22k vs −4.7k）」与 C/D 结论并存的原因：**TM Lab 重放使用固定 initial_stop + 机械 EOD**，与全栈策略（PP/Chandelier/MM 干预 stop 路径）**非同一数据生成过程**——TM Lab 结论 **不可**直接映射为「改 production 开关」。

**结论**：**KEEP** `eod_flat_enabled=True`（全品种默认）；hc 净亏根因 **不在 EOD/PP 单开关**，而在 setup 构成 + STOP 大亏（6 笔 −30k）+ PP 慢车道止损迁移。

**下一步（默认 1 项）**：**(C) 归档 PA2 Event 线**；hc 侧转 **setup 过滤 / STOP 结构**（OPP13/15/19），或 **(D) setup 级 TM 细读**。

**等待确认**：是否 (C) 冻结 Event 线，(D) hc setup 细读，或 hc **OPP 拖累项 Purification** 回测。→ **已执行 D**。

---

## 2026-07-12 EXP-009E — hc setup 级 TM 细读

**窗口**：2023-05-17 ~ 2026-05-16 | **含成本** | **n=48**  
**CLI**：`python -m research.run_hc_setup_tm_detail`（兼容）| `python -m research.run_setup_tm_detail --symbol hc` | `--all`  
**输出**：`research/output/exp009e_hc_setup_tm_detail.csv`  
**数据**：production ACTUAL（exit_reason）+ EXP-009B TM Lab（同 cohort STOP_EOD / FIXED_1R）

### A. ACTUAL setup 盈亏排序

| Setup | n | WR | net | 主出场 |
|-------|---|-----|-----|--------|
| OPP13_RANGE_FAIL_HIGH | 1 | 0% | **−17,225** | PP×1 |
| OPP15_WEDGE（空/无向） | 12 | 25% | **−8,133** | PP×8 (−10.8k) / EOD×3 (+4.1k) |
| OPP15_WEDGE_LONG | 2 | 0% | **−7,130** | PP / EOD |
| OPP12_OVERSHOOT_LONG | 2 | 0% | **−6,887** | STOP×2 |
| OPP19_OD_REV_SHORT | 7 | 43% | **−4,460** | CHAN×3 / PP×1 / STOP×1 / BE×2 |
| OPP19_OD_REV_LONG | 7 | 29% | **−2,640** | 分散 |
| OPP08_BREAKOUT_LONG | 1 | 0% | −742 | BE |
| OPP12_OVERSHOOT_SHORT | 1 | 100% | +3,882 | EOD |
| OPP16_TWO_BAR_LONG | 2 | 100% | **+8,064** | CHAN×2 |
| OPP16_TWO_BAR_SHORT | 10 | 40% | **+10,588** | EOD×1 (+17.8k) / PP×5 (+9.5k) / STOP×2 (−16.5k) |
| OPP08_BREAKOUT_SHORT | 3 | 67% | **+19,910** | CHAN×1 (+15.4k) / PP×2 (+4.5k) |

**盈利簇**：OPP08 空 + OPP16 多空 ≈ **+38.6k**  
**拖累簇**：OPP13 + OPP15 全 + OPP12 多 + OPP19 全 ≈ **−46.5k**

### B. 生产栈相对 STOP_EOD（TM Lab Δ = STOP_EOD − ACTUAL）

| 分类 | Setup | ACTUAL | STOP_EOD | Δ |
|------|-------|--------|----------|---|
| **栈减损** | OPP19_SHORT | −4,460 | **+17,589** | **+22,049** |
| **栈减损** | OPP16_LONG | +8,064 | +27,564 | +19,499 |
| **栈减损** | OPP13 | −17,225 | −6,665 | +10,560 |
| **栈增值** | OPP15_WEDGE | −8,133 | −17,373 | −9,240 |
| **栈增值** | OPP08_SHORT | +19,910 | +16,610 | −3,300 |
| **栈增值** | OPP19_LONG | −2,640 | −8,030 | −5,389 |
| 中性 | OPP16_SHORT / OPP12 | — | — | \|Δ\|≤0.5k |

### C. 已证实结论

1. **hc 净亏是 setup 结构问题，不是全局 EOD/PP 开关问题**（与 009C/D KEEP 一致）。
2. **最大单笔拖累**：OPP13 一笔 PP −17.2k；**最大频率拖累**：OPP15 楔形 14 笔合计 ≈ −15.3k（PP 主导）。
3. **TM「STOP_EOD 优于 ACTUAL」几乎全部来自 OPP19_SHORT（+22k）+ OPP16_LONG（+19k）+ OPP13（+11k）**；对 OPP15 / OPP08 空，生产栈反而更好或少亏。
4. OPP16 空：**EOD +17.8k 与 STOP −16.5k 对冲**——关 EOD 会伤这条盈利腿（与 009D 全品种关 EOD −6.8k 一致）。
5. OPP19 空：FIXED_1R / STOP_EOD 均为正，ACTUAL 为负 → **入场尚可、出场栈减损**；但 009C 证明 **全局关 PP 不能救**（EOD 迁移伤全局）。

### D. Purification 候选（待回测，非本报告结论）

| 动作 | 依据 | 静态粗估* |
|------|------|-----------|
| 关 OPP13 | 1 笔 −17k，纯 PP | +17k |
| 关 OPP15（楔形） | 14 笔 −15k | +15k |
| 关 OPP12 多 / 或 OPP12 全 | 多 −6.9k | +7k |
| 关 OPP19 空（或仅空） | ACTUAL −4.5k；TM 显示栈害 | +4.5k（静态）|
| **保留** | OPP08 空、OPP16 多空 | 盈利核 |

\*静态加总 **不可**代替回测（EXP-005 已证 setup 非独立）。

**下一步（默认 1 项）**：hc **OPP Purification**（关 OPP13+OPP15±OPP19 空）单轮对照；或 (C) 冻结 Event 线。

**等待确认**：是否跑 Purification 回测（请指定关闭列表），或 (C) 归档 Event 线。→ **已执行多品种 setup 细读（009E 扩展）**。

---

## 2026-07-12 EXP-009E′ — 多品种 setup 级 TM 细读（rb / hc / MA）

**窗口**：2023-05-17 ~ 2026-05-16 | **含成本** | **1m TQ CbC**  
**CLI**：`python -m research.run_setup_tm_detail --all`  
**输出**：`exp009e_{rb,hc,ma}_setup_tm_detail.csv` + `exp009e_setup_tm_detail_all.csv`

### 品种总览

| 品种 | n | 总净盈亏 | PF | setup 数 | 盈利 setup | 拖累 setup |
|------|---|----------|-----|----------|------------|------------|
| **rb** | 37 | **+23,086** | 1.26 | 9 | OPP16_LONG (+34.8k)、OPP15 (+15.9k)、OPP13 (+9.7k) | OPP12_SHORT (−12.2k)、OPP16_SHORT (−8.6k)、OPP02_LONG (−7.1k) |
| **hc** | 48 | **−4,774** | 0.95 | 11 | OPP08_SHORT (+19.9k)、OPP16 多空 (+18.7k) | OPP13 (−17.2k)、OPP15 (−15.3k)、OPP12 多 (−6.9k) |
| **MA** | 20 | **+40,209** | 1.72 | 7 | **OPP16_SHORT (+77.9k)** | OPP16_LONG (−17.9k)、OPP15 (−10.1k)、OPP13_LOW (−9.5k) |

### 跨品种共性（已证实）

1. **OPP16 多空方向偏性因品种而异**：rb/MA **空**强（MA 空 +77.9k 占总额 194%）；hc **空**仍盈但 STOP 对冲大；rb **多**强（+34.8k），MA **多**拖 (−17.9k)。
2. **OPP15 楔形**：rb **+15.9k（盈）** vs hc/MA **−8k/−10k（亏）**——同 setup **不可跨品种硬禁**。
3. **OPP13**：rb 盈 (+9.7k)、hc 单笔大亏 (−17.2k)、MA 分化（HIGH +871 / LOW −9.5k）。
4. **管理栈 vs STOP_EOD（TM Δ）无统一方向**：hc OPP19_SHORT Δ+22k（栈害）；MA OPP16_SHORT Δ+12k（栈害）；rb OPP16_LONG Δ−3.2k（栈益）。**Purification 须分品种**。

### 分品种 Purification 候选（静态，待回测）

| 品种 | 建议关/弱 | 建议保留 |
|------|-----------|----------|
| **hc** | OPP13、OPP15、OPP12 多 | OPP08 空、OPP16 |
| **rb** | OPP12 空、OPP16 空、OPP02 多（小样本） | OPP16 多、OPP15、OPP13 |
| **MA** | OPP16 多、OPP15、OPP13_LOW | OPP16 空（核心） |

**下一步（默认 1 项）**：分品种 Purification 对照回测（hc 优先）；或 (C) 归档 Event 线。

**等待确认**：Purification 关闭列表 + 品种，或 (C) 归档 Event 线。→ **已执行 hc Purification（009F）**。

---

## 2026-07-12 EXP-009F — hc OPP Purification（OPP13+OPP15）

**窗口**：2023-05-17 ~ 2026-05-16 | **含成本** | **1m TQ CbC**  
**CLI**：`python -m research.run_opp_purification --symbol hc`  
**硬禁**：`disabled_setups` 前缀匹配

**排障（同轮）**：OPP15 Path B'（`WEDGE_B_PRIME` / `_LONG`）原先 **直接 buy/short**，绕过 `_setup_disabled`；已补门禁 + `_try_arm_wedge_setup` 前缀检查。修前「关 OPP15」实际只禁掉 OPP13（Δ=+17.2k）；修后重跑下表。

| 版本 | disabled | 总净盈亏 | Sharpe | 笔数 | WR | PF | maxDD% | ΔPnL |
|------|----------|----------|--------|------|-----|-----|--------|------|
| 基线 | (none) | −4,774 | −0.07 | 48 | 35.4% | 0.95 | −14.98% | — |
| **关 OPP13+OPP15** | `OPP13_,OPP15_` | **+27,715** | **0.46** | **33** | 42.4% | **1.56** | **−11.11%** | **+32,489** |
| 关 OPP13+OPP15+OPP19空 | `OPP13_,OPP15_,OPP19_5M_OD_REV_SHORT` | **+32,175** | **0.54** | 26 | 42.3% | **1.73** | −10.93% | +36,948 |

### 修后剩余 setup（关 OPP13+OPP15）

| Setup | n | net |
|-------|---|-----|
| OPP08_SHORT | 3 | +19,910 |
| OPP16_SHORT | 10 | +10,588 |
| OPP16_LONG | 2 | +8,064 |
| OPP12_SHORT | 1 | +3,882 |
| OPP08_LONG | 1 | −742 |
| OPP19_LONG | 7 | −2,640 |
| OPP19_SHORT | 7 | −4,460 |
| OPP12_LONG | 2 | −6,887 |

**已证实（hc 样本内）**：

1. 关 OPP13+OPP15：净盈亏 **−4.8k → +27.7k**，PF 0.95→1.56，笔数 48→33，MDD 改善。
2. 再关 OPP19 空：额外 +4.5k（至 +32.2k），PF 1.73；与 009E 静态 OPP19 空 −4.5k 接近。
3. Δ≈静态拖累加总（OPP13+OPP15≈−32.5k）——本样本 setup 近似可加，**仍不能**外推 rb/MA（009E′：OPP15 在 rb 为盈利核）。

**结论**：**HOLD（hc 样本内）** — 可写入 **hc profile** `disabled_setups="OPP13_,OPP15_"`（或含 OPP19 空）待你确认；**禁止**写入 rb/MA（EXP-012x 先例）。

**下一步（默认 1 项）**：确认是否固化 hc profile；或 (C) 归档 Event 线；或 rb/MA 分品种 Purification。

**等待确认**：是否 (1) hc 写 profile 关 OPP13+OPP15，(2) 加关 OPP19 空，(3) 仅 HOLD 不写码，(C) 归档 Event 线。

---

## 2026-07-12 EXP-027 — Phase-2 Production OPP 影子账本

**目标**：分解 alpha 来源 — 信号原始期望 → gate 增量 → arbitration → exit → sizing。  
**约束**：复用 **production OPP 定义**（`_try_production_arm` / OPP15 B' 直进 gate 子集），非 Event detector 近似。

**实现**：

| 组件 | 路径 |
|------|------|
| 核心模块 | `strategies/pa_cta/shadow_ledger.py` |
| 策略 hook | `shadow_ledger_enabled` + `_try_production_arm` / `_try_opp15_direct_entry` |
| 回测导出 | `strategies/pa_cta/backtest.py::export_shadow_ledger` |
| 入口 | `python -m research.run_shadow_ledger --symbol rb` |

**每条候选记录**：时间/品种/setup/方向、入场价/结构止损/初始 R、15m context（always_in/trend_phase/ATR ratio/AFF）、各 gate pass/fail、disposition（ARMED/GATE_BLOCKED/PREEMPTED/POS_SKIP/TRADED）、forwards（MFE/MAE/1R/2R/60m/120m/EOD 含成本）。

**Phase-2.1 待做**：5m bar dry-scan 捕获「前序 setup 抢占、从未到达 arm」的候选。

**默认行为**：`shadow_ledger_enabled=False` — 不影响 production 下单逻辑。

### EXP-027A — rb 全窗影子账本（2023-05-17→2026-05-16，含成本）

**Production 回测对照**：38 RT，净盈亏 **+18,112**，Sharpe 见当轮回测（与 EXP-026B 同量级）。

**候选漏斗（220 条）**：

| disposition | n | fwd120 均 | EOD net 均 | hit_1R |
|-------------|---|-----------|------------|--------|
| TRADED | 38 | **+53.7** | +33.1 | 68.4% |
| ARMED（未成交） | 111 | −104.4 | −73.1 | 40.5% |
| GATE_BLOCKED | 68 | −128.4 | −83.3 | — |
| PREEMPTED | 3 | −431.9 | −205.2 | — |
| **全样本** | 220 | −89.0 | — | — |

**Gate 拦截（68 条，100% 来自 production gate 链）**：

| first_blocking_gate | n | 被拦信号 fwd120 均 |
|---------------------|---|-------------------|
| dual_core | 37 | −138.1 |
| vsa | 31 | −116.9 |

无 aff / late_phase / opp13_volume 拦截（该窗 arm 到达层）。

**Setup × 成交（TRADED fwd120）**：

| setup | traded | fwd120 |
|-------|--------|--------|
| OPP16_LONG | 7 | +177.8 |
| OPP13_HIGH | 2 | +173.1 |
| OPP15_B_PRIME | 7 | +69.3 |
| OPP08_SHORT | 8 | +45.4 |
| OPP16_SHORT | 8 | +16.6 |
| OPP12_SHORT | 4 | −64.6 |
| OPP19_LONG/SHORT | 各1 | 负 |

**已证实**：

1. **Gate 增量（聚合）**：被 dual_core/VSA 拦下的候选 fwd120 均值为负（−117～−138），与 TRADED 子集（+54）方向相反——该窗 gate 在 arm 层有**正向过滤**作用（待验证：是否 setup 异质）。
2. **Arbitration**：仅 3 条 PREEMPTED（OPP02/OPP16），样本过小。
3. **Exit/confirm 增量**：111 条 ARMED 未成交 fwd120 为负（−104），而 TRADED 为正（+54）——状态机/confirm 路径有显著**选择效应**（非 gate）。
4. OPP15：32 候选仅 7 成交；25 条 ARMED 未成交 fwd120 拖累全 setup 均值（−121）。

**输出**：`research/output/shadow_ledger_rb.csv`（220 行）

**汇总脚本**：`python -m research.run_shadow_gate_summary --symbol rb`  
→ `research/output/shadow_gate_{disposition,blocks,setup,chain}_rb.csv`

**下一步（默认 1 项）**：按 setup × gate 做条件期望曲面（需 Phase-2.1 dry-scan 补全未到达 arm 的候选）。

---

## 2026-07-12 EXP-027B — rb/hc/ma 全窗影子账本对照

**区间**：2023-05-17→2026-05-16，production profile，含成本。  
**入口**：`run_shadow_ledger` + `run_shadow_gate_summary`  
**交叉表**：`research/output/shadow_gate_cross_symbols.csv`

### Production 回测（对照）

| 品种 | RT | 净盈亏 | 候选 | TRADED |
|------|----|--------|------|--------|
| rb | 38 | **+18,112** | 220 | 38 |
| hc | 28 | **−12,366** | 253 | 28 |
| ma | 14 | **+701** | 186 | 14 |

### 分解链 fwd120（元，聚合）

| 品种 | raw_all | GATE_BLOCKED | ARMED未成交 | TRADED | raw→traded Δ |
|------|---------|--------------|-------------|--------|--------------|
| rb | −89.0 | −128.4 | −104.4 | **+53.7** | **+142.7** |
| hc | −25.1 | −32.5 | −24.5 | **+8.2** | **+33.3** |
| ma | −62.9 | −28.9 | −117.3 | **+69.2** | **+132.1** |

### Gate 拦截构成

| 品种 | dual_core | vsa | setup_disabled | 其它 |
|------|-----------|-----|----------------|------|
| rb | 37 (−138) | 31 (−117) | 0 | — |
| hc | 54 (−32) | 18 (−54) | **58 (−37)** | opp13_vol 4 (+133) |
| ma | 51 (−98) | 20 (+6) | **13 (+186)** | late_phase 1 |

（括号内为该 gate 被拦候选的 fwd120 均值）

### 已证实（三品种同窗）

1. **confirm/exit 选择效应跨品种成立**：三品种 TRADED fwd120 均高于 raw；rb/ma 提升 >130 元，hc 仅 +33（弱）。
2. **rb gate 聚合过滤为正**（被拦 −128 vs TRADED +54）；**hc/ma 弱或不稳**——hc 被拦 −32.5 接近 raw，ma 被拦 −28.9 **优于** raw（−62.9），即 ma 上部分 gate 可能拦掉了更好信号（尤其 `setup_disabled` 子集 fwd120 **+186**，n=13）。
3. **hc `setup_disabled`（009F′ 关 OPP13/15/19空）**：58 条被禁 fwd120 −37 —— 与「禁负向 setup」方向一致（该窗）。
4. **ma `setup_disabled`**：13 条被禁 fwd120 **+186** —— 与 hc 相反；**不能**把 hc 硬禁直接外推到 ma。

### 输出文件

- `shadow_ledger_{rb,hc,ma}.csv`
- `shadow_gate_{disposition,blocks,setup,chain}_{rb,hc,ma}.csv`
- `shadow_gate_cross_symbols.csv`

**结论**：**HOLD** — 影子账本跨品种可用；alpha 主要在 **confirm→TRADED 选择**，非单纯 gate；品种间 gate 符号不一致。

**下一步（默认 1 项）**：(C) Phase-2.1 dry-scan，或对 ma `setup_disabled` 子集做 setup 级拆解（不开新回测，只读 CSV）。

**等待确认**：选 (C) dry-scan / (D) ma disabled 子集拆解 / 暂停。

---

## 2026-07-12 EXP-027C — Phase-2.1 dry-scan（路由抢占补记）

**实现**：

| 组件 | 路径 |
|------|------|
| Pattern 只读匹配 | `strategies/pa_cta/shadow_dry_scan.py` |
| 路由末尾补记 | `on_5min_bar` `finally` → `_shadow_dry_scan_bar` |
| OPP13 占位标签 | `OPP13_DAY_HIGH_FIRST_TEST` / `BULLDOZER_SKIP` 等 |
| CSV 字段 | `source` = `ARM` \| `DRY_SCAN` |

**硬约束**：gate 决策 **始终** 走 `_production_gates_pass`；shadow 仅日志；`bar_winner` 仅在 **实际 commit/成交** 后设置（修复 shadow 改变 PnL 的 bug）。

**rb 全窗（含 dry-scan，含成本）**：

| 指标 | shadow OFF | shadow ON |
|------|------------|-----------|
| 净盈亏 | +9,647 | **+9,647**（一致） |
| RT | 39 | 39 |
| 候选 | — | **235**（+15 vs 2.0） |

**disposition 增量（235 条）**：

| segment | n | fwd120 均 |
|---------|---|-----------|
| TRADED | 39 | +53.7 |
| ARMED | 111 | −104.4 |
| GATE_BLOCKED | 68 | −128.4 |
| **PREEMPTED** | **17** | **−89.4** |
| （DRY_SCAN） | 17 | — |

**PREEMPTED top 来源**（`shadow_gate_preempted_rb.csv`）：`OPP13_DAY_HIGH_FIRST_TEST`、`OPP16_*` 同 bar 次优 setup、OPP15/OPP02 路由占位。

**未做**：`HAS_POSITION` 全量 GLOBAL_SKIP（噪声过大且曾干扰 gate 计数；待只读 gate 评估后再开）。

**结论**：**KEEP** — dry-scan 补全 arbitration 层；production 成交与 EXP-026B 基线 **bit-identical**。

**下一步**：对 hc/ma 重跑 shadow+dry-scan 更新三品种表；或 ma `setup_disabled` 子集拆解（只读 CSV）。

---

## 2026-07-12 EXP-027D — rb/hc/ma 三品种表（含 dry-scan）

**区间**：2023-05-17→2026-05-16，production profile，含成本；shadow ON 与 OFF 成交一致。  
**交叉表**：`research/output/shadow_gate_cross_symbols.csv`

### Production + 候选漏斗

| 品种 | 净盈亏 | RT | 候选 | DRY_SCAN | PREEMPTED | TRADED | BLOCKED | ARMED |
|------|--------|-----|------|----------|-----------|--------|---------|-------|
| rb | **+9,647** | 39 | 235 | 17 | 17 | 39 | 96 | 83 |
| hc | **−12,366** | 28 | 276 | 23 | 23 | 28 | 134 | 91 |
| ma | **+701** | 14 | 203 | 17 | 17 | 14 | 85 | 87 |

### 分解链 fwd120（元）

| 品种 | raw_all | GATE_BLOCKED | ARMED未成交 | PREEMPTED | TRADED |
|------|---------|--------------|-------------|-----------|--------|
| rb | −87.4 | −145.8 | −68.1 | −134.5 | **+35.8** |
| hc | −20.0 | −32.5 | −24.5 | **+36.1** | **+8.2** |
| ma | −55.0 | −28.9 | −117.3 | **+30.9** | **+69.2** |

### Gate 构成

| 品种 | top_gates |
|------|-----------|
| rb | dual_core:37; vsa:31; production_gates:28（多为 OPP15 volume=0 / 未 commit） |
| hc | setup_disabled:58; dual_core:54; vsa:18; opp13_volume:4 |
| ma | dual_core:51; vsa:20; setup_disabled:13; late_phase:1 |

### 已证实（更新）

1. **confirm→TRADED 选择效应**三品种仍成立；rb/ma 提升大，hc 弱。
2. **PREEMPTED（dry-scan）**：rb 被抢占候选 fwd120 偏负（−135）；**hc/ma 被抢占子集 fwd120 为正**（+36 / +31）——该窗路由抢占可能拦掉了更好信号（样本小，待验证）。
3. dry-scan 增量：rb +17 / hc +23 / ma +17 条，均为 PREEMPTED，无 GLOBAL_SKIP。

**结论**：**HOLD** — 三品种影子账本已同步 dry-scan；仲裁层跨品种符号不一致。

**下一步（默认 1 项）**：(D) 只读拆解 ma/hc `setup_disabled` 子集，或暂停。

---

## 2026-07-12 EXP-009F′ — hc profile 固化（用户选 (2)）

**采纳**：`SYMBOL_PROFILES["hc"]["disabled_setups"]="OPP13_,OPP15_,OPP19_5M_OD_REV_SHORT"`  
（009F 样本内对照：基线 −4.8k → 关13+15+19空 **+32.2k**，PF 1.73）

**边界**：仅 **hc**；rb/MA **不写**（009E′ OPP15 在 rb 盈利；EXP-012x 跨品种 Purify 已 REVERT）。  
`LEAN_PROFILE_KEYS` 已补 `disabled_setups`，经 `build_strategy_setting` 注入。

**结论**：**KEEP（hc profile）** — 待用户确认是否归档 Event 线 / 是否再跑一遍 hc 回测复核。

---

## 2026-07-13 EXP-M0 — pa_minimal OPP08+OPP16 基线与首层消融（rb888）

**目标**：独立 `strategies/pa_minimal/` 包；仅 OPP08/OPP16；M0-BASE / M0-NULL / M1-01（Dual Core OFF）。  
**数据**：TQ CbC 2023-05-17～2026-05-16，含成本。  
**输出**：`research/output/exp_m0_minimal_rb.csv`

| 版本 | 净盈亏 | Sharpe | 最大回撤率 | RT | 胜率 | PF | OPP08(n/PnL) | OPP16(n/PnL) | 候选→通过→武装 |
|------|--------|--------|------------|-----|------|-----|--------------|--------------|----------------|
| M0-BASE | −58,992 | −0.71 | −33.9% | 43 | 32.6% | 0.61 | 20/−42,006 | 23/−16,986 | 229→191→191 |
| M0-NULL | **爆仓**（RT 合计 −345,722） | — | — | 155 | 29.0% | 0.42 | 48/−65,597 | 105/−273,916 | 557→557→557 |
| M1-01 Dual Core OFF | −68,109 | −0.78 | −36.3% | 44 | 31.8% | 0.58 | 20/−42,006 | 24/−26,104 | 229→198→198 |

**Candidate Ledger（M0-BASE blocks）**：`vsa:30`, `dual_core:8`。

**已证实**：
1. 背景门禁有效：M0-NULL 全关后交易数 3.6×、最终爆仓；不能作为可交易下限，仅作对照。
2. M1-01 关 Dual Core 比 BASE 更差（−7.1k），拦截的 8 笔候选有保护价值。
3. OPP08 两品种合计亏损大于 OPP16；OPP16 在 BASE 下 23 笔 −17k，相对可控但仍负期望。
4. pa_minimal 路由无其他 OPP 成交（M0-BASE/M1 other=0）；M0-NULL 有 2 笔 UNKNOWN（待查 rollover/标签）。

**结论**：**保留 M0-BASE 背景栈**；Dual Core **不改（KEEP ON）**。极简双 setup 在全样本 rb 仍负期望，须继续背景消融，不宜直接实盘。

**下一步（默认 1 项）**：M1-02 单变量关 VSA（其余同 BASE），或先核对 dry-scan 与 candidate ledger 候选数一致性。

**等待确认**：是否继续下一层消融（VSA OFF）？

---

## 2026-07-13 EXP-M0B — 连续批次 B→A→C（用户授权）

**顺序**：B 一致性核对 → A 关 VSA → C1 R²+CHOP / C2 VWAP 三态。  
**数据**：rb TQ CbC 2023-05-17～2026-05-16，含成本。  
**输出**：`research/output/exp_m0_batch_abc_rb.csv`，`exp_m0_dryscan_compare_rb.json`

### B. dry-scan（干扫）vs 候选账本

| 指标 | 值 |
|------|-----|
| bars_checked | 4,909 |
| bars_with_signal | 229 |
| exact_match_bars | 229 |
| mismatch_bars | **0** |
| 候选账本 candidates | 229（与上轮 M0-BASE 相同） |
| 收益复现 | PnL −58,992 与 M0-BASE bit 一致 |

**结论**：**PASS** — 极简检测器与 `shadow_dry_scan` 的 OPP08/16 在同 bar、同上下文下完全一致；后续消融可信任候选定义。

### A / C 并列（对照 B-COMPARE-BASE = M0-BASE）

| 版本 | 净盈亏 | Sharpe | MDD% | RT | PF | OPP08 | OPP16 | 候选→通过 |
|------|--------|--------|------|-----|-----|-------|-------|-----------|
| M0-BASE | −58,992 | −0.71 | −33.9 | 43 | 0.61 | 20/−42k | 23/−17k | 229→191 |
| **M1-02 关 VSA** | −68,920 | −0.80 | −35.9 | 47 | 0.58 | 21/−49k | 26/−20k | 228→220 |
| **C1 R²+CHOP** | −88,034 | −1.50 | −45.5 | 41 | 0.34 | 41/−90k | **0** | 80→71 |
| **C2 VWAP 三态** | −54,570 | −0.68 | −32.1 | 33 | 0.59 | 10/−44k | 23/−11k | 237→203 |

### 已证实

1. **VSA 有保护作用**：关 VSA 多亏约 10k，拦截约 30 条偏负候选 → **KEEP VSA ON**。
2. **R²+CHOP 三态不适合当前 OPP16 路由**：映射到趋势态后 OPP16 笔数为 0，且总盈亏更差 → **REVERT**。
3. **VWAP 三态**：全样本亏损略小于 BASE（Δ约 +4.4k），但仍为负期望；OPP08 笔数减半，OPP16 仍负。未做样本内/样本外（IS/OOS）拆分前 **不升级为新基线**。
4. Dual Core、VSA 两层消融均显示「关掉更差」→ 生产式背景栈中这两层暂保留。

**结论**：**当前最佳仍为 M0-BASE 背景栈**（Brooks 上下文 + Dual Core + VSA）。C2 记为「全样本略优但未过 OOS 门禁」的候选，不替换基线。

**下一步（默认 1 项）**：对 M0-BASE 做 IS/OOS 切分报告；或继续单变量消融「趋势末段门禁 OFF」；或进入武装层固定 cohort 对照。

**等待确认**：选 IS/OOS 报告 / 关 late_phase / 武装研究 / 暂停。

---

## 2026-07-13 EXP-M0-ISOOS — M0-BASE 样本内/样本外（rb）

**协议**：整窗回测 1 次，按 `entry_time` 切分（与 EXP-023/025 日历一致）。  
**IS**：2023-05-17～2024-12-31｜**OOS**：2025-01-01～2026-05-16  
**CLI**：`python -m research.run_pa_minimal_is_oos --symbol rb`  
**输出**：`research/output/exp_m0_is_oos_rb.csv`

| 窗 | 分组 | n | 胜率 | PF | 净盈亏 | 均PnL | 去极值PnL | 单笔占比 |
|----|------|---|------|-----|--------|-------|-----------|----------|
| FULL | ALL | 43 | 32.6% | 0.61 | −58,992 | −1,372 | −34,892 | 41% |
| FULL | OPP08 | 20 | 30.0% | 0.34 | −42,006 | −2,100 | −51,408 | 22% |
| FULL | OPP16 | 23 | 34.8% | 0.81 | −16,986 | −739 | +7,114 | 142% |
| **IS** | ALL | 38 | 34.2% | 0.72 | **−32,008** | −842 | −55,702 | 74% |
| IS | OPP08 | 19 | 31.6% | 0.37 | −35,913 | −1,890 | −45,315 | 26% |
| IS | OPP16 | 19 | 36.8% | **1.07** | **+3,904** | +205 | −19,789 | 607% |
| **OOS** | ALL | **5** | 20.0% | 0.26 | **−26,984** | −5,397 | −2,884 | **89%** |
| OOS | OPP08 | 1 | 0% | 0 | −6,093 | — | — | 100% |
| OOS | OPP16 | 4 | 25% | 0.31 | −20,891 | −5,223 | +3,209 | 115% |

### 已证实

1. **OOS n=5 < 8** → 按计划只记「未知」，不可据此 KEEP/升级任何因子。
2. **合计 IS/OOS 同向为负**；自身未过「OOS 净盈亏>0」门槛。
3. **OPP16 在 IS 弱正（+3.9k，PF 1.07）但 OOS 转负且异向**；去极值后 IS 亦翻负 → 右尾/单笔依赖强，不可当已证实 alpha。
4. **OPP08 两窗均为负**；OOS 仅 1 笔，无统计意义。
5. OOS 单笔极端占比 89% → 样本外结果由极少交易主导。

**结论**：**HOLD / 未知（OOS）** — M0-BASE 不是可交易正期望栈；OPP16 的样本内弱正 **未** 在样本外复现。

**下一步（默认 1 项）**：武装层固定候选对照（不改背景）；或单变量关 late_phase 看是否改善 IS OPP16 稳定性（仍须 OOS，且 n 仍可能不足）。

**等待确认**：武装研究 / 关 late_phase / 暂停。

---

## 2026-07-13 EXP-M0-ARM — 固定候选武装对照（离线 A/B/C）

**协议**：1 次 M0-BASE 回测导出 `gate_pass` 候选（n=191）→ 同一 cohort 离线重放三种武装；出场冻结为止损 / 1R / 120m；1 手毛额（不含手续费滑点账户层）。  
**CLI**：`python -m research.run_pa_minimal_arm_lab --symbol rb`  
**输出**：`exp_m0_arm_cohort_rb.csv` / `exp_m0_arm_detail_rb.csv` / `exp_m0_arm_summary_rb.csv`

| 规则 | 分组 | 候选 | 成交 | 成交率 | 均滑点(tick) | 1R命中 | 均MFE(R) | 均MAE(R) | 均R | 1手毛盈亏 | PF |
|------|------|------|------|--------|--------------|--------|----------|----------|-----|-----------|-----|
| **A CURRENT** | ALL | 191 | 38 | 19.9% | 2.05 | 28.9% | 0.64 | 0.50 | 0.20 | **+1,329** | **2.01** |
| A | OPP08 | 27 | 15 | 55.6% | 0.00 | 26.7% | 0.63 | 0.58 | 0.16 | +378 | 1.70 |
| A | OPP16 | 164 | 23 | 14.0% | 3.39 | 30.4% | 0.64 | 0.45 | 0.22 | +952 | 2.22 |
| B NEXT_CLOSE | ALL | 191 | 24 | 12.6% | 3.38 | 29.2% | 0.64 | 0.45 | 0.24 | +1,082 | 2.39 |
| B | OPP08 | 27 | **1** | **3.7%** | 3.00 | 0% | 0.67 | 0.24 | 0.62 | +130 | ∞ |
| B | OPP16 | 164 | 23 | 14.0% | 3.39 | 30.4% | 0.64 | 0.45 | 0.22 | +952 | 2.22 |
| C RETEST | ALL | 191 | 105 | 55.0% | 2.73 | 23.8% | 0.54 | 0.55 | 0.04 | **−68** | **0.99** |
| C | OPP08 | 27 | 11 | 40.7% | 3.64 | 18.2% | 0.54 | 0.61 | −0.03 | −211 | 0.70 |
| C | OPP16 | 164 | 94 | 57.3% | 2.63 | 24.5% | 0.53 | 0.55 | 0.05 | +143 | 1.03 |

未成交主因：A/B 的 OPP16 多为 `no_confirm`；C 多为 `invalidated_stop` / `no_reclaim`。

### 已证实

1. **候选集合固定**：三规则均为 191 条过门候选（实现未污染）。
2. **B（统一收盘确认）严重伤害 OPP08**：成交率 55.6%→3.7%；OPP16 与 A 相同（本就 PENDING_CONFIRM）→ **不采纳 B**。
3. **C（回踩收回）提高成交率但抹平边缘**：合计 PF≈1.0、毛盈亏近 0 → **不采纳 C**（本冻结出场下）。
4. **A（现行：OPP08 FAST_TRACK + OPP16 PENDING_CONFIRM）** 在固定出场下毛盈亏与 PF 最优 → **保留现行武装**。
5. 本结果为离线独立重放 + 简化出场；**不等于**含成本 live 账户 PnL（live M0-BASE 仍为 −59k）。武装层未证明能单独翻正。

**结论**：**KEEP A（现行武装）**；B/C **REVERT**。无需再为 B/C 做 live 确认回测。

**下一步（默认 1 项）**：关 late_phase 单变量消融；或暂停并转向「为何固定 1R 毛正但 live 账户负」的成本/定仓/出场诊断。

**等待确认**：关 late_phase / 成本-出场诊断 / 暂停。

---

## 2026-07-13 EXP-M1-03 — 关趋势末段门禁（late_phase）单变量消融（rb）

**变更**：`late_phase_gate_enabled=False`，其余同 M0-BASE。

| 版本 | 净盈亏 | Sharpe | MDD% | RT | PF | 候选→通过 | blocks |
|------|--------|--------|------|-----|-----|-----------|--------|
| M0-BASE | −58,992 | −0.71 | −33.9 | 43 | 0.61 | 229→191 | vsa:30, dual_core:8 |
| M1-03 关 late_phase | **−58,992** | **−0.71** | **−33.9** | **43** | **0.61** | 229→191 | 同上 |

IS/OOS 亦 **bit-identical**（IS −32,008 n=38；OOS −26,984 n=5）。`late_phase_block_count=0`。

**已证实**：在 OPP08/OPP16 极简栈 + rb 全窗内，**趋势末段门禁从未拦截任何候选**（`trend_phase!=LATE` 或方向/上下文未命中 OPP08 软禁条件）。消融为**空操作**。

**结论**：**KEEP late_phase ON**（无收益也无害于本 cohort）；该层对当前双 setup **不可检验**（无触发样本）。

**下一步（默认 1 项）**：成本/定仓/出场诊断（解释武装 Lab 毛正 vs live −59k）；或继续背景消融「AFF sizing OFF」。

**等待确认**：成本-出场诊断 / AFF sizing OFF / 暂停。

---

## 2026-07-13 EXP-M0-GAP — 武装 Lab 毛正 vs live 账户负（成本/定仓/出场）

**问题**：固定候选武装 Lab A 显示 1 手毛盈亏约 **+1,329**，但 M0-BASE live 账户 **−58,992**。  
**方法**：1 次 M0-BASE 回测分解 round-trip；对照 `exp_m0_arm_detail_rb.csv`。  
**CLI**：`python -m research.run_pa_minimal_gap_diag --symbol rb`  
**输出**：`exp_m0_gap_trips_rb.csv` / `exp_m0_gap_summary_rb.csv`

### 三层分解

| 层 | 事实 |
|----|------|
| **成本** | 价差毛利 **+30,960**；手续费 4,552 + 滑点 **85,400** = 成本 89,952（约 2.9×\|毛利\|）→ 净 −58,992 |
| **定仓** | 手数中位/最大 **50**；**93%** 顶满 `max_position`；滑点公式 `volume×size×slippage`（rb: size=10, slip=2）→ 绝对成本随手数线性放大 |
| **出场** | live 非 Lab 的「止损/1R/120m」：`FAST_LANE_TRAIL` 16 笔净 **−52.6k**；`PROFIT_PROTECT`/`EOD_FLAT` 为正；`INITIAL`/`SIGNAL_BAR_INVALID` 大幅为负 |

### 1 手折算对照

| 口径 | 值 |
|------|-----|
| live sum(毛利/手数) | **+730** |
| live sum(净盈亏/手数) | **−1,082** |
| live 中位 1 手往返成本 | **≈42.2 元** |
| Lab A 1 手毛盈亏 | **+1,329**（38 笔；出场 TIME_120/1R/STOP） |
| Lab A − 中位成本 | **≈ −273**（已非正） |

笔数：Lab 成交 38 vs live 43（持仓路径不同，集合不完全相同）。

### 已证实

1. **live 价差层仍为正毛利（+31k）**；账户亏损由 **成本 > 毛利** 造成，主因滑点。
2. **顶满 50 手**把本可 ~42 元/手的往返成本放大到账户级 ~9 万成本。
3. **出场路径是第二缺口**：同信号空间下 Lab 冻结 1R 毛边约 +1.3k/手合计；live 折算毛利仅 +730，且 `FAST_LANE_TRAIL` 桶净亏最大。
4. 即便把 Lab 毛边扣掉现实 1 手成本，合计也 **≈0 附近略负** → 武装层「毛正」**不能**直接当可交易 alpha。

**结论**：**缺口已解释，非实现 bug**。优先杠杆在（a）降有效成本敏感度（更小风险预算/手数上限，或验收滑点假设），（b）出场族是否比现行 trail/protect 更接近 Lab 的 1R 冻结——须固定入场 cohort 再测，禁止改出场反改入场集。

**下一步（默认 1 项）**：在固定入场 cohort 上对照两族出场（延续 vs 反转）vs 现行出场；或先把 `max_position`/风险预算做单变量成本敏感度（须你确认才改参回测）。

**等待确认**：两族出场 cohort / 定仓敏感度 / 暂停。


## 2026-07-13 EXP-M0-P2 — 极简 OPP08/OPP16 第二阶段（rb）

**目标**：冻结 cohort → 出场/定仓 → 形态质量 → 背景门禁 → 武装微调 → 跨品种诊断 → 停止/升级。

**CLI**：`python -m research.run_pa_minimal_phase2 --symbol rb`

### 冻结基线
- candidates=229 gate_pass=191 armed=191
- live RT=43 net=-58,992
- 成本估 1 手往返≈42.1；manifest=`frozen_manifest_rb.json`

### 出场 / 定仓
- 武装 A 成交=38 毛=+1329 扣估成本后=-270
- 出场族汇总见 `p2_exit_summary_rb.csv`
- 定仓：跳过
- **判定**：`CONTINUE`

### 形态
- OPP16 前棒形态 mismatch=87.0%
- 形态门禁：`HOLD_ORIGINAL`

### 背景
- `REVERT`（见 `p2_background_gates_rb.csv`）

### 武装
- `SKIPPED`

### 跨品种
- `PHASE_A_ONLY`

### 最终
- **HOLD_NO_PROMOTE**：未同时通过形态/背景/出场转正；默认保留武装 A + Dual Core + VSA，不升级规则。


## 2026-07-13 EXP-CTX-LAYERS — 15m 快/慢连续背景层（基建，未开闸）

**假设**：离散 `market_context` 保留作路由；另算快层(10×15m)与慢层(30×15m)连续因子，供 OPP08/16 适配分与可选软门禁。

**改动**：
- 新增 `strategies/pa_cta/context_layers.py`
- `strategy.py`：`on_15min_bar` 刷新 `_context_layers` / `ctx_*`；`context_layer_gate_enabled` **默认 False**
- `pa_minimal` 候选账本记录 `ctx_trend_quality` / `opp08_fit` / `opp16_fit` 等
- 影子账本 GATE 链插入 `context_layer`（仅 gate 开启时生效）

**行为**：默认**不改变**入场集合（与 M0-BASE bit 预期一致）。开闸需单变量对照。

**决策**：**HOLD（基建）** — 待固定 cohort 事件研究后再决定是否 `context_layer_gate_enabled=True`。


## 2026-07-13 EXP-CTX-LAYERS-BT — 快/慢层门禁 OFF vs ON（rb）

**协议**：pa_minimal M0-BASE；单变量 `context_layer_gate_enabled`；含成本 2023-05-17～2026-05-16。

| 版本 | 净盈亏 | Sharpe | MDD% | RT | 候选→通过 | blocks |
|------|--------|--------|------|-----|-----------|--------|
| GATE_OFF（默认） | −58,992 | −0.71 | −33.9 | 43 | 229→191 | vsa:30, dual_core:8 |
| GATE_ON | −49,427 | −0.64 | −32.5 | 38 | 231→179 | vsa:28, context_layer:16, dual_core:8 |
| Δ | **+9,565** | +0.07 | +1.4pp | −5 | — | 拦 16 条 |

**已证实**：默认关闸与 M0-BASE bit 一致；开闸全样本减亏但**仍为负期望**；未做 IS/OOS。

**决策**：**HOLD** — 默认保持 `context_layer_gate_enabled=False`；开闸作候选，须 OOS 后再议 KEEP。

---

## 2026-07-13 EXP-CTX-ISOOS — 快/慢层门禁 ON 样本内/样本外（rb）

**协议**：整窗回测 1 次，`context_layer_gate_enabled=True`；按 `entry_time` 切 IS/OOS（与 EXP-M0-ISOOS 日历一致）。  
**CLI**：`python -m research.run_pa_minimal_is_oos --symbol rb --ctx-gate-on`  
**输出**：`research/output/exp_m0_is_oos_rb_ctx_on.csv`

| 窗 | 版本 | 分组 | n | 胜率 | PF | 净盈亏 | 均PnL | 去极值PnL |
|----|------|------|---|------|-----|--------|-------|-----------|
| FULL | GATE_ON | ALL | 38 | 34.2% | 0.63 | −49,427 | −1,301 | −25,327 |
| FULL | M0-BASE | ALL | 43 | 32.6% | 0.61 | −58,992 | −1,372 | −34,892 |
| **IS** | GATE_ON | ALL | 33 | 36.4% | 0.77 | **−22,443** | −680 | −46,137 |
| **IS** | M0-BASE | ALL | 38 | 34.2% | 0.72 | −32,008 | −842 | −55,702 |
| IS | GATE_ON | OPP08 | 15 | 40.0% | 0.58 | −15,460 | −1,031 | −24,863 |
| IS | M0-BASE | OPP08 | 19 | 31.6% | 0.37 | −35,913 | −1,890 | −45,315 |
| IS | GATE_ON | OPP16 | 18 | 33.3% | 0.88 | **−6,983** | −388 | −30,677 |
| IS | M0-BASE | OPP16 | 19 | 36.8% | 1.07 | **+3,904** | +205 | −19,789 |
| **OOS** | GATE_ON | ALL | **5** | 20.0% | 0.26 | **−26,984** | −5,397 | −2,884 |
| **OOS** | M0-BASE | ALL | **5** | 20.0% | 0.26 | **−26,984** | −5,397 | −2,884 |

### 已证实

1. **OOS 与 M0-BASE 逐笔一致**（n=5、净盈亏 −26,984、OPP08/OPP16 拆分相同）→ 门禁拦掉的 5 笔均在 IS 段，样本外成交集合未变。
2. **OOS n=5 < 8** → 仍只记「未知」，不可 KEEP 开闸。
3. **IS 合计改善约 +9.6k**（−22,443 vs −32,008），主要来自少做 OPP08 亏损单（19→15 笔、−35.9k→−15.5k）。
4. **OPP16 IS 由弱正翻负**（+3.9k → −7.0k）→ 门禁在样本内砍掉了原先仅有的弱正信号，且**未换来 OOS 改善**。
5. 全样本开闸减亏（−49k vs −59k）与 EXP-CTX-LAYERS-BT 一致；IS/OOS 切分说明收益全部来自 IS 过滤，OOS 零增量。

**结论**：**HOLD / 未知（OOS）** — `context_layer_gate_enabled` 默认保持 **False**。开闸可作「IS 减亏」候选，但 OPP16 样本内弱正被抹平、OOS 未复现，**不满足 KEEP 门禁**。

**下一步（默认 1 项）**：武装层固定 cohort 对照（不改背景）；或跨品种扫 GATE_ON 看 IS 改善是否泛化（须用户授权批量）。

**等待确认**：武装研究 / 跨品种 GATE_ON 扫描 / 暂停。

---

## 2026-07-13 EXP-CTX-CROSS — 快/慢层门禁跨品种 OFF vs ON

**协议**：`CROSS_SYMBOL_UNIVERSE` 8 品种 × 2（关闸/开闸）；含成本整窗；单变量 `context_layer_gate_enabled`。  
**CLI**：`python -m research.run_pa_minimal_ctx_cross`  
**输出**：`research/output/exp_ctx_gate_cross_summary.csv` / `exp_ctx_gate_cross_detail.csv`

| 品种 | OFF 净盈亏 | ON 净盈亏 | Δ净盈亏 | OFF n | ON n | ctx拦 | OFF档 | ON档 |
|------|-----------|----------|---------|-------|------|-------|-------|------|
| i | −20,505 | −27,542 | **−7,037** | 20 | 14 | 19 | LOSS | LOSS |
| jm | −71,787 | −56,197 | +15,589 | 22 | 19 | 10 | LOSS | LOSS |
| p | −224,283 | −226,758 | −2,476 | 105 | 100 | 27 | LOSS | LOSS |
| y | −208,177 | −188,472 | +19,705 | 88 | 78 | 31 | LOSS | LOSS |
| ag | **+28,544** | **+30,678** | +2,135 | 35 | 34 | 9 | MARGINAL | MARGINAL |
| rb | −58,992 | −49,427 | +9,565 | 43 | 38 | 16 | LOSS | LOSS |
| hc | −20,033 | −5,877 | +14,156 | 26 | 22 | 6 | LOSS | LOSS |
| ta | −56,294 | −51,399 | +4,895 | 19 | 16 | 6 | LOSS | LOSS |

### 聚类（GATE_ON）

- **PROFIT**：无
- **MARGINAL**：ag
- **LOSS**：i, jm, p, y, rb, hc, ta
- **Δ净盈亏>0**：jm, y, ag, rb, hc, ta（6/8）
- **Δ净盈亏<0**：i, p（2/8）

### 已证实

1. 开闸在多数品种上**全样本减亏**（6/8），与 rb 单品种结论方向一致，但**无一进入 PROFIT**。
2. **档位未升级**：唯一正期望品种仍为 ag（MARGINAL），开闸仅 +2.1k / Sharpe 0.25→0.27。
3. **非单调**：i 开闸更差（−7.0k），主要因 OPP08 进一步恶化（−38.5k→−45.6k）；p 略差。
4. p/y 两档均接近爆仓量级（净亏 >20 万），开闸无法挽救；y 开闸后 MDD≈−95%。
5. rb 与先前 EXP-CTX-LAYERS-BT 一致（Δ≈+9.6k），交叉验证通过。

**结论**：**HOLD** — `context_layer_gate_enabled` 默认保持 **False**。跨品种显示「减亏常见、正期望未出现、有品种变差」，不满足 KEEP/默认开闸标准。

**下一步（默认 1 项）**：武装层固定 cohort 对照（不改背景门禁）。

**等待确认**：武装研究 / 暂停。

---

## 2026-07-13 EXP-GATE-SOFT — Dual Core 软化 + VSA 同时段相对量（基建）

**动机**：Dual Core / VSA 定位合理，但前者硬拒单、后者量分位混窗有时段季节性偏差。

### Dual Core（`dual_core_soft_enabled=True`，默认开）

| 旧（hard） | 新（soft） |
|-----------|-----------|
| 冲突直接拒单 | `_dual_core_allows_entry` 恒 True |
| VWAP 三态硬切 | 用偏离度 → `size_mult` / `target_mult` |
| OPP08 异侧拒单 | 异侧 / 反向 VWAP → 降仓 + 缩 MM 目标 |
| OPP16 看 CHOP/TREND | 看 `vwap_distance_atr` 衰竭程度（`dual_core_exhaustion_*`） |

- 定仓：`_calc_brooks_volume` × `_dual_core_size_mult`
- 目标：`_calc_measured_move_target` × `_dual_core_target_mult`
- 回退：`dual_core_soft_enabled=False` 恢复旧硬门禁

### VSA（`vsa_session_relative_enabled=True`，默认开）

| 旧 | 新 |
|----|----|
| 近 40 根 5m 混窗分位 | 同 `(hour, minute)` 历史相对量（默认 15 个交易日槽） |
| 夜盘/开盘/午前混比 | 样本不足（&lt;8）回退旧混窗 |

- 仍为硬熔断（无量空涨/出货等规则不变），只改量能口径。
- 5m 棒在信号逻辑之后 `_record_vsa_slot_volume`，当前棒不进自身样本。

**已证实（代码）**：冒烟通过（OPP08 冲突降仓、OPP16 衰竭加权、同时段分位可算）。  
**未证实**：对 rb/跨品种净盈亏的影响（须对照回测）。

**决策**：**HOLD（基建）** — 默认已切 soft + 同时段 VSA；与旧 M0-BASE **入场集合/仓位不可直接 bit 比**。对照请用 `dual_core_soft_enabled=False` + `vsa_session_relative_enabled=False`。

**下一步（默认 1 项）**：rb 单变量对照（旧硬 Dual Core+混窗 VSA vs 新 soft+同时段）。

**等待确认**：跑对照回测 / 先武装研究 / 暂停。

---

## 2026-07-13 EXP-GATE-SOFT-BT — Dual Core/VSA 旧 vs 新（rb，含成本）

**协议**：pa_minimal M0-BASE 整窗；两配置各 1 次回测。  
**LEGACY**：`dual_core_soft_enabled=False` + `vsa_session_relative_enabled=False`  
**NEW**：`dual_core_soft_enabled=True` + `vsa_session_relative_enabled=True`  
**CLI**：`python -m research.run_pa_minimal_gate_soft --symbol rb`  
**输出**：`research/output/exp_gate_soft_rb.csv`

| 版本 | 净盈亏 | Sharpe | MDD% | RT | 候选→通过 | dual_core拦 | vsa拦 | soft降仓次数 |
|------|--------|--------|------|-----|-----------|------------|-------|-------------|
| LEGACY | **−58,992** | −0.71 | −33.9 | 43 | 229→191 | 8 | 30 | 0 |
| NEW | −67,645 | −0.93 | −35.1 | 44 | 229→198 | 0 | 31 | **130** |
| Δ | **−8,653** | −0.22 | −1.2pp | +1 | +7 通过 | −8 | +1 | — |

| 分组 | LEGACY | NEW | Δ |
|------|--------|-----|---|
| OPP08 | −42,006 / n=20 | −42,006 / n=20 | 0 |
| OPP16 | −16,986 / n=23 | −25,639 / n=24 | **−8,653** |

### 已证实

1. **LEGACY 与历史 M0-BASE bit 一致**（−58,992 / 43 RT）→ 对照有效。
2. **NEW 全样本更差**（−8.7k）；主因 OPP16 多放行 1 笔且原有多头盈利被 soft 降仓稀释（OPP16 多 +17.3k→+2.7k）。
3. soft 模式 **dual_core 账本拦单 8→0**，但 `soft_reduce=130` → 多数成交以缩小仓位/目标进场，未改善净期望。
4. 同时段 VSA 仅多拦 1 条（30→31），**不是主因**；恶化主要来自 Dual Core 软化。
5. OPP08 两版相同（硬拦掉的 8 条在 soft 下改以小仓进场，OPP08 合计未改善）。

**结论**：**HOLD / 默认回退 LEGACY** — 已将 `dual_core_soft_enabled` 与 `vsa_session_relative_enabled` **默认改回 False**（代码保留，可显式开启调参）。rb 上 soft+同时段 **未验证**为改进。

**下一步（默认 1 项）**：调 soft 乘数（如 OPP16 降仓过猛）单变量消融；或武装层固定 cohort（不改背景）。

**等待确认**：调 soft 参数 / 武装研究 / 暂停。

---

## 2026-07-13 EXP-GATE-SOFT-ABL — OPP16 soft 乘数消融（rb，VSA 混窗固定）

**协议**：`dual_core_soft_enabled=True` + `vsa_session_relative_enabled=False`；三变体单批对照。  
**LEGACY 参照**：−58,992 / 43 RT（EXP-GATE-SOFT-BT）  
**CLI**：`python -m research.run_pa_minimal_gate_soft_ablate --symbol rb`  
**输出**：`research/output/exp_gate_soft_ablate_rb.csv`

| 变体 | 净盈亏 | ΔLEGACY | RT | soft降仓 | OPP16 | OPP16多 |
|------|--------|---------|-----|----------|-------|---------|
| V0_SOFT_ORIG（原 OPP16 罚则） | −71,098 | −12,106 | 44 | 128 | −29,092 | +1,219 |
| **V1_OPP16_OFF**（OPP16 不参与 soft） | **−67,429** | **−8,437** | 44 | 1 | −25,423 | **+8,153** |
| V2_OPP16_LITE（缓和乘数+有利侧跳过附加罚） | −68,533 | −9,541 | 44 | 128 | −26,528 | +5,002 |

### 已证实

1. **三变体均未优于 LEGACY**；本批最优 V1 仍差 **−8.4k**。
2. **V1（OPP16 关闭 soft）优于 V0/V2** → OPP16 软化是主要拖累；关闭后 OPP16 多由 +1.2k→+8.2k，但仍低于 LEGACY 的 +17.3k。
3. **V2 缓和乘数不够**：soft_reduce 仍 128，净盈亏介于 V0/V1 之间。
4. 44 RT vs LEGACY 43 → soft 放行原先 hard 拦掉的 dual_core 单（+1 笔）未带来净改善。
5. 重构后 V0（仅 soft+混窗 VSA）−71.1k，略差于上轮 NEW（−67.6k，含同时段 VSA）→ VSA 同时段对 soft 栈有小幅缓冲，但均劣于 LEGACY。

**结论**：**HOLD / 保持 LEGACY 默认**。若继续 soft 路线，优先 **V1（OPP16 不参与 soft）** 作下一调参起点；**不满足 KEEP**。

**下一步（默认 1 项）**：OPP08 soft 是否改回 hard 等价阈值（仅拦不缩）单变量；或转武装层 cohort。

**等待确认**：OPP08 hard 对照 / 武装研究 / 暂停。

---

## 2026-07-13 EXP-ALPHA-V1 — 稳定 Alpha 研究协议落地

**假设 ID**：EXP-ALPHA-V1  
**协议**：`ALPHA_PROTOCOL_V1`（见 `research/ALPHA_PROTOCOL.md`）  
**改动**：冻结 8 OPP 检测器指纹；`alpha_shadow_mode` 全品种 shadow 记账；`candidate_ledger` 扩展 MFE/MAE/10–80m 净 R；`run_pa_minimal_alpha_discovery` + `pa_minimal_alpha_validation` + `run_pa_minimal_alpha_promote`。

| 阶段 | 产出 | 状态 |
|------|------|------|
| 0 协议+审计 | `alpha_protocol_manifest.json`、路由审计 5 条 | **DONE** |
| 1 shadow 数据集 | `research/output/alpha_discovery/shadow_candidates_*.csv` | **RUNNING**（8 品种） |
| 2 稳定性门禁 | `stability_report.csv` → REJECT/PROVISIONAL/PROMOTE | 随阶段 1 |
| 3 CTA 晋级 | `run_pa_minimal_alpha_promote`（仅 PROMOTE_TO_CTA） | 待阶段 2 |
| 4 Forward | holdout ≥2026-05-17；CONFIRMED 须 RT≥30 且 ≥6 月 | **协议已写** |

**已证实**：开发窗 2023–05–17～2026–05–16 **不得**标 CONFIRMED_ALPHA；标签上限 `PROMOTE_TO_CTA`。

**待验证假设**：全 OPP shadow 池是否存在过门禁切片（须等 8 品种扫描结束）。

| 日期 | pa_minimal | multi | EXP-ALPHA-V1 | ALPHA_PROTOCOL_V1 shadow+validation | 待跑 | — | — | — | **PENDING** | 见 `research/ALPHA_PROTOCOL.md` |

### EXP-ALPHA-V1 首轮结果（7/8 品种，ag 缺 2312 月文件）

**数据**：`shadow_candidates_all.csv` n=70,314（gate_pass=4,059）；`stability_report.csv` 16 切片 **全部 REJECT**，**无 PROMOTE_TO_CTA**。

| OPP×方向 | n | mean_net_r@40m | bootstrap_lb | 标签 |
|----------|---|----------------|--------------|------|
| OPP15 多 | 46 | −0.11 | −0.24 | REJECT |
| OPP08 空 | 218 | −0.58 | −0.70 | REJECT |
| OPP16 空 | 720 | −0.55 | −0.64 | REJECT |
| OPP13 空 | 298 | −0.89 | −1.10 | REJECT |

**已证实**：在冻结协议 + 保守成本 + 门禁后 gate_pass 池内，**无一 OPP 方向通过时间/品种/集中度门禁**；CTA 晋级 **SKIP**（`cta_promote_result.json`）。

**待验证假设**：补全 `ag` 2312 月 Parquet 后重跑是否改变排序（当前 ag 未入池）。

**结论**：开发窗最多 **PROVISIONAL 上限亦未达**（全 REJECT）；**不是稳定 alpha**。CONFIRMED 仍须 ≥2026-05-17 holdout。

**下一步（须确认）**：补 `ag` 数据后重扫 / 维持 HOLD 不再扩 OPP / 转武装层 cohort。

