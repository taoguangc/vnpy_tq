# Bindable Pre-Review — CID_002（consumption interface only）

> **Type**: Bindable Pre-Review（≠ Bindable designation · ≠ Verified · ≠ Alpha · ≠ new Observation）  
> **Status**: **COMPLETE** ✓  
> **Review ID**: `BPR_CID_002_V0_1`  
> **Date**: 2026-07-22  
> **Authorization**: `Authorize Bindable Pre-Review`  
> **Parents**: `SAR_CID_002_V0_5` · `SIF_CID_002_V0_1` · `SIF_CID_002_V0_1_1` · `SIF_CID_002_V0_2_0`  
> **Contracts**: `SAC-v1` · `SEVF-v1` · `CEMB-v1` · `ADAP-v1`

## Review record

```text
================================================
BPR_CID_002_V0_1

Bindable designation:     WITHHELD
Verified designation:     WITHHELD
Alpha:                    NONE

Asset classification:     Testing Asset（dual-surface）
  • Mechanism surface:    @0.1.0 / @0.1.1
  • Risk-wrapper surface: @0.2.0

Bindable Candidate:       NO（gaps remain — see §6）
================================================
```

## 1. Scope（what this review answers）

```text
✓ Is identity complete enough to name a consumer contract?
✓ Are interfaces / dependencies transparent?
✓ How may this asset be consumed without polluting H_MECH?
✓ Is Bindable designation warranted now?

✗ Does NOT grant Bindable / Verified / Production
✗ Does NOT run backtests or expand KEEP counts
✗ Does NOT retune sizing for PnL
✗ Does NOT reopen RC001-B
```

## 2. Dual-surface identity（mandatory separation）

CID_002 is **one strategy_id** with **two non-substitutable consumption faces**:

| Surface | Identity | Answers | Does not answer |
|---------|----------|---------|-----------------|
| **Mechanism** | `STRAT_TREND_BROOKS_SCALP_02@0.1.0` / `@0.1.1` · `SIF_CID_002_V0_1` / `V0_1_1` | H_MECH auditability（entry/exit/detector attribution；multi-year/cost/multi-symbol） | Account survival under fixed_size=1 @200k |
| **Risk wrapper** | `STRAT_TREND_BROOKS_SCALP_02@0.2.0` · `SIF_CID_002_V0_2_0` | H_CAPITAL_GATE / capital survival controls | Morphology edge / Alpha |

```text
BROOKS_SCALP_FP@0.1.0          ← morphology（shared）
        |
        +-- @0.1.1             ← mechanism + rollover reference
        |
        +-- @0.2.0             ← positioning / risk wrapper only
```

**Hard rule for any consumer（Context, portfolio, report）:**

```text
Cite H_MECH only against @0.1.x hashes.
Cite capital survival only against @0.2.0 hashes.
Never treat EXP009 KEEP as H_MECH upgrade.
Never treat H_MECH KEEP as capital safety.
```

## 3. Identity completeness checklist（SAC-v1）

| Required field | @0.1.0 | @0.1.1 | @0.2.0 | Pre-Review note |
|----------------|--------|--------|--------|-----------------|
| `strategy_id` / `version` | ✓ | ✓ | ✓ | Same id；versions distinct |
| `source_manifest` / `source_hash` | ✓ | ✓ | ✓ | Content-addressed；git commit of binding bytes still pending |
| `parameter_manifest` / `parameter_hash` | ✓ full | ✓（mech params） | ✓ hash；manifest in freeze thinner | @0.2.0 should carry full typed manifest in freeze body（gap G1） |
| `market_scope` | `UNBOUND_AT_ASSET` | same | same | CEMB-ok for Testing；Bindable consumer still needs EXP-declared scope（gap G2） |
| `execution_model` | ✓（fixed_size） | inherited | sizing_rule_class changed | @0.2.0 freeze must restate execution_model（gap G3） |
| `evidence_lineage` | ✓ mech EXPs | ✓ | ✓ capital EXPs | Surfaces must not be mixed in citations |
| `class_tags` | trend | trend | trend+positioning | OK |
| `context_independence` | attested true | inherits | inherits | Detector `del context`；ContextEngine orchestration-only |
| `not_fabricated_for_context` | true | inherits | inherits | OK |
| `architecture_attestation` | §5 in V0_1 | partial | missing in V0_2_0 doc | Restate for @0.2.0（gap G4） |

**Identity verdict:** sufficient for **Testing Asset** citation；**not** sufficient for Bindable lock without G1–G4 closure + separate Bindable identity approval.

## 4. Interface map（consumer-facing）

### 4.1 Morphology interface

```text
Detector:  BROOKS_SCALP_FP@0.1.0
Input:     ArrayManager window + Context object（ignored in v0.1）
Output:    DetectionResult | None · explicit PatternState FSM
Guarantee: no orders · no position · no Strategy mutation
```

### 4.2 Orchestration interface

```text
Strategy:  BrooksScalpPaafStrategy（@0.1.0）
           → V011 on_rollover_adjust
           → V020 sizing + kill-switch
Path:      ContextEngine.update → detector.detect → stop entry → 1m exits → trade_log
Deviation: Detector constructed directly（no Registry catalog wiring）— declared since SIF V0_1
```

### 4.3 Risk / capital interface（@0.2.0 only）

