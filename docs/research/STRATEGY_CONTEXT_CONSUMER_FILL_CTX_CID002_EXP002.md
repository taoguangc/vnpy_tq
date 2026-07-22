# Context Consumer Experiment Fill — CTX_CID002_EXP002

> **Status**: **CLOSED** ✓ · Observation **COMPLETE** · Outcome **KEEP**  
> **Experiment ID**: `CTX_CID002_EXP002`  
> **Date**: 2026-07-22  
> **Authorization**: Delegation-50J  
> **Prior**: `CTX_CID002_EXP001` CLOSED KEEP · `CCED_CID_002_V0_1`  
> **Eval**: [`STRATEGY_CONTEXT_CONSUMER_EVALUATION_CTX_CID002_EXP002.md`](STRATEGY_CONTEXT_CONSUMER_EVALUATION_CTX_CID002_EXP002.md)  
> **ER**: [`STRATEGY_CONTEXT_CONSUMER_EVIDENCE_REVIEW_CTX_CID002_EXP002.md`](STRATEGY_CONTEXT_CONSUMER_EVIDENCE_REVIEW_CTX_CID002_EXP002.md)  
> **Parents**: `BDR_CID_002_V0_1` · `CC-CID_002-v1` · `SIF_CID_002_V0_1_1` · A1 · Decision 019  
> **RC001-B**: **NOT REOPENED**

## Record

```text
================================================
CTX_CID002_EXP002 — CLOSED · KEEP

Hypothesis:     H_CTX_FILTER temporal OOS ADMITTED（non-inert）
Strategy:       MECH @0.1.1 only
Context role:   Filter F1（identical to EXP001）
Scope:          rb · 2025
N0 / N1 / D:    1053 / 828 / 365
Alpha claim:    NONE
================================================
```

## 1. Identity bindings（must match at run）

Same as EXP001 MECH surface:

| Field | Value |
|-------|-------|
| `consumer_surface` | `MECH` |
| `strategy_id` | `STRAT_TREND_BROOKS_SCALP_02` |
| `version` | `0.1.1` |
| `freeze_id` | `SIF_CID_002_V0_1_1` |
| `source_hash` | `1877dffe2108ba4237469b52bccc589d479811d4aea82c2764900cf74ad1d4c8` |
| `parameter_hash` | `3ff061891488a9d9f5641cf147efc1e70c8d4cb8410540858d8b727bd485d1ab` |
| `source_revision` | `833ae4740e6da3e2e3a42899d2bd4229f61785d6` |
| `detector_binding` | `BROOKS_SCALP_FP@0.1.0` |
| `context_version` | `A1-CTX-PS-v1.0.0` |
| `filter_id` | `F1_EXPANSION_ONLY` |

Mismatch → **abort**.

## 2. Primary hypothesis（one）

**Family**: `H_CTX_FILTER`

**Primary（falsifiable · temporal OOS）**:

> Under docs/07 · rb · **2025** · frozen MECH `@0.1.1` and identical Filter F1,
> the filter remains **non-inert** relative to unfiltered B0
> （`N0 ≥ 1` AND (`N1 ≠ N0` OR `D ≥ 1`)）
> without Context generating entries or supplying sizing alpha.

**Null**: Filter inert on 2025（`N1 == N0` AND `D == 0`）→ HOLD  
**Identity / role violation** → REVERT

## 3. Single variable

```text
VARIABLE_0: Filter F1 on/off（same as EXP001）
PERIOD: 2025-01-01 .. 2025-12-31 · warmup 2024-12-01
（year is the controlled OOS dimension vs EXP001）
```

## 4. Scope package

| Item | Value |
|------|-------|
| Symbol | `rb.SHFE` |
| Period | `2025-01-01` … `2025-12-31` |
| Warmup | `2024-12-01` |
| Data / costs | docs/07 · rate `0.00003` · slippage `1.0` · capital `200000` |

## 5. Decision rule（non-PnL primary）

Identical structure to EXP001 §5（KEEP / HOLD / REVERT）.  
PnL descriptive only.

## 6. Artifacts

```text
research/output/evidence/CTX_CID002_EXP002/
  run_metadata.json
  baseline_trades_audit.csv
  filtered_trades_audit.csv
  permission_denials.csv
  context_state_sample.json
  pre_registration.json
```

## 7. Non-claims

```text
❌ Context Alpha / Production
❌ PnL improvement as KEEP rationale
❌ RC001-B reopen
❌ Multi-symbol in this EXP
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-22 | PRE-REGISTERED under Delegation-50J |
| 2026-07-22 | Observation KEEP · CLOSED |
