# OPP17 Climax-Reversal Morphology Spec — CID_005

> **Type**: Morphology Spec（≠ Identity Freeze · ≠ Observation）  
> **Status**: **FROZEN** ✓  
> **Spec ID**: `OPP17_MS_V0_1`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-25T  
> **Parent**: `NSAD_CID_005_V0_1`  
> **Provenance**: git `e2bfc0c…` · `strategies/pa_cta/opp/opp17.py`（REWRITE_AS_PAAF · not byte-copy）

## Spec record

```text
================================================
OPP17_MS_V0_1

Detector id: OPP17@1.0.0（Candidate）
Timeframe:   5m completed bars
Context:     IGNORED in detect()（Decision 019 consumer later only）
Alpha:       NONE
================================================
```

## 1. Indicators（on signal AM）

| Name | Definition | Default |
|------|------------|---------|
| ATR | `am.atr(atr_period)` | `atr_period=14` |

## 2. Prior climax bar

On completed bars `prev = bars[-2]`, `bar = bars[-1]`:

```text
prev_range = prev.high − prev.low
require: prev_range > atr × climax_range_atr
prev_mid = (prev.high + prev.low) / 2
```

Default: `climax_range_atr=2.5`（legacy `climax_rev_range_atr`）

## 3. Long setup

```text
prev.close < prev.open
AND bar.close > prev_mid
AND bar.high − bar.low > 0

entry = bar.high
stop  = bar.low
```

## 4. Short setup

```text
prev.close > prev.open
AND bar.close < prev_mid
AND bar.high − bar.low > 0

entry = bar.low
stop  = bar.high
```

## 5. Explicit simplifications vs legacy mixin

```text
❌ effective_context allow-list（climax_rev_context）
❌ is_oo gate
❌ tick pad on trigger（entry uses bar high/low）
❌ stop_buffer / _cap_*_stop（stop = bar extreme）
❌ pending-confirm FSM（Strategy owns stop-entry）
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | OPP17_MS_V0_1 FROZEN · Delegation-25T |
