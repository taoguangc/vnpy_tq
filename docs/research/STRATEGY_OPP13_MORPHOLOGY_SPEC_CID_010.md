# OPP13 Day-Boundary Single-Touch Morphology Spec — CID_010

> **Type**: Morphology Spec（≠ Identity Freeze · ≠ Observation）  
> **Status**: **FROZEN** ✓  
> **Spec ID**: `OPP13_MS_V0_1`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-25AP  
> **Parent**: `NSAD_CID_010_V0_1`  
> **Provenance**: git `e2bfc0c…` · `strategies/pa_cta/opp/opp13.py` Path A only

## Spec record

```text
================================================
OPP13_MS_V0_1

Detector id: OPP13@1.0.0（Candidate）
Timeframe:   5m completed bars
Scope:       Day-high / day-low SINGLE-TOUCH fail only
Context:     IGNORED in detect()
Alpha:       NONE
================================================
```

## 1. Day levels

```text
Reset day_high / day_low when bar.time == 09:06（legacy）OR levels unset
Else update: day_high = max(…, high) · day_low = min(…, low)
Requires Strategy note_bar_datetime
CbC: adjust_levels(shift)
```

## 2. Single-touch signal

```text
tolerance = day_boundary_tolerance × pricetick
Default: day_boundary_tolerance=5.0

SHORT（day-high touch）:
  |high − day_high| ≤ tolerance
  close < open
  upper_shadow ≥ range × boundary_reversal_shadow_ratio（0.45）
  close ≤ low + range × boundary_reversal_close_ratio（0.30）
  entry = low · stop = high + tick

LONG（day-low touch）: symmetric
```

## 3. Explicit OUT of scope

```text
❌ day_high double-top / FIRST_TEST FSM
❌ always_in · market_context · late_phase · volume stack
❌ bulldozer / bearish-pulse skip filters
❌ pd_blocks · is_oo
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | OPP13_MS_V0_1 FROZEN · Delegation-25AP |
