# SMC VWAP Z-Score Long Morphology Spec — CID_014

> **Type**: Morphology Spec · **Status**: **FROZEN** ✓  
> **Spec ID**: `SMC_ZSCORE_LONG_MS_V0_1` · Delegation-25BG · 2026-07-24  
> **Parent**: `NSAD_CID_014_V0_1`  
> **Provenance**: git `e2bfc0c…` · Setup B `_try_setup_b_stat` + `_update_zscore`

```text
Detector: SMC_ZSCORE_LONG@1.0.0 · 5m · LONG only · Context IGNORED · Alpha NONE
```

## Rules

```text
Session VWAP（Strategy injects from 1m ledger）:
  Reset at 21:00 Asia/Shanghai（new trading day）
  vwap = cum_turnover / cum_volume

Z-score on completed 5m am:
  length = min(vwap_length, count) · require length ≥ 10
  z = (close − vwap) / std(close[-length:] − vwap)

LONG when z < −zscore_threshold（default 2.5）:
  entry = high
  stop  = min(low[-lookback:]) − stop_buffer × tick
  require entry > stop + min_risk_ticks（default 5）

Defaults: vwap_length=60 · lookback=5 · stop_buffer=2
```

## OUT

```text
❌ OB / Setup A/C · Delta hard gate · scale-out · short mirror
```
