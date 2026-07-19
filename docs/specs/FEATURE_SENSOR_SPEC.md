# Feature Sensor Architecture Specification（RFC）

> **Status**: Draft（RFC — Ready for Architecture Review）  
> **Target version**: PAAF v0.3.x（接口冻结后实现；本文件不授权实现）  
> **Path**: `docs/specs/FEATURE_SENSOR_SPEC.md`  
> **规则优先级**: `AGENTS.md` > `PAAF_PROJECT_SPEC.md` / 宪章 > Accepted Specs > 本 Draft  
> **变更规则**: 先改本 Spec，再改代码；破坏性变更须 ADR。  
> **实现门禁**: 本 Spec **Accepted** 且 Decision 015 Accepted 之前，禁止实现 Feature Sensor / ATRCompression / FeaturePipeline。

本文件定义 **Feature Sensor（特征传感器）** 的接口与边界。  
它冻结契约，不冻结任何具体指标算法（ATR / ADX / ER 等）。

**Stable API, Replaceable Implementation.**

---

## 0. 与已冻结决策的关系

| 决策 | 约束 |
|------|------|
| Decision 002 | Context 基线 `MarketState` 仍为 `UNKNOWN\|TREND\|RANGE`；Compression **不得**进入 Context 基线枚举 |
| Decision 008 | Feature Layer 曾延后；本 Spec + Decision 015 提议在 **Evidence 之后** 受控引入 Feature Sensor |
| Decision 009 | Context 是 Semantic Layer，不是 Feature Layer |
| Decision 011 | 无证据不得 Production |
| Decision 013 | Opportunity 路径继续使用 DetectionResult；本 Spec **不替代** |
| Decision 014 | Framework First, Alpha Later；Feature Sensor ≠ Alpha |

本 Draft 若与 Accepted ADR 冲突，以 Accepted 为准，直至 Decision 015 Accepted 覆盖。

---

## 1. Design Goals

### 1.1 定义

**Feature Sensor 是只读市场数据的确定性传感器：输出数值特征与状态度量，不发现交易机会，不下单。**

### 1.2 双路径架构（冻结）

```text
                Market Data
                     |
        +------------+-------------+
        |                          |
        v                          v

 Feature Sensor              Opportunity Detector

        |                          |
        v                          v

 FeatureResult              DetectionResult

        |                          |
        |                          v
        |                    Opportunity
        |                          |
        +------------+-------------+
                     |
                     v
              Evidence Engine
```

| 路径 | 输出 | 可否带 Direction | 可否构造 Opportunity |
|------|------|------------------|----------------------|
| Feature Sensor | `FeatureResult` | **禁止** | **禁止** |
| Opportunity Detector | `DetectionResult` → `Opportunity` | 允许（在 Opportunity / DetectionResult） | 允许 |

### 1.3 MUST / MUST NOT

| MUST | MUST NOT |
|------|----------|
| 读只读窗口 / Context | `buy` / `sell` / 持仓 |
| 返回 `FeatureResult \| None`（或每 bar 恒输出，见 §3） | 返回 `DetectionResult` / `Opportunity` / `Signal` |
| 数值 `values` 为 `Mapping[str, float]` | `BUY` / `SELL` / `LONG` / `SHORT` 进入 values 或 diagnostics |
| 显式 identity：`sensor_id` / `sensor_version` / `symbol` / `timeframe` / `timestamp` | 修改 Context；隐藏全局状态；携带 experiment / evidence / pipeline 业务语义 |
| 可序列化、可审计 | 声称 Production Alpha；跳过 Evidence |

---

## 2. FeatureResult（接口草案）

### 2.1 形状

```python
@dataclass(frozen=True)
class FeatureResult:
    sensor_id: str
    sensor_version: str
    schema_version: str                 # 默认 "1.0"
    symbol: str                         # 观测身份；一等字段，禁止塞入 diagnostics
    timeframe: str                      # 如 "1m"；一等字段
    timestamp: datetime                 # timezone-aware，默认 UTC
    values: Mapping[str, float]         # 发布后只读
    diagnostics: Mapping[str, str]      # 计算诊断；发布后只读
```

Sensor 生命周期状态（EXPERIMENT / …）属于 **Sensor Descriptor / Registry**，不属于单次 FeatureResult。

### 2.2 Identity vs Diagnostic（Q3）

| 类别 | 字段 | 用途 |
|------|------|------|
| **Identity（必须稳定）** | `sensor_id`, `sensor_version`, `schema_version`, `symbol`, `timeframe`, `timestamp` | persistence key、audit、replay |
| **Values** | `atr_ratio`, `compression_score`, … | 观测数值 |
| **Diagnostics（可随实现演进）** | `calculation_status`, `warmup_state`, `missing_data_flag`, `input_timeframe` | debugging / monitoring |

