# PAAF 路线图

> 版本：3.0.0 · 更新日期：2026-07-19  
> 路线图**可变**；宪章与规格冻结后，改路线图不等于改哲学。

---

## Sprint 计划

### 阶段总览

```text
Phase 0  Research Chaos（AFF）           — 已结束
Phase 1  Architecture Foundation（v0.1） — 已结束（Tag v0.1.1）
Phase 2  Evidence Platform（v0.2+）      — 当前
Phase 3  Production CTA                  — 未开始
```

### Sprint 1 — Framework（已完成）

目标：**框架跑通，不关心收益。**

| 交付物 | 状态 |
|--------|------|
| Foundation + Context Spec + Context Engine | **完成** → Tag `v0.1.1` |
| CSV Logger / vn.py 可加载 Strategy | 待做（可与 Phase 2 并行） |

#### PAAF v0.1.1 里程碑

```text
PAAF v0.1.1

✓ Context API Frozen
✓ Context Lifecycle Frozen
✓ Context Contract Frozen

Market State
  Not Implemented
```

### Sprint 2 — Evidence Platform / Detector Framework（当前）

目标：**先 Framework，后 OPP；无证据不进 Production。**

| 版本 | 交付 | 状态 |
|------|------|------|
| v0.2.0 | `docs/specs/DETECTOR_FRAMEWORK_SPEC.md` | **Accepted**（Decision 013） |
| v0.2.1 | `DetectionResult` / `PatternState` / 必要类型（`Signal` Deprecated） | **完成**（Commit 005/006） |
| v0.2.2 | `Opportunity` + DetectionResult 引用 + lineage | **完成**（Commit 007/008） |
| v0.2.3 | Descriptor Catalog Registry + Capability Query | **完成**（Commit 009/010） |
| v0.2.4 | Detector Pipeline Verification + `DEMO_MINIMAL` | **完成**（Commit 011/012；待分支 Review） |

原则：Decision 011（无证据不进生产）；Decision 012（`feature/*` / `research/*`）。

真实 OPP（如 OPP16）在 v0.2.4 管线验证之后，进入 v0.3.x 证据驱动实现。

#### PAAF v0.2.3 里程碑

```text
✓ Context
✓ DetectionResult
✓ Opportunity
✓ Registry

Detector Framework Ready
```

Registry 以后只增加 Descriptor；不得为新 Detector 重写基础架构。Demo Pipeline 验证仍属于 v0.2.4。

#### PAAF v0.2 Detector Framework 里程碑

```text
✓ Context
✓ DetectionResult
✓ Opportunity
✓ Registry
✓ Detector Pipeline Verification
✓ Minimal Opportunity Logger

Detector Framework Complete
Alpha Not Implemented
```

下一阶段：**v0.3 Evidence Engine Core 实现**（Manifest / ArtifactReference / EvidenceRecord / Provenance）。
Market State 顺延到 v0.4；ATR Compression 仍为 EXPERIMENT Sensor 候选，不得跳过 Evidence。

实现顺序（禁止跳过）：

```text
Evidence Engine Implementation RFC（Accepted）
    → Evidence Engine Skeleton（models ← 当前 → provenance → repository）
    → Evidence Storage / Evaluation
    → ATR Compression Experiment Sensor
    → Promotion Review
```

| Spec / ADR | 状态 | 说明 |
|------|------|------|
| `FEATURE_SENSOR_SPEC.md` | **Accepted** | 双路径；Q1–Q5 关闭 |
| `EVIDENCE_ENGINE_SPEC.md` | **Accepted** | Evidence Object + Validation Protocol + Storage |
| `EVIDENCE_ENGINE_IMPL_RFC.md` | **Accepted** | IQ1–IQ5 关闭；Phase 0 models 已授权 |
| Decision 015 | **Accepted** | 双路径；Intent+Evidence+Enablement |

---

## Release

| 版本 | 含义 |
|------|------|
| v0.1.0 | Framework Skeleton |
| v0.1.1 | Context Engine Foundation（**Tagged**） |
| v0.2.0 | Detector Framework Spec |
| v0.2.1–0.2.4 | DetectionResult → Opportunity → Registry → Pipeline Verification |
| v0.3.x | Evidence Engine |
| v0.4.x | Market State（证据之后） |
| v0.5.x | Opportunity Library（真实 OPP） |
| v0.6.x | Decision Engine |
| v0.7.x | Execution Adapter |
| v1.0 | Production CTA |

---

## Git 约定

### Commit

```text
feat(context): add Context Engine
feat(detector): implement OPP16
feat(logger): export trade log
refactor(strategy): decouple signal engine
docs: update detector specification
test: add detector unit tests
```

禁止：`update` / `fix` / `modify` 这类无信息提交说明。

### Branch

- `main`：永远可运行（稳定点；Decision 012）
- 功能：`feature/detector-framework`、`feature/market-state` …
- 实验：`research/e0-compression`、`research/e3-transition` …
- 完成：Review 后 Merge 回 `main`；发布打 Annotated Tag

---

## 明确不做（在论证通过前）

- 机器学习 / 深度学习信号
- 无约束参数搜索与自动「优化到年化」
- 为证明 Brooks 正确而扭曲数据或成本
- 大爆炸式重写整个 `strategies/` 树
- 将 Feature Engine 插入冻结信号主链（见下）

## 后续项（未立项实现）

| 项 | 状态 | 说明 |
|----|------|------|
| Feature Layer（ATR/EMA/ADX 等） | E0 假设 | 若实现，只作 Context/Risk 的计算依赖；**不得**改主链为 Market→Feature→Context |
| `research/run_*.py` 三层治理 | 待治理专项 | experiments / validation / reports；不与 Foundation 补强捆绑 |

---

## 变更方式

更新本文件时：改「更新日期」，在 `CHANGELOG.md` 记一条；**不**悄悄改宪章条款。
