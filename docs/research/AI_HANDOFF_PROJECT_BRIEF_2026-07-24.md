# PAAF / vnpy_tq — AI 交接简报（2026-07-24）

> **用途**：把本仓库当前状态喂给其他 AI / 新会话。先读本文件，再按「必读顺序」下钻。  
> **类型**：交接简报（≠ 授权回测 · ≠ 授权 Commit · ≠ 重开战役）  
> **仓库**：`C:\projects\vnpy_tq` · 分支：`feature/detector-framework`  
> **最高契约**：根目录 `AGENTS.md`（v3）· 冲突时 `AGENTS.md` > 本简报 > 聊天话术

---

## 1. 项目是什么 / 不是什么

| 是 | 不是 |
|----|------|
| **PAAF**（Price Action Alpha Framework，价格行为 Alpha 框架）= **研究平台** | Brooks 书的软件复刻 |
| 每个检测器 / 策略资产 = **可证伪假设** | 已证实的交易圣杯 |
| 证据驱动晋级 | 叙事驱动上线 / 为年化调参 |

**一句话使命**：在中国商品期货上，用接近实盘的数据，寻找具有统计显著性的价格行为 Alpha（可交易优势）。默认零假设：**无 Alpha**，直到证据晋级。

**不追逐利润**：禁止以提高回测收益为优化目标。只优化研究质量、可解释性、可复现性、统计有效性、生产真实性。

---

## 2. 硬约束（其他 AI 不得违反）

### 2.1 数据冻结（正式研究）

- 天勤 TQSDK **离线**
- **1 分钟** K 线
- **自动换月（CbC）**
- **无复权**
- **真实手续费 + 真实滑点**

偏离须用户明确批准，并标为独立数据实验。

### 2.2 运行分层

```text
行情 → 情境(Context) → 检测器注册表(Detector Registry) → 风控 → 执行 → 日志
```

- **检测器**：纯计算；只返回信号或空；不下单、不读持仓、不改策略。
- **情境 0.1**：只发布 **未知 / 趋势 / 区间**；不产生交易。压缩等是待验证假设。
- **策略**：只编排，不写形态定义。
- **周期默认**：**信号 = 5 分钟合成 K**；**风控 = 1 分钟**。个别机会点可声明 15m/60m。

### 2.3 回测与 Git

- **须用户明确说跑回测才执行**；探索/调参配额见 `AGENTS.md`。
- **无 CSV / 等价审计输出 → 不得称已证实 / 不得为此求 Commit**。
- **未经用户明确要求：不 Commit、不 Push**。
- Closed 实验不可变；行为变化须新 `experiment_id` / 新版本（Decision 017）。

### 2.4 研究顺序（Decision 017 摘要）

Evidence Platform → Validation Protocol → 其后才是 Market State / Opportunity 扩张。  
负证据一等公民。无单独立项时，勿把「再开一堆 OPP」当默认进度。

---

## 3. 当前态势（截至 2026-07-24）

### 3.1 策略资产战役队列

```text
姿态：LEAVE_SHELF_EXHAUSTED（货架耗尽、先离开）· standing
战役编号 CID_003–014：全部 PAUSED · Alpha = NONE
CID_015：未开设
裸「授权你决定N次」：只再确认 Leave，≠ 重开战役 / ≠ 选菜单
```

指针：`docs/campaigns/README.md`  
姿态：`docs/research/STRATEGY_POSTURE_LEAVE_SHELF_EXHAUSTED.md`

### 3.2 种子货架诚实账

| 来源 | 状态 |
|------|------|
| `e2bfc0c…/strategies/pa_cta/opp/*` 优先 PA 种子 | 已消耗（约 CID_003–012） |
| SAFIP I008 `smc_orderflow_vwap` 单轴 | OB（CID_013）+ Z-score（CID_014）已测完 · Alpha NONE |
| I008 Setup C / Setup A / 全混合 | 多轴或多假设 · **不作薄 NSAD** |
| `pa_minimal` | 与 opp/ 同源 bundle · 不优先整包恢复 |

### 3.3 战役一览（CID_003–014）

| CID | 资产 | 一句话 |
|-----|------|--------|
| 003 | `STRAT_REV_OPP16_01` | OPP16 反转 |
| 004 | `STRAT_REV_OPP12_01` | OPP12 |
| 005 | `STRAT_REV_OPP17_01` | OPP17 |
| 006 | `STRAT_TREND_OPP08_01` | OPP08 趋势 |
| 007 | `STRAT_SESS_OPP19_01` | OPP19 开盘突破 |
| 008 | `STRAT_TREND_OPP02_01` | OPP02 |
| 009 | `STRAT_REV_OPP15_01` | OPP15 |
| 010 | `STRAT_REV_OPP13_01` | OPP13 单触 |
| 011 | `STRAT_SESS_OPP19_REV_01` | OPP19 反转版（≠007） |
| 012 | `STRAT_REV_OPP13_DT_01` | OPP13 双顶残差（≠010） |
| 013 | `STRAT_SMC_OB_LONG_01` | SMC 订单块多头 |
| 014 | `STRAT_SMC_ZSCORE_LONG_01` | VWAP Z-score 超跌多 |

