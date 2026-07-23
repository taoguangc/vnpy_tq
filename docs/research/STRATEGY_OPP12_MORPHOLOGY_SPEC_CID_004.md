# OPP12 Overshoot-Fail Morphology Spec — CID_004

> **Type**: Morphology Spec（≠ Identity Freeze · ≠ Observation）  
> **Status**: **FROZEN** ✓  
> **Spec ID**: `OPP12_MS_V0_1`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-25O  
> **Parent**: `NSAD_CID_004_V0_1`  
> **Provenance**: git `e2bfc0c…` · `strategies/pa_cta/opp/opp12.py`（REWRITE_AS_PAAF · not byte-copy）

## Spec record

```text
================================================
OPP12_MS_V0_1

Detector id: OPP12@1.0.0（Candidate）
Timeframe:   5m completed bars
Context:     IGNORED in detect()（Decision 019 consumer later only）
Alpha:       NONE
================================================
```

## 1. Indicators（on signal AM）

| Name | Definition | Default |
|------|------------|---------|
| ATR | `am.atr(atr_period)` | `atr_period=14` |
| EMA | `am.ema(ema_period)` | `ema_period=20` |

## 2. Reversal bar（from legacy `bar_patterns` defaults）

On bar `b` with `range = high−low > 0`:

**Bull reversal**

```text
lower_shadow >= range × 0.40
close >= high − range × 0.25
body >= range × 0.15
```

**Bear reversal**

```text
upper_shadow >= range × 0.40
close <= low + range × 0.25
body >= range × 0.15
```

## 3. Long setup（overshoot fail）

```text
depth = EMA − close
atr × overshoot_atr_mult <= depth <= atr × overshoot_max_atr_mult
AND bull reversal
AND close > open

entry = high   （stop-entry trigger）
stop  = low
```

Defaults: `overshoot_atr_mult=1.2` · `overshoot_max_atr_mult=2.5`

## 4. Short setup（overshoot fail）

```text
close > EMA + atr × overshoot_atr_mult
AND bear reversal

entry = low
stop  = high
```

```text
Note: legacy short side had no max-ATR cap — retained.
```

## 5. Explicit simplifications vs legacy mixin

```text
OMITTED from v1.0.0 Candidate:
  • _pd_blocks_* prior-day level veto
  • stop_buffer / tick pad on stop
  • is_oo opening-bar veto
  • pending-confirm state machine（orchestrator uses stop entry directly）
  • BULL/BEAR_CHANNEL Context pre-filter（Context independence）

These are declared deviations · not silent “improvements for PnL”.
```

## 6. Non-claims

```text
❌ Alpha / edge
❌ Faithful bit-identical pa_cta OPP12
❌ Context routing
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | OPP12_MS_V0_1 FROZEN · Delegation-25O |
