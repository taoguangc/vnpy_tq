# SEVF Fill / Pre-registration — CID_002 EXP001

> **Type**: Experiment Fill + Pre-registration（≠ Authorization · ≠ Observation · ≠ Backtest · ≠ Evidence）  
> **Status**: **PRE-REGISTERED** ✓  
> **Experiment ID**: `STRAT_BS02_EXP001`  
> **Spec**: [`SEVF_SPEC_CID_002_V0_1`](STRATEGY_SEVF_SPECIFICATION_CID_002.md)  
> **Identity**: [`SIF_CID_002_V0_1`](STRATEGY_IDENTITY_FREEZE_CID_002.md)  
> **Date**: 2026-07-22  
> **Authorization**: User option **1** — `Authorize SEVF Fill / Pre-registration for CID_002`  
> **Machine record**: `research/output/evidence/STRATEGY_SEVF_FILL_CID_002_EXP001/pre_registration.json`

## Record

```text
================================================
STRAT_BS02_EXP001 — PRE-REGISTERED ✓ · OBSERVATION CLOSED

Hypothesis family: H_MECH
Observation:        EXECUTED 2026-07-22
Evaluation:         CLOSED → KEEP（see STRATEGY_SEVF_EVALUATION_CID_002_EXP001.md）
Evidence:           mechanism audit package present
================================================
```

## 1. Identity binding（must match freeze）

| Field | Pre-registered value |
|-------|----------------------|
| `strategy_id` | `STRAT_TREND_BROOKS_SCALP_02` |
| `version` | `0.1.0` |
| `freeze_id` | `SIF_CID_002_V0_1` |
| `source_hash` | `3ba12893e43db6805e5af2012d811a7f0034143dbedb102637afd7a5819b9589` |
| `parameter_hash` | `3ff061891488a9d9f5641cf147efc1e70c8d4cb8410540858d8b727bd485d1ab` |
| `source_revision` | `CONTENT_ADDRESSED:3ba12893e43db6805e5af2012d811a7f0034143dbedb102637afd7a5819b9589` |
| `git_anchor_head` | `878bce01e610226972dcabf05342cc196e22f6e1` |
| `detector_binding` | `BROOKS_SCALP_FP@0.1.0` |
| `class_tags` | `["trend"]` |
| `strategy_class` | `strategies.paaf.brooks_scalp_paaf_strategy.BrooksScalpPaafStrategy` |

At run time: recompute `source_hash` / `parameter_hash`; mismatch → **abort**（do not evaluate）.

## 2. Primary hypothesis（one）

**Family**: `H_MECH`

**Primary hypothesis（falsifiable）**:

> Under the declared market scope and frozen data/cost/fill bindings, `STRAT_TREND_BROOKS_SCALP_02@0.1.0` produces at least one closed round-trip whose audit record attributes signal→entry→exit（with stop/target/time-stop fields）to `BROOKS_SCALP_FP@0.1.0`, and the run artifact echoes the frozen `source_hash` and `parameter_hash`.

**Baseline / null expectation**:

```text
Null for this EXP = “no auditable closed round-trip attributable to the frozen detector”
（not a profitability null）
```

**Not claimed**:

```text
❌ expectancy > 0
❌ Alpha / Brooks correctness
❌ Bindable / Verified
❌ Context trading value
```

## 3. Single variable

```text
VARIABLE_0:
  Execute first Observation under frozen identity
  + newly declared market_scope package below

Baseline comparator:
  Absence of auditable closed round-trips under the same scope
```

No detector, exit, sizing, filter, or Context-gate changes in this EXP.

## 4. Market scope package（CEMB fill）

| Field | Declared value | Selection rationale（non-PnL） |
|-------|----------------|------------------------------|
| `symbols` | `["rb"]` | Project default research primary（scripts / CAP-CTX / OPP16 event harness continuity）；**not** chosen by historical return |
| `universe_policy` | `SINGLE_SYMBOL_FIRST_SCOPE` | First Testing scope only；multi-symbol needs a new EXP |
| `session` | `ALL_SESSIONS_IN_1M_STREAM` | Use full TQ 1m continuous stream as loaded（day+night as present） |
| `period_start` | `2024-01-01`（Asia/Shanghai calendar date） | Bounded first IS calendar year |
| `period_end` | `2024-12-31`（Asia/Shanghai calendar date） | Same |
| `warmup_start` | `2023-12-01` | Indicator/FSM warmup；evaluation window excludes warmup-only trades if engine tags allow；else document |
| `sample_role` | `IN_SAMPLE_MECHANISM` | Not OOS； not validation |
| `data_protocol_version` | `docs/07_DATA_SPEC.md` **v1.0.0** | TQ offline · 1m · CbC · unadjusted · real costs |

