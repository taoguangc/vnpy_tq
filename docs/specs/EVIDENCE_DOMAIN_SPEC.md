# Evidence Domain Specification

> **Status**: Accepted（Frozen for Evidence Domain Contract v1.0）
> **Accepted date**: 2026-07-20
> **Version**: 1.0.0
> **Decision**: 017（Evidence-first Research Roadmap）；亦服从 001 / 011 / 015 / 016
> **Path**: `docs/specs/EVIDENCE_DOMAIN_SPEC.md`
> **规则优先级**: `AGENTS.md` > Decision 017 > 本 Spec > `EVIDENCE_ENGINE_SPEC.md`（引擎叙事）> 实现代码
> **变更规则**: 先改本 Spec，再改代码；破坏性字段变更须升 `schema_version` 并 ADR。
> **实现门禁**: 本 Spec **只冻结研究对象合同**。不授权 Workflow / Repository API 变更、Portfolio、Dashboard、新 OPP/Alpha。

**一句话**：冻结「实验条件 → 产物引用 → 评估 → 证据归档」的领域对象与不变式；不规定怎么存、怎么跑、怎么展示。

**与 `EVIDENCE_ENGINE_SPEC.md` 的关系**：

| 文档 | 职责 |
|------|------|
| **本 Spec** | Domain Contract：对象是什么、不可变规则、禁止行为 |
| `EVIDENCE_ENGINE_SPEC.md` | Engine 目标、晋级叙事、与 Feature/Opportunity 边界 |
| `*_IMPL_RFC.md` | 实现切片（Workflow / Repository / Evaluation 持久化） |

冲突时：本 Spec + Decision 017 > Engine Spec 中过时的「草案」描述。

**参考实现（行为不得被本轮文档静默改写）**：

- `strategies/paaf/evidence/models.py`
- `strategies/paaf/evaluation/models.py`
- `strategies/paaf/evidence/provenance.py`

---

## 1. Purpose

Evidence Domain 回答：

1. 什么是 Experiment（实验条件身份）？
2. 什么是 Artifact（产物引用）？
3. 什么是 Evaluation（评估判断）？
4. 什么是 Evidence（结论归档）？
5. 它们如何关联？
6. 哪些字段 / 对象不可变？
7. 哪些行为禁止？

Evidence Domain **不**回答：

- 如何落盘 / 数据库 schema
- 如何展示 / Dashboard / Web UI
- 如何编排 Workflow / 跑脚本
- 如何生成交易 Alpha / 下单

---

## 2. Design Principles

1. **Research is append-only**（Decision 017）：不覆盖、不改写历史 Evidence / Closed 实验结论。
2. **Evaluation ≠ Evidence**：Evaluation 是 Assessment（按协议的当前判断）；Evidence 是归档的研究结论快照。
3. **Evaluation 不 mutate EvidenceRecord**：评估结果不得就地改写已发布 Evidence。
4. **Artifact 用 Reference，不内嵌内容**：Evidence / Manifest 只持有 `ArtifactReference`（或 URI+hash），不塞入数据集本体。
5. **Negative Evidence 是一等公民**（Decision 017）：与 Positive 同等归档价值。
6. **No detector enters Production without Evidence**（Decision 011）：本 Domain 为门禁提供可审计对象，不负责下单。
7. **对象默认 frozen / 映射只读**：实现须阻止 `evidence.decision = "KEEP"` 这类原地赋值。

---

## 3. Domain Model

当前冻结 `schema_version = "1.0"`（与实现常量一致）。

### 3.1 ExperimentManifest

**定义**：一次实验的**可复现身份**——描述假设所绑定的条件与指纹，**不是**实验结果。

**是**：

- `experiment_id`、主体 id/version（实现字段名现为 `sensor_id` / `sensor_version`，亦用于 detector 等主体；语义为 **subject 身份**）
- `parameters` + `parameter_fingerprint`
- `code_revision` / `data_fingerprint` / `environment_fingerprint`
- `artifact_refs: tuple[ArtifactReference, ...]`

**不是 / 禁止**：

```text
ExperimentManifest.result = ...
ExperimentManifest.decision = ...
ExperimentManifest.pnl = ...
```

Manifest 不得承载 KEEP/REVERT/HOLD，不得承载交易结果。

### 3.2 ArtifactReference

**定义**：实验产生或依赖的**不可变产物**的引用；永不加载产物内容本身。

最低字段（已冻结）：

| 字段 | 含义 |
|------|------|
| `artifact_id` | 稳定 ID |
| `uri` | 相对或逻辑 URI |
| `content_hash` | 内容指纹 |
| `artifact_type` | 类型标签（如 `feature_results` / `detection_events`） |
| `schema_version` | 本引用模式版本 |

