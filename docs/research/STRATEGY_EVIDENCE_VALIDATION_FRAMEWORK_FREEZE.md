# Strategy Evidence and Validation Framework Freeze

> **Type**: Framework Freeze（≠ Asset Selection · ≠ Identity Freeze · ≠ Implementation · ≠ Backtest）  
> **Status**: **FROZEN** ✓  
> **Framework ID**: `SEVF-v1`  
> **Date**: 2026-07-22  
> **Authorization**: Three-round delegated decision — round 2  
> **Confirmed Design**: [`STRATEGY_EVIDENCE_VALIDATION_FRAMEWORK_DESIGN.md`](STRATEGY_EVIDENCE_VALIDATION_FRAMEWORK_DESIGN.md) v0.1  
> **Confirmation**: [`STRATEGY_EVIDENCE_VALIDATION_FRAMEWORK_CONFIRMATION.md`](STRATEGY_EVIDENCE_VALIDATION_FRAMEWORK_CONFIRMATION.md) — **PASS**  
> **Identity Contract**: [`STRATEGY_ASSET_CONTRACT_FREEZE.md`](STRATEGY_ASSET_CONTRACT_FREEZE.md) — `SAC-v1` **FROZEN**

## Freeze record

```text
================================================
STRATEGY EVIDENCE AND VALIDATION FRAMEWORK SEVF-v1

Framework: FROZEN ✓
Strategy assets selected: NONE
Strategy identities frozen: NONE
Implementation / Backtest / Observation: NONE
================================================
```

## 1. Purpose

`SEVF-v1` freezes how a `SAC-v1` asset produces evidence, is evaluated, and
is independently validated. It does not define strategy logic or an Alpha claim.

```text
Identity → Experiment → Artifact → Evaluation → Evidence → Validation
```

## 2. Mandatory experiment binding

Each experiment must bind a complete `SAC-v1` snapshot:

```text
strategy_id · version · source_revision
source_manifest · source_hash
parameter_manifest · parameter_hash
market_scope · execution_model
class_tags · architecture_attestation
```

```text
Any source_hash or parameter_hash change
  → new identity version
  → new experiment ID
  → never rewrites Closed evidence
```

## 3. Mandatory pre-registration and audit outputs

Every experiment records:

| Field | Frozen requirement |
|-------|--------------------|
| Primary hypothesis | One falsifiable sentence |
| Baseline | Explicit comparator or null expectation |
| Scope | Symbol/universe, session, period, data protocol |
| Execution | Costs, slippage, fill model and risk/execution assumptions |
| Variable | Exactly one primary changed variable |
| Metric / stop rule | Declared before execution |
| Fingerprint | Code and configuration identities |
| Outputs | CSV or equivalent auditable event/trade-level data |
| Evaluation | KEEP, HOLD or REVERT plus uncertainty statement |

No auditable output means **no evidence claim and no lifecycle promotion**.

## 4. Frozen outcome semantics

| Outcome | Frozen meaning |
|---------|----------------|
| `KEEP` | Supports retaining the stated hypothesis within its declared scope; eligible for independent validation |
| `HOLD` | Insufficient, conflicting, or scope-limited; no promotion |
| `REVERT` | Contradicts the primary hypothesis or a pre-registered gate; close/revert tested version |

```text
KEEP ≠ Alpha proven ≠ Bindable ≠ Production
HOLD / REVERT ≠ deletion of negative evidence
```

Metrics are selected in a Run Spec for the hypothesis under test. `SEVF-v1`
freezes no universal profit, Sharpe, PF, win-rate, or drawdown threshold.

## 5. Frozen lifecycle evidence requirements

| State | Frozen requirement |
|-------|--------------------|
| `Candidate` | May have no evidence; not Bindable |
| `Testing` | Pre-registered EXP + exact identity snapshot |
| `Verified` | Closed auditable experiment and Evidence Review supporting the stated hypothesis |
| `Bindable` | `SAC-v1` lineage, identity, architecture and Context-independence conditions all verified; separate identity-freeze approval required |
| `Deprecated` | Negative evidence supports retirement; archive remains immutable |

```text
Verified / Bindable
        ≠
production-ready
        ≠
trading edge established
```

Evidence maturity remains governed by the project E0 → E4 ladder. No state
auto-promotes another state or evidence level.

## 6. Frozen validation protocol

Validation is a new, independently registered experiment:

```text
same frozen identity
  + one validation dimension
  + new experiment ID
  + new artifact / evaluation / evidence
```

Allowed validation dimensions:

```text
temporal OOS · symbol/universe · cost sensitivity
reproducibility replay · declared market-scope robustness
```

Forbidden:

```text
❌ Re-run until a positive result appears
❌ Select parameters after results
❌ Mix detector, exit, filter and sizing changes in one experiment
❌ Change identity while retaining the old experiment lineage
❌ Use Context to rescue an asset-evidence hypothesis
```

## 7. Context and portfolio separation

```text
Strategy Asset Evidence
        ≠
Context Consumer Evidence
        ≠
Portfolio Evidence
```

A future Context Consumer experiment requires a new experiment ID and a frozen
independent StrategyIdentity. It cannot reopen `RC001_B_EXP001` and cannot
retroactively constitute strategy-asset evidence.

## 8. Modification rule

```text
SEVF-v1 is immutable.

Any outcome, lifecycle, validation, or artifact requirement change:
  → new Framework ID / version
  → new confirmation and freeze
  → existing Closed evidence remains unchanged
```

## 9. Explicit non-authorizations

```text
❌ Select strategy families or assets
❌ Freeze a StrategyIdentity
❌ Implement or modify strategy code
❌ Backtest / Observation
❌ Parameter / PnL optimization
❌ Portfolio construction
❌ RC001-B reopen
❌ Context Alpha / return / drawdown claim
```

## 10. Next delegated decision

```text
Round 3:
  Design Strategy Asset Family Inventory and Classification Protocol
```

The protocol may define inventory scope and classification tests; it must not
select a strategy, modify code, or initiate an experiment.

## Revision record

| Date | Change |
|------|--------|
| 2026-07-22 | `SEVF-v1` frozen under the three-round delegated decision |
