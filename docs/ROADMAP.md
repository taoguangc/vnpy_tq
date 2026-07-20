# PAAF 路线图

> 版本：3.2.0 · 更新日期：2026-07-20  
> 路线图**可变**；宪章与规格冻结后，改路线图不等于改哲学。  
> **研究顺序以 Decision 017 为准**；本文件不得与之冲突。  
> **架构基线**：`docs/reviews/ABR-001_ARCHITECTURE_FREEZE_REVIEW.md`

---

## 阶段总览

```text
Phase 0  Research Chaos（AFF）                 — 已结束
Phase 1  Architecture Foundation（v0.1）       — 已结束（Tag v0.1.1）
Phase 2  Evidence Foundation                   — Completed（≠ v0.3 Completed）
Phase 3  Evidence Platform（v0.3）             — In Progress
Phase 4  Validation Protocol（v0.4）           — 下一
Phase 5+ Market State → Opportunity → …      — 其后
```

大版本进入下一阶段前须通过 **ABR**（Architecture Baseline Review）。

---

## PAAF Phase 2 — Evidence Foundation

```text
PAAF Phase 2 — Evidence Foundation

✓ Detector Framework Frozen
✓ Evidence Domain Frozen
✓ Research Governance Frozen

Status:
Completed
```

> **Completed ≠ v0.3 Completed。**  
> Phase 2 收口的是「框架 + Evidence Domain 合同 + 研究治理语义」。  
> v0.3 Evidence Platform（Repository Append-only / Projection / Portfolio）仍在进行。

依据：v0.2.4 Pipeline；`EVIDENCE_DOMAIN_SPEC.md` v1.0；`research/README.md`；ABR-001。

### Detector Framework（已完成明细）

| 版本 | 交付 | 状态 |
|------|------|------|
| v0.2.0–0.2.4 | Spec → DetectionResult → Opportunity → Registry → Pipeline + DEMO | **完成** |

```text
✓ Context / DetectionResult / Opportunity / Registry
✓ Detector Pipeline Verification / Minimal Opportunity Logger
Detector Framework Complete — Alpha Not Implemented
```

---

## PAAF v0.3 — Evidence Platform

```text
PAAF v0.3 — Evidence Platform

✓ Architecture Freeze Review（ABR-001）
□ Repository Append-only
□ Projection Layer
□ Portfolio Projection

Status:
In Progress
```

| 项 | 说明 |
|----|------|
| ABR-001 | **Completed** — 架构基线已建立；本项勾选 |
| Repository Append-only | 强化 create-only 合同与测试；禁止 update/replace/overwrite |
| Projection Layer | 概念 Spec：Projection ≠ Domain；只读 |
| Portfolio Projection | Portfolio 作为第一种 Projection；不反向写 Domain |

**Done Definition（v0.3）**：上表除 ABR 外三项完成，且不引入新 OPP/Alpha/Market State。

**明确不做（v0.3）**：新 OPP、新 Market State、新 Alpha、Feature→交易主链、Dashboard 强绑 Domain。

**切片备忘**：Evidence/Evaluation 实现切片已部分可用；产品化与 append-only 收紧仍属上表 □ 项。

| 附属 backlog | 状态 |
|--------------|------|
| **CLEANUP-001** Registry `_adapt_legacy` | Low / Backlog |
| **CLEANUP-002** 扫除遗留 Signal 主输出表述 | Low / Backlog（ABR VOC-001） |
| **REPO-001** Repository refinement | High（v0.3 主线） |
| **SPEC-001** Projection Layer Spec | Medium（v0.3） |

---

## PAAF v0.4 — Validation Protocol（下一）

目标：**验证协议**，不是 Multi-Symbol Engine。

```text
Every Candidate Detector
  → Automatically Validated
  → Multi-Symbol
  → Roll-aware
  → Evidence Generated
```

进入 v0.4 前须完成 v0.3 Done Definition + **ABR-002**。

---

## 已关闭研究快照（append-only；禁止原地复活）

ATR / Volume / OI / Close Location Feature EXP001 与 `OPP16_EXP001` 均 **Closed（inconclusive / Negative Evidence）**。  
Decision 016：暂停 rb「标量 Feature ↔ RV_60」同构。  
Decision 017：Closed 实验不可变；新条件 → 新 `experiment_id`。

| Spec / ADR | 状态 | 说明 |
|------|------|------|
| Decision 017 | **Accepted** | Evidence-first 路线 |
| ABR-001 | **Completed** | Architecture Baseline |
| `EVIDENCE_DOMAIN_SPEC.md` | **Accepted** | Domain Contract v1.0 |
| Feature / DATA / OPP16 EXP001 族 | **Closed** | 见各 Index |

---

## Release（Decision 017）

| 版本 | 含义 |
|------|------|
| v0.1.x | Context Foundation |
| v0.2.x | Detector Framework |
| **v0.3.x** | **Evidence Platform**（当前） |
| **v0.4.x** | **Validation Protocol** |
| v0.5.x | Market State |
| v0.6.x | Opportunity Library |
| v0.7.x | Decision Engine |
| 其后 | Execution / Production CTA |

---

## Git 约定

### Commit

```text
feat(context): add Context Engine
docs(paaf): accept decision 017 evidence-first roadmap
docs(arch): complete abr-001 architecture baseline review
```

禁止：`update` / `fix` / `modify` 这类无信息提交说明。

### Branch

- `main`：永远可运行（Decision 012）
- 功能：`feature/*`；实验：`research/*`
- 完成：Review 后 Merge；发布打 Annotated Tag

---

## 明确不做（在论证通过前）

- 机器学习 / 无约束参数搜索 / 为 Brooks 扭曲数据
- 大爆炸式重写 `strategies/`
- Feature 插入冻结交易主链
- **v0.3 期间未经立项的新 OPP / Alpha**
- **覆盖或原地复活 Closed 实验**
- Projection 回写 Domain

## 后续项

| 项 | 状态 | 说明 |
|----|------|------|
| Feature Layer | E0 | 只作计算依赖；禁交易捷径 |
| Architecture Whitepaper v1.0 | 后置 | Repository + Projection 概念稳定后 |
| Research Portfolio Dashboard | Projection | UI 后置 |

---

## 变更方式

改本文件须同步检查 Decision 017 与最新 ABR；哲学级变更走新 ADR。
