# Epoch 3 Positioning — Capability Expansion & Research Governance Stabilization

**Status:** **CLOSED at Gate CONDITIONAL**（2026-07-21） · Phase 3.6 positioned  
**Prior:** [`EPOCH_2_SUMMARY.md`](EPOCH_2_SUMMARY.md)  
**Closure:** [`EPOCH_3_SUMMARY.md`](EPOCH_3_SUMMARY.md) — **CLOSED at Gate CONDITIONAL**  
**Next framing:** [`PHASE_36_EXIT_CRITERIA_RESOLUTION.md`](../research/PHASE_36_EXIT_CRITERIA_RESOLUTION.md)  
**Path:** `docs/releases/EPOCH_3_POSITIONING.md`

## One-sentence definition

> **Epoch 3 从「Context Capability 是否存在？」转向「Context Capability 是否具有足够稳定性与可扩展性，值得进入 Research Capability Layer？」——不是 Alpha / 策略阶段。**

**Closure addendum**：存在性 Evidence 已立；**策略安全消费尚未成立**（Gate CONDITIONAL）。

## Core question shift

| Epoch | Question |
|-------|----------|
| 2.0 | Does descriptive condition structure exist under registered conditions? |
| **3.0** | Is K001 a local phenomenon, or a **reusable research capability** with sufficient robustness? |

```text
Epoch 2:  idea → controlled research object → qualified knowledge
Epoch 3:  qualified knowledge → robustness & expansion → capability candidacy
```

## Hard boundaries（Epoch 3 仍禁止）

```text
❌ RC001 Accepted / Opportunity evaluation
❌ Market State Engine 漂移（K001 → classifier → strategy filter）
❌ Alpha / trading experiments
❌ Gate auto-open from K001 Strengthen
❌ 以提高回测收益为优化目标
```

Gate v1 保持 **BLOCKED** 直至独立 Gate Review（Phase 3.4）。

---

## Phase map

```text
3.1 Governance Consolidation          ✓ COMPLETE
3.2 RUN003 Cross-sectional Evidence   ✓ CLOSED
3.3 Observation Expansion Evidence    ✓ CLOSED（RUN004 Liquidity Structure）
3.4 Independence Evidence             RUN005 **CLOSED** ✓ · Partial confirmed · P4 **PARTIAL**
3.5 Gate v2 Policy Preparation        Confirmation PASS ✓
3.5 Gate v2 Review                    **CLOSED** ✓ — **CONDITIONAL**
3.6 Exit Criteria Resolution          **POSITIONED**（informal；NOT AUTHORIZED）
3.x Capability Portfolio Bar Review   v0.3 — **BAR NOT MET**（P4 PARTIAL）
```

**Epoch 3 outcome**：研究对象值得继续研究；**尚未**证明可被策略研究安全消费。

```text
Knowledge retained ≠ Capability ready ≠ Trading authorized
Next value: reduce uncertainty（L1 Independence coupling）≠ more supporting samples
```

---

## Phase 3.2 — RUN003 Cross-sectional（CLOSED ✓）

| Item | Status |
|------|--------|
| Spec / Fill / Auth | CONFIRMED / CONFIRMED / GRANTED |
| Observation | COMPLETE — SUPPORTED |
| Evidence Review | PASS |
| K001 Review | REMAIN STRENGTHENED QUALIFIED + universe expansion |
| Registered Action | STRENGTHEN **CONSUMED** |
| Closure | [`CAP_CTX_001_RUN003_CLOSURE_REVIEW.md`](../research/CAP_CTX_001_RUN003_CLOSURE_REVIEW.md) **CLOSED** ✓ |
| Gate / RC001 | BLOCKED / UNCHANGED |

---

## Phase 3.1 — Governance Consolidation（complete）

**Goal:** 将 RUN001/RUN002 事实标准固化为可复用治理。

| Deliverable | Status |
|-------------|--------|
| [`CROSS_EVIDENCE_GOVERNANCE.md`](../research/CROSS_EVIDENCE_GOVERNANCE.md) | **v1.2 Governance Baseline** ✓ |
| [`CROSS_EVIDENCE_GOVERNANCE_REVIEW.md`](../research/CROSS_EVIDENCE_GOVERNANCE_REVIEW.md) | Review PASS WITH REVISION |

### Evidence types（taxonomy）