```text
sizing_mode ∈ {RISK_FRACTION_OF_CAPITAL, FIXED_LOTS}
risk_per_trade · hard_max_lots · capital_floor_ratio
equity_est = capital + Σprice_pnl − Σ(commission+slippage)
equity ≤ floor → flatten + halt entries
EXP metadata must echo: capital_assumption · sizing_mode · kill_events
```

### 4.4 Future Context consumer role（Decision 019 / SAC §4）

```text
ALLOWED later（new experiment_id only）:
  Filter · Risk Modifier · Monitoring · Permission

FORBIDDEN inside this asset’s signal path:
  Context → entry generation
  Context score → sizing alpha
  Hidden regime gate duplicating unpublished Context
```

Current attestation: **independent signal path**（detector ignores Context）. ContextEngine remains orchestration scaffolding, not edge.

## 5. Dependency transparency

| Dependency | Binding | Consumer note |
|------------|---------|---------------|
| Data | `docs/07_DATA_SPEC.md` · TQ offline · 1m · CbC · unadjusted · real costs | EXP must restate |
| Fill | `VNPY_CTA_BACKTEST_ENGINE_DEFAULTS_AT_EXP_REGISTRATION` | not silent |
| Cost numbers | resolved at EXP registration（CEMB） | not invented in identity |
| Rollover harness | `RolloverBacktestingEngine` + `on_rollover_adjust`（@0.1.1+） | required for CbC continuity claims |
| Parent mechanism | `@0.1.1` immutable | @0.2.0 must not mutate parent bytes |
| Evidence store | `research/output/evidence/STRAT_BS02_EXP*` | append-only；Closed EXPs immutable |

## 6. Gaps blocking Bindable（and Verified）

| ID | Gap | Why it blocks |
|----|-----|----------------|
| **G0** | No formal **Verified** designation | SEVF/SAC: Bindable sits after Verified-class evidence package acceptance；H_MECH KEEP ≠ Verified stamp |
| **G1** | `@0.2.0` freeze thinner than SAC full record | Full `parameter_manifest` + attestations should live in freeze body / machine JSON |
| **G2** | `market_scope = UNBOUND_AT_ASSET` | Acceptable for Testing；Bindable consumer contract needs an explicit bound profile or standing “EXP-declares-scope” consumer rule with acceptance |
| **G3** | `@0.2.0` `execution_model` not restated | sizing_rule_class changed；consumers must not inherit fixed_size semantics from @0.1.x |
| **G4** | `@0.2.0` architecture attestation not restated | Risk-wrapper deviations（equity_est approximation vs engine balance）must be explicit |
| **G5** | Binding sources still content-addressed / uncommitted | SAC prefers immutable repo revision；content-hash OK for Testing；Bindable wants commit lock when bytes stable |
| **G6** | Capital evidence single-symbol smoke | EXP009 KEEP on `i` ≠ multi-symbol capital contract；PARTIAL capital safety |
| **G7** | Dual-surface citation risk | Without a published Consumer Contract, reports will merge layers |

```text
Closing G1–G7 may create a Bindable Candidate path.
This Pre-Review does NOT close them and does NOT grant Bindable.
```

## 7. Asset classification（outcome）

```text
Primary class:     Testing Asset
Sub-roles:
  • Research Mechanism Asset     → consume @0.1.1 for H_MECH citations
  • Capital-gated Research Consumer Candidate
                                 → consume @0.2.0 for survival / sizing tests
  • Strategy Component（future）  → only after G0–G7 + separate auth
  • Production Candidate         → NOT OPEN

Rejected class now:
  • Bindable Strategy Asset
  • Verified Trading Asset
  • Portfolio Component
```

### Consumer Contract（draft — binding for this Pre-Review）

```text
CC-CID_002-v0.1

1. Name the surface（@0.1.1 or @0.2.0）before any claim.
2. H_MECH claims require matching source_hash/parameter_hash of @0.1.x.
3. Capital claims require SIF_CID_002_V0_2_0 + EXP008/009 lineage.
4. Context may only attach as Filter / Risk Modifier / Monitoring / Permission
   under a new experiment_id — never as entry alpha inside this asset.
5. UNBOUND_AT_ASSET forbids implying a production universe.
6. KEEP ≠ Alpha ≠ Bindable ≠ permission to live-trade.
7. Negative evidence（EXP008 REVERT, H_NULL REVERT）remains first-class.
```

## 8. Decisions of this review

```text
1. Bindable Pre-Review COMPLETE.
2. Bindable designation WITHHELD.
3. Classification = Testing Asset（dual-surface）with published Consumer Contract draft.
4. Natural next gates（须另授）are gap-closure / Verified review / Pause —
   not “more KEEP collection”.
```

## 9. Next（须另授）

```text
V. Authorize Verified Review for Mechanism Surface @0.1.1
   （formal lifecycle stamp；still ≠ Bindable）

G. Authorize Bindable Gap-Closure Charter
   （G1–G7 docs/identity only · no PnL search）

C. Pause Epoch 5

P. Authorize Context Consumer Experiment Design
   （only after a Bindable asset exists — currently blocked）
```

## Hard guarantees

```text
✓ No Bindable / Verified / Alpha granted
✓ No code / parameter / backtest under this authorization
✓ Mechanism and capital layers kept separate
✓ CAP-CTX-001 CLOSED · RC001-B not reopened
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-22 | BPR_CID_002_V0_1 COMPLETE · Testing Asset · Bindable WITHHELD |
