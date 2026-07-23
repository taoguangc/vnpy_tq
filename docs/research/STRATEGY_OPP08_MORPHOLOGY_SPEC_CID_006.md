# OPP08 Strong-Breakout Morphology Spec — CID_006

> **Type**: Morphology Spec（≠ Identity Freeze · ≠ Observation）  
> **Status**: **FROZEN** ✓  
> **Spec ID**: `OPP08_MS_V0_1`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-25Z  
> **Parent**: `NSAD_CID_006_V0_1`  
> **Provenance**: git `e2bfc0c…` · `strategies/pa_cta/opp/opp08.py`（REWRITE_AS_PAAF · not byte-copy）

## Spec record

```text
================================================
OPP08_MS_V0_1

Detector id: OPP08@1.0.0（Candidate）
Timeframe:   5m completed bars
Context:     IGNORED in detect()
Alpha:       NONE
================================================
```

## 1. Indicators

| Name | Definition | Default |
|------|------------|---------|
| ATR | `am.atr(atr_period)` | `atr_period=14` |
| EMA | `am.ema(ema_period)` | `ema_period=20` |

## 2. Strong bar

```text
body = |close − open|
range = high − low > 0
body ≥ range × strong_bar_body_ratio
range > atr × strong_bar_atr_mult
```

Defaults: `strong_bar_body_ratio=0.6` · `strong_bar_atr_mult=1.0`

## 3. Long setup

```text
strong bar
AND close > open
AND close > EMA
AND close > prev.high

entry = bar.high
stop  = bar.low
```

## 4. Short setup（symmetric）

```text
strong bar
AND close < open
AND close < EMA
AND close < prev.low

entry = bar.low
stop  = bar.high
```

## 5. Explicit simplifications vs legacy mixin

```text
❌ effective_context STRONG_BULL / STRONG_BEAR / BEAR_CHANNEL
❌ BEAR_CHANNEL asymmetric recent_5bar_low branch
❌ climax flags / is_oo / stop_cap / tick pad
❌ pending / fast-track FSM（Strategy owns stop-entry）
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | OPP08_MS_V0_1 FROZEN · Delegation-25Z |
