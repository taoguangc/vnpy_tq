# Evidence Evaluation Implementation RFC（Phase 2）

> **Status**: Draft（Implementation RFC — Ready for Review）  
> **Accepted date**: —  
> **Target version**: PAAF v0.3.x Phase 2  
> **Path**: `docs/specs/EVIDENCE_EVALUATION_IMPL_RFC.md`  
> **Parent Specs**: `EVIDENCE_ENGINE_SPEC.md`、`EVIDENCE_ENGINE_IMPL_RFC.md`、`EXPERIMENT_WORKFLOW_IMPL_RFC.md`（Accepted）  
> **Related**: `FEATURE_SENSOR_SPEC.md`、Decision 015（Accepted）  
> **规则优先级**: `AGENTS.md` > Parent Specs > 本 Implementation RFC > 代码  
> **实现门禁**: 本 RFC **Accepted** 之前，禁止提交 Evaluation 代码；仍禁止 ATR / FeaturePipeline / Promotion / DecisionEngine。

本文件限定 **Phase 2 实现切片**：在 Experiment Workflow 之上，标准化 Outcome / Metric / Evaluation Result，使 Evidence 可统计验证，而不被单个 Sensor（如 ATR）反向塑形。

**目标一句**：定义通用 Evaluation 契约；任何 Sensor / Detector 假设都能挂接，不实现具体 Alpha。

---

## 1. Objective

Phase 0–1 已交付：

```text
Hypothesis → Experiment → Manifest → ArtifactReference → Evidence → Replay
```

仍缺标准化：

```text
Outcome Extraction
Metric Calculation
Evaluation Result
```

当前 `EvidenceRecord.outcome` / `metrics` 仅为扁平 Mapping，不足以表达：

- 预登记度量定义  
- 结果窗口与样本量  
- 评价结论与可审计计算身份  

Phase 2 交付：

```text
Artifact Reference
        ↓
OutcomeRecord
        ↓
MetricRecord(s)
        ↓
EvaluationResult
        ↓
(link to Evidence; append-only)
```

成功标准：

1. Evaluation 对象不可变、可序列化、可 fingerprint  
2. Metric **预登记**后才可出现在结果中（禁止事后发明指标）  
3. Evaluation **不 mutate** 已 persist 的 EvidenceRecord  
4. Fixture 可跑通完整 evaluation → evidence 组装；无真实 Sensor / 无 TQ 大数据  

---

## 2. Scope

### 2.1 In Scope

| 组件 | 职责 |
|------|------|
| `OutcomeDefinition` | 预登记：测什么、窗口、单位 |
| `OutcomeRecord` | 一次 outcome 观测汇总（非逐 bar 大表） |
| `MetricDefinition` | 预登记：度量名、公式身份、停止条件键 |
| `MetricRecord` | 一次度量结果（标量 + sample_n） |
| `EvaluationResult` | 将 outcome/metrics 汇总为 KEEP/REVERT/HOLD + 引用 |
| Evaluation fingerprint helpers | 确定性 hash（复用 Phase 0 hashing） |
| Persist evaluation artifacts | 经 Repository 扩展或同布局落盘 |
| Contract tests | 预登记校验、append-only、fingerprint、与 Evidence 链接 |

### 2.2 Out of Scope（硬禁）

```text
ATRCompressionSensor / 任何 Feature 计算
FeaturePipeline / FeatureResult 生产
真实行情 Parquet 批处理引擎
IC / Sharpe / PF 作为默认内置必选度量库（可登记，但不在 Phase 2 实现计算器）
Promotion Automation / Sensor 状态机推进
DecisionEngine / Strategy ranking / 交易信号
自动把 KEEP 写成 PRODUCTION
参数搜索 / 收益优化
```

Phase 2 **只定义契约与组装**；具体统计函数（如 realized volatility）可在后续 Evaluation Library RFC 中按需登记，本切片可用 **caller-supplied numeric results**（类似 fixture hash）。

---

## 3. Design Principle：Generic before Sensor

正确：

```text
Generic Evaluation Contract
        ↓
Any Sensor / Detector Hypothesis
```

禁止：

```text
ATR needs X
        ↓
Evaluation shaped only for ATR
```

因此：

- 字段命名不得硬编码 `atr_*` / `compression_*`  
- Example 可用 compression 叙事，契约本身保持 subject-agnostic  

---

## 4. Append-only vs “Evidence Update”

Parent Spec 示意曾写 “Evidence Update”。Phase 2 **明确**：

