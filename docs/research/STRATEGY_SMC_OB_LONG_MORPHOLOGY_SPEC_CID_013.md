# SMC Bullish Order-Block Morphology Spec — CID_013

> **Type**: Morphology Spec（≠ Identity Freeze · ≠ Observation）  
> **Status**: **FROZEN** ✓  
> **Spec ID**: `SMC_OB_LONG_MS_V0_1`  
> **Date**: 2026-07-24  
> **Authorization**: Delegation-25BD  
> **Parent**: `NSAD_CID_013_V0_1`  
> **Provenance**: git `e2bfc0c…` · `smc_orderflow_vwap_strategy.py` · `_update_smc_structure` + reclaim

## Spec record

```text
================================================
SMC_OB_LONG_MS_V0_1

Detector id: SMC_OB_LONG@1.0.0（Candidate）
Timeframe:   5m completed bars
Scope:       Bullish OB after liquidity sweep · LONG reclaim only
Context:     IGNORED in detect()
Alpha:       NONE
================================================
```

## 1. Liquidity sweep → Order Block

```text
Requires am.count ≥ smc_min_bars（16）and ≥ smc_pool_bars+2（14）

After current bar is in am[-1]:
  pool = lows of am.low[-(pool+2):-2]
  sweep bar = am[-2]
  IF sweep.low < min(pool) AND sweep.close > min(pool):
    ob_low  = min(sweep.open, sweep.close)
    ob_high = sweep.high
    FSM → OB_SET

Defaults: smc_pool_bars=12 · smc_min_bars=16
```

## 2. Invalidation

```text
If OB_SET and close < ob_low → IDLE（OB destroyed）
```

## 3. LONG confirmation（Freeze pick）

```text
Pick: close reclaim above ob_high
  OB_SET AND close > ob_high
  → LONG
  entry = high
  stop  = ob_low − ob_stop_buffer × pricetick（default buffer=2）
  → IDLE（OB consumed）
```

## 4. Explicit OUT of scope

```text
❌ VWAP z-score hard gate · bar-delta hard gate
❌ Setup B / Setup C toggle paths
❌ OPP16 slow-channel · scale-out
❌ Short / bearish OB mirror
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-24 | SMC_OB_LONG_MS_V0_1 FROZEN · Delegation-25BD |