Evidence Store 定位键至少为：

```text
(sensor_id, sensor_version, symbol, timeframe, timestamp)
```

（加上 experiment / parameter 指纹由 Experiment 记录提供。）

### 2.3 允许的 value 键（示例，非穷尽）

```text
atr_ratio
volatility_percentile
volume_zscore
trend_probability
range_probability
compression_score
```

键名须 `snake_case`；新增键优先进 Spec 附录或 Descriptor `output_schema`，避免同义拼写爆炸。

### 2.4 禁止（FeatureResult）

```text
# 交易语义
direction, action, side, signal, order, buy, sell, long, short
weight, position_size, breakout_weight

# Experiment / 复现身份
experiment_id, run_id, parameter_set, git_hash, dataset_hash

# Evidence / 研究结论
evidence_metric, p_value, sharpe, decision, conclusion

# Pipeline 运行态
pipeline_status, dispatch_id
```

出现在 `values` 或 `diagnostics` → 契约失败。  
`symbol` / `timeframe` 不得放入 `diagnostics`。

### 2.5 序列化

- `to_dict()` / `from_dict()`
- JSON 友好；Enum → value；datetime → ISO 8601
- 未知 `schema_version` 明确失败

### 2.6 FeatureResult Versioning（Q2 Resolved）

FeatureResult 采用双版本模型：

| 字段 | 含义 | 升级条件 |
|------|------|----------|
| `schema_version` | FeatureResult 外层数据结构与序列化契约版本 | 字段、字段类型或编码格式发生不兼容变化 |
| `sensor_version` | Sensor 计算行为及输出契约版本 | 算法、特征定义、输出键集合或算法默认常量变化 |

规则：

1. FeatureResult 必须 `frozen=True`；`values` 与 `diagnostics` 在构造时防御性复制并以只读 Mapping 发布（例如 `MappingProxyType`）。
2. Result 写入 Evidence Store 或 Backtest Artifact 后即为 **published**，不得覆盖或修改。
3. Sensor 行为变化必须生成新 `sensor_version`；历史结果继续引用原版本。
4. 显式实验参数不属于 `sensor_version`，须作为独立 Parameter Set 保存。
5. 历史证据必须保留原始 `schema_version`、`sensor_version` 及完整参数配置或其不可变指纹。

```yaml
sensor:
  id: atr_compression
  version: "1.0"

parameters:
  atr_window: 14
  baseline_window: 100
```

同一算法使用不同实验参数，不自动升级 `sensor_version`；算法实现、特征语义或默认常量改变才升级。

**边界说明**：在 `values: Mapping[str, float]` 外层类型不变时，增加
`compression_score` 属于 Sensor 输出契约变化，升级 `sensor_version`；
只有 FeatureResult 外层字段、字段类型或序列化编码改变才升级 `schema_version`。

### 2.7 Metadata Ownership（Q3 Resolved）

FeatureResult **不携带** experiment 身份或 evidence 解释。

```text
Sensor Descriptor  --defines-->  FeatureResult  --observes-->  Experiment
                                                              --reproduces-->
                                                         Evidence --evaluates--> Decision
```

| 层 | 职责 | 拥有（示例） | 禁止 |
|----|------|--------------|------|
| **Sensor Descriptor** | 描述 Sensor 是什么 | `sensor_id`, `sensor_version`, capabilities, `output_schema`, `parameter_schema` | 实际参数值、`experiment_id`、`run_id`、evidence conclusion |
| **FeatureResult** | 一次确定性市场观测 | identity + `values` + `diagnostics` | experiment / evidence / pipeline 业务语义 |
| **Experiment** | 保证可复现 | `experiment_id`, parameter_set, code_revision, data_fingerprint, `run_id`, environment | 改写已发布 FeatureResult |
| **Evidence** | 解释 Feature 是否有预测价值 | hypothesis, windows, outcome, metrics, result, conclusion, references | 把观测直接写成 BUY/SELL |

Pipeline **不拥有业务语义**：只负责 load / transform / dispatch / collect。  
运行态进入独立 `PipelineRunContext`，**禁止**回写 FeatureResult。

Evidence 正确形态是假设—观测—结果—结论，**禁止** `compression_score → BUY`。

### 2.8 与 DetectionResult 的隔离

| | FeatureResult | DetectionResult |
|--|---------------|-----------------|
| 目的 | 市场传感 / 证据输入 | 机会检出 |
| Direction | 禁止 | 允许 |
| Opportunity | 禁止提升 | 允许 |
| Registry 类型 | Sensor Descriptor（未来） | Detector Descriptor（已有） |

---

## 3. Sensor 输出策略

