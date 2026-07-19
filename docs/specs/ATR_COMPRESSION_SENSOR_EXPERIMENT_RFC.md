# ATR Compression Sensor Experiment RFC（Phase 3.1）

> **Status**: Accepted（Frozen for Phase 3.1 ATR Compression EXPERIMENT Sensor）
> **Accepted date**: 2026-07-19
> **Target version**: PAAF v0.3.x Phase 3.1
> **Path**: `docs/specs/ATR_COMPRESSION_SENSOR_EXPERIMENT_RFC.md`
> **Parent Spec**: `FEATURE_SENSOR_SPEC.md`（Accepted）、`EVIDENCE_ENGINE_SPEC.md`（Accepted）
> **Impl 依赖**: Feature Sensor Framework Phase 3.0（Accepted / Implemented）、Evidence + Workflow + Evaluation（Implemented）
> **规则优先级**: `AGENTS.md` > Parent Spec > 本 RFC > 代码
> **实现门禁**: 本 RFC **已 Accepted**，授权实现 ATR 为 EXPERIMENT Feature Sensor；**仍禁止**交易信号 / 方向 / Opportunity Detector / Production 晋级 / 参数搜索。

本文件是 PAAF **第一次受控 Alpha 实验**的登记，而非 Alpha 上线。它把「ATR 压缩」从 AFF 阶段的直觉，重新定位为一个必须走完 Evidence Gate 的**研究假设**。

**一句话**：ATR Compression 是一个 `EXPERIMENT` Feature Sensor，v1 只产出 `atr_ratio` 观测，供 Evaluation / Evidence 验证是否具备预测价值；在证据晋级前，它不是 Alpha、不是 Detector、不下单。

**身份冻结**：

```text
ATR Compression Sensor
=
Experiment Feature Producer
≠
Alpha Strategy
≠
Opportunity Detector
```

---

## 0. 零假设（Null Hypothesis）

> 默认：`atr_ratio` 对未来已实现波动**无预测价值**（H0）。

本实验的目的**不是**证明 ATR 压缩有效，而是产出可审计证据，让数据决定接受或拒绝 H0。发现收益变高不构成继续调参的理由（见 `AGENTS.md` §2 不追逐利润）。

---

## 1. Objective

Phase 3.0 已交付框架：

```text
Market Data → Feature Sensor → FeatureResult → Feature Artifact
                                                     ↓
                              Experiment / Evaluation / Evidence / Replay
```

Phase 3.1 交付**第一个真实 Sensor 实验**：

```text
ATRCompressionSensor (EXPERIMENT)
    ↓
FeatureResult{ atr_ratio }
    ↓
Feature Artifact（append-only）
    ↓
OutcomeDefinition（未来 N-bar realized volatility）
    ↓
EvaluationResult（预注册 Primary Metric）
    ↓
EvidenceRecord（接受 / 拒绝 H0）
```

成功标准（**过程**成功，非收益成功）：

1. ATR Sensor 是纯函数 Feature Sensor，`FeatureResult` 无任何交易语义。
2. 假设、Outcome、Metric 在**观测前**登记（预注册），杜绝事后择优。
3. 完整链路可 Replay：sensor_version + parameter_fingerprint + code_revision + data_fingerprint + environment_fingerprint。
4. 产出 EvidenceRecord，明确写「接受 / 拒绝 / 未证实」，不得只写「有效」。
5. 包内**不出现**交易信号、breakout、仓位、方向、strategy 权重。

---

## 2. Scope

### 2.1 In Scope

| 组件 | 职责 |
|------|------|
| ATR Compression **Hypothesis 登记** | 写入本 RFC + Experiment Manifest |
| Input Contract | 只读行情窗口（OHLC）→ Sensor 输入 schema |
| `ATRCompressionSensor` | 纯计算，产 `FeatureResult`（EXPERIMENT） |
| FeatureResult schema | **v1 仅** `atr_ratio` + diagnostics；`compression_score` 延后 |
| Experiment Manifest 绑定 | parameters / fingerprint / artifact_refs |
| Outcome Definition | 未来 N-bar realized volatility（非交易 PnL） |
| Evaluation linkage | 预注册 Primary Metric → EvaluationResult |
| Evidence generation | EvidenceRecord 引用 artifact + evaluation |
| Contract tests | 确定性、无交易语义、round-trip |

