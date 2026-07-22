# Consumer Call ACL — CID_002（M2）

> **Type**: Consumer Boundary / Call ACL Freeze  
> **Status**: **FROZEN** ✓  
> **Contract ID**: `ACL_CID_002_V0_1`  
> **Date**: 2026-07-22  
> **Authorization**: Bindable Maturity Gap Closure Pack · `BMGCP_CID_002_V0_1`  
> **Parents**: `CC-CID_002-v1` · `CPA_CID_002_V0_1` · `CSD_CID_002_V0_1` · `AMR_CID_002_V0_1` M2

## Purpose

```text
Close AMR M2: name who may call Detector / Risk / Strategy,
so Context + Strategy + Risk cannot silently become one black box.
```

## 1. Principals（callers）

| Principal ID | Meaning |
|--------------|---------|
| `P_DETECTOR` | `BrooksScalpFirstPullbackDetector`（`BROOKS_SCALP_FP@0.1.0`） |
| `P_ORCH_MECH` | MECH orchestrator `@0.1.1`（`BrooksScalpPaafStrategyV011`） |
| `P_ORCH_RISK` | RISK orchestrator `@0.2.0`（capital-gated subclass） |
| `P_CTX_FILTER` | Context Filter adapter（`strategies/paaf/context_consumer/*`） |
| `P_CTX_ENGINE` | A1 Published State publisher / PAAF ContextEngine |
| `P_HARNESS` | Research harness / EXP runner（scripts） |
| `P_ENGINE` | vn.py backtest engine（fills · account） |

## 2. Call ACL matrix（FROZEN）

Legend: **ALLOW** · **DENY** · **N/A**

| Caller ↓ \\ Callee → | Detector.detect | Orch submit entry | Risk sizing/kill | Engine buy/sell | Ctx publish tag |
|----------------------|-----------------|-------------------|------------------|-----------------|-----------------|
| `P_HARNESS` | ALLOW（via orch） | N/A | N/A | N/A | ALLOW（setup） |
| `P_ORCH_MECH` | ALLOW | ALLOW（self） | DENY | ALLOW | DENY（may read via adapter only） |
| `P_ORCH_RISK` | ALLOW | ALLOW（self） | ALLOW（self） | ALLOW | DENY |
| `P_CTX_FILTER` | DENY | DENY（gates only） | DENY | DENY | ALLOW（read） |
| `P_CTX_ENGINE` | DENY | DENY | DENY | DENY | ALLOW（self publish） |
| `P_DETECTOR` | N/A（self） | DENY | DENY | DENY | DENY |
| `P_ENGINE` | DENY | DENY | DENY | N/A（self） | DENY |

### Hard rules（normative）

```text
1. Detector MUST NOT call buy/sell, Risk, or invent Context tags.
2. Context Filter MAY only PERMIT/DENY an existing DetectionResult
   path; MUST NOT create DetectionResult or change size/stop/target.
3. Context Engine MUST NOT generate entries or sizing alpha.
4. RISK surface MAY size/halt; MUST NOT rewrite H_MECH claims.
5. MECH surface MUST NOT claim capital safety from RISK KEEP.
6. Harness MAY compose Filter adapter OUTSIDE G5 binding bytes.
7. Any report MUST cite CC-CID_002-v1 Surface ID before claims.
```

## 3. Allowed compositions

```text
ALLOWED:
  P_HARNESS → P_ORCH_MECH → P_DETECTOR → P_ENGINE
  P_HARNESS → P_CTX_FILTER(P_ORCH_MECH) → P_ENGINE
  P_HARNESS → P_ORCH_RISK → P_DETECTOR → P_ENGINE

FORBIDDEN:
  P_CTX_* → invent entries
  P_CTX_* → sizing alpha
  Collapsing MECH+RISK+Context into one unlabeled “strategy PnL”
  Mutating G5 binding bytes to “fit” Context
```

## 4. Relationship to Component Split

```text
CSD_CID_002_V0_1 remains DESIGN ONLY.
ACL_CID_002_V0_1 binds callability NOW under versioned surfaces.
Future physical split must migrate this ACL to new principal IDs
（new ACL version）— no silent rewrite.
```

## 5. Closure verdict（M2）

```text
AMR M2 documentary gap: CLOSED
Bindable maturity upgrade: NOT granted by this freeze
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-22 | ACL_CID_002_V0_1 FROZEN |
