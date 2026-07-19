# Feature Sensor Implementation RFC（Phase 3.0）

> **Status**: Accepted（Frozen for Phase 3.0 Feature Sensor Framework）
> **Accepted date**: 2026-07-19
> **Target version**: PAAF v0.3.x Phase 3.0  
> **Path**: `docs/specs/FEATURE_SENSOR_IMPLEMENTATION_RFC.md`  
> **Parent Spec**: `FEATURE_SENSOR_SPEC.md`（**Accepted**）  
> **Related**: Decision 015、Evidence / Evaluation / Workflow Impl RFCs（Accepted）  
> **规则优先级**: `AGENTS.md` > Parent Spec > 本 Implementation RFC > 代码  
> **实现门禁**: 仅授权 FeatureResult / SensorRegistry / Base protocol / DEMO / artifact helper；仍禁止 ATRCompression / TrendDetector / ranking / trading。

本文件限定 **Phase 3.0 实现切片**：把已 Accepted 的 Feature Sensor Architecture 落成可运行契约与 Registry，使 FeatureResult 能接入 Experiment / Evidence 链，**不**实现任何真实 Alpha Sensor。

**目标一句**：建立 Feature Observation Producer 框架；ATR 留待 Phase 3.1 独立 RFC。

---

## 1. Objective

Phase 0–2.1 已交付：

```text
Experiment → Manifest → ArtifactRef → Evidence → Evaluation → Persistence
```

仍缺：

```text
Market Data
    ↓
Feature Sensor
    ↓
FeatureResult
    ↓
（接入 Experiment / Evaluation）
```

Phase 3.0 交付：

```text
FeatureResult runtime model
BaseFeatureSensor protocol
SensorDescriptor + SensorRegistry
Fixture / DEMO sensor（非 ATR）
Workflow 挂接点（收集 FeatureResult → ArtifactReference）
Contract tests
```

成功标准：

1. FeatureResult immutable + 禁止 Direction / Opportunity / experiment 身份污染  
2. SensorRegistry 与 DetectorRegistry **分册**  
3. Sensor 默认状态 EXPERIMENT；无 Evaluation 不得 PRODUCTION  
4. Fixture sensor 可产出 FeatureResult 并经 Workflow 登记 ArtifactReference  
5. 包内无 ATR / ADX / 真实行情批处理引擎  

---

## 2. Scope

### 2.1 In Scope

| 组件 | 职责 |
|------|------|
| `FeatureResult` | Accepted Spec §2 运行时模型 |
| `SensorCapability` / `SensorDescriptor` | 注册目录项（不含 directions） |
| `SensorRegistry` | `(sensor_id, sensor_version)` 注册 / 查询 |
| `BaseFeatureSensor` | `observe(...) -> FeatureResult \| None` |
| `DEMO_CONSTANT` 或等价 Fixture Sensor | 证明框架可跑；状态 EXPERIMENT |
| Parameter Set 绑定点 | 参数进 ExperimentContext，不进 FeatureResult |
| Artifact 写出钩子（最小） | FeatureResult 序列 → 文件 + `hash_file` → ArtifactReference |
| Contract tests | 边界、Registry、禁止交易语义、与 Detector 隔离 |

### 2.2 Out of Scope（硬禁）

```text
ATRCompressionSensor / compression_score 算法
TrendDetector / 任何真实 OPP Feature
FeaturePipeline 编排引擎（可后续 RFC）
Feature ranking / IC 计算
Trading signal / Opportunity / DetectionResult
Sensor 自动晋级 PRODUCTION
vn.py BarData 泄漏进 FeatureResult
真实 TQ 全量回测作为本切片验收
```

---

## 3. Package Boundary

```text
strategies/paaf/
    sensors/
        __init__.py
        models.py           # FeatureResult, SensorCapability, SensorDescriptor, SensorStatus
        base.py             # BaseFeatureSensor
        registry.py         # SensorRegistry
        demo_constant.py    # Fixture EXPERIMENT sensor
        artifact.py         # optional: serialize FeatureResults → ArtifactReference
```

