# Verification Maturity Package — CID_002（M3）

> **Type**: Verification Maturity Package Freeze  
> **Status**: **FROZEN** ✓  
> **Package ID**: `VMP_CID_002_V0_1`  
> **Date**: 2026-07-22  
> **Authorization**: Bindable Maturity Gap Closure Pack · `BMGCP_CID_002_V0_1`  
> **Parents**: `SEVF-v1` · `VR_CID_002_MECH_V0_1_1`（+ E3 A1） · `AMR_CID_002_V0_1` M3

## Purpose

```text
Close AMR M3: evidence enrichment ≠ verification maturity.
Freeze: independent-set protocol · assumptions freeze · RISK Verified scope decision.
```

## 1. Execution assumptions freeze（research）

| Assumption | Frozen binding |
|------------|----------------|
| Data | `docs/07_DATA_SPEC.md` @ 1.0.0 · TQ offline · 1m · CbC · unadjusted |
| Costs / fills | `CEMB-v1` · EXP-declared rate/slippage/capital |
| Runtime | `EI_CID_002_V0_1` |
| Call boundary | `ACL_CID_002_V0_1` |
| Consumer citation | `CC-CID_002-v1` |
| Decision metrics | PnL/Sharpe **forbidden** as primary KEEP/REVERT for H_MECH / H_CTX_FILTER |

```text
Any maturity-grade claim MUST restate this assumptions block.
Silent substitution → invalid claim.
```

## 2. Independent verification-set protocol

```text
DEFINITION（VMP）:
  An Independent Verification Set（IVS）is a pre-registered scope that:
    1. uses a new experiment_id
    2. does not reuse the hypothesis-forming sample as the sole support
    3. freezes identity hashes before Observation
    4. names Surface ID + EI + ACL versions
    5. has pre-registered KEEP/HOLD/REVERT rules
    6. produces Closed CSV/equivalent artifacts + Evidence Review

IVS is a PROTOCOL, not an automatic new EXP under this pack.
```

### Admitted IVS already on file（MECH）

| Set | Role |
|-----|------|
| EXP007 multi-symbol 2024 | cross-symbol auditability |
| EXP011 rb/2025 | temporal OOS · E3 |
| CTX_CID002_EXP002 rb/2025 | Context filter OOS capability |

```text
These satisfy research IVS for their declared hypotheses.
They do NOT auto-satisfy Production verification.
```

### Required for any future maturity-upgrade claim

```text
• Cite at least one IVS per claim family
• Negative evidence retained（immutable）
• Failure handling declared（see §3）
```

## 3. Failure handling（normative）

| Failure class | Handling |
|---------------|----------|
| Identity hash mismatch | **ABORT** · no KEEP/REVERT evaluation |
| ACL violation（Context writes entries / sizing） | **REVERT** claim family · record as integrity fail |
| Capital death under fixed_size（e.g. `i`） | **NOT** H_MECH falsification · route to RISK surface |
| Filter inert（N1==N0 & D==0） | **HOLD** for H_CTX_FILTER · not Alpha |
| PnL used as primary gate | **REVERT** methodological · discard maturity claim |
| Closed EXP rewrite | **FORBIDDEN**（Decision 017） |

## 4. RISK Verified scope decision

```text
DECISION R-V0（historical · BMGCP pack time）:
  RISK @0.2.0 was NOT Verified under the pack alone.

DECISION R-V2（2026-07-22）:
  VR_CID_002_RISK_V0_2_0 GRANTED — H_CAPITAL_GATE · E2 only.
  See STRATEGY_VERIFIED_REVIEW_CID_002_RISK_V020.md
  E3 OOS and Production Bindable remain separate.
```

## 5. Closure verdict（M3）

```text
AMR M3 documentary gap: CLOSED
RISK Verified: NOT GRANTED（explicit scope decision）
Bindable maturity upgrade: NOT granted by this freeze
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-22 | VMP_CID_002_V0_1 FROZEN |