典型模式（尤其 011/013/014）：**H_MECH KEEP + H_EDGE REVERT → Alpha NONE**。

### 3.4 旁路进行中（≠ 重开 Leave）

情境过滤草案（待用户钉死 Q1–Q4）：

- 文件：`docs/research/STRATEGY_CONTEXT_FILTER_SPEC_HTF_MA20_LONG_DRAFT.md`
- 规格号：`CFS_HTF_BIAS_MA20_LONG_V0_1`
- 内容：大周期偏多 + 站上均线 20（做多侧）· **只定义背景怎么算**
- **未授权**：写代码、回测、绑旧 CID 救边、改情境一级枚举

### 3.5 平台 / 纪元（勿与 CID_003–014 混谈）

- Epoch 4：CAP-CTX 等能力研究有独立闭环文档（见 `docs/releases/`）。
- Epoch 5：策略研究阶段定位 / 契约冻结（SAC / SEVF / SAFIP）——见 `docs/releases/EPOCH_5_*`。
- 契约：`SAC-v1` · `SEVF-v1` · `SAFIP-v1` 已冻结设计。

---

## 4. 双表面与「有没有 Alpha」怎么判

### 4.1 两层假设（禁止塌缩）

| 层 | 英文 | 问什么 | KEEP 意味 |
|----|------|--------|-----------|
| 机制 | **H_MECH** | 形态路径是否存在、可审计 | 机制观察保留 · **≠ Alpha** |
| 交易边 | **H_EDGE** | 真实成本下是否有统计净期望 | 才接近「像不像边」 |

评价语义（SEVF-v1）：**KEEP / HOLD / REVERT**。  
KEEP ≠ Alpha proven ≠ Bindable ≠ Production。

### 4.2 近期 H_EDGE 常用预注册门槛（CID 战役）

```text
ABORT：source_hash / parameter_hash 不匹配
HOLD ：n_gate < 50
KEEP ：n≥50 且 median_mfe>median_mae 且 share≥0.55
       且 mean_net>0 且 p_one_sided_gt0<0.05
REVERT：n≥50 但 KEEP 条件未全过
```

诊断年 + 样本外年；无审计输出不得当证据。  
**禁止**单独用总盈亏 / 年化 / 夏普当 KEEP 理由。

### 4.3 Alpha 梯子

```text
无 Alpha（默认）
  → H_MECH KEEP？
  → H_EDGE KEEP？（常要诊断 + OOS）
  → 更高栏（多周期/多品种/成本/指纹/可解释/负证据保留）
  → Alpha Candidate 请愿（仍 ≠ Verified）
  → Alpha Verified → Bindable / Production（Production 须用户确认 + E4）
```

**现行事实**：CID_003–014 在 AERC 下均为 **Alpha NONE**（无 H_EDGE KEEP，或未达 Candidate 栏）。

### 4.4 用户已提出的改进方向（条件优势）

「优势要配背景（如大周期看多、站上 MA20）才可能体现」  
→ 正确建模为 **条件假设 / 情境过滤假设（H_CTX_FILTER）**，  
→ **不是**在 Closed `experiment_id` 上加过滤救边，  
→ **不是**把过滤本身叫 Alpha。  
草案已写，待确认甲/乙方案后才能实现标签计算器。

---

## 5. 其他 AI 接手前的必读顺序

| 顺序 | 路径 | 何时 |
|------|------|------|
| 0 | 本简报 | 每轮 |
| 1 | `AGENTS.md` | 每轮 |
| 2 | `docs/campaigns/README.md` | 战役状态 |
| 3 | `PAAF_PROJECT_SPEC.md` | 改方向 / 架构 |
| 4 | `docs/01`–`07` | 按任务选读 |
| 5 | `DECISIONS.md`（017/018/019） | 研究顺序 / 契约 / 情境消费边界 |
| 6 | `docs/specs/CONTEXT_ENGINE_SPEC.md` | 改情境 |
| 7 | 对应 `STRATEGY_*_CID_0XX*` | 动某场战役时 |

技能（冲突时规范优先）：

- `.claude/skills/vnpy-cta-backtest`
- `.claude/skills/vnpy-quant-python`
- `.claude/skills/quant-backtest-validation-tool`

---

