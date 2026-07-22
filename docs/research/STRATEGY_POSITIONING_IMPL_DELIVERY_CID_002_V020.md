# Positioning Lineage 0.2.0 — Implementation Delivery

> **Status**: **DELIVERED** ✓  
> **Date**: 2026-07-22  
> **Authorization**: user **A** — `Authorize Implementation of Positioning Lineage 0.2.0`  
> **Freeze**: [`STRATEGY_IDENTITY_FREEZE_CID_002_V020.md`](STRATEGY_IDENTITY_FREEZE_CID_002_V020.md) · `SIF_CID_002_V0_2_0`

## Delivered artifacts

| Artifact | Path |
|----------|------|
| Strategy | `strategies/paaf/brooks_scalp_paaf_strategy_v020.py` |
| Unit tests | `tests/test_paaf_brooks_scalp_v020.py`（7 PASS） |
| Identity freeze | `SIF_CID_002_V0_2_0` |
| Capital gate EXP008 | `research/output/evidence/STRAT_BS02_EXP008/` · **REVERT**（cost-blind equity） |
| Capital gate EXP009 | `research/output/evidence/STRAT_BS02_EXP009/` · **KEEP**（kill-switch） |

## Controls implemented

```text
sizing_mode ∈ {RISK_FRACTION_OF_CAPITAL, FIXED_LOTS}
lots = floor(risk_cash / (stop_distance×size + round_trip_friction))
hard_max_lots cap；lots=0 → skip（no force）
equity_est = capital + Σ price_pnl − Σ(commission+slippage)
equity ≤ capital_floor → flatten + halt new entries
```

## Explicit non-claims

```text
❌ Bindable / Verified / Alpha
❌ H_MECH upgraded by sizing
❌ @0.1.1 bytes mutated
❌ PnL optimization
```

## Next（须另授）

```text
B. Authorize Bindable Pre-Review（consumption interface only）
C. Pause Epoch 5
D. Further capital-gate / multi-symbol positioning EXPs
```
