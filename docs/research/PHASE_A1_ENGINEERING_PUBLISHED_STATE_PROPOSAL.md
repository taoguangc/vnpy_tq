# Phase A1 — Engineering / Published State Proposal（G2 · E1）

> **Type**: Engineering Capability Proposal（≠ Spec Change · ≠ RC001 · ≠ Strategy · ≠ Backtest）  
> **Status**: **Confirmation PASS** ✓ — Eligible for A1 Spec Draft  
> **Version**: 0.2  
> **Date**: 2026-07-21  
> **Path**: `docs/research/PHASE_A1_ENGINEERING_PUBLISHED_STATE_PROPOSAL.md`  
> **Spec**: [`CAP_CTX_A1_ENGINEERING_PUBLISHED_STATE_SPECIFICATION.md`](CAP_CTX_A1_ENGINEERING_PUBLISHED_STATE_SPECIFICATION.md) — **v0.2 Confirmation PENDING**
> **Gate**: [`CONTEXT_CAPABILITY_GATE_V2_REEVALUATION.md`](CONTEXT_CAPABILITY_GATE_V2_REEVALUATION.md) — CONDITIONAL · **G2 BLOCK**  
> **Bar**: [`CAPABILITY_PORTFOLIO_BAR_REVIEW.md`](CAPABILITY_PORTFOLIO_BAR_REVIEW.md) v0.4 — E1 **NOT READY**  
> **Knowledge**: K001 Strengthened Qualified + Independence Qualified  
> **Spec boundary**: [`CONTEXT_ENGINE_SPEC.md`](../specs/CONTEXT_ENGINE_SPEC.md) v0.1.1 Accepted — **本 Proposal 不修改 Spec**  
> **Prior**: Draft v0.1 → PASS WITH REVISION → v0.2 → **Confirmation PASS**

### Confirmation（binding）

```text
================================================
PHASE_A1_ENGINEERING_PUBLISHED_STATE_PROPOSAL v0.2

Confirmation: PASS ✓

R1–R5: COMPLETE ✓
Scope: Engineering Published State Validation

Excluded:
  Implementation · RC001 · Strategy · Backtest · Gate Unlock

Eligible next: A1 Spec Draft

K001: Strengthened Qualified + Independence Qualified
Gate v2: CONDITIONAL
Capability Candidate: NO
RC001: NOT STARTED
Strategy: NONE
================================================
```

### Purpose（binding）

```text
Published State Reliability Validation
        ≠
Alpha Validation
        ≠
Strategy Validation
        ≠
Context Effectiveness Validation（→ RC001）
```

```text
G2:  Context 在系统路径上是否可靠存在？
RC001: Context 能否改善策略选择？（后置）
```

**先 A1，后 RC001-A。**

---

## 0. Authority Boundary

| 本 Proposal **是** | 本 Proposal **不是** |
|--------------------|----------------------|
| Engineering / Published State 立项 | Spec 静默升版 / ADR 替代 |
| Runtime Contract + 工程验收设计 | Detector / Strategy / Backtest |
| Gate G2 / Bar E1 输入准备 | Capability Candidate 自动指定 |
| 只读状态发布可靠性 | Effectiveness / Alpha / 买卖信号 |

```text
Engineering Validation ≠ Capability Validation
Draft ≠ Confirmation ≠ Impl Auth ≠ Spec change
```

---

## 1. Why A1 now

| Layer | Status |
|-------|--------|
| Evidence / Independence | Qualified PASS ✓ |
| Claim Boundary | Frozen ✓ |
| Gate v2 | CONDITIONAL · **G2 BLOCK** |
| Portfolio E1 | **NOT READY** |
| Candidate / RC001 | NO / deferred |

最大缺口：**稳定消费（Engineering）**。跳过 A1 做 RC001 → offline/online 不一致会污染消费实验。

---

## 2. EQ-A1（frozen）

