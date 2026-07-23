# OPP02 EMA-Pullback Morphology Spec — CID_008

> **Type**: Morphology Spec（≠ Identity Freeze · ≠ Observation）  
> **Status**: **FROZEN** ✓  
> **Spec ID**: `OPP02_MS_V0_1`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-25AJ  
> **Parent**: `NSAD_CID_008_V0_1`  
> **Provenance**: git `e2bfc0c…` · `strategies/pa_cta/opp/opp02.py`

## Spec record

```text
================================================
OPP02_MS_V0_1

Detector id: OPP02@1.0.0（Candidate）
Timeframe:   5m completed bars
Scope:       EMA pullback continuation（single bar）
Context:     IGNORED in detect()
Alpha:       NONE
================================================
```

## 1. Trend-side proxy（replaces always_in）

```text
LONG side:  close > EMA
SHORT side: close < EMA
```

## 2. Touch + body + wick

```text
touch_band = atr × ema_pullback_touch_atr

LONG:
  low ≤ EMA + touch_band
  close > open
  body / range ≥ ema_pullback_min_body_ratio
  upper_wick < range × wick_max_fraction

SHORT: symmetric（high ≥ EMA − touch_band · close < open · lower wick）

entry = bar high/low · stop = bar low/high
```

Defaults: `touch_atr=1.0` · `min_body=0.35` · `wick_max=0.45` · `ema=20` · `atr=14`

## 3. Explicit simplifications vs legacy

```text
❌ always_in LONG/SHORT
❌ AFF / R² gates
❌ pd_blocks · is_oo · stop_cap · tick pad · pending-confirm
✓ close-vs-EMA side proxy declared here
```

## 4. Differentiation vs BROOKS_SCALP_FP / OPP08

```text
≠ BROOKS multi-bar trend-leg → pullback FSM
≠ OPP08 strong bar beyond prior extreme（breakout）
= single completed bar · EMA touch + directional body
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | OPP02_MS_V0_1 FROZEN · Delegation-25AJ |
