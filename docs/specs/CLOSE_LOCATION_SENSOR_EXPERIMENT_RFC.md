# Close Location Sensor Experiment RFC

> **Status**: Accepted（Frozen for `CLOSE_LOCATION_EXP001`）
> **Accepted date**: 2026-07-19
> **Experiment family**: `CLOSE_LOCATION`
> **First run id**: `CLOSE_LOCATION_EXP001`
> **Path**: `docs/specs/CLOSE_LOCATION_SENSOR_EXPERIMENT_RFC.md`
> **Parent**: `FEATURE_SENSOR_SPEC.md`、`FEATURE_ROLL_ANNOTATION_POLICY_RFC.md`、Decision 016
> **规则优先级**: `AGENTS.md` > Parent Spec > 本 RFC > Run Spec > 代码
> **实现门禁**: Accepted 授权后续实现 EXPERIMENT Sensor；**不授权跑数 / 交易**。跑数须按 Run Spec 另授权。

**一句话**：测 bar 内收盘位置是否与后续短窗 **signed** 收益有关；不是买卖信号。

**身份**：

```text
Close Location Sensor = EXPERIMENT Feature Producer
≠ Opportunity Detector
≠ 交易策略
≠ Volume/OI/ATR ↔ RV_60 同构实验
```

---

## 0. 为何合规（Decision 016）

Decision 016 禁止在 `rb` 上新开「单标量 Feature → Spearman(RV_60)」同构实验。  
本实验满足条件 3（结构特征）且 Outcome **不是** RV_60：

| 项 | 冻结 |
|----|------|
| Feature | `close_location = (close-low)/(high-low)` |
| Outcome | 未来 N 根 **signed** log-return 之和（方向延续） |
| Metric | Spearman ρ |
| Roll | 强制双报 `full` + `ex_roll` |

---

## 1. 零假设与单一假设

```text
H0:
  close_location 与未来 N 根 signed log-return 无统计关联。

H1:
  close_location 与未来 N 根 signed log-return 存在可检出关联。

Primary Outcome:
  SR_N = sum(log_return[t+1 : t+N])

Primary Metric:
  Spearman ρ(close_location_t, SR_N,t)
```

禁止同实验再测 RV、成交量、持仓或交易 PnL。

---

## 2. Feature 定义（已冻结）

| 项 | 冻结值 |
|----|--------|
| `sensor_id` | `close_location` |
| `sensor_version` | `1.0` |
| 输出键 | **仅** `close_location` |
| 公式 | `(close[t]-low[t]) / (high[t]-low[t])` |
| `high == low` | `null` + diagnostics |
| 冷启动 | 无完整 OHLC → `null` |
| Input | 只读 `high` / `low` / `close` |

Diagnostics（最低）：

| 字段 | 含义 |
|------|------|
| `warmup_state` | `insufficient` / `ready` |
| `calculation_status` | `ok` / `zero_range` / … |
| `roll_neighborhood` | `"true"` / `"false"` |

Sensor **不**因换月 drop 行。

---

## 3. 数据与换月纪律

| 项 | 冻结值 |
|----|--------|
| symbol / tf | `rb` / `1m` |
| 价格 | CbC **无复权**（Decision 001） |
| 区间 | `2024-01-01` … `2025-12-31` |
| N | `60` |
| sampling | 非重叠 `60` |
| Roll W | `60` |
| 主结论样本 | 主=`ex_roll`，次=`full`（必须双报） |

---

## 4. Evidence Gates（跑数前冻结；与 Volume/OI 同尺）

`association_detected` 当且仅当：

1. `ex_roll` 的 `|ρ| >= 0.10`
2. `ex_roll` 的 95% CI 不跨 0
3. `full` 与 `ex_roll` 的 ρ 同号
4. `|ρ_full - ρ_ex_roll| <= 0.05`

否则 `inconclusive`；治理 **HOLD**；不晋级；不声明普遍无关联。

---

## 5. Closed Questions（CQ1–CQ4）

| ID | 冻结决议 | 日期 |
|----|----------|------|
| CQ1 | Outcome = **signed** log-return 之和（非 abs / 非 RV） | 2026-07-19 |
| CQ2 | `N=60` | 2026-07-19 |
| CQ3 | 首跑 `rb` 单品种 | 2026-07-19 |
| CQ4 | 强制双报；主=`ex_roll`，次=`full` | 2026-07-19 |

---

## 6. Out of Scope

```text
交易信号 / 方向下单 / 仓位
RV_60 / volume_ratio / oi_rel_change
参数搜索 / 多品种首跑结论
改 Decision 001
改写 ATR / Volume / OI / DATA 产物
Production 晋级
```

---

## 7. Accepted Gate

CQ1–CQ4 已关闭。Decision 001 不变；不授权交易。

下一步：实现 Sensor + 单测 → 另授权 `CLOSE_LOCATION_EXP001` 跑数。

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-19 | 0.1.0-draft | 首稿：Decision 016 条件 3 候选 |
| 2026-07-19 | 1.0.0 | Accepted：CQ1–CQ4 全按建议冻结 |