### 2.2 Out of Scope（本 RFC 明确禁止）

```text
Trading signal / direction / BUY / SELL / LONG / SHORT
Breakout execution / breakout_probability
Strategy weighting / position sizing
ATRCompressionDetector（Opportunity 路径）
Production promotion / 自动上线
参数搜索 / grid 扫描 / 为凑指标连跑
多品种批量结论（首版单品种 E1）
compression_score 定义与实现（延后独立 RFC）
```

---

## 3. Hypothesis Registration

登记的**单一**假设（一个实验只验证一个假设）：

```text
Hypothesis (H1):
  atr_ratio 与未来 N 根 bar 的已实现波动（realized volatility）
  存在统计上可检出的关联（相对 H0 无关联）。

Null (H0):
  atr_ratio 与未来已实现波动无统计关联。

Primary Outcome:
  RV_N = std(log_return[t+1 : t+N])

Primary Metric:
  Spearman correlation(atr_ratio, future_RV_N)

Secondary Analysis（允许，不得事后择优为结论）:
  分桶 low / medium / high atr_ratio → 比较 mean future RV
  必须标注 secondary；禁止实验后选择最好桶作为结论。

Scope:
  单品种 rb、时间框架 1m、冻结数据基线（§4）。E1 级别。
```

**关键约束**：这是关于「atr_ratio → 未来波动」的**观测关联**假设，**不是**「压缩 → 突破方向 → 买入」的交易假设。方向与执行属于未来 Opportunity 路径，需另开 RFC。

---

## 4. Experiment Universe & Data Baseline（冻结）

### 4.1 Universe（AQ1 Accepted）

| 项 | 冻结值 |
|----|--------|
| symbol | `rb` |
| timeframe | `1m` |

未来扩展（`i` / `jm` / `HC` 等）必须作为**新的 Experiment Run**，不得修改本实验身份。

### 4.2 Data Baseline

严格沿用 `docs/07_DATA_SPEC.md`：

| 项 | 值 |
|----|-----|
| Source | 天勤 TQSDK Offline |
| Bar | 1 Minute |
| Continuous | CbC 自动换月 |
| Price | 无复权 |
| Cost | 真实手续费 + 滑点（本实验为 Feature 观测，不涉及成交，但数据流保持一致） |

**data_fingerprint** 进入 Experiment Manifest，保证 Replay。

---

## 5. Input Contract

Sensor 输入沿用 Phase 3.0 契约：`observe(*, symbol, timeframe, timestamp, window, context=None, parameters=None)`。

```text
window: Mapping[str, Any]
  预期包含只读 OHLC 序列（如 high[], low[], close[]），
  长度 ≥ baseline_window + atr_period。
```

约束：

- Sensor **不**访问持仓 / 订单 / Repository / 未来 bar。
- 窗口不足 → always-emit（§6.2 AQ4）；不返回 None。
- Sensor **不**过滤换月 bar（§6.3 AQ5）；只标注。
- 数据源适配（vn.py BarData / parquet）不在本 RFC，使用 fixture / loader 提供 `window`。

---

## 6. FeatureResult Schema

### 6.1 v1 Output（AQ2 Accepted）

**只输出 `atr_ratio`。`compression_score` 延后。**

```text
Phase 3.1 ATR Sensor v1 output:
  atr_ratio only
  compression_score = reserved / deferred（独立后续 RFC）
```

定义：

```text
atr_ratio =
  ATR(atr_period)
  /
  rolling_mean(ATR(atr_period), baseline_window)
```

默认参数（实验配置，非 sensor_version）：

```yaml
parameters:
  atr_period: 14
  baseline_window: 100
```

示例（ready）：

```python
FeatureResult(
    sensor_id="atr_compression",
    sensor_version="1.0",
    symbol="rb888",
    timeframe="1m",
    timestamp=...,
    values={
        "atr_ratio": 0.62,
    },
    diagnostics={
        "atr_period": "14",
        "baseline_window": "100",
        "warmup_state": "ready",
        "rollover_flag": "false",
    },
)
```

**禁止**在 v1 FeatureResult 中实现或填充 `compression_score`（二次映射引入 threshold / normalization / nonlinear transform，会增加研究自由度）。

### 6.2 Warmup（AQ4 Accepted）

Always-emit；**不得**用 `0.0` 表示缺失（0 是有效 atr_ratio）。

