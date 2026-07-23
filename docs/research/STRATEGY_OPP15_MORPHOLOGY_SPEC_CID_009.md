# OPP15 Wedge Path-A Morphology Spec — CID_009

> **Type**: Morphology Spec（≠ Identity Freeze · ≠ Observation）  
> **Status**: **FROZEN** ✓  
> **Spec ID**: `OPP15_MS_V0_1`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-25AM  
> **Parent**: `NSAD_CID_009_V0_1`  
> **Provenance**: git `e2bfc0c…` · `strategies/pa_cta/opp/opp15.py` Path A · `wedge.py` scanner

## Spec record

```text
================================================
OPP15_MS_V0_1

Detector id: OPP15@1.0.0（Candidate）
Timeframe:   5m completed bars
Scope:       Wedge Path A only（strong-bar reverse through trigger）
Context:     IGNORED in detect()
Alpha:       NONE
================================================
```

## 1. Scanner（pure）

```text
Module: strategies/paaf/morphology/wedge.py（extracted from pa_cta/wedge.py）
HH3 → short candidate · LL3 → long candidate
Defaults: n_min=3 · alpha_threshold=0.85
Arm requires: status wedge_valid:* AND ≥2 bars after p3_idx
```

## 2. FSM

```text
IDLE → ARMED when valid HH3/LL3 scanned（no Context / MTF / session gates）
ARMED → IDLE on:
  · invalidate（short: high > p3 + tick · long: low < p3 − tick）
  · expire（bars_since > wedge_arm_trigger_max_bars）
  · SIGNAL Path A（then reset）
```

Default: `wedge_arm_trigger_max_bars=4`

## 3. Path A signal

```text
Strong bar: body ≥ range × strong_bar_body_ratio
            AND range > atr × strong_bar_atr_mult
Defaults: 0.6 · 1.0

SHORT（HH3）:
  close < open · close < trigger_line
  trigger_line = min(low[-2], low[-3])（exclude signal bar）
  entry = bar.low · stop = p3_high + tick

LONG（LL3）: symmetric（trigger = max(high[-2], high[-3])）

Declared vs legacy: legacy min(low[-1], low[-2]) makes close < trigger
impossible; Path A uses prior two extremes excluding the signal bar.
```

## 4. Explicit OUT of scope

```text
❌ Path B' alpha-decay
❌ MTF 15m exhaustion zone
❌ market_context / always_in / late_phase / session clock / atr floor
❌ pd_blocks · stop_cap · tick-padded entry trigger
```

## 5. Strategy injection

```text
✓ note_bar_datetime（arm clock）
✓ set_pricetick / adjust_levels on CbC shift
✓ PatternState serializes FSM
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | OPP15_MS_V0_1 FROZEN · Delegation-25AM |
