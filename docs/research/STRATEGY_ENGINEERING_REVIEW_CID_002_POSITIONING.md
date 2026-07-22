# CID_002 Positioning Engineering Review

> **Type**: Positioning / Capital Engineering Review  
> **Status**: **COMPLETE** ✓  
> **Review ID**: `ENG_REV_CID_002_POSITIONING_V0_1`  
> **Date**: 2026-07-22  
> **Authorization**: `Authorize Positioning Engineering Review for CID_002`  
> **Parents**: `SAR_CID_002_V0_3` · `SIF_CID_002_V0_1_1`（@0.1.1）· EXP007  
> **Implementation**: **NOT AUTHORIZED** by this review（later granted separately as user **A** → see delivery note）

## Review record

```text
================================================
ENG_REV_CID_002_POSITIONING_V0_1

H_MECH claims: UNCHANGED（still retained）
Capital safety: OPEN RISK confirmed
@0.1.1 bytes: NOT MUTATED
New positioning lineage: DESIGNED ONLY（not implemented）
Bindable / Alpha: NOT GRANTED
================================================
```

## 1. Problem separation（mandatory）

| Problem | Question | EXP007 status |
|---------|----------|---------------|
| **A. Mechanism** | Detector→entry→exit auditable? | **KEEP** on rb/i/MA |
| **B. Capital engineering** | Can fixed research capital survive the trade stream? | **OPEN RISK**（`i` capital≤0） |

```text
A and B are different hypotheses.
Mixing them → false H_MECH FAIL or false “needs more Alpha”.
```

## 2. Observed capital breach（facts）

From `STRAT_BS02_EXP007`（@0.1.1 · docs/07 · 2024 · `fixed_size=1` · `capital=200_000`）:

| Symbol | Contract size（harness） | Auditable exits | Engine capital |
|--------|-------------------------|-----------------|----------------|
| rb | 10 | 1303 | survived（net PnL descriptive −34671） |
| **i** | **100** | 1243 | **breach：capital≤0**（PnL stats unreliable） |
| MA | 10 | 1100 | survived（descriptive −31521） |

```text
i multiplier is 10× rb under the same “1 lot” fixed_size.
High trade frequency × large yuan-per-point × no risk throttle
→ path-dependent equity wipe under 20万 research capital.
```

This does **not** falsify H_MECH. It falsifies the implicit claim:

```text
“fixed_size=1 is a safe universal consumption default across {rb,i,MA} at 200k”
```

## 3. Current positioning model（@0.1.0 / @0.1.1）

```text
sizing_rule_class: fixed_size
default:           1 contract
no:                risk-per-trade throttle
no:                symbol margin / volatility scaling
no:                max-contracts / kill-switch on equity
no:                portfolio heat map
```

Inherited from CID_001 defaults for **hypothesis continuity**, not as a production capital policy.

## 4. Consumption-interface options（pre-Bindable）

Before Bindable designation, CID_002 must declare how it may be consumed:

| Interface | Meaning | Fit today |
|-----------|---------|-----------|
| **Research Mechanism Asset** | Evidence object；runs may use diagnostic capital / size | **YES**（current） |
| **Standalone Trading Asset** | Single-account consumer with capital safety gates | **NO** until positioning lineage |
| **Portfolio Component** | Sized by portfolio risk budget | **NO**（portfolio phase not open） |

```text
Recommended interim designation language:
  “Testing Mechanism Asset with Open Capital Risk”
not
  “tradeable strategy”
```

## 5. Positioning policy（design freeze candidate）

If a repair lineage is later authorized, it should implement **capital safety**, not return chasing:

### 5.1 Required controls（minimum）

```text
1. risk_unit_mode ∈ {FIXED_LOTS, RISK_FRACTION_OF_CAPITAL}
2. If RISK_FRACTION_OF_CAPITAL:
     risk_per_trade ∈ (0, 1] of capital at entry
     lots = floor( risk_cash / (stop_distance × contract_size) )
     lots ≥ 0；lots=0 → skip trade（no force）
3. hard_max_lots per symbol（predeclared table）
4. equity_kill_switch: if equity ≤ capital_floor → flat + halt new entries
5. research_capital_assumption echoed in every EXP metadata
```

### 5.2 Explicit non-goals of positioning lineage

```text
❌ Optimize lots to maximize PnL / Sharpe
❌ Re-tune detector / exits while “fixing size”
❌ Erase @0.1.1 mechanism evidence
❌ Silent Bindable upgrade
```

### 5.3 Suggested identity pattern（when implementation authorized）

```text
strategy_id: STRAT_TREND_BROOKS_SCALP_02
version:     0.2.0   （positioning lineage；not a silent 0.1.2 patch）
parent:      SIF_CID_002_V0_1_1
detector:    BROOKS_SCALP_FP@0.1.0（morphology unchanged）
change_set:  sizing / capital controls only
```

```text
0.1.1 remains the mechanism+rollover reference.
0.2.0 becomes the capital-consumable candidate（still not Bindable until gates pass）.
```

## 6. Research-run capital protocol（immediate，no code change）

Until 0.2.0 exists, any further Observation on @0.1.1 must declare one of:

| Mode | Rule |
|------|------|
| `DIAGNOSTIC_CAPITAL` | Capital/size may be raised solely to avoid engine death；**PnL not decision metric** |
| `MECH_ONLY_SYMBOLS` | Restrict mechanism EXPs to symbols that did not breach under 200k（e.g. rb, MA）unless diagnostic mode |
| `ABORT_ON_BREACH` | Capital≤0 → EXP outcome **HOLD** for capital gate（separate from H_MECH） even if trades auditable |

Recommended default for new @0.1.1 EXPs:

```text
Declare capital_gate separately from H_MECH.
Do not expand universe to chase “more KEEP”.
```

## 7. Gate checklist after this review

| Gate | Status |
|------|--------|
| Identity @0.1.1 | FROZEN |
| Mechanism auditability | RETAINED |
| Multi-period / cost / multi-symbol H_MECH | RETAINED |
| **Capital safety** | **OPEN at review time** → later PARTIAL via `@0.2.0` EXP009 |
| Positioning lineage 0.2.0 | **DESIGNED here** → later **IMPLEMENTED**（`SIF_CID_002_V0_2_0`） |
| Bindable | NOT READY |
| Alpha | NONE |

## 8. Decisions of this review

```text
1. Confirm i breach = capital engineering failure，not H_MECH failure.
2. Do not mutate @0.1.1.
3. Specify 0.2.0 positioning lineage design（§5）without implementation.
4. Require explicit capital_gate protocol on future @0.1.1 runs（§6）.
5. Bindable pre-review may discuss consumption interface（§4）but not designate.
```

## 9. Explicit non-authorizations

```text
❌ Implement 0.2.0 sizing code now
❌ Re-run EXP007 with larger capital to “fix” KEEP
❌ Change fixed_size after seeing i PnL
❌ Bindable / Production designation
❌ Portfolio construction
```

## 10. Next（须另授）

```text
A. Authorize Implementation of Positioning Lineage 0.2.0
B. Authorize Bindable Pre-Review（consumption interface only）
C. Pause Epoch 5
```

## Machine note

`research/output/evidence/STRATEGY_POSITIONING_REVIEW_CID_002/review.json`

## Revision record

| Date | Change |
|------|--------|
| 2026-07-22 | Positioning Engineering Review complete · 0.2.0 design-only |
