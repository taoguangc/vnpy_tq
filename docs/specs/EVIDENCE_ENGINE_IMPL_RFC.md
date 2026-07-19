# Evidence Engine Implementation RFC（Phase 0）

> **Status**: Accepted（Frozen for Phase 0 implementation）  
> **Accepted date**: 2026-07-19  
> **Target version**: PAAF v0.3.0 Phase 0  
> **Path**: `docs/specs/EVIDENCE_ENGINE_IMPL_RFC.md`  
> **Parent Spec**: `docs/specs/EVIDENCE_ENGINE_SPEC.md`（**Accepted**）  
> **Related**: `FEATURE_SENSOR_SPEC.md`（Accepted）、Decision 015（Accepted）  
> **规则优先级**: `AGENTS.md` > Parent Spec > 本 Implementation RFC > 代码  
> **实现门禁**: 仅授权 Phase 0 models → provenance → repository 切片；仍禁止 ATR / FeaturePipeline / Evaluation。

本文件限定 **Phase 0 实现切片**：架构契约已在 Parent Spec 冻结；此处冻结范围、包边界、持久化策略与测试契约。

**目标一句**：建立可审计 Evidence 基础设施；不包含 Feature 计算、不包含 Alpha 判断。

---

## 1. Objective

Phase 0 交付：

```text
Hypothesis / Experiment identity
        ↓
Immutable artifacts + provenance
        ↓
EvidenceRecord reference
```

不交付：

```text
Feature computation → ranking → auto-promotion → trading
```

成功标准：

1. 领域对象不可变、可序列化、字段校验明确失败  
2. 同输入 → 同 fingerprint（确定性）  
3. Filesystem repository：save / load / 禁止覆盖  
4. 无 ATR、无 FeaturePipeline、无 Decision、无收益排序  

---

## 2. Scope

### 2.1 In Scope

| 组件 | 职责 |
|------|------|
| `ExperimentManifest` | 实验复现身份与参数指纹 |
| `ArtifactReference` | 对不可变 Artifact 的 URI/hash 引用（不加载内容） |
| `EvidenceRecord` | 假设 / 结论 / 对 Manifest 与 Artifact 的引用 |
| Provenance / Hash utilities | 内容哈希、manifest 指纹、确定性序列化 |
| `EvidenceRepository` | filesystem 持久化边界（非 Database） |
| Contract tests | immutable、hash、repository 三组 |

### 2.2 Out of Scope（硬禁）

```text
ATRCompressionSensor
FeaturePipeline / FeatureResult 计算
DecisionEngine
StrategyIntegration / CTA wiring
Performance Ranking（IC / Sharpe / PF 排名）
Promotion Automation（KEEP → PRODUCTION）
SQL / EvidenceDatabase / ResearchDB
Market State 算法
参数搜索 / 收益优化
```

Phase 0 **不**实现 Evaluation Layer 度量库；`EvidenceRecord.metrics` 可为空 Mapping，或仅透传预登记键，不做统计计算。

---

## 3. Package Boundary

现有包根为 `strategies/paaf/`。Phase 0 新增：

```text
strategies/paaf/evidence/
    __init__.py          # 仅导出公开契约类型与 Repository 接口
    models.py            # ExperimentManifest / ArtifactReference / EvidenceRecord
    hashing.py           # 确定性 hash / fingerprint
    provenance.py        # Envelope / Provenance 组装与校验
    repository.py        # EvidenceRepository（filesystem）
```

| 模块 | 拥有 | 禁止 |
|------|------|------|
| `models.py` | frozen dataclass 契约 | I/O、numpy、vnpy、交易类型 |
| `hashing.py` | 纯函数 hash | 读盘以外的业务语义；禁止把 runtime timestamp / random UUID 编入指纹 |
| `provenance.py` | 校验 Observation Key / Provenance 完整性 | 加载 Parquet 行情；计算 Feature |
| `repository.py` | save/load、append-only 路径规则 | SQL；静默覆盖；改写已存在文件 |

**命名**：

- 允许：`EvidenceRepository`
- 禁止：`EvidenceDatabase`、`ResearchDB`、`EvidenceStoreService`（避免暗示 ORM/DB 抽象）

未来可替换 backend（filesystem → object storage → DB）而不改 `models.py`。

Domain 对象默认放在 `evidence/models.py`；若后续与 `domain.py` 共享序列化工具，仅抽取无业务纯函数，不把 Evidence 塞进交易 Domain 丛林。

---

## 4. Object Ownership

