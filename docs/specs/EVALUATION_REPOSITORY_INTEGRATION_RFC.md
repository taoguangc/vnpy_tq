# Evaluation Repository Integration RFC（Phase 2.1）

> **Status**: Accepted（Frozen for Phase 2.1 Evaluation Persistence）  
> **Accepted date**: 2026-07-19  
> **Target version**: PAAF v0.3.x Phase 2.1  
> **Path**: `docs/specs/EVALUATION_REPOSITORY_INTEGRATION_RFC.md`  
> **Parent Specs**: `EVIDENCE_EVALUATION_IMPL_RFC.md`、`EVIDENCE_ENGINE_IMPL_RFC.md`、`EXPERIMENT_WORKFLOW_IMPL_RFC.md`（Accepted）  
> **Related**: Decision 015、`FEATURE_SENSOR_SPEC.md`（Accepted）  
> **规则优先级**: `AGENTS.md` > Parent Specs > 本 Implementation RFC > 代码  
> **实现门禁**: 仅授权 Repository 扩展 + 最小 evaluation fingerprint；仍禁止 Metric Calculator / ATR / Promotion / Ranking。

本文件限定 **Phase 2.1 实现切片**：把已 Accepted 的 Evaluation 契约变成可审计持久化产物，并接入现有 `EvidenceRepository`，**不修改**已 persist 的 EvidenceRecord。

**目标一句**：EvaluationResult 成为 Auditable Artifact，进入完整 Evidence Chain。

---

## 1. Objective

Phase 2 已交付内存契约：

```text
OutcomeDefinition / OutcomeRecord
MetricDefinition / MetricRecord
EvaluationResult
```

仍缺：

```text
EvaluationResult（内存）
        ↓
Auditable Artifact（磁盘）
        ↓
Replay / Evidence Chain
```

Phase 2.1 交付：

```text
Experiment
    ├── Manifest
    ├── Definitions（Outcome / Metric）
    ├── EvaluationResult(s)
    └── Evidence（可选链接；不 mutate）
```

成功标准：

1. Definition / EvaluationResult save → load 等价  
2. append-only；二次 save 同 id → `FileExistsError`  
3. KEEP 治理路径要求 EvaluationResult **已 persist**（不仅是内存对象）  
4. Replay 可恢复 evaluation + 可选 evidence 链接  
5. 无计算器、无 Sensor、无 Evidence 原地修改  

---

## 2. Scope

### 2.1 In Scope

| 组件 | 职责 |
|------|------|
| Repository API 扩展 | save/load/exists：OutcomeDefinition、MetricDefinition、EvaluationResult |
| Storage layout | experiment 目录下 definitions + evaluation results |
| Path / ID 校验 | 复用 Phase 0 路径穿越防护 |
| Replay helper（最小） | load evaluation；校验与 Evidence metadata `evaluation_id` 链接（若存在） |
| Contract tests | round-trip、append-only、isolation、KEEP persist gate、无 Evidence mutation |

### 2.2 Out of Scope（硬禁）

```text
Metric Calculator / formula 执行器
Sharpe / IC / PF 实现
ATRCompression / Feature Sensor / FeaturePipeline
Promotion / Sensor 状态机
Ranking / Strategy weight
修改已存在 EvidenceRecord
自动注入 Evidence.metadata
新建独立 EvaluationDatabase
```

---

## 3. Design Principle

```text
EvidenceRepository = persistence boundary
Evaluation models   = research evaluation contract
```

扩展 Repository **不**把评价逻辑塞进存储层：

| 允许 | 禁止 |
|------|------|
| 序列化 / 路径 / create-once | 计算 metric value |
| 校验 ID 路径安全 | 生成 evaluation_id |
| 校验 KEEP 需要已 persist evaluation（可选在 workflow 层） | 改写 Evidence conclusion |

---

## 4. Storage Layout（冻结候选）

与 EQ4（per-experiment definitions）对齐，建议：

```text
research/output/evidence/<experiment_id>/
├── manifest.json
├── definitions/
│   ├── outcomes/
│   │   └── <outcome_id>.json
│   └── metrics/
│       └── <metric_id>.json
├── evaluation/
│   └── <evaluation_id>.json
├── evidence/
│   └── <evidence_id>.json
└── artifacts/                 # 仍仅引用，不管理二进制
```

说明：

- Definitions 属于**实验声明**，不是全局 Registry  
- EvaluationResult 是独立 artifact，不是 Evidence 内嵌字段  
- 一个 Experiment 可有多个 EvaluationResult；一个 Evidence 通过显式 `metadata["evaluation_id"]` 链接其中一个（EQ3）  

### 4.1 备选布局（Open Question RQ1）

用户 Review 曾示意聚合文件：

```text
definitions/outcomes.json
definitions/metrics.json
```

默认倾向仍用 **per-id 文件**（与 Evidence/Manifest create-once 模式一致，避免改聚合文件破坏 append-only）。若 Accepted 选择聚合文件，须定义「整文件 create-once」或「键级 create-once」语义。

---

## 5. Repository Extension Contract

在现有 `EvidenceRepository` 上扩展（同一类，同一 `root_path`）：

```text
save_outcome_definition(def) / load_outcome_definition(experiment_id, outcome_id)
save_metric_definition(def)  / load_metric_definition(experiment_id, metric_id)
save_evaluation(result)      / load_evaluation(experiment_id, evaluation_id)

outcome_definition_exists(...)
metric_definition_exists(...)
evaluation_exists(...)
```