| 模块 | 拥有 | 禁止 |
|------|------|------|
| `sensors/models.py` | 契约类型 | I/O；vnpy；numpy 必需依赖 |
| `sensors/base.py` | observe 协议 | 下单；改 Context；生成 Opportunity |
| `sensors/registry.py` | Descriptor 目录 | 与 DetectorRegistry 混装 |
| `sensors/demo_constant.py` | 固定/可测观测 | 冒充 Alpha；PRODUCTION |
| `sensors/artifact.py` | 行序列落盘 + hash | Evaluation 计算 |

命名：

- 允许：`SensorRegistry`、`FeatureResult`、`BaseFeatureSensor`  
- 禁止：`UniversalComponentRegistry`、`SignalSensor`、`AlphaSensor`  

---

## 4. Object Contracts（对齐 Parent Spec）

### 4.1 FeatureResult

```python
@dataclass(frozen=True)
class FeatureResult:
    sensor_id: str
    sensor_version: str
    schema_version: str
    symbol: str
    timeframe: str
    timestamp: datetime
    values: Mapping[str, float]
    diagnostics: Mapping[str, str]
```

校验：

- timezone-aware `timestamp`  
- `values` / `diagnostics` MappingProxyType  
- 禁止交易语义键与 experiment/evidence/pipeline 键（见 Parent Spec §2.4）  
- 生命周期状态 **不**出现在 FeatureResult  

### 4.2 SensorStatus

复用治理枚举语义（可独立 Enum 或共享）：

```text
EXPERIMENT → VALIDATED → CANDIDATE → PRODUCTION → DEPRECATED
```

挂在 Descriptor，不挂 Result。

### 4.3 SensorCapability

```python
@dataclass(frozen=True)
class SensorCapability:
    requires: tuple[str, ...] = ()       # e.g. ("bars", "context")
    produces: tuple[str, ...] = ()       # feature value keys
    timeframe: str = "1m"
    emit_mode: str = "always"            # "always" | "sparse"
```

**禁止** `directions` 字段。

### 4.4 SensorDescriptor

```python
@dataclass(frozen=True)
class SensorDescriptor:
    sensor_id: str
    sensor_version: str
    status: SensorStatus
    capability: SensorCapability
    factory: Callable[[], BaseFeatureSensor]
    output_schema: tuple[str, ...] = ()
    parameter_schema: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
```

规则：

- PRODUCTION 必须有非空 `evidence_refs`  
- Descriptor 不持有实际参数值（参数属 Experiment）  

### 4.5 BaseFeatureSensor

```python
class BaseFeatureSensor(Protocol):
    def observe(
        self,
        *,
        symbol: str,
        timeframe: str,
        timestamp: datetime,
        window: Mapping[str, Any],   # 只读行情/窗口；具体形状本切片用 fixture dict
        context: Any | None = None,  # 只读 Context；禁止写回
        parameters: Mapping[str, str | int | float | bool] | None = None,
    ) -> FeatureResult | None: ...
```

约束：

- 纯函数式：同输入 → 同输出（除 diagnostics 中显式 warmup 状态）  
- 不得访问持仓 / 订单 / Repository  
- `parameters` 来自调用方 Experiment，不由 Sensor 生成 ID  

---

## 5. SensorRegistry

API（对齐 DetectorRegistry 形状，类型隔离）：

```text
register(descriptor)
unregister(sensor_id, sensor_version)
get(sensor_id, sensor_version) -> SensorDescriptor
list() / find(status=..., produces=...)
exists(sensor_id, sensor_version)
create(sensor_id, sensor_version) -> BaseFeatureSensor  # factory
```

禁止：

- `register(anything)`  
- 与 Detector 共用同一 dict  

---

## 6. Fixture Sensor（DEMO）

建议：`DEMO_CONSTANT` / `fixture_constant`

行为：

- `values={"fixture_value": 1.0}`（或 parameters 可控常数）  
- status=`EXPERIMENT`  
- 不声称 Alpha  
- 用于 Workflow / Artifact / Evaluation 联调  

**不是** ATR；不得使用 `compression_*` 键名冒充研究结论。

---

## 7. Experiment Workflow Integration Point