### 4.1 ExperimentManifest

```python
@dataclass(frozen=True)
class ExperimentManifest:
    experiment_id: str
    sensor_id: str
    sensor_version: str
    parameters: Mapping[str, str | int | float | bool]
    parameter_fingerprint: str
    code_revision: str
    data_fingerprint: str
    environment_fingerprint: str
    artifact_refs: tuple[ArtifactReference, ...]
    schema_version: str = "1.0"
```

职责：回答「结果如何产生」。  
不拥有：hypothesis conclusion、交易方向、Feature 数值序列。

### 4.2 ArtifactReference

```python
@dataclass(frozen=True)
class ArtifactReference:
    artifact_id: str
    uri: str                 # 相对 experiment 根或绝对 URI
    content_hash: str
    artifact_type: str       # e.g. "feature_results" | "outcomes" | "metrics"
```

职责：只引用，不加载。  
Repository 按需读文件；Reference 本身不持有 bytes。

### 4.3 EvidenceRecord（Phase 0 子集）

对齐 Parent Spec；Phase 0 **必填**最小集：

```python
@dataclass(frozen=True)
class EvidenceRecord:
    evidence_id: str
    experiment_id: str
    subject_kind: str          # "feature_sensor" | "opportunity" | "detector"
    subject_id: str
    subject_version: str
    hypothesis: str
    decision: str              # KEEP | REVERT | HOLD
    feature_artifact_uri: str
    artifact_hash: str
    observation: Mapping[str, float | str] = ...
    outcome: Mapping[str, float | str] = ...
    window: Mapping[str, int | str] = ...
    metrics: Mapping[str, float] = ...   # Phase 0 允许空；禁止内置 IC/Sharpe/PF 计算
    data_protocol_version: str = ""
    schema_version: str = "1.0"
    created_at: datetime = ...
    metadata: Mapping[str, str] = ...
```

`created_at` 是审计时间戳，**不得**进入 content hash / parameter_fingerprint。

Phase 0 初版可采用 `evidence_id`:`experiment_id` = 1:1（Parent Spec Q1）。

### 4.4 不进入这些对象的内容

```text
direction / action / weight
IC / Sharpe / PF / ranking scores（Evaluation Layer）
pipeline runtime status
mutable caches
```

---

## 5. Provenance Rules

### 5.1 确定性

```text
same canonical input  →  same fingerprint
changed bytes         →  different hash
```

实现：

- `hash_bytes(content: bytes) -> str`（如 sha256 hex）
- `hash_file(path) -> str`
- `fingerprint_manifest(manifest_dict_without_volatile_fields) -> str`

Canonical JSON：`sort_keys=True`、无无关空白、UTF-8。

### 5.2 禁止编入指纹

```text
runtime timestamp
random uuid
process id
wall-clock created_at
machine hostname（除非显式纳入 environment_fingerprint 的稳定字段表）
```

`environment_fingerprint` 由**显式声明**的环境字段表计算（如 python/numpy/pandas/vnpy 版本），不得塞入瞬时噪声。

### 5.3 Observation Key（校验用，不存进 FeatureResult）

```text
sensor_id + sensor_version + parameter_fingerprint
+ symbol + timeframe + timestamp
```

Phase 0 Repository 可校验 Manifest 的 `parameter_fingerprint` 与 parameters 一致；不实现 FeatureResult 写入器。

---

## 6. Persistence Strategy

### 6.1 Backend

Phase 0：**filesystem only**。不绑定数据库。

Repository 由调用方注入根路径：

```python
EvidenceRepository(
    root_path=Path("research/output/evidence"),
)
```

测试使用 `tmp_path`；不得硬编码绝对路径。

### 6.2 目录布局

与 Parent Spec 对齐（冻结路径）：

```text
research/output/evidence/<experiment_id>/
├── manifest.json
├── evidence/
│   └── <evidence_id>.json
└── artifacts/
    └── <artifact_id>/          # Phase 0 只保存引用，不管理二进制内容
```

一个 Experiment 可产生多个 EvidenceRecord。Phase 0 不引入 Run Lifecycle。

### 6.3 EvidenceRepository 契约

```text
save_manifest(manifest) -> None      # 若已存在 → 失败
load_manifest(experiment_id) -> ExperimentManifest
manifest_exists(experiment_id) -> bool

save_evidence(record) -> None        # 若已存在 → 失败
load_evidence(experiment_id, evidence_id) -> EvidenceRecord
evidence_exists(experiment_id, evidence_id) -> bool
```

