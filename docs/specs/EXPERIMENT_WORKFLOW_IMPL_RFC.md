# Experiment Workflow Implementation RFC（Phase 1）

> **Status**: Accepted（Frozen for Phase 1 implementation）  
> **Accepted date**: 2026-07-19  
> **Target version**: PAAF v0.3.x Phase 1  
> **Path**: `docs/specs/EXPERIMENT_WORKFLOW_IMPL_RFC.md`  
> **Parent Specs**: `EVIDENCE_ENGINE_SPEC.md`、`EVIDENCE_ENGINE_IMPL_RFC.md`（Accepted）  
> **Related**: `FEATURE_SENSOR_SPEC.md`、Decision 015（Accepted）  
> **规则优先级**: `AGENTS.md` > Parent Specs > 本 Implementation RFC > 代码  
> **实现门禁**: 仅授权 ExperimentContext / RunContext / Manifest+Evidence build/persist/replay；仍禁止 ATR / FeaturePipeline / Evaluation / Promotion。

本文件限定 **Phase 1 实现切片**：在 Phase 0 Evidence Foundation 之上，补齐「谁创建 Manifest / Evidence」的 workflow owner。

**目标一句**：验证一个研究实验可以完整走通生命周期；不产生真实 Alpha。

---

## 1. Objective

Phase 0 已交付：

```text
ExperimentManifest + ArtifactReference + EvidenceRecord
+ Provenance + EvidenceRepository
```

仍缺：

```text
ExperimentManifest
        ↑
        |
    谁创建它？
```

Phase 1 交付：

```text
Experiment
    ↓
Generate Artifact Reference
    ↓
Create Evidence
    ↓
Persist
    ↓
Replay
```

成功标准：

1. 调用方提供全部领域 ID；Workflow **不生成** UUID  
2. Manifest / Evidence 经 Repository append-only 落盘  
3. Replay 能从 Manifest + Evidence 重建 provenance（sensor / params / code / data / env）  
4. 无 Sensor 计算、无指标评估、无晋级自动化  

---

## 2. Scope

### 2.1 In Scope

| 组件 | 职责 |
|------|------|
| `ExperimentContext` | 实验身份、假设、参数、指纹输入；创建 Manifest 的输入边界 |
| `RunContext` | 单次执行时钟 / 环境声明；**不**引入 Run Lifecycle 目录 |
| Artifact registration helper | 从已有 URI + content_hash 构造 `ArtifactReference`（不复制二进制） |
| Evidence drafting helper | 组装 `EvidenceRecord`（调用方注入 `created_at` / IDs / decision） |
| Persist orchestration | 调 `EvidenceRepository.save_manifest` / `save_evidence` |
| Replay contract | 从 repository 加载并校验 fingerprint 一致性 |
| Contract tests | create → persist → reload → replay 等价 |

### 2.2 Out of Scope（硬禁）

```text
ATRCompressionSensor
FeatureResult 计算 / FeaturePipeline
Evaluation metrics（IC / Sharpe / PF / RV 计算引擎）
Promotion Automation / Sensor lifecycle 状态机推进
DecisionEngine / StrategyIntegration
Artifact binary storage / Parquet manager
SQL / Database
参数搜索 / 收益优化
Run Lifecycle 目录（runs/<run_id>/）—— 延后独立 RFC
```

Phase 1 **不**计算 Feature；可用**假想 / fixture** ArtifactReference（外部文件已存在或仅 URI 占位）。

---

## 3. Package Boundary

```text
strategies/paaf/evidence/
    models.py              # Phase 0 — 不变（除非破坏性 ADR）
    hashing.py             # Phase 0
    provenance.py          # Phase 0
    repository.py          # Phase 0
    workflow.py            # Phase 1 — NEW
    __init__.py
```

| 模块 | 拥有 | 禁止 |
|------|------|------|
| `workflow.py` | Context 对象、组装 Manifest/Evidence、编排 save/load/replay | 文件系统细节（委托 Repository）；hash 算法（委托 provenance）；交易语义 |
| `repository.py` | 持久化 | 不改领域 ID；不写 workflow 状态机 |

命名：

- 允许：`ExperimentContext`、`RunContext`、`ExperimentWorkflow`
- 禁止：`ExperimentEngine`、`ResearchOrchestrator`、`AlphaRunner`（暗示计算/交易）

---

## 4. Object Ownership

### 4.1 ExperimentContext

职责：描述「要跑什么实验」。

```python
@dataclass(frozen=True)
class ExperimentContext:
    experiment_id: str
    sensor_id: str
    sensor_version: str
    parameters: Mapping[str, str | int | float | bool]
    hypothesis: str
    code_revision: str
    data_fingerprint: str
    environment_fingerprint: str
    subject_kind: str = "feature_sensor"
    data_protocol_version: str = ""
```

规则：

- 全部 ID / fingerprint 由调用方提供  
- `parameters` 扁平标量；`parameter_fingerprint` **由 workflow 调用** `fingerprint_parameters` 计算后写入 Manifest  
- 不持有 Feature 数值序列  

### 4.2 RunContext

职责：单次执行的审计时钟与可选标签（**不是** Run Lifecycle 存储模型）。

```python
@dataclass(frozen=True)
class RunContext:
    experiment_id: str
    created_at: datetime          # 调用方注入；timezone-aware
    run_id: str | None = None     # 可选；若存在必须由调用方提供
    labels: Mapping[str, str] = ...
```

规则：

- `created_at` 不得进入 `parameter_fingerprint` / `fingerprint_manifest` 的配置身份  
- Phase 1 **不**强制 `run_id`；多个执行实例需要 run_id 时，必须由调用方提供
- Workflow / Repository 禁止生成 run_id
- `RunContext.experiment_id` 必须与 `ExperimentContext.experiment_id` 一致