两种合法模式（实现时选定并在 Descriptor 声明）：

| 模式 | 行为 |
|------|------|
| **Always emit** | 每 bar 输出 FeatureResult（含冷启动默认 / NaN 替代策略须显式） |
| **Sparse emit** | 条件不满足返回 `None`（仅当「无有效观测」；不是「无交易机会」） |

**禁止**用 `None` 表示「没有 Opportunity」——那是 Opportunity Detector 的语义。

---

## 4. Lifecycle（Sensor）

生命周期状态挂在 **Sensor Descriptor**（按 `(sensor_id, sensor_version)`），不挂在单次 FeatureResult。

与证据可见状态对齐（命名可复用 `DetectorStatus`，语义为 Sensor）：

```text
EXPERIMENT → VALIDATED → CANDIDATE → PRODUCTION → DEPRECATED
```

（`CANDIDATE` 是否正式加入枚举由 Q4 关闭；Draft 先保留为晋升讨论位。）

| 状态 | 允许 |
|------|------|
| EXPERIMENT | 研究臂、Evidence 采集；**默认** |
| VALIDATED | 有合格 evidence_refs；仍非 Decision 默认输入 |
| CANDIDATE | （Q4）通过既定 Gate、待用户确认是否进 Production profile |
| PRODUCTION | E4 + 用户确认 + 显式启用；可作为 Decision 输入 |
| DEPRECATED | 保留指纹与历史；默认不进入生产 profile |

**ATR Compression** 在本 Spec Accepted 后的首个实现，生命周期起点必须是 **EXPERIMENT Feature Sensor**，不得标 PRODUCTION，不得生成 Opportunity。

晋级：

```text
Experiment Sensor
    → Evidence Dataset
    → Statistical Validation
    → Production Feature
    → Decision Engine Input
```

客观 Gate（样本 / OOS / 多品种 / 稳健性 / 回退）见 **Q4**；细则以 Evidence Spec 为准，本 Spec 只约束默认状态与禁止交易语义。

---

## 5. 与 Registry / Pipeline 的关系

### 5.1 Registry（Q1 Resolved）

**决议：分册，不共用。**

```text
Registry
    |
    +-- DetectorRegistry   # 可执行机会检测组件
    |
    +-- SensorRegistry     # 研究特征生成组件
```

| | DetectorRegistry | SensorRegistry |
|--|------------------|----------------|
| 输出 | DetectionResult | FeatureResult |
| 目标 | Opportunity | Evidence |
| Direction | 允许 | **禁止** |
| 典型状态 | 可至 Production | 默认 Experiment |
| 验证 | 策略回测 / 机会证据 | 统计验证 |

**禁止** `UniversalComponentRegistry` / `registry.register(anything)`。

- 注册键：`(sensor_id, sensor_version)`（与 Detector 的 `(id, version)` 对称但分表）
- v0.2 `DetectorRegistry` API 形状可参考，**类型与能力契约不得混装**

### 5.2 Pipeline

```text
FeaturePipeline:  Market Data + Context → FeatureResult[]
OpportunityPipeline:  (现有 DetectorPipeline) → Opportunity[]
```

两者都可向 Evidence Engine 投递观测；**不得**在 FeaturePipeline 内构造 Opportunity。

现有 `DetectorPipeline` **保持不变**，直至本 Spec Accepted 后增量扩展。

---

## 6. Context 边界

- Feature Sensor **可读** Context（session / market_state / extras）
- Feature Sensor **不得写** Context
- 不得因 Feature 输出而扩展 Context 基线 `MarketState` 枚举（Decision 002）
- Compression 等度量只出现在 `FeatureResult.values`，不得伪装成 Context 一级状态

---

## 7. ATR Compression（定位，非实现）

| 项 | 决议 |
|----|------|
| 角色 | **EXPERIMENT Feature Sensor** |
| 输出示例 | `atr_ratio`, `compression_score`（及未来 evidence 用的 forward 观测由 Evidence Engine 定义） |
| 禁止 | `DetectionResult(direction=LONG)`、`Opportunity`、breakout weight、Production |
| 实现时机 | 本 Spec + Evidence Spec Accepted，且有实验登记之后 |
| AFF 历史 | 仅作假设来源；证据不继承，须在冻结数据协议下重采 |

---

## 8. v0.3 Removal Window（相关）

本 Spec 依赖并重申（细节见 Detector Framework Spec / Decision 015）：

1. 删除 Registry `_adapt_legacy` / 实例注册  
2. 删除 Domain `Signal`  
3. Direction 仅允许出现在 Opportunity 路径；FeatureResult 禁止  

---

## 9. Testing Requirements（Accepted 后实现时）

