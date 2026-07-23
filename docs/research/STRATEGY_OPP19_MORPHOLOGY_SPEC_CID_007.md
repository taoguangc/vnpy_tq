# OPP19 Opening-Drive Breakout Morphology Spec — CID_007

> **Type**: Morphology Spec（≠ Identity Freeze · ≠ Observation）  
> **Status**: **FROZEN** ✓  
> **Spec ID**: `OPP19_MS_V0_1`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-25AE  
> **Parent**: `NSAD_CID_007_V0_1`  
> **Provenance**: git `e2bfc0c…` · `strategies/pa_cta/opp/opp19.py` Path A only

## Spec record

```text
================================================
OPP19_MS_V0_1

Detector id: OPP19@1.0.0（Candidate）
Timeframe:   5m completed bars
Scope:       Opening-drive BREAKOUT only（OD_REV OUT）
Context:     IGNORED in detect()
Alpha:       NONE
================================================
```

## 1. Session windows

```text
Morning: 09:00–11:30
Night:   21:00–23:00
Outside window → reset FSM to IDLE
```

## 2. FSM

```text
IDLE → COLLECTING（new session / morning<09:20 / night<21:20）
COLLECTING → RANGE_SET when N bars collected AND
             (OR_high − OR_low) ≥ atr × opening_drive_range_atr_min
RANGE_SET → IDLE after signal OR bars_collected > range_set_max_bars（24）
```

Defaults: `opening_drive_bars=6` · `opening_drive_range_atr_min=0.2`

## 3. Strong bar（breakout bar）

```text
body ≥ range × strong_bar_body_ratio
range > atr × strong_bar_atr_mult
```

Defaults: `0.6` · `1.0`

## 4. Long / Short breakout

```text
LONG:  close > OR_high AND close > open AND body/range ≥ opening_drive_min_body
       AND strong bar
SHORT: close < OR_low AND close < open AND body/range ≥ opening_drive_min_body
       AND strong bar

entry = bar high/low · stop = bar low/high
```

Default: `opening_drive_min_body=0.50`

## 5. Explicit simplifications vs legacy

```text
❌ OD_REV path
❌ effective_context soft bans
❌ AFF / R² gates
❌ tick pad / stop_cap / fast-track FSM in Detector
✓ Strategy injects bar.datetime via note_bar_datetime
✓ PatternState serializes FSM
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | OPP19_MS_V0_1 FROZEN · Delegation-25AE |
