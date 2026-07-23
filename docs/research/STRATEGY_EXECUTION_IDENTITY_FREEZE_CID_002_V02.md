# Execution Identity Freeze — CID_002（V0.2 · Production-grade requirements）

> **Type**: Execution Identity Spec Freeze（≠ Production Bindable · ≠ Deploy certificate · ≠ Observation）  
> **Status**: **FROZEN** ✓  
> **Freeze ID**: `EI_CID_002_V0_2`  
> **Date**: 2026-07-23  
> **Authorization**: `授权你来决定`（Epoch 6 scoped · after RISK Verified E2）  
> **Supersedes for production-path citation**: extends `EI_CID_002_V0_1`（research pin retained）  
> **Parents**: `PBDR_CID_002_V0_1` · `VR_CID_002_RISK_V0_2_0` · `PBRR_CID_002_V0_3`

## Purpose

```text
Close documentary half of R-EI:
  freeze what Production Bindable WILL require for execution identity,
  plus pin current research dependency manifest hash.

Does NOT issue a deploy certificate.
Does NOT grant Production Bindable.
```

## 1. Inherited research pin（still valid）

| Field | Value |
|-------|--------|
| G5 `binding_source_revision` | `833ae4740e6da3e2e3a42899d2bd4229f61785d6` |
| Research env（from `EI_CID_002_V0_1`） | Python 3.13.13 · vnpy 4.4.0 · vnpy_ctastrategy 1.4.1 · Win10 |
| MECH / RISK hashes | unchanged vs freezes |

```text
Research Closed EXPs remain bound to EI_CID_002_V0_1 + G5.
EI_CID_002_V0_2 adds Production-path MUST requirements.
```

## 2. Dependency manifest pin（repo）

| Field | Frozen value |
|-------|----------------|
| `requirements.txt` sha256 | `53a3f3f5b2fafb7e7da2f4df5f7944e7ea5a2f183a326893b02fb6f0cec35530` |
| Declared floor | `vnpy>=4.0.0` · `vnpy_ctastrategy>=1.4.0` · `tqsdk>=3.7.0` |
| Capture host tip | `b59f207edbb7e6c1bab40bd268f7da49d187b00b`（at EI v0.2 authoring） |
| Captured runtime | Python 3.13.13 · vnpy 4.4.0 · vnpy_ctastrategy 1.4.1 |

```text
Manifest pin ≠ lockfile.
Production Bindable still requires a full dep lock（§3）.
```

## 3. Production Bindable MUST（not yet satisfied）

Before any future Production Bindable grant, consumers MUST present:

| # | Artifact | Status now |
|---|----------|------------|
| P1 | Immutable build artifact ID（wheel/container digest） | **MISSING** |
| P2 | Full dependency lockfile（e.g. `uv.lock` / `requirements.lock` with hashes） | **MISSING** |
| P3 | Runtime image or reproducible env cert（OS + Python + vn.py stack） | **MISSING**（only research pin） |
| P4 | Deploy revision ≠ research tip alone（tagged release / signed commit） | **MISSING** |
| P5 | Brokerage/runtime contract distinct from CTA backtest fill_binding | **MISSING** |

```text
EI_CID_002_V0_2 freezes the checklist.
Satisfying P1–P5 requires separate delivery auth + evidence.
```

## 4. Runtime contract（unchanged research path）

```text
Research runtime contract remains CEMB-v1 + docs/07 + CTA backtest fills.
Production path MUST NOT silently reuse backtest fill_binding as live truth.
```

## 5. Closure verdict（R-EI）

```text
R-EI documentary spec:     CLOSED（this freeze）
R-EI production satisfaction: OPEN（P1–P5 missing）
Production Bindable:          STILL WITHHELD
```

## Explicit non-grants

```text
❌ Production Bindable / Production Readiness
❌ Deploy certificate
❌ Alpha / E4 / live trading
❌ RISK/MECH Verified upgrade
❌ Observation / backtest
```

## Next（须另授）

```text
Deliver P1–P5 under a Deploy Identity Delivery auth
  — OR — remain paused（recommended after Epoch 6 Pause）
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | EI_CID_002_V0_2 FROZEN · Production MUST checklist |