> Can K001-linked descriptive context be published as a deterministic, parity-checked, failure-aware runtime state suitable for strategy **consumption interfaces**（filter / risk modifier）— without becoming a trading signal?

```text
可靠性（能否稳定发布）
        ≠
有效性（能否改善交易）
```

---

## 3. R1 — Published State ≠ Knowledge（binding）

```text
Published State is a technical projection of registered context observation.

It does not represent:
  - market truth
  - predictive probability
  - trading recommendation
```

| Field | Means | Does **not** mean |
|-------|-------|-------------------|
| `confidence` | **context computation confidence**（计算/数据完备置信） | trading confidence / win_probability / edge |
| `descriptive_state` | 注册观察的技术投影 | market regime truth claim |
| `state_validity` | 发布是否工程上可信 | “值得交易” |

```text
confidence = 0.8
        ≠
win_probability = 80%
```

违反此解耦 → Engineering Evidence **不得**包装为 Capability / Alpha 证据。

---

## 4. Relation to Accepted Spec

```text
CONTEXT_ENGINE_SPEC v0.1.1
  MarketState: UNKNOWN | TREND | RANGE
  Compression NOT baseline
  Context ≠ Feature ≠ Signal
```

当前实现：恒 `UNKNOWN`。A1 **不**静默改 Spec / 不升 Compression 入基线；映射经 Confirmation → Spec/Fill →（若需）ADR。

---

## 5. Work structure（frozen）

```text
1. ContextState Contract
        ↓
2. Deterministic Publish Test
        ↓
3. Batch / Streaming Parity
        ↓
4. Fault Handling（Negative Engineering Cases）
        ↓
5. Latency Measurement（engineering-only）
        ↓
6. Engineering Evidence Review
        ≠
Capability Validation / RC001
```

---

## 6. E1.1 — ContextState Contract（R2 · freeze at Spec）

Spec 阶段须冻结（Confirmation 后写入 A1 Spec；此处为 Proposal 推荐终形）：

```text
ContextState {
  timestamp,
  instrument,
  context_version,     # recipe / code / contract version identity
  state_validity,      # VALID | DEGRADED | INVALID
  descriptive_state,   # see below
  confidence,          # computation confidence ONLY（R1）
  diagnostics          # machine-readable reasons / traces；no orders
}
```

### `descriptive_state` — allowed

```text
{
  compression_state,      # descriptive tag only；≠ Spec baseline MarketState 升格
  volatility_condition,
  structure_tag
}
```

### `descriptive_state` — forbidden

```text
{
  direction_prediction,
  expected_return,
  trade_bias,
  buy_signal,
  sell_signal
}
```

消费语义：allow/block **既有**策略信号 · risk_modifier **hint**（须标非强制）· logging。  
**禁止**：Context 单独开仓。

---

## 7. E1.2 — Deterministic Publish + Parity（R3）

### Deterministic Publish Test

同输入 → 同 `context_version` → 同 `ContextState`（契约字段）。

### Batch ↔ Streaming Parity

**冻结比较对象**：

| Must match | Must **not** compare |
|------------|----------------------|
| same input bars | 最终交易结果 / PnL |
| same timestamp boundary | Sharpe / PF / 选股效率 |
| same `context_version` | RC001 effectiveness |
| **Published State equality**（契约字段） | Strategy outcome |

```text
Parity object = Published State
        ≠
Trade results
```

否则提前进入 RC001 → **INVALID scope**。

Pass：离散字段 identical；连续字段 ε 仅在 Spec/Fill 预注册（默认优先 bit-identical）。

---

## 8. E1.3 — Negative Engineering Cases（R5）

| Case | Expected |
|------|----------|
| missing bar | **DEGRADED** |
| duplicate timestamp | **INVALID** |
| **future data leakage** | **INVALID** |
| rollover mismatch | **INVALID** |
| session boundary mismatch | **DEGRADED** or **INVALID**（Fill 写死） |
| insufficient warmup | **INVALID** / no publish |
| symbol switch without contract | **INVALID** or **DEGRADED**（Fill 写死） |