典型类型示例（非穷尽）：dataset、feature_results、detection_events、report、log。  
**禁止**把 Artifact 字节流或 DataFrame 直接塞进 EvidenceRecord / Manifest。

### 3.3 EvaluationResult

**定义**：按预注册 Outcome / Metric 协议做出的 **Assessment（评估）**，不是市场真相（Truth）。

表达的是：

> 在声明的窗口、样本与度量下，当前判断是 KEEP / REVERT / HOLD。

不是：

> 该形态在宇宙中必然有效。

关联对象（实现已有）：

- `OutcomeDefinition` / `OutcomeRecord` — 预注册测什么、测到什么聚合值
- `MetricDefinition` / `MetricRecord` — 预注册指标身份与标量结果
- `EvaluationResult` — 聚合上述引用 + `decision` + `hypothesis` + 可选 `evidence_id`

规则：

- Evaluation **可以**引用尚未创建的 Evidence（`evidence_id is None`），此时不得宣称 KEEP（实现已约束）。
- Evaluation **不得**改写已存在的 `EvidenceRecord` 字段。
- Evaluation 元数据禁止交易语义键（实现：`action` / `buy` / `sell` / `direction` / `side` / `weight` 等）。

### 3.4 EvidenceRecord

**定义**：对研究结论的**不可变归档**。

最低语义（v1.0 实现字段）：

| 语义 | v1.0 字段 |
|------|-----------|
| 证据身份 | `evidence_id` |
| 实验身份 | `experiment_id` |
| 主体 | `subject_kind` / `subject_id` / `subject_version` |
| 假设 | `hypothesis` |
| 治理决策 | `decision` ∈ {`KEEP`, `REVERT`, `HOLD`} |
| 产物引用 | `feature_artifact_uri` + `artifact_hash`（历史字段名；适用于任意主体产物 URI） |
| 时间 | `created_at`（须带时区） |
| 观测/结果/窗口/度量 | `observation` / `outcome` / `window` / `metrics` |
| 协议 | `data_protocol_version` |
| 扩展 | `metadata`（仅 `str→str`） |

**评估引用**：v1.0 通过 `metadata["evaluation_id"]`（及 Manifest/Repository 并列文件）关联 Evaluation；正式 `evaluation_refs` 元组留待 schema 升级（见 §10）。

**谱系**：条件变化或结论修订 → **新** `evidence_id` / 新 `experiment_id`；可用 metadata 声明 `parent`（见 §5）。

---

## 4. Lifecycle

```text
ExperimentManifest（条件身份）
        ↓
ArtifactReference（产物引用，可多项）
        ↓
EvaluationResult（Assessment）
        ↓
EvidenceRecord（归档结论）
```

说明：

- 顺序是逻辑依赖，不是强制同进程 API。
- Closed 实验：禁止覆盖其 Manifest / Artifact / Evaluation / Evidence 内容。
- 新 Context / 新 Outcome / 新数据协议 → 新 `experiment_id`（Decision 017）；可声明 `parent=<closed_id>`。

---

## 5. Immutability Rules

1. Domain 对象发布后字段不可变（`frozen` dataclass + 只读 Mapping）。
2. **禁止**原地修改已归档 Evidence：

```python
# FORBIDDEN
evidence.decision = "KEEP"
```

3. 结论变化必须新记录：

```text
EV-...-001   decision=HOLD     classification=INCONCLUSIVE|NEGATIVE
EV-...-014   decision=KEEP     parent=EV-...-001
```

4. Closed Experiment 的磁盘产物与 Index 文档：禁止改写结论；纠错用新 Run / 新 ID，并标注 INVALID 旧 Run（若适用）。
5. `created_at` 是审计时钟；证据内容指纹可排除时钟（见 Provenance）。

---

## 6. Provenance Contract

Provenance 保证「同一声明条件可复核」，不是保证「赚钱」。

最低要求：

| 指纹 | 含义 |
|------|------|
| `parameter_fingerprint` | 与 `parameters` 一致 |
| `data_fingerprint` | 数据构造 / 文件集合 |
| `code_revision` | 代码修订（如 git HEAD） |
| `environment_fingerprint` | 运行环境摘要 |
| Artifact `content_hash` | 产物字节级复核 |

辅助约定（实现已有）：

- `fingerprint_parameters` / `fingerprint_manifest` / `fingerprint_evidence_body`
- Observation Key 可组装审计键，但**不**污染 FeatureResult 本体

Decision 001：正式证据默认绑定冻结 TQ 离线数据协议版本字符串。

---

## 7. Evidence Classification

