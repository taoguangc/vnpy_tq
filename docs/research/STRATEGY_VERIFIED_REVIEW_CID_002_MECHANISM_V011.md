# Verified Review — Mechanism Surface `@0.1.1`

> **Type**: Lifecycle Verified Review（≠ Bindable · ≠ Alpha · ≠ Production · ≠ Capital Surface）  
> **Status**: **COMPLETE** ✓  
> **Review ID**: `VR_CID_002_MECH_V0_1_1`  
> **Date**: 2026-07-22  
> **Authorization**: user **V** — `Authorize Verified Review for Mechanism Surface @0.1.1`  
> **Identity**: `SIF_CID_002_V0_1_1` · `STRAT_TREND_BROOKS_SCALP_02@0.1.1`  
> **Detector**: `BROOKS_SCALP_FP@0.1.0`  
> **Contracts**: `SAC-v1` · `SEVF-v1` · `CEMB-v1`  
> **Parents**: `SAR_CID_002_V0_6` · `BPR_CID_002_V0_1` · Delegation-50 / 50B / 50C bundles

## Review record

```text
================================================
VR_CID_002_MECH_V0_1_1

Surface:              Mechanism only（@0.1.1）
Hypothesis admitted:  H_MECH（auditability）
Lifecycle stamp:      Verified ✓（narrow）
Evidence level:       E3（multi-symbol + same-hash OOS EXP011）· NOT E4

Capital Surface @0.2.0:  NOT IN SCOPE
Bindable:                STILL WITHHELD
Alpha / Production:      NONE / NO
================================================
```

> **Amendment**: [`STRATEGY_VERIFIED_REVIEW_CID_002_MECHANISM_V011_AMENDMENT_E3.md`](STRATEGY_VERIFIED_REVIEW_CID_002_MECHANISM_V011_AMENDMENT_E3.md) · `VR_CID_002_MECH_V0_1_1_A1`

## 1. Scope（what Verified means here）

```text
Verified（this stamp）=
  Under frozen @0.1.1 identity hashes, H_MECH is supported by Closed
  auditable experiments + Evidence Review：
  signal → entry → exit reasons attributable to BROOKS_SCALP_FP
  across the declared scopes below.

Verified（this stamp）≠
  profitable strategy
  Bindable consumer asset
  capital survival
  Production / live default
  permission for Context routing
```

Hypothesis under review（only）:

```text
H_MECH: The frozen mechanism surface produces auditable
        DetectionResult → stop entry → STOP|TARGET|TIME_STOP exits
        attributable to BROOKS_SCALP_FP@0.1.0.
```

## 2. Same-hash evidence package（@0.1.1）

SAC/SEVF require Closed artifacts on the **same** `source_hash` / `parameter_hash`.

| Field | Value |
|-------|--------|
| `source_hash` | `1877dffe2108ba4237469b52bccc589d479811d4aea82c2764900cf74ad1d4c8` |
| `parameter_hash` | `3ff061891488a9d9f5641cf147efc1e70c8d4cb8410540858d8b727bd485d1ab` |
| `freeze_id` | `SIF_CID_002_V0_1_1` |

| EXP | Family | Scope | Outcome | Role for Verified |
|-----|--------|-------|---------|-------------------|
| EXP005 | H_MECH | rb/2024 · rollover smoke | **KEEP** | Same-hash mechanism after repair |
| EXP006 | H_ROBUST | rb/2024 · slippage×2 | **KEEP** | Cost dimension；auditability retained |
| EXP007 | H_MECH | {rb,i,MA}/2024 | **KEEP** | Multi-symbol auditability（E2 gate） |

Bundle Evidence Review: **PASS**（[`STRATEGY_DELEGATION_50C_EVIDENCE_BUNDLE.md`](STRATEGY_DELEGATION_50C_EVIDENCE_BUNDLE.md)）.

### Parent lineage（supporting · not same-hash）