| 允许 | 禁止 |
|------|------|
| 新建 `EvaluationResult` 并 persist | 修改已存在 `EvidenceRecord` |
| 在 **尚未 persist** 的 `build_evidence` 时填入 outcome/metrics 摘要 | `save_evidence` 后原地改 conclusion |
| 新 `evidence_id` 承载修订结论（新对象） | overwrite 同 `evidence_id` |

推荐主路径：

```text
1) Persist Manifest + ArtifactReference
2) Build EvaluationResult (from caller-provided outcomes/metrics)
3) Persist EvaluationResult
4) build_evidence(..., outcome=summary, metrics=summary, decision=...)
5) persist_evidence
```

或：

```text
Evidence first (HOLD + empty metrics) → 禁止
```

Phase 2 默认要求：**有 EvaluationResult 引用后才允许非空 metrics 的 KEEP**（HOLD/REVERT 仍须有 EvaluationResult 或显式空评估登记——见 Open Questions EQ2）。

---

## 5. Package Boundary

```text
strategies/paaf/evidence/
    models.py
    hashing.py
    provenance.py
    repository.py
    workflow.py
    evaluation.py          # Phase 2 — NEW
    __init__.py
```

| 模块 | 拥有 | 禁止 |
|------|------|------|
| `evaluation.py` | Definition/Record/Result 契约、组装、预登记校验 | I/O 细节（委托 Repository）；Sensor；统计库 |
| `repository.py` | 扩展 save/load evaluation（append-only） | 计算指标；生成 ID |
| `workflow.py` | 可选：链接 EvaluationResult → Evidence | 自动评价 |

命名：

- 允许：`EvaluationResult`、`MetricDefinition`、`OutcomeRecord`  
- 禁止：`AlphaScore`、`StrategyRanker`、`PerformanceOptimizer`  

---

## 6. Object Contracts（草案）

### 6.1 OutcomeDefinition / OutcomeRecord

```python
@dataclass(frozen=True)
class OutcomeDefinition:
    outcome_id: str                 # 调用方提供，如 OUT-RV-FWD60
    name: str                       # e.g. realized_volatility
    window: Mapping[str, int | str] # bars_forward, bar, session...
    unit: str = ""
    description: str = ""
    schema_version: str = "1.0"

@dataclass(frozen=True)
class OutcomeRecord:
    outcome_id: str                 # 必须引用已登记 Definition
    values: Mapping[str, float | str]
    sample_n: float
    artifact_refs: tuple[str, ...] = ()  # artifact_id 列表
    schema_version: str = "1.0"
```

### 6.2 MetricDefinition / MetricRecord

```python
@dataclass(frozen=True)
class MetricDefinition:
    metric_id: str                  # e.g. MET-SAMPLE-N, MET-MEAN-RV
    name: str
    formula_id: str                 # 稳定公式身份字符串；非可执行代码
    higher_is_better: bool | None = None
    description: str = ""
    schema_version: str = "1.0"

@dataclass(frozen=True)
class MetricRecord:
    metric_id: str
    value: float
    sample_n: float
    schema_version: str = "1.0"
```

规则：

- `MetricRecord.metric_id` ∈ 预登记 `MetricDefinition` 集合  
- Phase 2 **不**实现 `formula_id` 执行器；只校验存在与类型  

### 6.3 EvaluationResult

```python
@dataclass(frozen=True)
class EvaluationResult:
    evaluation_id: str              # 调用方提供，如 EVAL-20260719-001
    experiment_id: str
    evidence_id: str | None         # 可先评后挂 evidence；或评完再建 evidence
    hypothesis: str
    decision: str                   # KEEP | REVERT | HOLD
    outcome_refs: tuple[str, ...]   # outcome_id
    metric_refs: tuple[str, ...]    # metric_id（结果侧用 records 携带值）
    outcomes: tuple[OutcomeRecord, ...]
    metrics: tuple[MetricRecord, ...]
    created_at: datetime            # 调用方注入
    notes: str = ""
    metadata: Mapping[str, str] = ...
    schema_version: str = "1.0"
```

约束：

- `decision` 与 Evidence 相同枚举  
- `outcomes`/`metrics` 只读 Mapping；frozen dataclass  
- 禁止交易语义键：`direction` / `action` / `weight` / `buy` / `sell`  
- `created_at` **不**进入 evaluation body fingerprint  

### 6.4 Fingerprints

```text
fingerprint_outcome_definition
fingerprint_metric_definition
fingerprint_evaluation_body   # excludes created_at
```

同输入 → 同 hash；键序无关。

---

## 7. Persistence Layout

扩展 Phase 0/1 目录（仍 filesystem）：