### Future data leakage（binding）

```text
Context 最大工程风险之一 ≠ 慢
最大风险 = 离线计算偷偷使用未来信息
```

任何 forward-looking 输入进入 `state_t` 发布 → **INVALID**；计入 Engineering Evidence，**不得**解释为 K001 false。

---

## 9. E1.4 — Latency（R4 · demoted）

```text
1m bar close → context update → publish
  wall time < 100ms（p99；单品种；环境预注册）
```

定位：

```text
Engineering requirement only
        ≠
Production readiness
```

A1 **只**验证 Context Engine **execution latency**。  
**不**宣称已覆盖：broker feed · gateway · recovery · monitoring · 全链路生产 SLA。

Spec 更严 Design Target（μs）不因 A1 削弱，亦不在本阶段强制。

---

## 10. Non-goals

```text
❌ Alpha / Strategy / Effectiveness Validation
❌ RC001 Filter 回测 / 年化优化
❌ Candidate 自动指定 / Gate 自动 PASS
❌ 修改 Closed Evidence
❌ confidence → win_probability 叙事
❌ Parity via trade PnL
```

---

## 11. Success → Gate mapping（preview · not auto）

| A1 Outcome | Preview |
|------------|---------|
| PASS | G2 可评 PASS WITH QUALIFICATION；E1 READY WITH LIMITS；**另授** Gate Re-review |
| PARTIAL | G2 仍 CONDITIONAL |
| FAIL | Engineering block 保留；≠ K001 Downgrade |
| INVALID | 协议/泄漏/范围违规 |

```text
A1 Evidence PASS
        ↓
Gate v2 Re-review（另授）
        ↓
Capability Candidate Decision（另授）
        ↓
RC001 Authorization（另授）
        ↓
Context Filter Backtest
        ≠
A1 PASS → 马上策略
```

---

## 12. Open Items（before Confirmation）

| ID | Item | Status |
|----|------|--------|
| O1 | ContextState 终表 ↔ Spec `Context`/`extras` 映射 | **OPEN** → Spec |
| O2 | ADR 需求：研究 Published State vs MarketState | **OPEN** |
| O3 | Parity ε / 舍入 / 品种与窗 | **OPEN** → Fill |
| O4 | Failure 决策表终稿（含 session） | **OPEN** → Fill |
| O5 | Latency 测量环境冻结 | **OPEN** → Fill |

> O1–O5 可在 Confirmation 后由 **A1 Spec/Fill** 关闭；Confirmation 要求：R1–R5 边界已写入且不可弱化。

---

## 13. Proposal checklist（v0.2）

| ID | Check | Verdict |
|----|-------|---------|
| A1P1 | Reliability ≠ Effectiveness / Alpha | **PASS** |
| A1P2 | R1 State≠Knowledge；confidence≠win_prob | **PASS** |
| A1P3 | R2 descriptive_state allow/forbid | **PASS** |
| A1P4 | R3 Parity = Published State only | **PASS** |
| A1P5 | R4 Latency ≠ Production readiness | **PASS** |
| A1P6 | R5 + future leakage INVALID | **PASS** |
| A1P7 | Spec 不静默修改 | **PASS** |
| A1P8 | No RC001/Strategy | **PASS** |

> Checklist PASS ≠ Confirmation PASS。

---

## 14. Next

```text
Confirmation PASS ✓
        ↓
A1 Spec Draft（另文）
        ≠
Implementation / RC001 / Strategy
```

当前：**Confirmation PASS**；Spec = Draft v0.1。

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-21 | 0.1 | Draft：EQ-A1；E1.1–E1.4；Spec 边界 |
| 2026-07-21 | 0.2 | PASS WITH REVISION：R1–R5；工作结构 1–6 |
| 2026-07-21 | 0.2 | **Confirmation PASS** — Eligible for A1 Spec Draft |