规则：

- append-only / create-once  
- 禁止 overwrite `manifest.json` / 已存在 `<evidence_id>.json`
- load 未知 ID → `FileNotFoundError`，不返回 `None`
- `(experiment_id, evidence_id)` 定位，禁止全仓扫描 evidence_id
- ID 作为路径片段时必须拒绝 `.`, `..`, `/`, `\`，防止越界
- 相同配置重跑 → 新 `experiment_id`，不得改历史

### 6.4 临时 vs 持久

进入 Evidence 的观测必须先有 ArtifactReference。Phase 0 Repository 只保存
Manifest / Evidence 元数据与引用，**不复制、不加载、不管理 Artifact 二进制**。

---

## 6.5 ID Responsibility

| ID | Owner |
|----|-------|
| `experiment_id` | Experiment author / coordinator |
| `artifact_id` | Artifact creator |
| `evidence_id` | Evidence author |
| `run_id`（未来） | Experiment runner |

Repository **只存取，不生成领域 ID**。Phase 0 不使用 UUID 自动生成器。

---

## 7. Test Contract

测试目录建议：`tests/test_paaf_evidence_*.py`（与现有 `tests/test_paaf_*` 一致）。

### 7.1 Model Tests

- frozen：赋值字段失败  
- Mapping 防御性只读（构造后不可写）  
- `to_dict` / `from_dict` 往返等价  
- 缺必填字段 / 非法 `decision` → 明确失败  
- 禁止交易语义键（若校验器存在）  

### 7.2 Hash Tests

- 同 canonical bytes → 同 hash  
- 改一字节 → 不同 hash  
- 同 parameters 不同键序 → 同 `parameter_fingerprint`  
- fingerprint **不含** `created_at`  

### 7.3 Repository Contract Tests

- save → load 等价  
- 二次 save 同 id → 失败（不可覆盖）  
- load 未知 id → `FileNotFoundError`
- 不同 experiment 目录隔离
- 路径穿越 ID 明确失败
- 不依赖 Parquet 全行情回测

禁止：以「收益好看」为断言；禁止联真实 TQ 大数据。

---

## 8. Commit Boundary（Accepted 后）

| Commit | Message | 内容 |
|--------|---------|------|
| 1 | `docs(paaf): add evidence engine implementation rfc` | 本文件 + 索引 |
| 2 | `feat(paaf): add evidence engine core models` | `models.py` + model tests |
| 3 | `feat(paaf): add evidence provenance helpers` | `hashing.py` / `provenance.py` + hash tests |
| 4 | `feat(paaf): add evidence artifact repository` | `repository.py` + repository tests |

每 commit 一概念；不夹带 ATR / Detector / ROADMAP 大改。

---

## 9. Implementation Sequence Gate

```text
本 RFC Draft
    → Review / Accepted
    → Commit 2 models
    → Commit 3 provenance
    → Commit 4 repository
    →（另 RFC）Evaluation Layer / ATR Experiment Sensor
```

**禁止**在本 RFC Accepted 前写 Phase 0 代码。  
**禁止**跳到 ATR Compression Sensor。

---

## 10. Open Questions（Implementation）— CLOSED

| ID | Accepted 决议 |
|----|---------------|
| IQ1 | Phase 0 使用 `artifacts/<artifact_id>/`；不引入 Run Lifecycle |
| IQ2 | `EvidenceRecord.created_at` 必填且由调用方注入 |
| IQ3 | `parameters` 仅允许扁平 `str\|int\|float\|bool` |
| IQ4 | `EvidenceRepository(root_path: Path)` 构造注入；默认相对路径 `research/output/evidence` |
| IQ5 | 不自动生成 `evidence_id`；调用方提供稳定业务 ID |

---

## 11. Freeze Criteria

- [x] IQ1–IQ5 关闭或显式推迟  
- [x] 与 `EVIDENCE_ENGINE_SPEC.md` / Feature Spec Storage 无矛盾  
- [x] Out of Scope 清单无歧义  
- [x] Commit 边界获同意  
- [x] `docs/README.md` 已索引  

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-19 | 0.1.0-draft | 首版 Phase 0 Implementation RFC：范围、包边界、Repository、测试与 Commit 切片 |
| 2026-07-19 | 1.0.0 | **Accepted**：IQ1–IQ5 关闭；ID Responsibility；授权 core models |
| 2026-07-19 | 1.0.1 | Repository 切片：多 Evidence 目录；metadata/reference only；双 ID load |
