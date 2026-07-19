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
| 数值 `values` 为 `Mapping[str, float]` | `BUY` / `SELL` / `LONG` / `SHORT` 进入 values 或 metadata 业务键 |
| 显式 `sensor_id` / `version` / lifecycle | 修改 Context；隐藏全局状态 |
| 可序列化、可审计 | 声称 Production Alpha；跳过 Evidence |

---

## 2. FeatureResult（接口草案）

### 2.1 形状

```python
@dataclass(frozen=True)
class FeatureResult:
    sensor_id: str
    version: str
    timestamp: datetime                 # timezone-aware，默认 UTC
    values: Mapping[str, float]         # 发布后只读
    metadata: Mapping[str, str]         # 仅字符串诊断键；发布后只读
    schema_version: str = "1.0"
    status: DetectorStatus = DetectorStatus.EXPERIMENT
```

### 2.2 允许的 value 键（示例，非穷尽）

```text
atr_ratio
volatility_percentile
volume_zscore
trend_probability
range_probability
compression_score
```

键名须 `snake_case`；新增键优先进 Spec 附录或 `metadata` 文档化清单，避免同义拼写爆炸。

### 2.3 禁止

```text
direction, action, side, signal, order, buy, sell, long, short
weight, position_size, breakout_weight
```

出现在 `values` 或作为业务语义的 `metadata` 键 → 契约失败。

### 2.4 序列化

- `to_dict()` / `from_dict()`
- JSON 友好；Enum → value；datetime → ISO 8601
- 未知 `schema_version` 明确失败

### 2.5 与 DetectionResult 的隔离

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

与证据可见状态对齐（复用 `DetectorStatus` 命名，语义为 Sensor）：

```text
EXPERIMENT → VALIDATED → PRODUCTION → DEPRECATED
```

| 状态 | 允许 |
|------|------|
| EXPERIMENT | 研究臂、Evidence 采集；默认 |
| VALIDATED | 有合格 evidence_refs；仍非 Decision 默认输入 |
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

- 注册键：`(sensor_id, version)`（与 Detector 的 `(id, version)` 对称但分表）
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

- FeatureResult frozen；values/metadata 只读  
- 禁止交易语义键  
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

### 待关闭（Review 顺序）

| ID | 主题 | 提案（待你确认） |
|----|------|------------------|
| **Q2** | FeatureResult Versioning | `schema_version`（契约）与 `version`（sensor 实现）分列；结果不可变；行为变更 → 新 `version`，不得原地改已发布结果 |
| **Q3** | Sensor Metadata Ownership | `metadata` 仅 Sensor 自有诊断键（`Mapping[str, str]`）；Pipeline / Evidence 附加信息进各自对象，不回写 FeatureResult |
| **Q4** | Promotion Criteria | Feature 侧不定义 KEEP/Production 规则；晋级门禁归 Evidence Spec；本 Spec 只要求 EXPERIMENT 默认与禁止 Direction |
| **Q5** | Experiment Data Storage | 落盘路径与表结构归 Evidence Spec（倾向 `research/output/evidence/<experiment_id>/`）；Feature Spec 不规定存储 |

**附带（原 Draft，建议并入 Q2 旁注）**

| 项 | 提案 |
|----|------|
| Emit 策略 | ATR Compression 默认 **Always emit**（连续序列利于 Evidence）；Sparse 仅当「无有效观测」 |
| Capability | Sensor 使用独立 `SensorCapability`（requires / produces(feature keys) / timeframe）；**不**复用含 directions 的 `DetectorCapability` |

---

确认方式：对 Q2–Q5 回复 `Q2 OK` / 修改意见即可逐条 CLOSED。

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