- FeatureResult frozen；`values` / `diagnostics` 只读  
- Identity 字段齐全；禁止把 `symbol`/`timeframe` 仅放进 diagnostics  
- 禁止交易语义键与 experiment/evidence/pipeline 污染键  
- `to_dict → from_dict` 等价  
- Sensor 不得构造 Opportunity / DetectionResult  
- Domain 无 vnpy/numpy/pandas/talib（计算可在 sensor 模块，Domain 只持契约类型）  
- 无 Parquet 全量回测作为单测  

---

## 10. Open Questions

### Q1 — Registry Boundary — **CLOSED**

**决议**：`DetectorRegistry` 与 `SensorRegistry` 分册；禁止通用万能 Registry。  
依据：输出类型、目标、Direction、生命周期与验证方式均不同。

---

### Q2 — FeatureResult Versioning — **CLOSED**

**决议**：采用 `schema_version` + `sensor_version` 双版本；Published Result
不可覆盖；实验 Parameter Set 独立存档。详见 §2.6。

---

### Q3 — Metadata Ownership — **CLOSED**

**决议**：四层所有权（Descriptor / FeatureResult / Experiment / Evidence）；
`symbol`+`timeframe` 为一等 Identity；`diagnostics` 仅计算诊断；
Pipeline 运行态进 `PipelineRunContext`，不回写 FeatureResult。详见 §2.2 / §2.7。

---

### 待关闭（Review 顺序）

| ID | 主题 | 提案（待你确认） |
|----|------|------------------|
| **Q4** | Promotion Criteria | 见下方 Q4 草案；Feature Spec 声明状态机，客观 Gate 数值归 Evidence Spec |
| **Q5** | Experiment Data Storage | 落盘路径与表结构归 Evidence Spec（倾向 `research/output/evidence/<experiment_id>/`）；Feature Spec 不规定存储 |

**附带（建议 Q4 旁关闭）**

| 项 | 提案 |
|----|------|
| Emit 策略 | ATR Compression 默认 **Always emit** |
| Capability | 独立 `SensorCapability`（requires / produces / timeframe）；不含 directions |

#### Q4 草案 — Sensor Lifecycle / Promotion Criteria

状态机（Descriptor 级）：

```text
EXPERIMENT → VALIDATED → CANDIDATE → PRODUCTION → DEPRECATED
```

| 跃迁 | 客观 Gate（原则；阈值进 Evidence Spec） | 谁批准 |
|------|------------------------------------------|--------|
| → VALIDATED | 单假设已登记；有可审计观测+outcome；预登记度量完成；decision ≠ 空 | Evidence + 研究结论 KEEP/HOLD 可 VALIDATED；REVERT 不得晋级 |
| → CANDIDATE | 满足 E2+ 级证据意图：多品种或多年份之一；OOS 窗口预登记且通过；稳健性（参数扰动不翻转结论）有记录 | 用户确认进入候选名单 |
| → PRODUCTION | E4 意图 + 用户显式确认 + profile 启用；evidence_refs 齐全 | **仅用户** |
| → DEPRECATED | 被替代版本、证据失效、或主动下线 | 用户或维护者 |

附加规则：

1. Feature Spec **不**把 KEEP 自动写成 PRODUCTION。  
2. 允许 **回退**：PRODUCTION → DEPRECATED（保留指纹）；新行为用新 `sensor_version`，禁止原地改历史。  
3. 参数扫描产生的 KEEP **不**升级 `sensor_version`，只绑定新 Experiment。  
4. ATR Compression 首版最高停在 EXPERIMENT，直到 Evidence Gate 关闭。

确认方式：对 Q4–Q5 回复 `Q4 OK` / 修改意见即可逐条 CLOSED。

---

## 11. Freeze Criteria

标记 **Accepted** 当且仅当：

- [ ] Open Questions 关闭或显式推迟  
- [ ] Decision 015 Accepted（或明确声明本 Spec 不覆盖 008）  
- [ ] 与 Decision 002/009/011/013/014 无未决议冲突  
- [ ] 明确：Accepted ≠ 授权 ATR 实现；实现另开切片 Commit  
- [ ] `docs/README.md` 已索引  

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-19 | 0.1.0-draft | 首版 Draft：Feature/Opportunity 双路径；FeatureResult；ATR 定位为 EXPERIMENT Sensor |
| 2026-07-19 | 0.1.1-draft | Review：Q1 CLOSED（DetectorRegistry / SensorRegistry 分册） |
| 2026-07-19 | 0.1.2-draft | Review：Q2 CLOSED（schema/sensor 双版本；参数集独立；历史结果不可覆盖） |
| 2026-07-19 | 0.1.3-draft | Review：Q3 CLOSED（四层所有权；symbol/timeframe Identity；diagnostics） |