规则：

1. **Manifest 前置**：save definition / evaluation 要求 `manifest.json` 已存在（与 Evidence 一致）  
2. **create-once**：已存在 → `FileExistsError`  
3. **missing** → `FileNotFoundError`（不返回 `None`）  
4. **experiment 隔离**：`(experiment_id, *id)` 定位  
5. **路径穿越拒绝**：复用 Phase 0 `_validate_path_segment`  
6. **不生成 ID**；调用方提供全部 id  
7. **不 mutate Evidence**；无 `update_evidence` / `append_metrics` API  

### 5.1 KEEP Persist Gate（治理）

EQ2 Accepted：KEEP 必须有可审计 Evaluation。

Phase 2.1 建议在 **Workflow 或薄编排层** 强制：

```text
if decision == KEEP:
    require evaluation_exists(experiment_id, evaluation_id)
    require evidence.metadata["evaluation_id"] == evaluation_id  # 调用方显式写入
```

Repository 本身可只做 persistence；是否在 `save_evidence` 内强制 KEEP gate 见 Open Question RQ2。

默认倾向：**Workflow 强制，Repository 不解释 decision**（保持存储层无业务语义）。

---

## 6. Replay Contract

最小 replay：

```text
load_manifest(experiment_id)
load_evaluation(experiment_id, evaluation_id)
optional: load_evidence(experiment_id, evidence_id)
verify:
  evaluation.experiment_id == experiment_id
  if evidence linked:
      evidence.metadata.get("evaluation_id") == evaluation_id
      evaluation.evidence_id in {None, evidence.evidence_id}  # 或必须相等见 RQ3
```

不要求：重算 metrics、重跑 Sensor、加载 Artifact 二进制。

---

## 7. Package Boundary

```text
strategies/paaf/
    evidence/
        repository.py      # EXTEND — evaluation persistence methods
        workflow.py        # OPTIONAL thin link helpers（另 commit）
    evaluation/
        models.py          # Phase 2 — 不变
        __init__.py
```

禁止新建 `EvaluationDatabase` / `ResearchDB`。

指纹 helpers（`fingerprint_evaluation_body` 等）若尚未实现，可在本 Phase 放入 `evaluation/provenance.py` 或复用 `evidence/hashing.py`；**不**在本切片实现公式。

---

## 8. Test Contract

`tests/test_paaf_evaluation_repository.py`：

1. Definition / EvaluationResult round-trip  
2. append-only（二次 save 失败）  
3. Manifest 未 persist 时 save evaluation 失败  
4. 不同 experiment 隔离  
5. 路径穿越 ID 拒绝  
6. KEEP + Evidence 链接：replay 可恢复 `evaluation_id`（调用方显式 metadata）  
7. save evaluation **不**改变已存在 Evidence 文件内容  

禁止：真实 TQ；禁止收益断言；禁止 ATR fixture 之外的传感器逻辑。

---

## 9. Commit Boundary（Accepted 后）

| Commit | Message | 内容 |
|--------|---------|------|
| 1 | `docs(paaf): add evaluation repository integration rfc` | 本文件 + 索引 |
| 2 | `feat(paaf): extend evidence repository for evaluation` | Repository API + storage + tests |
| 3 | `feat(paaf): add evaluation persist replay helpers` | 可选：workflow/replay 薄封装 + KEEP gate tests |

Commit 2 为 Phase 2.1 核心；Commit 3 可延后若 Review 要求更小切片。

---

## 10. Open Questions（Implementation）— CLOSED

| ID | Accepted 决议 |
|----|---------------|
| RQ1 | Definitions 使用 per-id 文件：`definitions/outcomes/<id>.json`、`definitions/metrics/<id>.json` |
| RQ2 | KEEP persist gate 由 Workflow 负责；Repository 不解释 decision |
| RQ3 | 双方非空时 `EvaluationResult.evidence_id` 必须等于 `Evidence.evidence_id`；已链接 metadata 不得指向其它 evaluation |
| RQ4 | `save_evaluation` 必须校验引用的 Outcome/Metric Definition 已 persist |
| RQ5 | 本切片交付 `fingerprint_evaluation_body`（排除 created_at / runtime / path） |

---

## 11. Freeze Criteria

- [x] RQ1–RQ5 关闭或显式推迟  
- [x] 与 Phase 0/1/2 append-only、EQ1–EQ6 无矛盾  
- [x] Out of Scope 明确排除 Calculator / ATR / Promotion  
- [x] Commit 边界获同意  
- [x] `docs/README.md` 已索引  

---

## 12. Relation to Later Phases

```text
Phase 0    Evidence Foundation              ✅
Phase 1    Experiment Workflow              ✅
Phase 2    Evaluation Models                ✅
Phase 2.1  Evaluation Persistence           ← Accepted；实现中
Phase 3    Feature Sensor Framework         （另 RFC）
Phase 4    ATR Compression Experiment       （另 RFC）
Phase 5    Adaptive Strategy Layer
```

**禁止**因 Evaluation Models 完成而跳入 ATR。  
**禁止**在 Persistence 切片中实现 Metric Calculator。

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-19 | 0.1.0-draft | 首版 Phase 2.1：Evaluation 持久化接入 EvidenceRepository；Auditable Artifact |
| 2026-07-19 | 1.0.0 | **Accepted**：RQ1–RQ5 关闭；授权 Repository 扩展与 evaluation body fingerprint |
