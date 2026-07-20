# ABR-001 — Architecture Baseline Review

> **Review ID**: ABR-001  
> **Title**: Architecture Baseline Review（第一次架构基线审计）  
> **Date**: 2026-07-20  
> **Status**: Completed  
> **Scope**: Documentation audit only — **no Python code changes** in this review  
> **Baseline refs**: Decision 001–017；`EVIDENCE_DOMAIN_SPEC.md` v1.0；`DETECTOR_FRAMEWORK_SPEC.md`；`research/README.md`  
> **Path**: `docs/reviews/ABR-001_ARCHITECTURE_FREEZE_REVIEW.md`

**一句话**：将 Phase 2（Evidence Foundation）收口为可引用的架构基线；记录概念漂移与
append-only 风险为 Backlog，不在本轮修实现。

**制度**：此后每完成一个大架构阶段须通过 ABR（`ABR-002` …）方可进入下一阶段：

```text
Spec → Implementation → Tests → ABR → Next Phase
```

**Phase 边界（防误解）**：

| 声明 | 含义 |
|------|------|
| Phase 2 — Evidence Foundation **Completed** | Detector Framework + Evidence Domain + Research Governance 已冻结 |
| **Completed ≠ v0.3 Completed** | v0.3 Evidence Platform（Repository Append-only / Projection / Portfolio）仍进行中 |

---

## Executive Summary

| 检查项 | 结论 |
|--------|------|
| A Vocabulary | **Pass with notes** — 核心词义可唯一化；遗留文档仍有 `Signal` 表述漂移 |
| B Lifecycle | **Pass** — 研究链与检测链两条合法路径清晰 |
| C Append-only | **Pass with notes** — Repository 用 `open("x")` 防覆盖；API 名仍为 `save_*` |
| D Decision xref | **Pass** — 011⊂017 重申；008→015 为受控演进，非冲突 |
| E Boundary | **Pass** — Domain Spec 不知 Portfolio；Detector 不依赖 Evidence 写路径 |
| F Layer dependency | **Pass with notes** — 未发现 Projection→写回流；命名与文档滞后列入 Backlog |
| G Backlog | 见 §F |

**Architecture Baseline**：自本 ABR 起，新 Context / Detector / Evidence / Validation /
Decision / Execution 应以本文件 + Accepted Specs 为参照，而非以偶然实现文件为参照。

---

## A. Vocabulary Audit

| 术语 | 唯一含义（基线） | 不得混用为 |
|------|------------------|------------|
| **Experiment** / `ExperimentManifest` | 假设与实验**条件身份** | 实验结果、PnL、decision |
| **Artifact** / `ArtifactReference` | 不可变产物的**引用**（URI+hash） | 产物内容本体；Evidence 本身 |
| **Evaluation** / `EvaluationResult` | **Assessment**（按协议的当前判断） | 市场真相；已归档 Evidence |
| **Evidence** / `EvidenceRecord` | 研究结论的**不可变归档** | Repository 实现；Dashboard |
| **DetectionResult** | Detector 发布的检测证据（非下单） | 遗留 `Signal`；Opportunity |
| **Opportunity** | 可选提升的研究机会目录对象 | 自动订单；Evidence |
| **Projection** | Domain 的只读观察方式（Portfolio/Timeline/…） | Domain 写模型；交易层 |
| **FeatureResult** | Feature Sensor 观测（无 Direction） | DetectionResult |
| **Context** | 市场状态语义层 | Feature 指标层 |

**发现（不修，仅记录）**：

| ID | 发现 | 严重度 |
|----|------|--------|
| VOC-001 | 历史文档/注释仍出现 `Signal \| None`；基线输出为 `DetectionResult \| None` | Medium — 已在 `02_ARCHITECTURE.md` v3.0 首页纠正；其它旧段落待扫 |
| VOC-002 | `ExperimentManifest.sensor_id` 语义含 detector 等主体（DQ1 Deferred） | Low — Domain Spec 已注明 |
| VOC-003 | `feature_artifact_uri` 历史字段名泛化不足（DQ4 Deferred） | Low |
| VOC-004 | `EVIDENCE_ENGINE_SPEC.md` §2 仍标「接口草案」，与 Domain Spec Accepted 并存 | Low — 文档对齐 backlog |

---

## B. Lifecycle Audit

### B.1 研究证据链（唯一合法）

```text
ExperimentManifest
        ↓
ArtifactReference（可多项）
        ↓
EvaluationResult
        ↓
EvidenceRecord
```

禁止：`Experiment → Evidence` 跳过 Evaluation 却宣称已评估晋级（探索冒烟除外，不得称 E1+）。  
禁止：Evaluation mutate 已发布 Evidence。

### B.2 检测器链（唯一合法）

```text
Context → Detector → DetectionResult → Opportunity
        →（future）Decision → Execution
```

晋级 Production 必须经过 **Evidence Gate（Decision 011）**。

### B.3 结论

两条链并行、经 Gate 衔接 — **Pass**。未发现文档要求 Detector 运行时写 Evidence。

---

## C. Append-only Audit

**设计意图（Pass）**：

- Evidence Domain Spec：禁止原地改 `evidence.decision`
- `EvidenceRepository` docstring：Append-only filesystem repository
- `_write_new_json` 使用 `path.open("x")` — 已存在则失败，不覆盖

**命名与完备性（Notes → Backlog）**：

