# OPP19 Opening-Drive Reversal Morphology Spec — CID_011

> **Type**: Morphology Spec（≠ Identity Freeze · ≠ Observation）  
> **Status**: **FROZEN** ✓  
> **Spec ID**: `OPP19_REV_MS_V0_1`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-25AS  
> **Parent**: `NSAD_CID_011_V0_1`  
> **Provenance**: git `e2bfc0c…` · `strategies/pa_cta/opp/opp19.py` OD_REV only  
> **Explicit**: ≠ `OPP19_MS_V0_1`（CID_007 OD-Breakout）

## Spec record

```text
================================================
OPP19_REV_MS_V0_1

Detector id: OPP19_REV@1.0.0（Candidate）
Timeframe:   5m completed bars
Scope:       Opening-drive REVERSAL only（OD-Breakout OUT）
Context:     IGNORED in detect()
Alpha:       NONE
================================================
```

## 1. Session windows

```text
Morning: 09:00–11:30 · Night: 21:00–23:00
Outside window → reset FSM to IDLE
Signal arm cutoff: morning ≤ 09:25 · night ≤ 21:25
```

## 2. FSM

```text
IDLE → BAR1_SET on session open bar with body/range ≥ opening_rev_body_ratio
       （shape UP/DOWN · mid=(H+L)/2 · bar1_range）
BAR1_SET → SIGNAL when bars_collected ≤ 2 and reverse bar clears mid
BAR1_SET → IDLE after bars_collected > 2 without signal · or session exit
```

Default: `opening_rev_body_ratio=0.45`

## 3. Reverse signal

```text
LONG:  bar1=DOWN · close>open · body/range ≥ ratio · close > bar1_mid
SHORT: bar1=UP   · close<open · body/range ≥ ratio · close < bar1_mid

Optional ATR band on bar1_range/atr ∈ [min, max]
Defaults: min=0.30 · max=2.50（pure ATR · not Context）

entry = bar high/low · stop = bar low/high
```

## 4. Explicit OUT of scope

```text
❌ OD-Breakout / OR range collection / RANGE_SET
❌ always_in · effective_context / opp19_rev_contexts
❌ CID_007 byte reuse / parameter transfer
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | OPP19_REV_MS_V0_1 FROZEN · Delegation-25AS |