```text
research/output/evidence/<experiment_id>/
├── manifest.json
├── evidence/<evidence_id>.json
├── evaluation/
│   ├── definitions/
│   │   ├── outcomes/<outcome_id>.json
│   │   └── metrics/<metric_id>.json
│   └── results/<evaluation_id>.json
└── artifacts/   # 仍仅引用
```

Repository 扩展建议 API：

```text
save_outcome_definition / load_outcome_definition
save_metric_definition / load_metric_definition
save_evaluation / load_evaluation
*_exists ...
```

规则与 Manifest/Evidence 相同：create-once、未知 ID → `FileNotFoundError`、路径穿越拒绝。

---

## 8. Workflow Integration

最小增量（Accepted 后实现）：

```python
# 伪代码
workflow.persist_manifest(manifest)
repo.save_outcome_definition(...)
repo.save_metric_definition(...)
evaluation = build_evaluation_result(...)  # evaluation.py
repo.save_evaluation(evaluation)
evidence = workflow.build_evidence(
    ...,
    decision=evaluation.decision,
    outcome=flatten(evaluation.outcomes),
    metrics=flatten(evaluation.metrics),
    metadata={"evaluation_id": evaluation.evaluation_id},  # 仅当调用方显式传入
)
workflow.persist_evidence(evidence)
```

WQ4 延续：Workflow **不自动**注入 metadata；`evaluation_id` 链接须调用方显式写入 `metadata` 或未来一等字段（见 EQ3）。

---

## 9. Test Contract

`tests/test_paaf_evidence_evaluation.py`：

1. Definition / Record / Result immutable + JSON round-trip  
2. 未登记 metric_id → 构建 EvaluationResult 失败  
3. Body fingerprint 排除 `created_at`  
4. Repository append-only + path isolation  
5. 禁止交易语义键  
6. Fixture 路径：caller-supplied values → Evaluation → Evidence（无 ATR）  

禁止：真实 TQ；禁止以收益高低为断言。

---

## 10. Commit Boundary（Accepted 后）

| Commit | Message | 内容 |
|--------|---------|------|
| 1 | `docs(paaf): add evidence evaluation implementation rfc` | 本文件 + 索引 |
| 2 | `feat(paaf): add evidence evaluation models` | `evaluation.py` 契约 + model tests |
| 3 | `feat(paaf): add evidence evaluation repository` | Repository 扩展 + tests |
| 4 | `feat(paaf): link evaluation to experiment workflow` | 可选编排 helper + integration test |

---

## 11. Open Questions（Implementation）

| ID | 问题 | 默认倾向 |
|----|------|----------|
| EQ1 | `EvaluationResult.evidence_id` 在评测时是否必填？ | 可选；允许先 EVAL 再建 Evidence，再建时回填须 **新** EvaluationResult（不可改旧对象） |
| EQ2 | 无 Evaluation 是否允许 `decision=KEEP`？ | 否；KEEP 必须有已 persist 的 EvaluationResult 引用 |
| EQ3 | `evaluation_id` 进 Evidence 一等字段还是 metadata？ | Phase 2：metadata 显式键 `evaluation_id`；一等字段留待 schema bump |
| EQ4 | Outcome/Metric Definition 作用域：全局还是 per-experiment？ | per-experiment 目录；跨实验复用靠相同 id 内容指纹比对 |
| EQ5 | Phase 2 是否内置任何公式实现？ | 否；仅 `formula_id` 字符串身份 |
| EQ6 | `sample_n` 用 `float` 还是 `int`？ | `float`（与现有 EvidenceRecord.metrics 一致）；语义为计数 |

关闭 EQ1–EQ6 后可将本 RFC 标为 **Accepted**。

---

## 12. Freeze Criteria

- [ ] EQ1–EQ6 关闭或显式推迟  
- [ ] 与 Phase 0/1 append-only / ID ownership 无矛盾  
- [ ] Out of Scope 明确排除 ATR / Promotion / 内置绩效优化  
- [ ] Commit 边界获同意  
- [ ] `docs/README.md` 已索引  

---

## 13. Relation to Later Phases

```text
Phase 0  Evidence Foundation           ✅
Phase 1  Experiment Workflow           ✅
Phase 2  Evidence Evaluation           ← 本 RFC
Phase 3  Feature Sensor Framework      （另 RFC）
Phase 4  ATR Compression Experiment    （另 RFC；须 Evaluation Gate）
Phase 5  Decision / Strategy Adaptation
```

**禁止**因 Workflow 完成而跳入 ATR。  
**禁止**用 ATR 需求反向改写本 Evaluation 契约。

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-19 | 0.1.0-draft | 首版 Phase 2 Evaluation RFC：Outcome/Metric/EvaluationResult；append-only；Generic-first |