## 6. 禁止清单（喂给 AI 的红线）

```text
❌ 聊天发明 Morphology Spec / 无 git 种子硬开 NSAD
❌ 复活 Closed 实验编号；同 id 下改参重跑粉饰
❌ H_MECH KEEP 写成「有 Alpha」
❌ 无用户授权跑回测 / 网格搜索冲年化
❌ 无用户要求 git commit / push
❌ 检测器下单或藏全局状态
❌ 用未来函数；用未收盘棒「提前」站上均线
❌ 裸「授权你决定」在 Leave standing 下解读为重开 CID_015
❌ 把情境过滤草案当成已冻结实现授权
```

---

## 7. 在现状上如何改进（建议路线图）

> 原则：**先提高研究分辨率，再开新资产战役。** 与 Leave 姿态兼容。

### P0 — 钉死情境过滤规格（低成本、高杠杆）

1. 用户确认草案 Q1–Q4（甲-1/2/3 · 乙-松/严 · 均线周期 · 下一步）。  
2. 将草案升为 **FROZEN 规格**（仍无回测）。  
3. 实现 **只读标签计算器 + 单测 + 审计 CSV**（无下单）。  
4. 单独做「标签无未来函数 / 可复现」证据——这是 **H_CTX_FILTER 机制**，不是 Alpha。

### P1 — 条件交易边实验（新实验编号）

5. 另授后：选 **一个** 已冻结资产（建议优先机制 KEEP 过、边 REVERT 的，如 CID_014 或 CID_013 表面），  
   预注册「无过滤 vs 仅背景为真」或「仅在背景内评估 H_EDGE」。  
6. 门槛仍用 SEVF；结论分开写：过滤有效性 ≠ 优势候选。  
7. **禁止**改旧 Closed id；必须新 `experiment_id`。

### P2 — 平台与文档卫生（提升可交接性）

8. 保持 `docs/campaigns/README.md` 为唯一战役指针；避免再堆积无指针的 Delegation 长文。  
9. 证据产物路径约定：`research/output/evidence/<EXP_ID>/`（常 gitignore；文档写清本地存在）。  
10. 新会话强制：先读本简报 + campaigns 指针，再动手。

### P3 — 何时才重开策略 NSAD

仅当出现其一：

- 用户明确唤醒（Setup C 多轴 / pa_minimal 单 OPP 抽取 / Resume scoped）；或  
- 情境过滤标签已有审计证据，且要开 **新** 条件资产设计；或  
- 新的可回收种子进入 inventory（非聊天发明）。

### 明确不优先

- 再扫一遍已 Alpha NONE 的 opp/ 形态「换参数碰运气」。  
- 无规格的「再加几个均线过滤看看」。  
- 把 Leave 当成失败；Leave 是复杂度预算下的正确停止。

---

## 8. 唤醒句模板（用户侧）

| 意图 | 示例唤醒 |
|------|----------|
| 确认过滤规格 | `确认情境过滤规格：甲-1，乙-松，均线在5分钟，仅冻结` |
| 实现标签（不回测） | `授权实现 CFS_HTF_BIAS_MA20_LONG 只读标签 + 单测` |
| 条件边实验 | `授权绑定 CID_014 新实验评估 MA20 过滤下的 H_EDGE` |
| 重开策略设计 | `Authorize NSAD Setup C (explicit multi-axis)` |
| 恢复某战役 | `Resume CID_0XX (scoped)` + 写清 power |
| 跑回测 | 明确说「跑回测」+ 范围 |

---

## 9. 工作树快照（写简报时）

```text
分支：feature/detector-framework
近期：Leave standing 系列文档已提交
可能未提交（以 git status 为准）：
  - docs/research/STRATEGY_CONTEXT_FILTER_SPEC_HTF_MA20_LONG_DRAFT.md
  - docs/campaigns/README.md / docs/README.md 指针改动
  - ?? .agents/skills/vnpy-multi-symbol/（通常勿当研究交付物提交）
```

其他 AI 开工前请再跑：`git status` · `git log -5 --oneline`。

---

## 10. 一句话交给下一任 AI

```text
PAAF 是证据驱动的期货价格行为研究平台，不是策略集合。
CID_003–014 已全部 Alpha NONE 并 Pause；现行 Leave standing。
下一步高价值工作是钉死并验证「大周期偏多 + 站上均线20」情境过滤标签，
用新实验编号做条件边，而不是救 Closed 实验或裸授权开 CID_015。
默认无 Alpha；H_MECH KEEP ≠ Alpha；无用户授权不回测、不 Commit。
```

## 修订记录

| 日期 | 变更 |
|------|------|
| 2026-07-24 | 初版交接简报 · 含 Leave 态势与情境过滤改进路线 |