| ID | 发现 | 严重度 |
|----|------|--------|
| APP-001 | 公共 API 名为 `save_manifest` / `save_evidence` / `save_evaluation`，非 `append_*`；行为已是 create-only | Low — Repository Refinement 可考虑别名或文档强化 |
| APP-002 | 未见 `update()` / `replace()` / `overwrite()` 公共方法 | Pass |
| APP-003 | Workflow 可重建 Evaluation 前须检查 `evaluation_exists`；依赖调用方纪律 | Medium — Refinement 应统一门禁文案与测试 |

本轮 **不改代码**。

---

## D. Decision Cross-reference Audit

| Decision | 与基线关系 | 结论 |
|----------|------------|------|
| 001 | 数据冻结；017 重申 | 一致 |
| 011 | 无证据不进 Production；017 §G 引用 | **交叉引用，非重复冲突** |
| 014 | Framework First | 与 017「先 Evidence Platform 再 Alpha」互补 |
| 015 | 双路径 Feature/Opportunity | 与顶层图一致 |
| 016 | 暂停 rb Feature↔RV_60 同构 | 017 重申有效 |
| 017 | Evidence-first 路线 | 本基线路图权威 |
| 008 | Feature Layer 延后 | **受控演进**：015 引入 Feature Sensor，仍禁交易捷径；非静默废止 |

**孤儿 Decision**：001–017 均可从当前路线追溯；无「已 Accepted 却零引用且与基线矛盾」项。  
**重复**：011 与 017§G 为有意重申 + 引用，建议保持引用、避免复制长文。

---

## E. Boundary Audit

| 边界 | 期望 | 观察 | 结论 |
|------|------|------|------|
| Evidence Domain ↔ Portfolio | Domain 不知 Portfolio | `EVIDENCE_DOMAIN_SPEC` 将 Portfolio/Query 列为 Out of scope / Deferred | Pass |
| Detector ↔ Evidence | Detector 不写 Evidence | `detectors/` 无 evidence import | Pass |
| Evaluation ↔ Evidence | Evaluation 不 mutate Evidence | Domain Spec 明确禁止；模型分册 | Pass |
| Projection ↔ Domain | 只读 | Projection 概念尚未实现；原则已写入 `02_ARCHITECTURE` | Pass（原则层） |
| research Archived ↔ Active | 语义隔离 | `research/README.md` Accepted | Pass |

---

## F. Layer Dependency Audit

**允许的依赖方向（示意）**：

```text
Data → Experiment → Evaluation → Evidence → Gate → Framework consumers
Projection ──read──► Evidence Repository（未来）
Detector ──read──► Context / window
Detector ──✗──► Evidence write API
Evidence Domain ──✗──► Portfolio / Dashboard
```

**观察**：

- 未发现已实现的 Projection 回流写 Domain（Projection 尚未落地）。
- Framework 包内 Risk/Execution 为骨架；不构成本次失败。

| ID | 发现 | 严重度 |
|----|------|--------|
| DEP-001 | `02_ARCHITECTURE` 旧版曾将交易链画成主首页且输出为 Signal | Fixed in docs v3.0.0（本轮文档） |
| DEP-002 | 未来 Portfolio 实现若 import 写 API，将违反 Principle 2 | Guard — Projection Spec 须写明 |

---

## G. Backlog（发现问题，本轮不修实现）

| ID | 项 | Priority | 说明 |
|----|-----|----------|------|
| **CLEANUP-001** | 删除 Registry `_adapt_legacy` / 旧实例注册 | Low | 已在 ROADMAP；Domain 之后 |
| **CLEANUP-002** | 全库文档扫除遗留 `Signal` 主输出表述 | Low | VOC-001 延伸 |
| **DOC-001** | `EVIDENCE_ENGINE_SPEC` 「草案」措辞与 Domain Spec 对齐 | Low | VOC-004 |
| **REPO-001** | Repository Append-only refinement（`save` 语义文档/`append` 别名/统一 exists 门禁测试） | High（v0.3） | APP-001/003 |
| **SPEC-001** | Projection Layer 概念 Spec（Portfolio 为第一种投影） | Medium（v0.3） | Decision 017 |
| **SPEC-002** | DQ1–DQ4 schema 升级评估（subject_id / evaluation_refs / classification / URI 名） | Low | Domain Spec §10 |
| **GOV-001** | ABR 强制门禁写入 AGENTS/ROADMAP（本轮已写入架构文） | Done（docs） | 制度 |

---

## H. Deliverables of this ABR

1. `docs/ROADMAP.md` — Phase 2 Completed；v0.3 checklist；**Completed ≠ v0.3 Completed**  
2. `docs/02_ARCHITECTURE.md` v3.0.0 — 顶层图 + Principle 1/2  
3. 本文件 — ABR-001 基线

**Explicitly out of scope**：Python 行为变更、Repository 重构、Portfolio 实现、Whitepaper、新 OPP。

---

## I. Sign-off

| 角色 | 结论 |
|------|------|
| Architecture Baseline | **Established** |
| Phase 2 — Evidence Foundation | **Completed**（≠ v0.3 complete） |
| Enter v0.3 remaining work | **Authorized by roadmap**：ABR-001 ✓ → Repository Append-only → Projection → Portfolio Projection |

---

## 修订记录

| 日期 | 说明 |
|------|------|
| 2026-07-20 | ABR-001 Completed；建立 PAAF 第一份 Architecture Baseline |
