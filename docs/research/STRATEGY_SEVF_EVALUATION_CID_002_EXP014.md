# SEVF Evaluation — STRAT_BS02_EXP014

> **Type**: Closed Evaluation  
> **Status**: **CLOSED** ✓  
> **Experiment ID**: `STRAT_BS02_EXP014`  
> **Date**: 2026-07-23  
> **Authorization**: `Authorize Offline Alpha Evidence Observation for STRAT_BS02_EXP014`  
> **Fill**: [`STRATEGY_SEVF_FILL_CID_002_EXP014.md`](STRATEGY_SEVF_FILL_CID_002_EXP014.md)  
> **Prior**: `STRAT_BS02_EXP013` **REVERT**（immutable）  
> **Artifacts**: `research/output/evidence/STRAT_BS02_EXP014/`

## Outcome

```text
Bundle outcome: REVERT
Hypothesis:     H_EDGE_OOS（rb/2025 · @0.1.1）
Framing held:   temporal completeness · NOT rescue of EXP013
```

## Diagnostics（identical gates to EXP013）

| Metric | Value | Gate | Pass? |
|--------|-------|------|-------|
| n_trade_log | 1053 | ≥50 | yes |
| n_round_trips | 987 | ≥50 | yes |
| median_mfe_ticks | 2.0 | > median_mae | **no**（mae=3.0） |
| share_mfe_gt_mae | 0.306 | ≥0.55 | **no** |
| mean_net_pnl | ≈ −30.19 | >0 | **no** |
| p_one_sided（μ>0） | 1.0 | <0.05 | **no** |

```text
structure_ok = False
expectancy_ok = False
→ REVERT
```

## Temporal chain

| EXP | Scope | H_EDGE screen | Status |
|-----|-------|---------------|--------|
| EXP013 | rb/2024 | REVERT | Closed |
| EXP014 | rb/2025 OOS | REVERT | Closed |

```text
EXP013 failure is not shown to be 2024-local under this screen:
same gates fail on 2025 OOS.
```

## Rule fidelity

```text
✓ Hash match @0.1.1
✓ Gates unchanged vs EXP013
✓ No param / metric / cost change
✓ Rescue framing rejected
✓ H_MECH not re-litigated
```

## Non-claims

```text
❌ Alpha / Alpha Candidate
❌ Permission to retune to flip KEEP
❌ Production / CSD
❌ “H_MECH invalid”（Verified retained）
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | CLOSED · REVERT |
