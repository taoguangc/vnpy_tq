# pa_minimal 亏损优化协议（单杠杆）

> 权威配额：`AGENTS.md` 回测配额、`docs/04_BACKTEST_SPEC.md`、`docs/06_RESEARCH_WORKFLOW.md`、`program_trading.md` §5–§6。  
> CTA 对照基线：`CTA_BASELINE_ID = OPP16_LONG_LAE`（`research/pa_minimal_baseline.py`）。

## 1. 原则

- **拆解**用于诊断；**优化**每次只动一个可证伪杠杆。
- 默认对照基线 = `MINIMAL_BASE_PROFILE`（OPP16 仅多 + defer invalid + LAE-2a + 顺宽逆严）。
- 扩 OPP / 开空 / 多 setup 白名单 = **对照实验**，不得未经用户确认写入 `MINIMAL_BASE_PROFILE`。

## 2. 因果层级（按序，勿平铺）

| 层级 | 问题 | 典型手段 | 优先级 |
|------|------|----------|--------|
| L1 | 该不该交易该 setup | 关 OPP、disabled_setups、shadow alpha | 最高 |
| L2 | 入场质量 | 入场前闸（LAE-2a 类）、production gate | 高 |
| L3 | 手数 / 风险 | risk_capital、AFF sizing、ATR regime | 中 |
| L4 | 出场 / 执行 | defer、buffer、queue sim | 低（基线冻结后再开） |

## 3. 单轮实验 SOP

```
1. 锁定基线（无 override 或显式 OPP16_LONG_LAE；多+空对照用 disabled_setups=2WAY）
2. 归因 → 写 1 句假设（单变量）
3. 最小 patch（一个参数 / 一个闸 / 一个 OPP 规则）
4. OFF vs ON 或影子对照（整命令计 1 轮回测）
5. IS 定规则（若适用）→ OOS 验证（不重挑阈值）
6. KEEP / REVERT / HOLD → append research/experiments.md
7. KEEP 且用户确认 → 写入 symbol_config / strategy 默认
```

## 4. 决策门禁（与 program_trading §6 一致）

| 结果 | 条件 |
|------|------|
| **KEEP** | ΔPnL 改善；硬门禁通过；OOS 未系统性杀赢家（或全窗 LIVE 与影子同向） |
| **REVERT** | OOS 翻车、误伤 TREND_OK、或主指标恶化 |
| **HOLD** | 样本不足（如 OOS n<8）、指标混杂 |

**已证实反例**：LAE-1 早平（症状→误修）；单 `slow_er` IS 优 OOS 杀光赢家。

## 5. 对照入口（示例）

| 目的 | 入口 |
|------|------|
| 四品种基线 | `python -m research.run_pa_minimal_cross_4detail --symbols rb,i,ma,ta` |
| LAE 闸 OFF/ON | `python -m research.run_pa_minimal_lae2a_gate_compare --symbols rb,i,ma,ta` |
| 扩 OPP 对照 | `strategy_overrides=ALL_OPP_EXCEPT_19_OVERRIDES` 等（Δ 仍对 OPP16_LONG_LAE） |
| 归因标签 | `python -m research.run_pa_minimal_lae0 --symbols rb,i,ma,ta` |
| 入场位置质量影子 | `python -m research.run_pa_minimal_opp16_entry_quality --symbols rb,i,ma,ta` |
| OPP16 原型 TC/TR/CT | `python -m research.run_pa_minimal_opp16_archetype --symbols rb,i,ma,ta` |
| 顺宽逆严入场 | `python -m research.run_pa_minimal_trend_asym_compare --symbols rb,i,ma,ta` |
| space/R 影子 | `python -m research.run_pa_minimal_opp16_space_r --symbols rb,i,ma,ta` |

## 6. 实验日志字段

追加 `research/experiments.md` 时须含：

- 假设 ID（`EXP-NNN`）
- 相对基线 `OPP16_LONG_LAE`
- 单变量改动摘要
- ΔPnL / Sharpe / 决策（KEEP|REVERT|HOLD）

## 7. 一句话

> 拆解是为了找到下一个可证伪的单杠杆；不是为了把亏损目录修成盈利目录。

## 8. 分阶段 OPP 漏斗（整体收益）

采用「单 OPP 干净审计 → 有限机制修复 → 增量加入组合 → 组合层统一优化」：

```
Candidate → Phase A 干净审计
  ├─ REJECT → 归档，下一候选
  ├─ MARGINAL → 最多 1 次机制修复（Phase B）
  └─ SURVIVOR → 跨品种 + IS/OOS（Phase C）
       └─ 通过 → 逐个加入 OPP16 锚点（Phase D）
            └─ 边际 Δ>0 → 组合成员冻结后再做全局门/权重
```

| 阶段 | 入口 | 门禁 |
|------|------|------|
| A | `python -m research.run_pa_minimal_opp_phase_a --opp OPP06` | 明显负期望 → REJECT |
| B | 例：`run_pa_minimal_opp08_short_sym_compare` | 全窗净>0、PF≥1、≥2/4 品种非负 |
| C | IS/OOS（样本内/样本外）专用脚本 | OOS 过薄 → SHADOW |
| D | `python -m research.run_pa_minimal_opp_portfolio_fit --opp X` | 组合 ΔPnL≤0 → 移除 |

**禁止**：一次打开全部 OPP 再筛选；禁止把负期望 OPP 用全局闸门「抢救」。

注册表：`research/pa_minimal_baseline.py` 的 `OPP_FUNNEL_QUEUE` / `OPP*_DISCOVERY`。
辅助：`research/opp_phase_funnel.py`。
