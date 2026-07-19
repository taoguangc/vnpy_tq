# OI Change Sensor Experiment RFC

> **Status**: Accepted（Frozen for `OI_CHANGE_EXP001`）
> **Accepted date**: 2026-07-19
> **Experiment family**: `OI_CHANGE`
> **First run id**: `OI_CHANGE_EXP001`
> **Path**: `docs/specs/OI_CHANGE_SENSOR_EXPERIMENT_RFC.md`
> **Parent**: `FEATURE_SENSOR_SPEC.md`、`FEATURE_ROLL_ANNOTATION_POLICY_RFC.md`（Accepted）
> **Sibling（独立，禁止合并结论）**: `VOLUME_RATIO_SENSOR_EXPERIMENT_RFC.md`
> **规则优先级**: `AGENTS.md` > Parent Spec > 本 RFC > Run Spec > 代码
> **实现状态**: Volume EXP001 已闭环；`OIChangeSensor@1.0` 已实现并通过契约测试。**不授权交易**。

**一句话**：用持仓量相对变化观测后续波动；默认无 Alpha，直到 Evidence 另有结论。

**身份**：

```text
OI Change Sensor = EXPERIMENT Feature Producer
≠ Opportunity Detector
≠ 交易策略
≠ 与 Volume 实验的联合结论
```

---

## 0. 零假设

> H0：`oi_rel_change` 与未来已实现波动无统计关联。

---

## 1. 单一假设（本实验只验证这一条）

```text
H1:
  oi_rel_change 与未来 N 根 1m bar 的已实现波动存在可检出关联。

Primary Outcome:
  RV_N = std(log_return[t+1 : t+N])   # N 默认 60

Primary Metric:
  Spearman ρ(oi_rel_change_t, RV_N,t)
```

禁止同实验再测成交量、量仓组合或交易 PnL。

---

## 2. Feature 定义（建议冻结；Accept 时可改）

| 项 | 建议值 |
|----|--------|
| `sensor_id` | `oi_change` |
| `sensor_version` | `1.0` |
| 输出键 | **仅** `oi_rel_change` |
| 公式 | `(oi[t] - oi[t-1]) / oi[t-1]` |
| `oi` 来源 | bar `open_interest`（loader：`close_oi` 优先，否则 `open_oi`） |
| 冷启动 | 无前值 → `null` |
| `oi[t-1] <= 0` 或非有限 | `null` + diagnostics |
| Input | 只读 `open_interest` 序列 |

Diagnostics（最低）：

| 字段 | 含义 |
|------|------|
| `warmup_state` | `insufficient` / `ready` |
| `calculation_status` | `ok` / `nonpositive_prev_oi` / … |
| `roll_neighborhood` | `"true"` / `"false"`（政策强制） |

Sensor **不**因换月 drop 行。  
选用**相对变化**而非绝对手数差，降低合约规模尺度干扰；绝对变化若以后要测，须新 `sensor_version` / 新实验。

---

## 3. 数据与换月纪律

| 项 | 冻结建议 |
|----|----------|
| symbol / tf | `rb` / `1m` |
| 价格 | CbC **无复权**（Decision 001） |
| 区间 | `2024-01-01` … `2025-12-31` |
| 换月 | **双报** `full` + `ex_roll` |

注意：换月瞬间持仓序列可能不连续；这正是双报的原因之一，**不是**改用复权的理由。

禁止：与 `VOLUME_RATIO_*` 合并 Evidence；用 PnL 验收。

---

## 4. Scope

### In

- Hypothesis / Sensor / Artifact / Outcome / Metric / Evidence
- Contract tests

### Out

```text
交易信号 / 方向 / 仓位
volume_ratio / 量仓联合
参数搜索 / 多品种首跑结论
改写 ATR / DATA / VOLUME_RATIO 产物
Production 晋级
```

---

## 5. Closed Questions（OQ1–OQ5）

| ID | 冻结决议 | 日期 |
|----|----------|------|
| OQ1 | 使用相对变化 `oi_rel_change`，不使用绝对差 | 2026-07-19 |
| OQ2 | Outcome `N=60` | 2026-07-19 |
| OQ3 | Primary Metric = Spearman ρ | 2026-07-19 |
| OQ4 | 强制双报；主=`ex_roll`，次=`full` | 2026-07-19 |
| OQ5 | `VOLUME_RATIO_EXP001` 闭环后才实现 / 跑本实验 | 2026-07-19 |

---

## 6. Accepted Gate

OQ1–OQ5 已关闭。Decision 001 不变；不授权交易；不与 Volume 实验合并假设。

工程顺序已冻结：**实现与跑数串行**，先 Volume，后 OI。

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-19 | 0.1.0-draft | 首稿：持仓相对变化；与 Volume 分实验 |
| 2026-07-19 | 1.0.0 | Accepted：OQ1–OQ5 全按建议冻结 |
| 2026-07-19 | 1.0.1 | Volume 闭环后实现 OI Sensor；实验语义不变 |