不足窗口时：

```json
{
  "atr_ratio": null,
  "diagnostics": {
    "warmup_state": "insufficient"
  }
}
```

实现注记：Phase 3.0 `FeatureResult.values` 当前为 `Mapping[str, float]`。Phase 3.1 实现允许最小契约扩展为 `Mapping[str, float | None]`，JSON round-trip 使用 `null`；不得引入 NaN/Inf。

### 6.3 Rollover（AQ5 Accepted）

```json
diagnostics: {
  "rollover_flag": "true"
}
```

- Sensor **产出事实**，不在 Sensor 内 drop bar。
- 过滤属于 Dataset preparation / Outcome construction / Evaluation 层。

### 6.4 Forbidden Keys

**禁止**（出现即契约失败）：

```text
direction / action / side / signal / buy / sell / long / short
weight / position_size / breakout_weight / breakout_probability
experiment_id / run_id / parameter_set / git_hash / dataset_hash
evidence_metric / p_value / sharpe / ic / decision
compression_score   # v1 显式延后，不得提前填入
```

- `symbol` / `timeframe` 为一等身份字段，不得放进 diagnostics。
- `parameter_fingerprint` 不进 FeatureResult。
- 预测指标属于 Evaluation/Evidence，**不回写** FeatureResult。

---

## 7. Sensor Versioning & Parameters

```yaml
sensor:
  id: atr_compression
  version: 1.0          # 算法身份：atr_ratio = ATR / rolling_mean(ATR)
parameters:
  atr_period: 14
  baseline_window: 100
```

- 改 `atr_period` / `baseline_window` → 新实验，**不**升级 sensor_version。
- 改 ATR 定义（例如改用不同 TR 公式）→ 升级 sensor_version。
- 引入 `compression_score` → 新 RFC + 新 sensor_version（或新字段 schema），不得原地塞进 v1。
- 首版状态固定 `EXPERIMENT`；无 Evidence 不得 CANDIDATE/PRODUCTION。

---

## 8. Outcome & Evaluation（AQ3 + AQ6 Accepted）

### 8.1 Primary Outcome（预注册）

```text
RV_N = std(log_return[t+1 : t+N])
N = 60 bars   # 冻结
```

### 8.2 Primary Metric（预注册）

```text
Spearman correlation(atr_ratio, future_RV_N)
```

避免假设线性关系。

### 8.3 Sampling Rule（AQ6 冻结 — 可信 Evidence 优先）

两层分离：

| 层 | 规则 |
|----|------|
| Feature Observation | **every bar**（Sensor 每根产出 FeatureResult） |
| Outcome Sampling | **non-overlapping**：`sampling_interval = N = 60` bars |

即评估样本点间隔 60 根 1m bar，避免重叠窗口导致有效样本量高估。

Phase 3.1 目标不是最大化样本量，而是**可信 Evidence**。

### 8.4 Secondary Analysis

允许分桶比较 mean future RV，必须标注 `secondary`；禁止实验后选择最好桶作为结论。

### 8.5 Linkage

```text
ExperimentContext(sensor_id="atr_compression", parameters=...)
    → SensorRegistry.create(...)
    → observe(...) over 冻结数据 → FeatureResult 序列（每 bar）
    → write_feature_artifact(...) → ArtifactReference
    → build_manifest(...) → persist_manifest
    → OutcomeDefinition(RV_N, N=60)
    → MetricDefinition(Spearman)
    → EvaluationResult（non-overlapping samples）
    → EvidenceRecord（accept_h1 / reject_h1 / inconclusive）
```

规则：

- Outcome / Metric 必须在 Evaluation **之前**登记，禁止事后择优。
- EvidenceRecord `conclusion` 用中性措辞，不得写「有效 Alpha」。
- Manifest 先持久化再建 Evidence。

---

## 9. Implementation Boundary（AQ7 Accepted）

- Sensor 实现层允许使用 `numpy` / `talib` 计算 ATR。
- `FeatureResult.values` **仅**标量 `float | None`；禁止泄漏 ndarray / Series / Bar 对象。
- 无交易语义、无 Strategy 耦合。

---

## 10. Test Contract

`tests/test_paaf_atr_compression_sensor.py`（及必要 fixture）：

