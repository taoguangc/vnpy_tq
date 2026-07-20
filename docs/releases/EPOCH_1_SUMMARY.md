# Epoch 1 Summary — Evidence-driven Architecture

**Closed as of:** Architecture Baseline v1（2026-07-20）  
**Tag:** `architecture-baseline-v1`  
**Status:** Active Epoch（infrastructure design closed）

## One-sentence definition

> **PAAF 已完成第一代架构（Architecture Baseline v1）的建立，并正式进入以 Evidence 为中心的平台建设阶段。后续工作的重点不再是设计基础设施，而是在不改变 Baseline 的前提下持续构建平台能力，并让研究成果通过统一的 Evidence Repository 被沉淀、消费和复用。**

## Epoch map

```text
Epoch 0（已结束）— 寻找 Alpha
  AFF → Feature → 假设 → 证伪

Epoch 1（当前）— Evidence-driven Architecture
  Decision → Contracts → Evidence → Repository → Projection（待 Sprint）

Epoch 2（未授权）— 仅当核心契约世界观必须重写时
```

Do not discuss Epoch 2 until foundation Contracts must be redefined.

## What matured

PAAF no longer relies primarily on developer self-discipline.  
It relies on **architecture constraints**:

```text
Architecture Baseline → Contracts → Governance → any implementer
```

Same path whether the implementer is a human or an AI Agent.

## Two tracks（Decision 017 / 018 end-state）

```text
PAAF
├── Platform（长期演进）— Projection / Repository / Query / Portfolio / Dashboard
└── Research（持续产生 Evidence）— OPP / Context 假设 / 多品种 / Feature
         │
         └── connected only via Evidence Repository
```

## What is closed vs what waits

| Closed | Waits for explicit Sprint start |
|--------|----------------------------------|
| Architecture design | Sprint 1 Projection consume |
| Contract Freeze | ABR-002 |
| Infrastructure Specs as foundation work | Push of baseline RC |

Sprint 1 start line（unchanged）:

> **Start Platform Construction Sprint 1：Projection Layer consumes Evidence Repository under Architecture Baseline v1.**

Operating detail: `docs/development/PLATFORM_CONSTRUCTION_PHASE.md`.
