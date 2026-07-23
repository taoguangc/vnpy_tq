# CID_003 Positioning Engineering Review

> **Type**: Positioning / Capital Engineering Review  
> **Status**: **COMPLETE** ✓  
> **Review ID**: `ENG_REV_CID_003_POSITIONING_V0_1`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-50B  
> **Parents**: `BPR_CID_003_V0_1` · `SIF_CID_003_V0_1_1` · EXP005  
> **Implementation**: **NOT AUTHORIZED**（design only）

## Review record

```text
================================================
ENG_REV_CID_003_POSITIONING_V0_1

H_MECH Verified: UNCHANGED（E3 retained）
Capital safety:  OPEN RISK confirmed（i · EXP005）
@0.1.1 bytes:    NOT MUTATED
@0.2.0 lineage:  DESIGNED ONLY
Alpha / Bindable: NOT GRANTED
================================================
```

## 1. Problem separation

| Problem | Question | Status |
|---------|----------|--------|
| A. Mechanism | OPP16→exit auditable? | **Verified E3** |
| B. Capital | Can fixed_size=1 survive {rb,i,MA} @200k? | **OPEN RISK**（i 爆仓） |

```text
A and B are different hypotheses.
Do not retune OPP16 morphology to “fix” capital.
Do not reopen H_EDGE to “fix” capital.
```

## 2. Observed capital breach（facts）

From `STRAT_RO16_EXP005`（@0.1.1 · docs/07 · 2024 · `fixed_size=1` · `capital=200_000`）:

| Symbol | Contract size | Auditable exits | Engine capital |
|--------|---------------|-----------------|----------------|
| rb | 10 | 1920 | survived（net descriptive −37703） |
| **i** | **100** | 2060 | **breach：capital≤0**（stats unreliable） |
| MA | 10 | 2091 | survived（descriptive −46831） |

```text
Root cause class（same as CID_002）:
  fixed_size=1 × large yuan-per-point（i）× high trade frequency
  × no risk throttle / kill-switch
  under 20万 research capital.
```

## 3. Current positioning（@0.1.1）

```text
sizing_rule_class: fixed_size
default:           1
no: risk-per-trade · hard_max_lots · equity kill-switch
```

Inherited for **hypothesis continuity**, not as production capital policy.

## 4. Recommended repair lineage（design freeze candidate）

```text
strategy_id: STRAT_REV_OPP16_01
version:     0.2.0
change:      positioning / capital controls only
detector:    OPP16@1.0.0 unchanged
parent:      @0.1.1（immutable Verified MECH）
```

### Minimum controls（if later implemented）

```text
1. risk_unit_mode ∈ {FIXED_LOTS, RISK_FRACTION_OF_CAPITAL}
2. RISK_FRACTION_OF_CAPITAL:
     lots = floor( risk_cash / (stop_distance × contract_size) )
     lots=0 → skip（no force）
3. hard_max_lots per symbol
4. equity kill-switch: equity_est ≤ capital_floor_ratio × capital
     → flatten + halt new entries
5. EXP metadata must echo sizing_mode · kill_events · capital_assumption
```

```text
Objective: capital survivability under research harness
NOT: maximize return / flip H_EDGE
```

### Suggested first capital EXP（when impl authorized）

```text
STRAT_RO16_EXP007 — H_CAPITAL_GATE smoke · i/2024 · @0.2.0
KEEP = no capital≤0 · ≥1 auditable exit · hash echo
≠ Alpha · ≠ H_MECH rewrite
```

## 5. Consumption options after design

| Interface | Fit today | After @0.2.0 KEEP（hypothetical） |
|-----------|-----------|-----------------------------------|
| Research Mechanism Asset | **YES**（@0.1.1 Verified） | still YES（cite MECH hashes） |
| Capital-gated research consumer | NO | possible on @0.2.0 only |
| Standalone Trading / Production | NO | still NO without Alpha + more gates |

## 6. Decision

```text
DO NOT edit @0.1.1
CREATE design-only charter pointer for @0.2.0
Implementation / Identity Freeze @0.2.0: NOT in this review
Bindable: still WITHHELD
```

## Non-goals

```text
❌ PnL improvement claim
❌ H_EDGE reopen
❌ Production Bindable
❌ Silent size change on @0.1.1
```

## Next（须新授权）

```text
A. Authorize Implementation of Positioning Lineage 0.2.0
B. Authorize Consumer Contract freeze CC-CID_003-v1（docs only）
C. Pause CID_003
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | Positioning Eng Review COMPLETE · design-only |
