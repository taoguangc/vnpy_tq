# SEVF Evaluation — STRAT_RO16_EXP002

> **Type**: Closed Evaluation  
> **Status**: **CLOSED** ✓  
> **Experiment ID**: `STRAT_RO16_EXP002`  
> **Date**: 2026-07-23  
> **Authorization**: `Authorize Offline Observation for STRAT_RO16_EXP002`  
> **Fill**: [`STRATEGY_SEVF_FILL_CID_003_EXP002.md`](STRATEGY_SEVF_FILL_CID_003_EXP002.md)  
> **Identity**: `SIF_CID_003_V0_1_1` · `@0.1.1`  
> **Artifacts**: `research/output/evidence/STRAT_RO16_EXP002/`（local · gitignored under `research/output/`）

## Outcome

```text
Bundle outcome: KEEP
Hypothesis:     H_MECH（auditability · rb/2024 · @0.1.1）
Meaning:        ≥1 auditable closed exit attributed to OPP16@1.0.0
                under repaired identity + pre-registered scope
                ≠ Alpha · ≠ Bindable · ≠ H_EDGE · ≠ Verified automatic
```

## Diagnostics

| Check | Result |
|-------|--------|
| source_hash / parameter_hash | **match** |
| missing on_rollover_adjust WARN | **absent** |
| closed trade_log rows in 2024 window | **1920** |
| attributed exits {STOP,TARGET,TIME_STOP} | **1920** |
| exit_reason mix（descriptive） | STOP 938 · TARGET 877 · TIME_STOP 105 |
| direction mix（descriptive） | 空 1095 · 多 825 |
| engine_total_net_pnl（descriptive only） | **−37703.02**（NOT a KEEP/REVERT driver） |

```text
Decision rule → KEEP（identity OK · no missing-hook WARN · attributed_exits ≥ 1）
```

## Contrast to EXP001（descriptive）

```text
EXP001 @0.1.0: HOLD · 0 exits（adapter window defect · IMMUTABLE）
EXP002 @0.1.1: KEEP · 1920 attributed exits
Single variable held: repair identity under same rb/2024 continuity scope
```

## Rule fidelity

```text
✓ Pre-registered gates only
✓ PnL not used as KEEP driver（despite negative net）
✓ Hashes echoed（@0.1.1 manifest includes adapter）
✓ No rescue retune under this auth
✓ EXP001 not rewritten
```

## Non-claims

```text
❌ Alpha / expectancy proven（net PnL negative on this run — descriptive）
❌ H_EDGE KEEP
❌ Bindable / Verified / Production
❌ Multi-symbol / OOS robustness
❌ “OPP16 profitable”
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | CLOSED · KEEP |