**Classification** 描述证据的科学类别；**decision** 描述治理动作。二者相关但不等价。

### 7.1 Classification（冻结枚举）

| 值 | 含义 |
|----|------|
| `POSITIVE` | 预注册门槛下支持假设（与治理 KEEP 常同向，但不自动 Production） |
| `NEGATIVE` | 预注册门槛下否定或明确无边沿（一等资产；如 OPP16 EXP001） |
| `INCONCLUSIVE` | 样本/效应不足以判定 |
| `REJECTED` | 协议失败、无效 Run、或假设被正式拒绝（含数据错误 INVALID 等） |
| `HOLD` | 暂停晋级 / 证据冲突 / 仅作冻结等待（治理上不前进） |

### 7.2 Decision（治理，已实现）

`KEEP` | `REVERT` | `HOLD`

### 7.3 v1.0 承载方式

正式字段 `classification` 尚未进入 `EvidenceRecord` schema 1.0。  
**冻结约定**：Classification 必须写入 `metadata`，推荐键：

- `hypothesis_conclusion` — 实验结论标签（如 `inconclusive` / `association_detected` / Negative 叙事）
- 或显式 `classification` ∈ 上表（字符串）

后续升 schema 将 Classification 升为一等字段时，不得抹去历史 metadata；须可迁移。

**Negative Evidence** 不得因「不好看」删除、覆盖或拒绝登记。

---

## 8. Serialization Contract

1. 每个 Domain 对象提供确定性 `to_dict()` / `from_dict()` 往返。
2. `schema_version` 必须存在且受实现校验。
3. 时间字段使用带时区的 ISO-8601。
4. Mapping 键为 `str`；Evidence `metadata` 值仅为 `str`；数值映射保持有限数。
5. 破坏性变更 → 新 `schema_version` + ADR；旧文件保留可读或迁移工具，禁止静默改写。

---

## 9. Forbidden Behaviors

| 禁止 | 原因 |
|------|------|
| 原地改 Evidence / Closed 产物 | 破坏 append-only |
| Evaluation mutate EvidenceRecord | Assessment 污染 Truth 归档 |
| Manifest 写入 result/PnL/decision | 条件与结论混淆 |
| Artifact 内容内嵌进 Evidence | 体积与可变性失控 |
| 无 Evidence 宣称 Production | 违反 Decision 011 |
| Dashboard / UI / DB 方言进入本 Spec | 合同被实现绑架 |
| 把 Workflow / Repository API 写进本 Spec | Domain 被编排层反向推动 |
| 删除 Negative / Inconclusive 记录 | 违反 Decision 017 |
| 交易语义键进入 Evaluation metadata | 证据层污染执行层 |

---

## 10. Open Questions

| ID | 问题 | 状态 |
|----|------|------|
| DQ1 | `ExperimentManifest.sensor_id` 是否重命名为 `subject_id`？ | **Deferred** — v1.0 保持字段名；语义按 subject 理解 |
| DQ2 | `EvidenceRecord.evaluation_refs: tuple[str, ...]` 是否升为一等字段？ | **Deferred** — v1.0 用 metadata；升 schema 时处理 |
| DQ3 | `classification` 是否升为一等字段？ | **Deferred** — v1.0 用 metadata；枚举已在 §7 冻结 |
| DQ4 | `feature_artifact_uri` 是否泛化为 `primary_artifact_uri`？ | **Deferred** — 历史名保留；语义为 primary artifact URI |
| DQ5 | Portfolio / Query 对象是否进入 Domain？ | **Out of scope** — Decision 017 概念层；另 Spec |

关闭 DQ 须新 ADR 或本 Spec 小版本，并伴随契约测试；**本轮不改代码**。

---

## 11. Freeze Gate

本 Spec **Accepted** 当且仅当：

- [x] 不含 Workflow / Repository API / Dashboard / Alpha 定义
- [x] 明确 append-only 与 Evidence 不可 mutation
- [x] 明确 Evaluation ≠ Evidence
- [x] 明确 Negative Evidence 一等公民与 Classification 枚举
- [x] 与现有 `schema_version=1.0` 实现可对齐（含 Deferred 字段策略）

下一阶段顺序（Decision 017 / 审计约定）：

```text
EVIDENCE_DOMAIN_SPEC（本文件）
        ↓
Contract Alignment（测试与文档对齐；仍尽量不改行为）
        ↓
Evidence Repository refinement
        ↓
Portfolio Index
```

Registry `_adapt_legacy` 删除见 ROADMAP **CLEANUP-001**；不在本 Spec 范围。

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-20 | 1.0.0 | Accepted：冻结 Evidence Domain Contract；不改实现行为 |