| Type | 目的 | CAP-CTX 案例 |
|------|------|----------------|
| **Discovery Evidence** | 发现现象 | RUN001 |
| **Temporal Evidence** | 时间稳定性 | RUN002 |
| **Cross-sectional Evidence** | 品种/结构稳定性 | RUN003（**CLOSED** ✓） |
| **Observation Expansion Evidence** | 观测族稳定性 | RUN004（**CLOSED** ✓ · Liquidity） |
| **Stress Evidence** | 边界/压力测试 | 未来 |

### Cross Evidence accumulation chain

```text
Discovery Evidence
        ↓
Qualified Knowledge
        ↓
Temporal Evidence
        ↓
Cross-sectional Evidence
        ↓
Observation Expansion Evidence
        ↓
Stress Evidence
        ↓
Capability Candidate          ← not reached
        ↓
Accepted Capability           ← not reached
```

### Knowledge state machine（documented）

```text
Candidate
   ↓
Qualified
   ↓
Strengthened Qualified          ← K001 current
   ↓
Capability Candidate            ← Epoch 3 target band
   ↓
Accepted Capability
```

**Transitions require explicit Knowledge Review**；无自动晋级。

---

## Phase 3.3 — Observation Expansion Evidence（CLOSED ✓）

**Theme:** Observation Family Expansion  
**Primary variable:** Observation family only  
**Status:** RUN004 **CLOSED** ✓ — Liquidity Structure · SUPPORTED → STRENGTHEN consumed

| Item | Status |
|------|--------|
| Spec / Fill / Auth | CONFIRMED / CONFIRMED / GRANTED · COMPLETE |
| Evidence Review | [PASS](../research/CAP_CTX_001_RUN004_EVIDENCE_REVIEW.md) |
| K001 Review | REMAIN Strengthened Qualified + Family expansion |
| Closure | [`CAP_CTX_001_RUN004_CLOSURE_REVIEW.md`](../research/CAP_CTX_001_RUN004_CLOSURE_REVIEW.md) |
| P3 | **MET**（≠ P4） |

**Binding retained:** Claim Boundary · Family ≠ Feature · P3 ≠ P4 · 失败不换 Family（本 Run 已通过）。

---

## Phase 3.4 — Independence Evidence（Proposal Draft）

**Theme:** Independent Validation of K001  
**Gap:** Portfolio Bar **P4**  
**Status:** Gate v2 Review **CLOSED** — **CONDITIONAL** ✓ · Candidate **NO** · RC001 **UNCHANGED** · Trading **NOT STARTED**

**Binding:** CONDITIONAL ≠ PASS；L1–L5 = Exit Criteria ≠ auto task queue；Knowledge ≠ Gate；Route A recommended。

---

## Phase 3.5 — Capability Gate v2 Review（deferred；原 3.4）

**Not now.** 须 Portfolio（含 P4）与 Engineering 更成熟后另授。

### Proposed Gate v2 additions（draft for later）

| Criterion | Question |
|-----------|----------|
| **G5 Robustness** | 是否跨时间、品种、市场环境？ |
| **G6 Incremental Value** | Context 是否提供 baseline 无法提供的信息？（description / decision quality / research efficiency——**非 PnL**） |
| **G7 Independence** | 是否独立于 volatility / trend / liquidity 的重复？ |

**Inputs:** K001 portfolio + Independence Evidence + Engineering signal readiness.

---

## Current status（as-of 2026-07-21）

```text
Epoch 3 Phase:
  3.1 Governance          COMPLETE ✓
  3.2 RUN003              CLOSED ✓
  3.3 Observation Exp.    CLOSED ✓（RUN004 Liquidity）
  3.4 Independence        Proposal Confirmation PASS ✓
  3.5 Gate v2             DEFERRED

K001:              Strengthened Qualified · {rb,i,MA,TA} · families Vol+Price+Liquidity
Governance:        CROSS_EVIDENCE_GOVERNANCE v1.2 Baseline ✓
Portfolio Bar:     NOT MET（P3 MET；P4 open）
Gate v1:           BLOCKED
Gate v2:           DEFERRED
RC001:             UNCHANGED
Trading:           NOT STARTED
```

## Recommended next action

**Phase 3.4 Independence Proposal** → Review → Confirmation（仅提案链）

