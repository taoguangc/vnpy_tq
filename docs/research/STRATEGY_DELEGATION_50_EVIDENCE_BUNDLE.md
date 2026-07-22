# Evidence Bundle — Delegation-50（EXP002–EXP004）

> **Type**: Closed Evidence Bundle + Asset Ledger Update  
> **Status**: **COMPLETE** ✓  
> **Date**: 2026-07-22  
> **Authorization**: `授权50轮由你来决定`  
> **Log**: [`STRATEGY_DELEGATION_50_EXECUTION_LOG.md`](STRATEGY_DELEGATION_50_EXECUTION_LOG.md)

## Outcomes

| EXP | Family | Scope | Outcome | Meaning |
|-----|--------|-------|---------|---------|
| `STRAT_BS02_EXP001` | H_MECH | rb/2024 | **KEEP** | Mechanism auditable（prior） |
| `STRAT_BS02_EXP002` | H_NULL | rb/2024 | **REVERT** | mean net_pnl distinguishable from 0（mean≈−26.2，p≪0.05） |
| `STRAT_BS02_EXP003` | H_ROBUST | rb/2025 | **HOLD** | audit join incomplete（exit_reason UNKNOWN） |
| `STRAT_BS02_EXP004` | H_ROBUST | rb/2025 | **KEEP** | Mechanism auditable on temporal OOS（trade_log audit） |

## Claim ledger

```text
H_MECH（rb/2024）:     RETAINED
H_MECH（rb/2025 OOS）: RETAINED via EXP004（EXP003 HOLD retained as negative audit lesson）
H_NULL（rb/2024）:     REJECTED（REVERT）— expectancy ≠ 0；direction is negative
H_ALPHA:               NOT CLAIMED（and not supported）
Verified / Bindable:   NOT GRANTED
```

```text
REVERT(H_NULL) because mean < 0 and significant
        ≠
Alpha proven
        ≠
delete H_MECH
```

## Evidence Review（bundle）

| Check | Result |
|-------|--------|
| Identity hashes on all runs | PASS |
| Pre-registered rules applied | PASS |
| EXP001 immutable | PASS |
| Negative evidence retained（EXP002 REVERT · EXP003 HOLD） | PASS |
| No parameter search | PASS |
| PnL not used as Alpha gate | PASS |

**Bundle Evidence Review: PASS**（completeness + rule fidelity）.

## Asset Review update（`SAR_CID_002_V0_2`）

```text
Lifecycle: Testing
Mechanism Evidence: Retained（IS + temporal OOS）
Null / no-edge claim: Rejected under rb/2024
Alpha: NONE
Verified: NO
Bindable: NO
```

```text
Identity Freeze
  → Testing
  → H_MECH retained（2024 + 2025）
  → H_NULL rejected（2024 · negative expectancy）
  → STOP
```

Open gates unchanged for Bindable:

```text
• on_rollover_adjust engineering（new identity version if bytes change）
• cost-sensitivity EXP
• multi-symbol scope（non-PnL policy）
• Bindable designation（explicit user auth）
```

## Artifacts

```text
research/output/evidence/STRAT_BS02_EXP002/
research/output/evidence/STRAT_BS02_EXP003/
research/output/evidence/STRAT_BS02_EXP004/
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-22 | Delegation-50 bundle closed · STOP with reserved rounds |
