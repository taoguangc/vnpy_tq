# OPP16 Two-Bar Reversal Detector Experiment RFC

> **Status**: Accepted（Frozen for `OPP16_EXP001`）
> **Accepted date**: 2026-07-20
> **Experiment family**: `OPP16`
> **First run id**: `OPP16_EXP001`
> **Path**: `docs/specs/OPP16_TWO_BAR_REVERSAL_EXPERIMENT_RFC.md`
> **Parent**: `DETECTOR_FRAMEWORK_SPEC.md`、`docs/03_DETECTOR_SPEC.md`、Decision 011 / 015
> **规则优先级**: `AGENTS.md` > Parent Spec > 本 RFC > Run Spec > 代码
> **实现门禁**: Accepted 授权实现 Candidate Detector + 单测；**不授权**跑数 / 交易 / Production。跑数须按 Run Spec 另授权。

**一句话**：在 PAAF 干净架构上，第一次用可审计证据检验「两棒反转」是否具备事件后边沿；不是复刻遗留 `pa_minimal` 收益叙事。

**身份**：

```text
OPP16 Detector = Candidate Opportunity Detector（E0）
≠ Feature Sensor
≠ 交易策略 / 自动下单
≠ 继承遗留「E2 暂定」结论
≠ DEMO_MINIMAL（管线验证件）
```

---

## 0. 为何现在做这条线

| 已完成 | 含义 |
|--------|------|
| Detector Framework + Pipeline | 可挂真实 OPP |
| Feature EXP001×4 | 标量关联线边际低（Decision 016） |
| ROADMAP | 真实 OPP（如 OPP16）是下一里程碑 |

本 RFC 只立项 **一个** 形态假设。零假设默认成立，直到 `OPP16_EXP001` 产出可审计 Evidence。

---

## 1. 零假设与单一假设

```text
H0:
  在冻结协议下，OPP16 事件触发后，未来 N 根的方向边沿
  与随机/无边沿 无实质差异（不可检出）。

H1:
  OPP16 事件触发后，同向未来边沿可检出
  （达到预注册门槛）。

唯一改动变量:
  OPP16 形态定义本身（见 §2）。

禁止同实验顺带改:
  出场规则族、仓位、成本模型、Context 滤波堆叠、参数搜索、多 OPP。
```

**遗留证据不迁移**：`docs/03` 登记表中 OPP16「E2 暂定」对 PAAF 新实现无效；本路径从 **Candidate / E0** 重取证。

---

## 2. 形态定义（已冻结）

时间框架：**5m**（由冻结 1m 合成）。

### 2.1 最小机械定义

设合成 5m 上当前完成棒为 `bar`，前一根为 `prev`：

| 方向 | 条件（全部满足） |
|------|------------------|
| LONG | `prev.close < prev.open`；`prev_range = prev.high-prev.low > 0`；`abs(prev.close-prev.open)/prev_range ≥ body_ratio`；`bar.close > (prev.high+prev.low)/2` |
| SHORT | 镜像：`prev` 阳线；`body_ratio` 同；`bar.close < prev mid` |

| 项 | 冻结值 |
|----|--------|
| `detector_id` | `OPP16` |
| `detector_version` | `1.0.0` |
| `opportunity_id` | `OPP16` |
| `body_ratio` | `0.5` |
| 对称 | 多空对称（共享编号） |
| Context 门禁（EXP001） | **无** |
| PatternState | 无跨 bar 状态机（单次完成棒判定） |
| 建议结构止损参考 | LONG：`bar.low`；SHORT：`bar.high`（仅写入 DetectionResult，**不下单**） |
| entry 参考 | 信号棒 `close`（观测用） |

### 2.2 刻意不做（EXP001）

- 遗留 `two_bar_rev_context`（STRONG_BULL 等）过滤
- `PENDING_CONFIRM` / 突破挂单语义
- `opp16_strict_shape` / pin / 1h 变体
- Strategy 内 soft/hard 禁令堆叠

理由：第一刀只验证 **裸形态**；Context / 确认 / 变体各自需要独立实验。

### 2.3 输出契约

返回 `DetectionResult | None`（禁止 `bool` / 遗留 `Signal`）：

- `status = EXPERIMENT`
- `tags` 含 `REVERSAL`（及可选 `custom:two_bar`）
- `direction` / `entry` / `stop` / `reason` / `metadata`
- 不调用买卖；不读持仓

---

## 3. 实验设计（已冻结）

| 项 | 冻结值 |
|----|--------|
| Universe | `rb` / 合成 **5m** / CbC 无复权 |
| Period | `2024-01-01` … `2025-12-31` |
| N（前瞻） | `60` 根 **5m** |
| 采样 | **事件触发**（每个 DetectionResult 一条）；去重规则见 Run Spec |
| Roll | 标注 + **双报** `full` / `ex_roll`（W=60 **1m** 邻域映射到事件时刻）；主=`ex_roll` |
| 成本 | 主结论 **不含**交易成本；真实成本仅作附录敏感 |

### 3.1 Primary Outcome / Metric

```text
对每个 OPP16 事件 t（方向 d ∈ {+1,-1}）:
  SR_N(t) = sum(log_return[t+1 : t+N])   # 在 5m close 序列上
  aligned = d * SR_N(t)

Primary Metric:
  mean(aligned) 于 ex_roll 样本
  以及 95% CI（bootstrap 或等价预注册区间）

Gate:
  见 Run Spec §2.1（预注册）
```

次要（必须报告，不单独决策）：命中率 `P(aligned>0)`、样本 n、full 敏感性、roll 剔除比例。

**禁止**把回测 PnL / 年化当作本实验主指标。

---

## 4. Out of Scope

```text
交易执行 / Risk 仓位
Production / Verified 晋级
继承遗留 E2 叙事
参数网格搜索
多品种首跑（E2 另立项）
Feature↔RV 同构实验
改 Decision 001
```

---

## 5. Closed Questions（OQ1–OQ6）

| ID | 冻结决议 | 日期 |
|----|----------|------|
| OQ1 | 最小定义（§2.1）；遗留 context 过滤另实验 | 2026-07-20 |
| OQ2 | 时间框架 **5m** | 2026-07-20 |
| OQ3 | EXP001 **不加** Context=Trend 门禁 | 2026-07-20 |
| OQ4 | Primary = aligned SR 均值 + 95% CI；命中率次要 | 2026-07-20 |
| OQ5 | 主结论 **不含**交易成本；成本仅附录敏感 | 2026-07-20 |
| OQ6 | `body_ratio = 0.5` | 2026-07-20 |

---

## 6. Accepted Gate

OQ1–OQ6 已关闭。Decision 001 不变。

下一步：

1. 实现 `OPP16Detector@1.0.0`（Candidate / E0）+ 单测（确定性、镜像、边界）；
2. Run Spec `OPP16_EXP001` 已同步 Accepted；
3. **仍不**自动跑数；须另授权；
4. 不得注册进默认生产臂。

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-20 | 0.1.0-draft | 首稿：PAAF 首个真实 OPP Candidate 实验线 |
| 2026-07-20 | 1.0.0 | Accepted：OQ1–OQ6 全按建议冻结 |
