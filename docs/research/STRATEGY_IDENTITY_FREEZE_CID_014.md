# Strategy Identity Freeze — CID_014 / STRAT_SMC_ZSCORE_LONG_01@0.1.0

> **Status**: **FROZEN** ✓ · `SIF_CID_014_V0_1` · Delegation-25BG · 2026-07-24  
> **Design**: `NSAD_CID_014_V0_1` · `SMC_ZSCORE_LONG_MS_V0_1`

```text
strategy_id: STRAT_SMC_ZSCORE_LONG_01 @0.1.0
lifecycle:   Candidate · Bindable NO · Alpha NONE
detector:    SMC_ZSCORE_LONG@1.0.0
source_hash: d7b250179147bf61f6b55c0197abcb8deb6bb4db1a3b987e3b12e7c55830ec14
parameter_hash: de4e92d2e55be6526c6452ed1dbea4d11b99a9f09ea6de855980045967109836
source_revision: (binding tip — set at STOP commit)
≠ CID_013 OB fork
```

## source_manifest

```json
[
  {"path": "strategies/paaf/detectors/smc_zscore_long.py", "sha256": "09c6a0ccf5967292c1881905810e5cff81fed684c8fe65bb4f5f5cab6ebe5d18"},
  {"path": "strategies/paaf/strat_smc_zscore_long_01.py", "sha256": "a1cea8558b1224c3b5be6daf43dc84725d5152ddbdff4113dc4bba733ff9b543"}
]
```

## parameter_manifest

```json
{
  "fixed_size": {"type": "int", "unit": "contracts", "value": 1},
  "max_hold_bars": {"type": "int", "unit": "bars_1m", "value": 50},
  "min_risk_ticks": {"type": "float", "unit": "ticks", "value": 5.0},
  "risk_reward": {"type": "float", "unit": "dimensionless", "value": 1.0},
  "stop_buffer": {"type": "float", "unit": "ticks", "value": 2.0},
  "stop_lookback": {"type": "int", "unit": "bars_5m", "value": 5},
  "vwap_length": {"type": "int", "unit": "bars_5m", "value": 60},
  "zscore_threshold": {"type": "float", "unit": "dimensionless", "value": 2.5}
}
```
