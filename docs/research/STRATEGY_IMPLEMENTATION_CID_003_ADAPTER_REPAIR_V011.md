# CID_003 Implementation — Adapter Repair Lineage @0.1.1

> **Status**: **IMPLEMENTED** ✓  
> **Date**: 2026-07-23  
> **Authorization**: user **A** — `Authorize Implementation of CID_003 adapter repair lineage @0.1.1`  
> **Engineering**: `ENG_REV_CID_003_ZERO_TRADE_V0_1`  
> **Identity**: `SIF_CID_003_V0_1_1`

## Changes

| Path | Change |
|------|--------|
| `strategies/paaf/adapters/vnpy_adapter.py` | `_series_len` = `min(count, len(close))`；`len` via `_array_window_len`（numpy 兼容）；`bars_from_am` 负下标 |
| `strategies/paaf/strat_rev_opp16_01_v011.py` | `StratRevOpp1601StrategyV011` · `strategy_version=0.1.1` |
| `strategies/paaf/strat_rev_opp16_01.py` | **unchanged**（@0.1.0） |
| `OPP16` detector | **unchanged** |
| `tests/test_paaf_adapter.py` | ArrayManager `count > size` regression |
| `tests/cid003/test_identity_hashes_v011.py` | @0.1.1 hash echo |

## Non-changes

```text
❌ Closed STRAT_RO16_EXP001 not reopened
❌ No Observation / Fill in this authorization
❌ No parameter change
❌ No Alpha / Bindable claim
```

## Fingerprints

```text
source_hash:    6dee22fe6c1eaf5958defa3f94db614ece5991bdbc58abc93d281bbd7b1164b5
parameter_hash: 76b124f47414af2da2e0cdfdc6afcd5025d2cca8ae3a5583ba667cc7e1e31c57
```