Phase 3.0 最小挂接（不实现完整 FeaturePipeline）：

```text
ExperimentContext (sensor_id, parameters)
    → SensorRegistry.create(...)
    → observe(...) → FeatureResult(s)
    → write feature artifact file
    → hash_file → ArtifactReference
    → build_manifest(artifact_refs=...)
    → （既有）Evidence / Evaluation 链
```

规则：

- FeatureResult **不**写入 experiment_id  
- Parameter fingerprint 仍由 Experiment / Manifest 负责  
- Observation Key 组装用既有 `build_observation_key`（provenance）  

---

## 8. Persistence Note

Feature artifact 内容可为 JSONL/JSON 行（本切片）：

```text
research/output/evidence/<experiment_id>/artifacts/<artifact_id>/feature_results.jsonl
```

Repository **不**强制管理二进制大表；`register_artifact_reference` 模式保持。  
是否扩展 EvidenceRepository 写 Feature 行见 Open Question SQ4。

---

## 9. Test Contract

`tests/test_paaf_feature_sensor_*.py`：

1. FeatureResult immutable / round-trip / 禁止 Direction 键  
2. SensorRegistry 分册与 key `(id, version)`  
3. PRODUCTION 无 evidence_refs → 注册失败  
4. DEMO sensor observe 确定性  
5. observe 不返回 DetectionResult / Opportunity  
6. Artifact helper：行序列 → hash 稳定  
7. 无 numpy/vnpy 泄漏进 FeatureResult.to_dict  

禁止：真实 TQ；禁止收益断言；禁止 ATR 单测冒充框架验收。

---

## 10. Commit Boundary（Accepted 后）

| Commit | Message | 内容 |
|--------|---------|------|
| 1 | `docs(paaf): add feature sensor implementation rfc` | 本文件 + 索引 |
| 2 | `feat(paaf): add feature result and sensor models` | `sensors/models.py` + tests |
| 3 | `feat(paaf): add sensor registry and base protocol` | registry + base + DEMO sensor + tests |
| 4 | `feat(paaf): add feature artifact registration helper` | artifact 写出 + workflow 挂接最小测试 |

---

## 11. Open Questions（Implementation）— CLOSED

| ID | Accepted 决议 |
|----|---------------|
| SQ1 | 独立 `SensorStatus`：EXPERIMENT / VALIDATED / CANDIDATE / PRODUCTION / DEPRECATED |
| SQ2 | Phase 3.0 使用 `Mapping[str, Any]` fixture；vn.py Adapter 后置 RFC |
| SQ3 | DEMO id = `demo_constant`，version = `1.0` |
| SQ4 | Feature artifact 写入 `sensors/artifact.py`；Repository 不管理 Feature 内容 |
| SQ5 | DEMO always emit；warmup 进入 diagnostics，不返回 None |
| SQ6 | Phase 3.0 不强制 Evaluation，仅挂接 ArtifactReference |

---

## 12. Freeze Criteria

- [x] SQ1–SQ6 关闭或显式推迟
- [x] 与 `FEATURE_SENSOR_SPEC.md` Q1–Q5 / Decision 015 无矛盾
- [x] Out of Scope 明确排除 ATR / ranking / trading
- [x] Commit 边界获同意
- [x] `docs/README.md` 已索引

---

## 13. Relation to Later Phases

```text
Phase 0–2.1  Evidence + Workflow + Evaluation + Persistence   ✅
Phase 3.0    Feature Sensor Contract                           ← 本 RFC
Phase 3.1    ATRCompression EXPERIMENT Sensor                  （另 RFC）
Phase 4      Decision / Strategy Adaptation
```

**禁止**在本 RFC Accepted 前实现 ATR。  
**禁止**用 ATR 需求反向修改本框架契约；ATR 变更应开 Phase 3.1 RFC。

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-19 | 0.1.0-draft | 首版 Phase 3.0：FeatureResult / SensorRegistry / DEMO fixture；排除 ATR |
| 2026-07-19 | 1.0.0 | **Accepted**：SQ1–SQ6 关闭；授权 Sensor framework 实现 |
