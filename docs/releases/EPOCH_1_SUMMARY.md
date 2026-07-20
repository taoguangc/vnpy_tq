# Epoch 1 Summary — Evidence-driven Architecture

**Checkpoint:** PAAF Epoch 1 Stable Checkpoint — Baseline v1 + Sprint 1 Complete  
**Tag:** `architecture-baseline-v1`  
**Status:** Frozen hold（Sprint 2 ⏸ Not Started）  
**Positioning:** Evidence-Driven Quantitative Research Operating System

## One-sentence definition

> **PAAF 已完成第一代架构（Architecture Baseline v1）的建立，并正式进入以 Evidence 为中心的平台建设阶段。后续工作的重点不再是设计基础设施，而是在不改变 Baseline 的前提下持续构建平台能力，并让研究成果通过统一的 Evidence Repository 被沉淀、消费和复用。**

## Stable checkpoint（内部共识 · 2026-07-20）

```text
PAAF Epoch 1 — Evidence-driven Architecture

Architecture Baseline v1
        ✓

Platform Construction Phase
        ✓

Sprint 1 — Projection Layer
        ✓

ABR-002 Infrastructure Compliance
        ✓ PASS WITH BACKLOG

Sprint 2
        ⏸ Frozen / Not Started
```

> **PAAF 已完成“如何可靠演进”的证明，下一阶段才开始证明“如何持续产生有效研究能力”。**

空窗期是故意保留的：基础规则已稳，下一步需求尚未被证据驱动明确提出。继续堆功能收益低、侵蚀 Baseline 风险高。

## Proven loops

Research knowledge loop:

```text
Hypothesis → Experiment → Evidence → Evaluation → Repository → Projection → Knowledge → Next Hypothesis
```

Engineering loop（Sprint 1 已跑通）:

```text
Architecture Baseline v1 → Contract → Implementation → Contract Test → ABR → Release
```

## Freeze（当前禁止）

- 新 Contract / Domain / 基础设施
- 新 Alpha 假设 / OPP 扩展
- Market State / Decision Engine
- Repository cleanup / Portfolio 增强 / Validation 设计混入本 checkpoint

## Sprint Start Check（非 Decision；启动门槛）

任何 Sprint 开始前须回答：

```text
1. What existing Contract does this consume?
2. What Evidence/Capability gap does it solve?
3. Why cannot this wait?
4. Does it modify Baseline?
```

理想答案：

```text
Consumes existing Contract: Yes
Solves identified gap: Yes
Cannot wait: Explained
Baseline change: No
```

若第 4 项为 Yes → 回到 Decision / Contract 流程，不得直接开 Sprint。

## Sprint 2（未启动）

须由**明确问题**驱动，非功能愿望。启动语：

> **Start Platform Construction Sprint 2: [具体能力] under Architecture Baseline v1.**

例：`Validation Infrastructure consumes Evidence Repository under Architecture Baseline v1.`

Validation（若进入）须遵守：判断证据质量，不制造 / 重算 Evidence。

## Two tracks

```text
PAAF
├── Platform — Projection / Repository / Query / …（Baseline 下生长）
└── Research — OPP / Feature / …（经 Evidence Repository 连接）
```

Operating detail: `docs/development/PLATFORM_CONSTRUCTION_PHASE.md`  
Sprint Start Check also: `docs/development/REVIEW_CHECKLIST.md`  
Sprint 1 report: `docs/releases/SPRINT_1_REPORT.md`
