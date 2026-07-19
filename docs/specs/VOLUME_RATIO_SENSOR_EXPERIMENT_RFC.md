# Volume Ratio Sensor Experiment RFC

> **Status**: Accepted（Frozen for `VOLUME_RATIO_EXP001`）
> **Accepted date**: 2026-07-19
> **Experiment family**: `VOLUME_RATIO`
> **First run id**: `VOLUME_RATIO_EXP001`
> **Path**: `docs/specs/VOLUME_RATIO_SENSOR_EXPERIMENT_RFC.md`
> **Parent**: `FEATURE_SENSOR_SPEC.md`、`FEATURE_ROLL_ANNOTATION_POLICY_RFC.md`（Accepted）
> **Sibling（独立，禁止合并结论）**: `OI_CHANGE_SENSOR_EXPERIMENT_RFC.md`
> **规则优先级**: `AGENTS.md` > Parent Spec > 本 RFC > Run Spec > 代码
> **实现门禁**: Accepted 授权后续实现 EXPERIMENT Sensor；**不授权跑数 / 交易**。跑数须按 Run Spec 另授权。

**一句话**：用相对成交量观测后续波动；默认无 Alpha，直到 Evidence 另有结论。

**身份**：

```text
Volume Ratio Sensor = EXPERIMENT Feature Producer
≠ Opportunity Detector
≠ 交易策略
≠ 与 OI 实验的联合结论
```

---

## 0. 零假设

> H0：`volume_ratio` 与未来已实现波动无统计关联。

目的是产出可审计证据，不是证明「放量有效」。

---

## 1. 单一假设（本实验只验证这一条）

```text
H1:
  volume_ratio 与未来 N 根 1m bar 的已实现波动存在可检出关联。

Primary Outcome:
  RV_N = std(log_return[t+1 : t+N])   # N 默认 60

Primary Metric:
  Spearman ρ(volume_ratio_t, RV_N,t)   # 预注册；禁止事后换指标
```

禁止同实验再测持仓量、量仓组合或交易 PnL。

---

## 2. Feature 定义（建议冻结；Accept 时可改）

| 项 | 建议值 |
|----|--------|
| `sensor_id` | `volume_ratio` |
| `sensor_version` | `1.0` |
| 输出键 | **仅** `volume_ratio` |
| 公式 | `volume[t] / mean(volume[t-W+1 : t+1])` |
| `W`（baseline_window） | **100** |
| 冷启动 | bars < W → `volume_ratio=null`，仍 emit |
| 分母为 0 | `null` + diagnostics |
| Input | 只读 `volume` 序列；可选透传价格供 Outcome，不进 values |

Diagnostics（最低）：

| 字段 | 含义 |
|------|------|
| `baseline_window` | W |
| `warmup_state` | `insufficient` / `ready` |
| `roll_neighborhood` | `"true"` / `"false"`（政策强制） |

Sensor **不**因换月 drop 行。

---

## 3. 数据与换月纪律

| 项 | 冻结建议 |
|----|----------|
| symbol / tf | `rb` / `1m` |
| 价格 | CbC **无复权**（Decision 001） |
| 区间 | `2024-01-01` … `2025-12-31`（与 ATR/DATA 对齐） |
| 换月 | 遵守 `FEATURE_ROLL_ANNOTATION_POLICY`：**双报** `full` + `ex_roll` |

禁止：复权替换基线；用 PnL 验收；与 `OI_CHANGE_*` 合并成一条 Evidence。

---

## 4. Scope

### In

- Hypothesis / Sensor / Artifact / Outcome / Metric / Evidence 链路
- Contract tests（确定性、无交易语义、换月标注字段）

### Out

```text
交易信号 / 方向 / 仓位
OI / 量仓联合特征
参数搜索 / 多品种首跑结论
改写 ATR / DATA EXP001
Production 晋级
```

---

## 5. Closed Questions（VQ1–VQ5）

| ID | 冻结决议 | 日期 |
|----|----------|------|
| VQ1 | `W=100` | 2026-07-19 |
| VQ2 | Outcome `N=60`（对齐 ATR） | 2026-07-19 |
| VQ3 | Primary Metric = Spearman ρ | 2026-07-19 |
| VQ4 | 强制双报；主=`ex_roll`，次=`full` | 2026-07-19 |
| VQ5 | 先 A 后 B；串行，禁止混读结论 | 2026-07-19 |

---

## 6. Accepted Gate

VQ1–VQ5 已关闭。Decision 001 不变；不授权交易；不与 OI 实验合并假设。

下一步：实现 Sensor + 单测 → 另授权 `VOLUME_RATIO_EXP001` 跑数。

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-19 | 0.1.0-draft | 首稿：成交量相对活跃度；与 OI 分实验 |
| 2026-07-19 | 1.0.0 | Accepted：VQ1–VQ5 全按建议冻结 |