```text
Symbol/period choice is a scope declaration for auditability.
It is NOT a performance ranking result.
Changing symbols/period after seeing results → FORBIDDEN（new EXP required）
```

## 5. Execution / cost / fill

| Binding | Value |
|---------|--------|
| `cost_binding` | `PROJECT_FROZEN_DATA_PROTOCOL` |
| `data_spec` | `docs/07_DATA_SPEC.md` v1.0.0 |
| `fill_binding` | `VNPY_CTA_BACKTEST_ENGINE_DEFAULTS_AT_EXP_REGISTRATION` |
| Fee/slippage numbers | From project `rb` cost tables / harness at run registration — not invented here |
| Signal TF | 1m |
| Order style | Stop entry；structural stop + `risk_reward` target；`max_hold_bars` time stop |
| Sizing | `fixed_size=1`（frozen parameter_manifest） |
| Zero-cost / adjusted price | **Forbidden** for this EXP ID |

## 6. Metrics

### Mandatory（audit）

```text
• closed_trade_count
• exit_reason_counts（STOP / TARGET / TIME_STOP / other）
• identity echo: strategy_id, version, source_hash, parameter_hash, experiment_id
• binding echo: cost_binding, fill_binding, data_protocol_version, symbols, period
• artifact paths（CSV or equivalent trade/event-level）
```

### Optional（reported, not KEEP drivers）

```text
net_pnl · expectancy · win_rate · PF · Sharpe · max_drawdown · MFE/MAE summaries
（may be printed for transparency; MUST NOT redefine KEEP/HOLD/REVERT after the fact）
```

## 7. Pre-registered decision rule

| Outcome | Rule |
|---------|------|
| **KEEP** | Run completes with auditable CSV/equivalent **and** `closed_trade_count ≥ 1` **and** each kept trade has attributable `detector_binding=BROOKS_SCALP_FP@0.1.0`（or equivalent detector id/version fields）**and** artifact identity hashes match §1 **and** at least one exit_reason ∈ {STOP, TARGET, TIME_STOP} |
| **HOLD** | Run completes with valid identity echo **but** `closed_trade_count = 0` **or** audit fields incomplete for all trades **or** sample/engine limitation documented without identity breach |
| **REVERT** | Identity hash mismatch vs freeze **or** trades/orders without detector attribution **or** run fails to produce required audit artifact after authorized execution **or** silent use of non-baseline data/cost mode |

Uncertainty statement required in evaluation regardless of outcome.

```text
KEEP under H_MECH ≠ Alpha ≠ Bindable ≠ permission for H_NULL without new EXP
```

## 8. Required outputs

```text
• trade/event-level CSV（or equivalent）under research/output/evidence/STRAT_BS02_EXP001/
• run metadata JSON echoing §1 and §4–§5
• evaluation note with KEEP|HOLD|REVERT + uncertainty
```

No auditable output → no evidence claim（`SEVF-v1`）.

## 9. Explicit non-authorizations

```text
✓ Fill / Pre-registration complete for STRAT_BS02_EXP001
❌ SEVF Authorization to execute Observation/Backtest
❌ Parameter changes
❌ Symbol/period shopping after results
❌ Context Consumer / RC001-B / Portfolio
❌ Lifecycle promotion beyond Testing start without evaluation
```

## 10. Next gate

```text
Observation AUTHORIZED and CLOSED → KEEP（H_MECH）
See: STRATEGY_SEVF_EVALUATION_CID_002_EXP001.md
```

Further steps require new authorization（H_NULL / OOS / Asset Review / Pause）.

## Revision record

| Date | Change |
|------|--------|
| 2026-07-22 | `STRAT_BS02_EXP001` pre-registered under `SEVF_SPEC_CID_002_V0_1` · H_MECH · rb · 2024 |
| 2026-07-22 | Observation authorized · executed · Closed KEEP |