1. 确定性：同输入窗口 + 同参数 → 同 `atr_ratio`。
2. 无交易语义：`FeatureResult.to_dict()` 不含禁止键；无 `compression_score`。
3. warmup：窗口不足 → `atr_ratio is None` + `warmup_state=insufficient`；always-emit。
4. 参数变化改结果但不改 sensor_version。
5. round-trip：含 `null` atr_ratio 的 JSON 序列化/反序列化一致。
6. 边界：常数序列 / 零波动窗口不产 NaN/Inf（明确处理）。
7. 无 numpy/vnpy 对象泄漏进 `to_dict`。
8. Evaluation sampling：non-overlapping 间距 = 60（wiring 测试）。

**禁止**：收益断言；用回测 PnL 做验收；把「指标好看」当测试通过条件。

---

## 11. Backtest / Compute Budget

- 本 RFC Accepted **不**等于授权跑数据。首次运行需用户单独明确「跑实验」指令。
- 首次为**单品种 rb、1m、单参数**观测运行（探索类，配额 ≤3，完整四段复盘）。
- 禁止顺带参数搜索 / grid / 连跑到指标达标。
- 无 CSV / Artifact 等价审计输出 → 不得称结论已证实、不得请求 Commit。

---

## 12. Commit Boundary

| Commit | Message | 内容 |
|--------|---------|------|
| 1 | `docs(paaf): add atr compression sensor experiment rfc` | Draft 文件 + 索引 |
| 2 | `docs(paaf): accept atr compression sensor experiment rfc` | AQ 关闭 + 状态 Accepted（本步） |
| 3 | `feat(paaf): add atr compression feature sensor` | Sensor + descriptor + optional null values + tests（**无交易**） |
| 4 | `feat(paaf): add atr compression experiment wiring` | Outcome/Metric 预注册 + non-overlapping Evaluation/Evidence 挂接 + tests |

运行数据、生成 Evidence 属独立步骤，需用户指令后进行。

---

## 13. Open Questions — CLOSED

| ID | Accepted 决议 |
|----|---------------|
| AQ1 | 冻结 Universe：`symbol=rb`，`timeframe=1m`；扩展品种另开实验 |
| AQ2 | v1 **只输出 `atr_ratio`**；`compression_score` 延后独立 RFC |
| AQ3 | Primary Outcome=`RV_N=std(log_return[t+1:t+N])`；Primary Metric=`Spearman(atr_ratio, RV_N)`；分桶为 secondary |
| AQ4 | always-emit；不足时 `atr_ratio=null` + `warmup_state=insufficient`（不用 0） |
| AQ5 | diagnostics `rollover_flag`；Sensor 不 drop；过滤在 Evaluation 层 |
| AQ6 | `N=60`；Feature 每 bar 观测；Outcome **non-overlapping**，`sampling_interval=60` |
| AQ7 | numpy/talib 可在 Sensor 实现层；FeatureResult 仅标量 |

---

## 14. Freeze Criteria

- [x] AQ1–AQ7 关闭
- [x] 与 `FEATURE_SENSOR_SPEC.md` / `EVIDENCE_ENGINE_SPEC.md` / Decision 015 无矛盾
- [x] Out of Scope 明确排除交易 / 方向 / 晋级 / compression_score
- [x] 预注册（Hypothesis / Outcome / Metric / N / sampling）先于观测
- [x] Commit 边界获同意
- [x] `docs/README.md` 已索引

---

## 15. Relation to Later Phases

```text
Phase 3.0  Feature Sensor Framework                 ✅
Phase 3.1  ATR Compression EXPERIMENT Sensor        ← 本 RFC Accepted
Phase 3.1b compression_score / 多品种扩展           （各自 RFC）
Phase 4    Decision / Strategy Adaptation（Opportunity 路径，另 RFC）
```

**禁止**用回测收益反向修改本实验契约（假设 / Outcome / Metric / N / sampling 一经预注册不得事后择优）。
ATR 若晋级，须走 Feature Sensor Lifecycle，且 PRODUCTION 需 Intent + Evidence + Explicit Enablement。

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-19 | 0.1.0-draft | 首版 Phase 3.1：ATR 压缩作为 EXPERIMENT Feature Sensor 登记；开列 AQ1–AQ7 |
| 2026-07-19 | 1.0.0 | **Accepted**：AQ1–AQ7 关闭；v1 仅 atr_ratio；N=60 non-overlapping；授权 EXPERIMENT Sensor 实现 |
