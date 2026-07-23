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

| # | Artifact | Status after `DID_CID_002_V0_1` |
|---|----------|----------------------------------|
| P1 | Immutable build artifact ID（wheel/container digest） | **PARTIAL**（content-addressed source+lock set · not image） |
| P2 | Full dependency lockfile | **CLOSED**（`requirements.lock`） |
| P3 | Runtime image or reproducible env cert | **PARTIAL**（host attestation only） |
| P4 | Deploy revision ≠ research tip alone | **PARTIAL**（delivery commit · not signed tag） |
| P5 | Brokerage/runtime contract ≠ backtest fills | **CLOSED**（`LRC-CID_002-v0.1`）· venue evidence pack still **OPEN** |


```text
See STRATEGY_DEPLOY_IDENTITY_DELIVERY_CID_002.md
Production Bindable still WITHHELD.
```

## 4. Runtime contract（unchanged research path）

```text
Research runtime contract remains CEMB-v1 + docs/07 + CTA backtest fills.
Production path MUST NOT silently reuse backtest fill_binding as live truth.
```

## 5. Closure verdict（R-EI）

```text
R-EI documentary spec:        CLOSED（EI_CID_002_V0_2）
R-EI production satisfaction: PARTIAL（DID_CID_002_V0_1 · P2 closed · others partial/draft）
Production Bindable:          STILL WITHHELD
```

## Next（须另授）

```text
Container digest · LRC freeze · RISK OOS E3 · or remain paused
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | EI_CID_002_V0_2 FROZEN · Production MUST checklist |
| 2026-07-23 | Linked DID_CID_002_V0_1 PARTIAL delivery |
