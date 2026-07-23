# Consumer Contract — CID_003（frozen）

> **Type**: Consumer Contract Freeze  
> **Status**: **FROZEN** ✓  
> **Contract ID**: `CC-CID_003-v1`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-50D（`授权你决定50次`）  
> **Closes**: BPR gap **G2**（dual-surface citation）

## Contract record

```text
================================================
CC-CID_003-v1

Purpose: Mandatory citation / consumption rules for CID_003
Alpha:   NONE
Production Bindable: NOT granted by this contract alone
================================================
```

## 1. Surfaces（non-substitutable）

| Surface ID | Identity | May claim | Must not claim |
|------------|----------|-----------|----------------|
| `MECH` | `STRAT_REV_OPP16_01@0.1.1` · `SIF_CID_003_V0_1_1` · Verified H_MECH · E3 | Mechanism auditability（OPP16→exit） | capital safety · Alpha · edge |
| `RISK` | `STRAT_REV_OPP16_01@0.2.0` · `SIF_CID_003_V0_2_0` · Verified H_CAPITAL_GATE · E3 | Capital survivability / kill-switch / sizing gate | H_MECH upgrade · Alpha · PnL edge |

```text
Detector（both）: OPP16@1.0.0
Every consumer report MUST name Surface ID before any claim.
Never collapse MECH KEEP + RISK KEEP into one Alpha story.
```

## 2. Standing market-scope rule

```text
Asset market_scope = UNBOUND_AT_ASSET（CEMB-v1）remains.

Every experiment / consumer run MUST pre-declare:
  symbols · session · period · data_protocol_version · capital_assumption

Inventing a preferred production universe at asset level: FORBIDDEN.
```

## 3. Context attachment（future）

```text
ALLOWED later（new experiment_id only · after Bindable research asset）:
  Filter · Risk Modifier · Monitoring · Permission

FORBIDDEN inside CID_003 signal path:
  Context → entries
  Context score → sizing alpha
```

```text
Evidence pointer（does not amend this freeze）:
  CTX_CID003_EXP001 KEEP — see SAR_CID_003_V1_8 / CCED_CID_003_V0_1
  ≠ Context routing permission · ≠ Production
```

## 4. Outcome semantics

```text
KEEP ≠ Alpha ≠ Bindable ≠ Production ≠ live permission
H_MECH Verified ≠ H_CAPITAL_GATE Verified ≠ H_EDGE
Negative evidence（EXP001 HOLD · EXP003/004 H_EDGE REVERT）is first-class.
```

## 5. Modification

```text
CC-CID_003-v1 is frozen.
Any rule change → CC-CID_003-v2（new freeze）· no silent rewrite.
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | v1 frozen under Delegation-50D |
