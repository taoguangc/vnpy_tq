# Epoch 2.0 — Evidence-driven Knowledge Growth

**Status:** Active（Research Phase）  
**Started:** 2026-07-20  
**Engineering:** Architecture Baseline v1 **Frozen**  
**Method:** PRM v1.0.1（含 Campaign Lifecycle）  
**Research focus:** Context Capability Proposal v0.2 — **Review Passed**（CAP-CTX-001 Candidate，未 Promote）

## Positioning

Epoch 1 建立 Engineering + Scientific Method + Evidence OS。  
Epoch 2 目标：**在不变 Baseline 的前提下，按 PRM 持续产生可信 Knowledge**。

```text
Question → Hypothesis → (Capability | RC) → Experiment → Evidence → Validation → Knowledge
```

## Current

| Item | Status |
|------|--------|
| RC001 Research Plan | v0.2 — Review Passed（Not Accepted） |
| Context Gate v1 | **BLOCKED** — [清单](../research/CONTEXT_CAPABILITY_GATE.md) |
| CTX Capability Proposal | **v0.2 Review Passed** — [Proposal](../research/CONTEXT_CAPABILITY_RESEARCH_PROPOSAL.md) |
| CAP-CTX-001 | **Candidate only**（Not promoted） |
| EXP / Code / Backtest | ⏸ Not authorized |
| Architecture change | ⏸ Forbidden |

## Implicit rule

> **Never skip PRM.**  
> Capability Research → Gate → RC001（禁止跳跃）.  
> Descriptive ≠ Predictive.  
> CAP ≠ Alpha RC.

## State graph（fixed）

```text
Epoch 2.0
PRM ✓
RC001 ✓ Review Passed
Context Gate ✓ BLOCKED
        ↓
CTX Capability Research Proposal
        ↓
Review Passed
        ↓
CAP-CTX-001 Candidate
        ↓
（另授）Promote → Gate → RC001 Ready
```

## Next

```text
决定是否 Promote → CAP-CTX-001
（当前：不急；不写代码；不跑回测）
```

## Roadmap hint（未冻结）

```text
CAP-CTX-001 — Context Capability（Foundation）
RC001 — Context + Opportunity（依赖 Gate）
…
```
