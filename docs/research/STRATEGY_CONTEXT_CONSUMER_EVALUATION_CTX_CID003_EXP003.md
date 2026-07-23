# Context Consumer Evaluation — CTX_CID003_EXP003

> **Status**: **CLOSED** ✓  
> **Experiment ID**: `CTX_CID003_EXP003`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-50G  
> **Harness**: `scripts/run_ctx_cid003_exp003.py`

## Outcome

```text
KEEP
H_CTX_FILTER multi-symbol continuity · MECH @0.1.1 · {rb,i,MA}/2024 · F1

Aggregate: all_symbols_KEEP
source_hash / parameter_hash: MATCH
PnL used as decision metric: NO
```

## Decision rule check

| Gate | Result |
|------|--------|
| Identity hashes | PASS |
| rb / i / MA each non-inert | PASS |
| Aggregate all KEEP | PASS |
| Context entries / sizing | NO |
| PnL primary | NO |

## Descriptive only（not decision）

| Symbol | B0 pnl | B1 pnl |
|--------|--------|--------|
| rb | −37703 | −21669 |
| i | 0* | −195770 |
| MA | −46831 | −27429 |

\*i B0 engine pnl reported `0` under MECH capital stress path — descriptive artifact；not a filter inert finding（N0=2060 · filter active）.

## Non-claims

```text
❌ Context Alpha · Production
❌ Capital safety from filter KEEP
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | CLOSED · KEEP |
