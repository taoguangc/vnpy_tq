# SEVF Evaluation — STRAT_TO08_EXP001

> **Status**: **CLOSED** ✓  
> **Experiment ID**: `STRAT_TO08_EXP001`  
> **Authorization**: Delegation-25AA  
> **Harness**: `scripts/run_strat_to08_exp001.py`

## Outcome

```text
KEEP
H_MECH · STRAT_TREND_OPP08_01@0.1.0 · rb/2024 · OPP08@1.0.0

closed = 1456
attributed = 1456
source_hash / parameter_hash: MATCH
PnL used as decision metric: NO
```

## Decision rule check

| Gate | Result |
|------|--------|
| Identity hashes | PASS |
| attributed ≥ 1 | PASS（1456） |
| rollover WARN missing hook | PASS（absent） |
| PnL primary | NO |

## Descriptive only

```text
engine_total_net_pnl: see run_metadata.json（not a KEEP rationale）
adjust_log_seen: False（no non-zero shift logged · hook present）
Note: high trade count is frequency, not Alpha
```

## Non-claims

```text
❌ Alpha / H_EDGE · Bindable · Production · Verified E2+
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | CLOSED · KEEP |
