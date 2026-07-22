# RC001-A — Context Filter Design

> **Type**: Controlled Experiment Design（Phase A · Context as Filter only）  
> **Status**: **Design COMPLETE** ✓ — Contract Review **PASS** ✓ — awaiting Controlled Experiment Spec
> **Version**: 0.1  
> **Date**: 2026-07-21  
> **Path**: `docs/research/RC001_A_CONTEXT_FILTER_DESIGN.md`  
> **Authorization**: [`RC001_A_DESIGN_AUTHORIZATION.md`](RC001_A_DESIGN_AUTHORIZATION.md) — **GRANTED**  
> **Candidate**: [`CAPABILITY_CANDIDATE_DESIGNATION_REVIEW.md`](CAPABILITY_CANDIDATE_DESIGNATION_REVIEW.md) — **NARROW**  
> **ADR**: Decision 019  
> **A1**: [`CAP_CTX_A1_RUN001_EVIDENCE_REVIEW.md`](CAP_CTX_A1_RUN001_EVIDENCE_REVIEW.md) — PASS  
> **Prior Campaign Plan**: [`RC001_RESEARCH_PLAN.md`](../campaigns/RC001_RESEARCH_PLAN.md) v0.2 — **Not Accepted**；本 Design **不**自动 Accepted 旧 Plan  
> **Gate**: CONDITIONAL v3.0 · **≠** Gate PASS

### Design Record（binding）

```text
================================================
RC001-A CONTEXT FILTER DESIGN v0.1

Status: Design COMPLETE ✓

Object: Context Infrastructure → Filter / Permission Layer
Capability: NARROW Candidate only
Context input: ContextState.v1（A1）— compression | expansion | invalid

NOT: Strategy Development / Alpha Mining / Param Opt / Backtest

Next: Contract Review → **PASS** · next = Controlled Experiment Spec（另授）→ Execution Auth → Backtest
================================================
```

---

## 1. Research Question（RC001-A）

### RQ-RC001-A

> 一个**已有、外部**策略信号，在接入 Context Infrastructure（Filter）后，策略**选择质量**是否相对无 Context 基线发生可审计改善？

### Not the question

```text
❌ Context 能不能赚钱
❌ Context 是否 Alpha
❌ 哪组参数年化最高
❌ Context 是否应直接下单
```

### Structural diagram（frozen）

```text
Baseline Strategy（external · Context-off）
        ↓
Performance Reference

Same Strategy（identical signals · Context-on Filter）
        ↓
Controlled Comparison
```

```text
Strategy Alpha（external）
       +
Context Infrastructure（A1 ContextState）
       ↓
Execution Permission（allow / block / reduce）
```

---

## 2. Three Binding Principles

### P1 — Strategy must be external

```text
Context does not create the strategy.
Context only gates pre-existing strategy_signal.
```

**Forbidden**

```python
if context_state == "compression":
    enter_long()
```

**Required pattern**

```python
if strategy_signal:
    if context.allow:   # Filter / Permission Layer
        execute()
```

### P2 — Phase A tests Filter only

| Allowed | Forbidden |
|---------|-----------|
| block low-quality environment | change entry rule |
| reduce exposure（pre-registered multiplier only） | change exit rule |
| monitoring / attribution flag | change parameters |
| allow/block on existing signals | change bar period |
| | change symbol universe |

```text
Filter ≠ Entry redesign
Filter ≠ Exit redesign
Filter ≠ Param search
```

### P3 — Evaluation is not return-centric

| Metric | Role | Notes |
|--------|------|-------|
| Trade count change | **Core** | 是否过度过滤 |
| Stability / dispersion of outcomes | **Core** | 选择质量稳定性 |
| Drawdown impact | **Primary risk** | 风险是否改善 |
| Sharpe change | Auxiliary | 非优化目标 |
| Return change | Auxiliary | 非优化目标；禁止作 sole success |

**Forbidden objective**

```text
找到最高收益参数 / maximize annual return
```

---

## 3. Context Input Contract（A1 · Decision 019）

### Published State consumed

```text
schema: ContextState.v1
context_version: A1-CTX-PS-v1.0.0
primary tag: compression | expansion | invalid
validity: VALID | DEGRADED | INVALID
confidence: computational only（≠ win probability）
```

### Filter interface（design freeze）

```text
ContextFilter.decide(strategy_signal, context_state) → Permission

Permission ∈ {
  ALLOW,          # pass-through
  BLOCK,          # no new entry（exit rules unchanged）
  REDUCE,         # size *= pre-registered factor only（if used）
  MONITOR_ONLY    # no trade effect；attribution flag
}
```

### Default Filter Policy（v0.1 proposal · Contract Review 可修订，不可扩成 signal）

| context_state / validity | Proposed Permission |
|--------------------------|---------------------|
| `invalid` OR validity=`INVALID` | **BLOCK** |
| validity=`DEGRADED` | **BLOCK** or **REDUCE**（二选一，Spec 冻结） |
| `compression` + VALID | **ALLOW** or **REDUCE**（Spec 冻结单路径） |
| `expansion` + VALID | **ALLOW** |

> 具体 ALLOW/REDUCE 映射在 **Controlled Experiment Spec** 冻结一条路径；**禁止**多路径网格搜索。

### Hard exclusions on Filter

```text
❌ permission → invent direction
❌ confidence → position size alpha curve-fit
❌ descriptive_state → expected_return
❌ MarketState TREND/RANGE silent swap for A1 tags（Decision 002 / 019）
```

---

## 4. Baseline Strategy Definition

### Requirement

```text
Baseline = external, pre-existing strategy signal source
        ≠ newly designed Context-era Alpha
```

