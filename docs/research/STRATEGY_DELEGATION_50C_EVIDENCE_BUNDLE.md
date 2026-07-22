# Evidence Bundle — Delegation-50C（EXP006–EXP007）

> **Status**: **COMPLETE** ✓  
> **Date**: 2026-07-22  
> **Authorization**: Delegation-50C  
> **Identity**: `SIF_CID_002_V0_1_1`（@0.1.1）

## Outcomes

| EXP | Family | Scope | Outcome |
|-----|--------|-------|---------|
| EXP006 | H_ROBUST cost | rb/2024 · slippage=2.0 | **KEEP**（1303 auditable） |
| EXP007 | H_MECH portability | {rb,i,MA}/2024 | **KEEP**（all three KEEP） |

### EXP007 per-symbol

| Symbol | Auditable exits | Status | Note |
|--------|-----------------|--------|------|
| rb | 1303 | KEEP | |
| i | 1243 | KEEP | engine reported **爆仓**（capital≤0）；PnL stats unreliable；mechanism audit still met |
| MA | 1100 | KEEP | |

```text
KEEP（portability）
        ≠
Alpha
        ≠
Bindable
        ≠
safe position sizing on i under fixed_size=1 · capital=200k
```

## Claim ledger update（@0.1.1）

```text
H_MECH rb/2024:              RETAINED（EXP005）
H_ROBUST cost×2 rb/2024:     RETAINED（EXP006）
H_MECH {rb,i,MA}/2024:       RETAINED（EXP007）
H_NULL @0.1.0 rb/2024:       still REJECTED（prior lineage；not re-tested here）
Verified / Bindable / Alpha: NO
```

## Evidence Review

| Gate | Result |
|------|--------|
| Identity hash @0.1.1 | PASS |
| Pre-registered rules | PASS |
| Cost stress single variable | PASS |
| Universe predeclared non-PnL | PASS |
| i bankruptcy isolated as sizing uncertainty | PASS（not silent Alpha） |

**Bundle Evidence Review: PASS**

## Asset Review `SAR_CID_002_V0_3`

```text
0.1.0: immutable prior ledger
0.1.1: Testing · mechanism retained（cost + multi-symbol）
Capital safety: OPEN RISK（Positioning Review COMPLETE · 0.2.0 design-only）
Open:  implement 0.2.0 · Bindable pre-review · Pause
```

## Stop

```text
Delegation-50C STOP — do not auto-Bindable or optimize size for i PnL
Positioning Engineering Review authorized separately → see
STRATEGY_ENGINEERING_REVIEW_CID_002_POSITIONING.md
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-22 | EXP006/007 closed · SAR V0.3 · STOP |
| 2026-07-22 | Positioning Review linked · capital OPEN · 0.2.0 design-only |
