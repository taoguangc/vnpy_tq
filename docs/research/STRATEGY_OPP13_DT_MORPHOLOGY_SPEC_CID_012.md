# OPP13 Day-High Double-Top Morphology Spec — CID_012

> **Type**: Morphology Spec（≠ Identity Freeze · ≠ Observation）  
> **Status**: **FROZEN** ✓  
> **Spec ID**: `OPP13_DT_MS_V0_1`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-25AV  
> **Parent**: `NSAD_CID_012_V0_1`  
> **Provenance**: git `e2bfc0c…` · `strategies/pa_cta/opp/opp13.py` · `_try_day_high_double_top` only

## Spec record

```text
================================================
OPP13_DT_MS_V0_1

Detector id: OPP13_DT@1.0.0（Candidate）
Timeframe:   5m completed bars
Scope:       Day-high FIRST_TEST → LH second-test SHORT only
Context:     IGNORED in detect()
Alpha:       NONE
================================================
```

## 1. Day levels

```text
Reset day_high / day_low when bar.time == 09:06（legacy）OR levels unset
On day reset: also reset FSM → IDLE · clear first_test_high
Else update: day_high = max(…, high) · day_low = min(…, low)
Requires Strategy note_bar_datetime
CbC: adjust_levels(shift) for day levels + first_test_high
```

## 2. Quality day-high short bar（legacy extract）

```text
is_quality_day_high_short:
  upper_shadow ≥ range × quality_shadow_ratio（0.40）
  close ≤ high − range × quality_close_from_high_ratio（0.35）
  AND boundary-bear shape:
    upper_shadow ≥ range × boundary_reversal_shadow_ratio（0.45）
    close ≤ low + range × boundary_reversal_close_ratio（0.30）
```

## 3. FSM

```text
IDLE → FIRST_TEST:
  |high − day_high| ≤ day_high_second_test_ticks × pricetick（default 3）
  AND is_quality_day_high_short
  → arm FIRST_TEST · first_test_high = high · bar_count = 0
  detect() returns None（state only）

FIRST_TEST → timeout IDLE:
  each subsequent bar: bar_count += 1
  if bar_count > day_high_second_test_max_bars（12）→ reset IDLE

FIRST_TEST → SIGNAL（SHORT）→ IDLE:
  bar_count ≤ max_bars
  high ≤ first_test_high
  high ≥ first_test_high − day_high_lh_max_ticks × pricetick（10）
  AND is_quality_day_high_short
  → entry = low · stop = high + tick · reset FSM
```

## 4. Explicit OUT of scope

```text
❌ day-boundary single-touch Path A（CID_010 · OPP13_MS_V0_1）
❌ day-low mirror double-bottom
❌ always_in · market_context · late_phase · volume stack · pd_blocks · is_oo
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | OPP13_DT_MS_V0_1 FROZEN · Delegation-25AV |