### Design-time baseline candidate（pending Contract Review lock）

| Field | Value |
|-------|-------|
| Candidate ID | **OPP16**（两棒反转） |
| Lineage parent | `OPP16_EXP001`（Closed · Decision 017 immutable） |
| Relation to old RC001 Plan | Same Opportunity lineage；**new** experiment_id under RC001-A |
| Context-off arm | OPP16 signals · no ContextFilter |
| Context-on arm | **Identical** OPP16 signals · ContextFilter only |

### Lock rules

```text
✓ Same symbol / window / cost / data protocol on both arms
✓ Same OPP16 parameters on both arms（no retune）
❌ No new detector / no entry-exit redesign in RC001-A
❌ No multi-strategy horse race in Phase A
```

Contract Review may reject OPP16 and nominate another **external** Closed baseline — must remain external + frozen params.

---

## 5. Controlled Comparison Design

### Arms（exactly two in Phase A）

| Arm | ID | Treatment |
|-----|-----|-----------|
| Control | RC001-A-CTRL | Context-off · baseline signals only |
| Treatment | RC001-A-FILT | Context-on · same signals + ContextFilter |

### Identity constraints

```text
same strategy_signal stream
same data (TQ offline / 1m / CbC / unadjusted / real cost)
same universe & window（Spec 冻结）
differ ONLY by ContextFilter permission application
```

### Success / failure framing（non-PnL）

| Outcome class | Meaning |
|---------------|---------|
| FILTER_HELPFUL | Trade count ↓ without catastrophic under-sample；DD/stability improve or hold；aux metrics not sole driver |
| FILTER_HARMFUL | Over-filter（trade count collapse）或风险/稳定性明显恶化 |
| FILTER_INCONCLUSIVE | 无稳定分离 / 样本不足 |
| CONTRACT_INVALID | Filter violated P1–P3 / Decision 019 |

Numeric thresholds → **Controlled Experiment Spec**（not this Design）。

---

## 6. Evaluation Metric Freeze（Campaign Design layer）

### Primary（must report）

1. **Trade count**（absolute + % vs control）  
2. **Stability**（预注册：e.g. rolling expectancy dispersion / hit-rate dispersion — Spec 定义）  
3. **Max drawdown**（or comparable risk path metric）vs control  

### Auxiliary（may report · must not optimize）

4. Sharpe change  
5. Total / annualized return change  

### Explicit non-goals

```text
❌ Maximize return
❌ Maximize Sharpe as search objective
❌ Parameter grid / walk-forward “best filter”
```

---

## 7. Narrow Candidate / Governance Bindings

| Binding | Effect on RC001-A |
|---------|-------------------|
| NARROW Infrastructure Candidate | RC001-A Design eligible；FULL Candidate claims forbidden |
| P5 PARTIAL residual | Results carry Falsification qualification；≠ erase P5 gap |
| Price Family residual | Independence qualification retained on Knowledge side |
| Decision 019 | Consumption verbs only |
| Gate CONDITIONAL | ≠ Gate PASS；≠ Strategy Entry Gate fully open |
| Portfolio Bar NOT MET | ≠ BAR MET via RC001-A Design |

```text
RC001-A Design COMPLETE
        ≠
RC001 Accepted
        ≠
Backtest authorized
        ≠
Strategy research free-for-all
```

---

## 8. Phase Roadmap（authorization gates）

```text
RC001-A Design          ← COMPLETE（this doc）
        ↓
Contract Review         ← 另授（确认 baseline lock + Filter 单路径）
        ↓
Controlled Experiment Spec  ← 另授（窗口/品种/阈值/门槛/LER）
        ↓
Execution Authorization ← 另授
        ↓
Backtest（first strategy-consumption evidence）
        ↓
Evidence Review
        ↓（另授）
RC001-B Controlled Strategy Integration（仍非 Alpha mining）
```

### Current position

```text
RC001-A Design: COMPLETE ✓
Contract Review: NOT STARTED
Experiment Spec: NOT STARTED
Backtest: NOT STARTED
Strategy Development: FORBIDDEN in Phase A
```

---

## 9. Relation to legacy `RC001_RESEARCH_PLAN.md`

| Legacy Plan v0.2 | RC001-A Design v0.1 |
|------------------|---------------------|
| Context = MarketState UNKNOWN/TREND/RANGE | Context = **A1 ContextState** compression/expansion/invalid |
| Gate v1 BLOCKED as hard stop | Gate v2 CONDITIONAL + **NARROW Candidate** opens Design only |
| EXP002 Context-on after Gate Pass | Phase A Filter comparison under Narrow |
| Not Accepted | Remains Not Accepted；RC001-A does **not** Accepted legacy Plan |

```text
Legacy Plan = historical lineage / OPP16 parent pointer
RC001-A     = current executable Design track under NARROW
```

---

## 10. Deliverables of this Design phase

| Deliverable | Status |
|-------------|--------|
| RQ + structural diagram | ✓ |
| P1–P3 principles | ✓ |
| ContextFilter interface | ✓ |
| Baseline candidate（OPP16） | ✓ pending Contract Review lock |
| Metric roles（core vs aux） | ✓ |
| Phase gate map | ✓ |
| Code / backtest | **NOT in scope** |

---

## 11. Next authorization entry

```text
Authorize RC001-A Contract Review
```

或合并：

```text
Authorize RC001-A Controlled Experiment Spec
```

（仅当 Contract 已锁 baseline + 单路径 Filter。）

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-21 | 0.1 | Design COMPLETE：Filter-only；OPP16 baseline candidate；非收益中心评价；无回测 |