| EXP | Identity | Note |
|-----|----------|------|
| EXP001–004 | `@0.1.0` | Continuity of H_MECH / H_NULL story；**cannot** alone stamp `@0.1.1` Verified |
| EXP004 OOS 2025 | `@0.1.0` | Temporal support for morphology class；**not** `@0.1.1` E3 |

```text
Parent KEEP may inform confidence.
Only EXP005–007 satisfy same-hash Verified input for @0.1.1.
```

## 3. Gate checklist

| Gate | Result | Note |
|------|--------|------|
| Identity frozen | PASS | `SIF_CID_002_V0_1_1` |
| Same-hash Closed EXPs | PASS | EXP005–007 |
| Auditable exits / detector attribution | PASS | H_MECH KEEP semantics |
| Evidence Review fidelity | PASS | 50C bundle |
| Single hypothesis（no PnL promotion） | PASS | no Alpha gate |
| Capital breach isolated | PASS | EXP007 `i` capital≤0 ≠ H_MECH fail |
| Risk Surface `@0.2.0` excluded | PASS | dual-surface rule from BPR |
| docs/03 Verified「跨样本或跨品种」 | PASS via **跨品种**（EXP007） | |
| E3 same-hash multi-year/OOS | **FAIL / residual R1** | no `@0.1.1` 2025 OOS |
| Bindable readiness | **N/A · withheld** | BPR G0–G7 remain |

## 4. Decision

```text
GRANT:  Lifecycle status Verified on Mechanism Surface @0.1.1
        for hypothesis H_MECH（auditability）only.

BOUND:  Declared scopes of EXP005–007（docs/07 · 2024 · listed symbols/cost）.
LEVEL:  Evidence maturity E2（multi-symbol）.
HOLD:   E3 / E4 / Alpha / Bindable / Production / Capital Verified.
```

### Explicit non-grants

```text
❌ Verified does not transfer to @0.2.0
❌ Verified does not imply H_NULL re-test on @0.1.1
❌ Verified does not clear Bindable gaps（G0–G7）
❌ Verified does not authorize live trading
❌ Verified does not reopen RC001-B or CAP-CTX-001
```

## 5. Residuals（do not block this narrow stamp）

| ID | Residual | Effect |
|----|----------|--------|
| **R1** | No same-hash temporal OOS on `@0.1.1` | Blocks E3；does not block E2-Verified via multi-symbol |
| **R2** | H_NULL only on `@0.1.0` | Expectancy story stays on parent；not required for H_MECH Verified |
| **R3** | `UNBOUND_AT_ASSET` + EXP-declared scopes | Consumer must restate scope；Bindable still open |
| **R4** | Content-addressed sources（uncommitted） | Testing/Verified allowed；Bindable prefers repo revision |
| **R5** | `i` capital death under fixed_size=1 | Capital Surface / `@0.2.0` problem — not H_MECH falsification |

## 6. Consumer citation rule（extends CC-CID_002-v0.1）

```text
When citing “Verified mechanism”:
  • identity = STRAT_TREND_BROOKS_SCALP_02@0.1.1
  • freeze  = SIF_CID_002_V0_1_1
  • claim   = H_MECH auditability · E2
  • MUST NOT cite as Alpha / Bindable / capital-safe / @0.2.0 Verified
```

## 7. Next（须另授）

```text
G. Authorize Bindable Gap-Closure Charter
C. Pause Epoch 5
O. Authorize @0.1.1 temporal OOS（E3 attempt · new EXP · still ≠ Bindable）
P. Context Consumer Experiment Design（still blocked until Bindable）
```

## Hard guarantees

```text
✓ No new Observation / backtest under this authorization
✓ No code / parameter change
✓ No Bindable / Alpha / Production grant
✓ Capital Surface untouched
✓ Negative evidence retained（EXP002 · EXP003 · EXP007 capital note · EXP008）
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-22 | VR_CID_002_MECH_V0_1_1 COMPLETE · Verified GRANTED（narrow H_MECH · E2） |
