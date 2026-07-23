# SEVF Evaluation — STRAT_BS02_EXP012

> **Type**: Closed Evaluation  
> **Status**: **CLOSED** ✓  
> **Experiment ID**: `STRAT_BS02_EXP012`  
> **Date**: 2026-07-23  
> **Authorization**: Delegation-50M  
> **Fill**: [`STRATEGY_SEVF_FILL_CID_002_EXP012.md`](STRATEGY_SEVF_FILL_CID_002_EXP012.md)  
> **Artifacts**: `research/output/evidence/STRAT_BS02_EXP012/`

## Outcome

```text
Bundle outcome: KEEP
Hypothesis:     H_CAPITAL_GATE（temporal OOS · @0.2.0 · 2025）
Residual:       R-RISK-OOS CLOSED under pre-registered non-PnL rule
```

## Per-symbol

| Symbol | Outcome | closed | kill | end_balance | note |
|--------|---------|--------|------|-------------|------|
| rb | **KEEP** | 1053 | 0 | ≈168265 | no capital≤0 |
| i | **KEEP** | 415 | 1 | ≈82667 | kill engaged；halted |
| MA | **KEEP** | 1075 | 0 | ≈168766 | no capital≤0 |

```text
end_balance reported for audit only — NOT a KEEP/REVERT metric.
```

## Rule fidelity

```text
✓ Predeclared universe {rb,i,MA}
✓ Identity hash match @0.2.0
✓ Period 2025 OOS vs EXP008–010/2024
✓ capital≤0 sole REVERT gate（not PnL）
✓ H_MECH not re-evaluated
✓ EXP008 REVERT retained as negative prior
```

## Non-claims

```text
❌ Alpha · Bindable · Production · live
❌ H_MECH upgrade
❌ Profitability / E4
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | CLOSED · KEEP |