```text
RUN004 Closed ✓ · P3 MET
        ↓
Portfolio Bar still NOT MET（P4 open）
        ↓
Phase 3.4 Independence Proposal Confirmation PASS ✓
        ↓
Independence Spec Confirmation PASS ✓
        ↓
RUN005 CLOSED ✓ · Partial confirmed
        ↓
Gate v2 CLOSED — CONDITIONAL ✓
        ↓
Phase 3.6 Exit Criteria Resolution（positioned）
        ↓
（另授）L1 Independence repair → … → Gate Re-Review
  ≠ more P1–P3 samples
  ≠ strategy / PnL backtest now
```

1. **Do not** designate Capability Candidate  
2. **Do not** 未立项启动 Independence Observation / RUN005  
3. **P3 ≠ P4** 仍绑定；**Robustness ≠ Independence**  

### PAAF Research State

```text
Architecture:           COMPLETE
Evidence System:        OPERATIONAL
PRM:                    ACTIVE
K001:                   Strengthened Qualified · Family expansion
Capability Portfolio:   ASSESSED — Bar NOT MET（P3 MET；P4 NOT MET）
Gate:                   BLOCKED
RC001:                  UNCHANGED
Trading:                NOT STARTED
```

---

## 修订记录

| 日期 | 说明 |
|------|------|
| 2026-07-21 | Epoch 3 Summary；Phase 3.6 Exit Criteria positioned；L1 P0 |
| 2026-07-21 | Gate v2 Closure 对齐；Exit Criteria ≠ task queue；Route A recommended |
| 2026-07-21 | Gate v2 Review **CONDITIONAL**；lift L1–L5；RC001/Trading/Candidate unchanged |
| 2026-07-21 | Gate v2 Policy **Confirmation PASS**；Review Preparation Draft opened |
| 2026-07-21 | Gate v2 Policy v0.2：Readiness≠K001；G1–G4/G5–G10；P4 PARTIAL conditional block |
| 2026-07-21 | RUN005 Independence Review confirmed；Gate v2 Policy Draft v0.1 opened |
| 2026-07-21 | RUN005 CLOSED：Partial / NARROW；P4 PARTIAL；Portfolio Bar v0.3 |
| 2026-07-21 | IER Freeze Ceremony COMPLETE；IER-CTX-005 v1.0 sealed；Obs still NONE |
| 2026-07-21 | RUN005 Manifest + C-ENV Draft（identity only）；IER/Obs pending |
| 2026-07-21 | RUN005 Auth **Confirmation PASS**；CP3 OPEN；Manifest/Obs still none |
| 2026-07-21 | RUN005 Auth v0.2：GRANTED WITH CONDITIONS；R1/R2；Confirmation PENDING |
| 2026-07-21 | Fill Confirmation PASS；RUN005 Auth Draft v0.1 NOT GRANTED |
| 2026-07-21 | Independence Fill v0.2：IER Freeze；Access Level；Bias Matrix；Outcome→Action |
| 2026-07-21 | Independence Spec Confirmation PASS；Fill Draft v0.1 Mode B+C |
| 2026-07-21 | Independence Spec Draft v0.1：EQ-CTX-005；Modes A–D；B+C 建议；Failure mapping |
| 2026-07-21 | Phase 3.4 Proposal **Confirmation PASS**；Eligible for Independence Spec |
| 2026-07-21 | Phase 3.4 Proposal v0.2：Taxonomy I1–I5；Controlled Independence；Claim Boundary；Confirmation PENDING |
| 2026-07-21 | Phase 3.4 Independence Proposal Draft；Gate v2 → 3.5 |
| 2026-07-21 | RUN004 CLOSED；P3 MET；Portfolio Bar v0.2；next = P4 |
| 2026-07-21 | RUN004 Fill Draft v0.1：Liquidity Structure + M3 |
| 2026-07-21 | RUN004 Spec Confirmation PASS；Fill 可立项 |
| 2026-07-21 | RUN004 Spec PASS WITH REVISION → v0.2；EQ / Governance / Claim Boundary |
| 2026-07-21 | RUN004 Spec Draft v0.1；Family 未冻结；Observation Expansion |
| 2026-07-21 | Phase 3.3 Proposal Confirmation PASS；Spec 可立项 |
| 2026-07-21 | Phase 3.3 Proposal PASS WITH REVISION → v0.2；Family governance |
| 2026-07-21 | Portfolio Bar Review：BAR NOT MET；P3/P4 缺口 |
| 2026-07-21 | RUN003 Auth GRANTED；Phase 3.2 AUTHORIZED；Controlled Observation Window |
| 2026-07-21 | Epoch 3 定位；Phase 3.1–3.4；RUN003/004 proposed not authorized |
