# Strategy Evidence and Validation Framework — Design

> **Type**: Framework Design（≠ Framework Freeze · ≠ Asset Selection · ≠ Implementation · ≠ Backtest）  
> **Status**: **CONFIRMED** ✓ · authority frozen as `SEVF-v1`  
> **Version**: 0.1  
> **Date**: 2026-07-22  
> **Authorization**: Delegated decision following `SAC-v1` Contract Freeze  
> **Contract**: [`STRATEGY_ASSET_CONTRACT_FREEZE.md`](STRATEGY_ASSET_CONTRACT_FREEZE.md) — `SAC-v1` **FROZEN**  
> **Phase**: [`STRATEGY_RESEARCH_PHASE_AUTHORIZATION.md`](STRATEGY_RESEARCH_PHASE_AUTHORIZATION.md) — Epoch 5 **ACTIVE**

## Design record

```text
================================================
STRATEGY EVIDENCE AND VALIDATION FRAMEWORK v0.1

Status: CONFIRMED ✓
Confirmation: PASS
Framework Freeze: SEVF-v1 FROZEN（subsequent delegated decision）
Candidate asset selection: NONE
Strategy implementation: NONE
Backtest / Observation: NONE
================================================
```

## 1. Purpose

Define how a `SAC-v1` strategy asset accumulates auditable evidence, receives
an evaluation outcome, and may progress through its asset lifecycle.

```text
StrategyIdentity
  → pre-registered experiment
  → immutable artifact
  → evaluation
  → evidence record
  → validation
  → lifecycle decision
```

The framework answers:

> 在不追逐收益、不选择事后最佳参数的前提下，策略资产如何被保留、否证或暂停？

It does **not** answer whether a particular Trend, Mean-reversion, or
Volatility strategy should be selected.

## 2. Frozen-input alignment

Every eventual experiment under this framework must bind a `SAC-v1`
StrategyIdentity snapshot:

```text
strategy_id · version · source_revision
source_manifest · source_hash
parameter_manifest · parameter_hash
market_scope · execution_model
class_tags · architecture_attestation
```

```text
Changing source_hash or parameter_hash
        =
new identity version / new experiment
        ≠
overwrite a Closed result
```

## 3. Evidence unit（per experiment）

Each experiment must pre-register exactly one primary hypothesis and include:

| Element | Required design content |
|---------|-------------------------|
| Identity binding | Full `SAC-v1` snapshot and hashes |
| Research question / hypothesis | Falsifiable one-sentence primary hypothesis |
| Baseline | Explicit comparator or null expectation |
| Market / period | Predeclared symbols, session and time window |
| Data / execution | Frozen data protocol, costs and fill model |
| Single variable | One primary changed variable only |
| Metric / stop rule | Predeclared in the Run Spec, not selected afterward |
| Audit outputs | CSV or equivalent event / trade-level output plus configuration fingerprint |
| Evaluation | KEEP / HOLD / REVERT with stated uncertainty |

This carries forward `docs/06_RESEARCH_WORKFLOW.md`: no CSV or equivalent
auditable output means no evidence claim or lifecycle promotion.

## 4. Evidence outcomes（draft semantics）

| Outcome | Meaning | Lifecycle consequence |
|---------|---------|-----------------------|
| **KEEP** | Result supports retaining the tested hypothesis under its declared scope | Eligible for independent validation; not production |
| **HOLD** | Insufficient, conflicting, or scope-limited result | No promotion; retain artifact and state uncertainty |
| **REVERT** | Result contradicts the primary hypothesis or fails a predeclared gate | Close/revert the tested version; retain negative evidence |

```text
KEEP ≠ Alpha proven ≠ Bindable ≠ Production
HOLD / REVERT ≠ delete history
```

No return, Sharpe, PF, win-rate, or drawdown threshold is frozen at framework
level. Such metrics and thresholds belong to a single pre-registered experiment,
where their relevance to the stated hypothesis can be audited.

## 5. Lifecycle decision matrix（draft）

| Asset state | Preconditions |
|-------------|---------------|
| **Candidate** | `SAC-v1` record draft; no evidence claim |
| **Testing** | Identity snapshot + pre-registered EXP; code / parameter changes create a new identity |
| **Verified** | At least one Closed experiment with auditable output, Evidence Review that supports the stated hypothesis, and no unresolved identity mismatch |
| **Bindable** | `SAC-v1` evidence-lineage requirements met; architecture and Context-independence attested; identity freeze approved separately |
| **Deprecated** | Predeclared or independently replicated negative evidence supports retirement; history remains immutable |

`Verified` means “the evidence package is complete for the defined scope”; it
does not mean positive trading edge, multi-market generalization, or production
readiness.

## 6. Validation rules（draft）

Validation uses a **new** experiment ID and consumes prior evidence read-only:

```text
New experiment
  → binds the same frozen identity
  → varies only the registered validation dimension
  → produces new artifacts / evaluation / evidence
```

Permitted validation dimensions, one per experiment:

```text
• temporal OOS
• symbol / universe
• execution-cost sensitivity
• reproducibility replay
• declared market-scope robustness
```

Forbidden:

```text
❌ Re-run until a positive outcome appears
❌ Select parameters after viewing results
❌ Mix new detector, exit, filter and sizing changes in one experiment
❌ Rewrite source or parameters while claiming the same identity
❌ Use Context to rescue a strategy-asset hypothesis
```

## 7. Context and portfolio boundary

Strategy Asset Evidence is independent of Context-consumption evidence:

```text
Strategy Asset Experiment
        ≠
Context Consumer Experiment
        ≠
Portfolio Construction
```

Any future Context Consumer experiment:

```text
• uses a new experiment ID;
• binds an already frozen independent StrategyIdentity;
• treats Context only as Filter / Risk Modifier / Monitoring / Permission;
• does not reopen RC001-B;
• does not demonstrate strategy-asset evidence retroactively.
```

## 8. Explicit non-goals

```text
❌ Select a strategy family or code path
❌ Authorize new strategy implementation
❌ Run backtests / observations
❌ Freeze an individual asset identity
❌ Optimize PnL or define a universal profit threshold
❌ Claim Context improves returns, risk, or selection
❌ Build a portfolio
```

## 9. Confirmation result

Framework Design v0.1 was confirmed and subsequently frozen as
[`SEVF-v1`](STRATEGY_EVIDENCE_VALIDATION_FRAMEWORK_FREEZE.md).

```text
Confirmation PASS
        ≠
Framework Freeze
        ≠
Asset selection / implementation / backtest
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-22 | Framework Design v0.1 created under delegated decision; no strategy asset selected |
| 2026-07-22 | Confirmation **PASS**; Framework Freeze remains separate |
| 2026-07-22 | Framework frozen as [`SEVF-v1`](STRATEGY_EVIDENCE_VALIDATION_FRAMEWORK_FREEZE.md) |
