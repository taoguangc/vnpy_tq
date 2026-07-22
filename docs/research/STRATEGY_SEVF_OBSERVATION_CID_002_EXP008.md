# STRAT_BS02_EXP008 — Observation note

> **Hypothesis**: `H_CAPITAL_GATE`（not H_MECH）  
> **Outcome**: **REVERT**  
> **Identity attempted**: pre-fix `@0.2.0` with cost-blind `equity_est`

## Fact

Under i · 2024 · capital=200_000 · risk-fraction defaults, engine `end_balance` hit ≤0 while strategy `equity_est` stayed ≈199850 and `kill_events=0`.

## Interpretation

```text
Price-only equity_est ignores CTA commission+slippage.
On i（size=100）friction alone can exhaust 20万 before kill fires.
→ capital gate failed；morphology not blamed.
```

## Follow-up

Cost-aware equity + friction-in-lot-gate shipped in same `@0.2.0` freeze bytes；re-observed as **EXP009 KEEP**.
