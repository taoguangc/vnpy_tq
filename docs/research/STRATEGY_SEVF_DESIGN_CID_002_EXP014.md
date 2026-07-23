# SEVF Design Note — STRAT_BS02_EXP014（H_EDGE OOS）

> **Type**: Experiment Design（companion to Fill）  
> **Status**: **DESIGNED** ✓  
> **Experiment ID**: `STRAT_BS02_EXP014`  
> **Date**: 2026-07-23  
> **Authorization**: `Authorize SEVF Fill for STRAT_BS02_EXP014`  
> **Parent**: `AERD_CID_002_V0_1` · prior `STRAT_BS02_EXP013` **REVERT**（immutable）

## Purpose（strict）

```text
Complete the H_EDGE temporal evidence chain.

Ask: Is EXP013 failure local to rb/2024, or does the same
     pre-registered edge screen also fail on 2025 OOS?

NOT: “Try again to rescue / flip EXP013.”
```

## Single hypothesis

```text
H_EDGE_OOS:
  On a calendar year that did not form the EXP013 edge screen,
  frozen MECH @0.1.1 still exhibits the same identifiable
  risk-reward structure gates（A excursion + B positive mean net）.
```

## Single variable

```text
VARIABLE = evaluation calendar year（2025 vs EXP013/2024）
HELD CONSTANT =
  identity hashes · detector · stops/targets/params · costs ·
  symbol rb · KEEP/REVERT metric definitions · gates
```

## Forbidden（explicit）

```text
❌ change entry / detector / stop / target / parameters
❌ change cost model
❌ change evaluation metrics or thresholds
❌ PnL optimization / post-hoc gate shopping
```

## Outcome interpretation（pre-declared）

| Outcome | Meaning |
|---------|---------|
| **REVERT** | H_EDGE rejected on OOS too · strong negative package with EXP013 |
| **KEEP** | OOS screen PASS only → Alpha Candidate **reconsideration allowed** · still NOT Alpha |
| **HOLD** | insufficient n / inapplicable |

```text
Either way: H_MECH Verified retained independently.
Production / CSD: not opened by this EXP.
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | Designed · temporal completeness framing |