### 4.3 ArtifactRegistration

输入：调用方已有的 `artifact_id` / `uri` / `content_hash` / `artifact_type`。  
输出：`ArtifactReference`。  
禁止：读大文件进内存、复制 parquet、自动生成 hash（hash 由调用方用 `hash_file` / `hash_bytes` 预先算好后传入）。

可选 helper：

```python
def register_artifact_reference(...) -> ArtifactReference
```

### 4.4 ExperimentWorkflow（编排，非引擎）

建议最小 API：

```python
class ExperimentWorkflow:
    def __init__(self, repository: EvidenceRepository) -> None: ...

    def build_manifest(
        self,
        context: ExperimentContext,
        artifact_refs: tuple[ArtifactReference, ...] = (),
    ) -> ExperimentManifest: ...

    def persist_manifest(self, manifest: ExperimentManifest) -> None: ...

    def build_evidence(
        self,
        context: ExperimentContext,
        *,
        run_context: RunContext,
        evidence_id: str,
        decision: str,
        feature_artifact_uri: str,
        artifact_hash: str,
        observation: Mapping[str, float | str] = ...,
        outcome: Mapping[str, float | str] = ...,
        window: Mapping[str, int | str] = ...,
        metrics: Mapping[str, float] = ...,
    ) -> EvidenceRecord: ...

    def persist_evidence(self, evidence: EvidenceRecord) -> None: ...

    def replay(
        self,
        experiment_id: str,
        evidence_id: str,
    ) -> tuple[ExperimentManifest, EvidenceRecord]: ...
```

`replay`：load + `verify_parameter_fingerprint`；失败明确抛错。

---

## 5. Lifecycle Flow（Phase 1）

```text
Caller supplies IDs + parameters + fingerprints
        |
        v
ExperimentContext + RunContext
        |
        v
register_artifact_reference  (optional fixtures)
        |
        v
build_manifest → persist_manifest
        |
        v
build_evidence → persist_evidence
        |
        v
replay(experiment_id, evidence_id)
        |
        v
assert fingerprints / bodies consistent
```

不包含：Sensor.detect → FeatureResult → Evaluation → KEEP 自动晋级。

---

## 6. Replay Contract

Replay 必须恢复并校验：

```text
sensor_id / sensor_version
parameter_fingerprint ↔ parameters
code_revision
data_fingerprint
environment_fingerprint
artifact uri + hash（引用，不加载内容）
evidence decision / hypothesis
```

不要求：重新计算 Feature、重跑行情、重算统计指标。

---

## 7. Persistence Interaction

继续使用 Phase 0 布局：

```text
research/output/evidence/<experiment_id>/
├── manifest.json
├── evidence/<evidence_id>.json
└── artifacts/          # Phase 1 仍可不创建；仅 Reference
```

Workflow 不绕过 Repository；不直接写文件。

---

## 8. Test Contract

`tests/test_paaf_evidence_workflow.py`：

1. **Build manifest**：parameters 键序不同 → 相同 `parameter_fingerprint`  
2. **Persist round-trip**：build → save → load 等价  
3. **Append-only**：重复 persist 同 id → `FileExistsError`  
4. **Replay**：reload 后 `verify_parameter_fingerprint` 通过  
5. **ID ownership**：Workflow API 无 `uuid` 导入 / 无自动 `evidence_id`  
6. **Out of scope**：模块内无 ATR / numpy / vnpy 依赖  

禁止：真实 TQ 大数据；禁止收益断言。

---

## 9. Commit Boundary（Accepted 后）

| Commit | Message | 内容 |
|--------|---------|------|
| A | `docs(paaf): add experiment workflow implementation rfc` | 本文件 + 索引 |
| B | `feat(paaf): add experiment workflow context` | Context + Manifest/Evidence build/persist/replay + contract tests |

Review 已明确本轮以 Workflow 生命周期为单一概念，B 包含最小 persist/replay 编排。

---

## 10. Open Questions（Implementation）— CLOSED

| ID | Accepted 决议 |
|----|---------------|
| WQ1 | `run_id` 可选；若存在由调用方提供；Workflow/Repository 不生成 |
| WQ2 | `build_evidence` 要求 Manifest 已 persist；缺失明确失败，不自动保存 |
| WQ3 | 测试允许 fixture hash；正式实验必须真实 content hash |
| WQ4 | Workflow 不自动注入 metadata；只透传调用方显式字段 |
| WQ5 | 包文件使用 `evidence/workflow.py` |

---

## 11. Freeze Criteria

- [x] WQ1–WQ5 关闭或显式推迟  
- [x] 与 Evidence Phase 0 / Feature Spec 无矛盾  
- [x] Out of Scope 明确排除 ATR / Evaluation / Promotion  
- [x] Commit 边界获同意  
- [x] `docs/README.md` 已索引  

---

## 12. Relation to Later Phases

```text
Phase 0  Evidence Foundation          ✅
Phase 1  Experiment Workflow          ← 本 RFC
Phase 2  Evidence Evaluation          （另 RFC）
Phase 3  Experiment Sensor（ATR）      （另 RFC；须 Evidence Gate）
```

**禁止**因 Phase 0/1 完成而跳入 ATR。

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-19 | 0.1.0-draft | 首版 Phase 1 Workflow RFC：Context / Persist / Replay；排除 Sensor 与 Evaluation |
| 2026-07-19 | 1.0.0 | **Accepted**：WQ1–WQ5 关闭；授权受控 Manifest/Evidence 生命周期 |
