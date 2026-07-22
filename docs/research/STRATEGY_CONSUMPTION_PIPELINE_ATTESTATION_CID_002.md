# Consumption Pipeline Attestation — CID_002（P0）

> **Type**: Architecture / Interface Attestation  
> **Status**: **ATTESTED** ✓  
> **Attestation ID**: `CPA_CID_002_V0_1`  
> **Date**: 2026-07-22  
> **Authorization**: Delegation-50D · `BGC-CID_002-v1`  
> **Surfaces**: MECH `@0.1.1` · RISK `@0.2.0`

## Pipeline（canonical）

```text
Input Contract（bars / ArrayManager · docs/07 · EXP-declared scope）
    ↓
Detector State（BROOKS_SCALP_FP@0.1.0 PatternState FSM）
    ↓
Signal Intent（DetectionResult | None · Context ignored in detect）
    ↓
Order Proposal（stop entry · structural stop/target from detector）
    ↓
Risk Wrapper（@0.2.0 only: lots · skip_zero · kill-switch · else @0.1.x fixed_size）
    ↓
Execution（vn.py CTA backtest fills · CEMB cost/fill bindings）
    ↓
Logger / Evidence（trade_log · EXP artifacts）
```

## Stage contracts

| Stage | Producer | Consumer may rely on | Must not assume |
|-------|----------|----------------------|-----------------|
| Input | EXP harness + docs/07 | 1m CbC unadjusted bars | invent universe |
| Detector State | `BrooksScalpFirstPullbackDetector` | pure FSM / Signal|None | orders / equity |
| Signal Intent | detector | entry/stop/target/reason | Context edge |
| Order Proposal | strategy orchestrator | stop order intent | fill certainty |
| Risk Wrapper | `@0.2.0` | sizing + halt semantics | mechanism Alpha |
| Execution | engine | registered fill/cost model | live brokerage identity |
| Logger | strategy `_trade_log` | audit fields | completeness of engine balance |

## Declared deviations

```text
• Detector constructed directly（no Registry catalog wiring）— since SIF V0_1
• ContextEngine.update called for orchestration；detect() discards Context
• @0.2.0 equity_est approximates engine balance（rate+slippage+price pnl）；
  may diverge from engine end_balance pathologically — kill uses equity_est
• CtaTemplate remains the execution host（PAAF orchestration inside）
```

## Binding

```text
This attestation documents callability.
It does NOT grant Bindable / Production / Alpha.
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-22 | CPA_CID_002_V0_1 attested |
