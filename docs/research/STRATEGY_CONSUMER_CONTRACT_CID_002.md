# Consumer Contract — CID_002（frozen）

> **Type**: Consumer Contract Freeze  
> **Status**: **FROZEN** ✓  
> **Contract ID**: `CC-CID_002-v1`  
> **Date**: 2026-07-22  
> **Authorization**: Delegation-50D · Charter `BGC-CID_002-v1`  
> **Closes**: BPR gap **G7**（dual-surface citation）· mitigates **G2**

## Contract record

```text
================================================
CC-CID_002-v1

Bindable: NO
Alpha:    NONE
Purpose:  Mandatory citation / consumption rules for CID_002
================================================
```

## 1. Surfaces（non-substitutable）

| Surface ID | Identity | May claim | Must not claim |
|------------|----------|-----------|----------------|
| `MECH` | `@0.1.0` / `@0.1.1` · Verified on `@0.1.1` | H_MECH auditability · E2 | capital safety · Alpha · Bindable |
| `RISK` | `@0.2.0` · `SIF_CID_002_V0_2_0` | H_CAPITAL_GATE / survival controls | H_MECH upgrade · Alpha · Bindable |

```text
Every consumer report MUST name Surface ID before any claim.
```

## 2. Standing market-scope rule（G2 mitigation）

```text
Asset market_scope = UNBOUND_AT_ASSET（CEMB-v1）remains.

Every experiment / consumer run MUST pre-declare:
  symbols · session · period · data_protocol_version · capital_assumption

Inventing a preferred production universe at asset level: FORBIDDEN.
```

## 3. Context attachment（future）

```text
ALLOWED（new experiment_id only，after a Bindable asset exists）:
  Filter · Risk Modifier · Monitoring · Permission

FORBIDDEN inside CID_002 signal path:
  Context → entries
  Context score → sizing alpha
```

## 4. Outcome semantics

```text
KEEP ≠ Alpha ≠ Bindable ≠ Production ≠ live permission
Negative evidence is first-class and immutable.
```

## 5. Modification

```text
CC-CID_002-v1 is frozen.
Any rule change → CC-CID_002-v2（new freeze）· no silent rewrite.
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-22 | v1 frozen under Delegation-50D |
