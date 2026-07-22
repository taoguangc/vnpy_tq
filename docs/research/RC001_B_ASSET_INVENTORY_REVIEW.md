# RC001-B — Asset Inventory Review

> **Type**: Asset Inventory Review（≠ Strategy Research · ≠ Recovery · ≠ Re-bind · ≠ Backtest）  
> **Status**: **COMPLETE** ✓  
> **Date**: 2026-07-22  
> **Authorization**: `Authorize RC001-B Asset Inventory Review`  
> **Scope**: `RC001-B Asset Inventory Review Phase` only  
> **Parent Closure**: [`RC001_B_EXP001_CLOSURE_REVIEW.md`](RC001_B_EXP001_CLOSURE_REVIEW.md) — **CLOSED — BLOCKED**  
> **Contract**: [`RC001_B_CONTRACT_FREEZE.md`](RC001_B_CONTRACT_FREEZE.md) — **FROZEN · unmodified**  
> **Bind artifact**: `research/output/evidence/RC001_B_EXP001/strategy_identity_bind.json` — remains **UNBOUND**

### Review Record（binding）

```text
================================================
RC001-B ASSET INVENTORY REVIEW

Objective: Do bindable orthogonal S1/S2 assets exist?

Valid S1: NOT FOUND
Valid S2: NOT FOUND

C-BIND: NOT SATISFIED
EXP001: remains CLOSED — BLOCKED

Contract change: NONE
Strategy fabrication: NONE
Backtest / Observation: NONE
================================================
```

---

## 0. Unique question

> 当前仓库 / 历史 artifact 是否存在满足 RC001-B Contract 的正交 S1/S2 策略资产？

判定对象：

| Role | Class |
|------|-------|
| **S1** | Trend-oriented strategy |
| **S2** | Non-trend / Mean-Reversion strategy |

必须可绑定（Contract §1.2）：

```text
identity · version · source revision · parameter set · hash · lineage
```

另须满足：Context 独立、非为 RC001-B 新造、非按 PnL 挑选。

---

## 1. Inventory Scope Results

### 1.1 Repository Strategy Tree（`strategies/`）

| Asset | Present | CtaTemplate | Bindable as S1/S2? | Reason |
|-------|---------|-------------|--------------------|--------|
| `TemplateStrategy` | YES | YES | **NO** | Skeleton；无交易语义 |
| `PaafStrategy` | YES | YES | **NO** | 编排器；不定义正交 CTA 身份 |
| `OPP16` detector | YES | NO | **NO alone** | 检测器 ≠ 完整 S1/S2 CTA；且仅一件，无法成对 |
| `demo_minimal` | YES | NO | **NO** | Demo detector |
| Sensors / engines / evidence | YES | NO | **NO** | 非策略资产 |

```text
Current tree CTA shells:
  TemplateStrategy  → ❌
  PaafStrategy      → ❌
```

### 1.2 Referenced Historical Assets（`classic_*`）

| Check | Result |
|-------|--------|
| Referenced | **YES** — `scripts/run_classic_baseline_compare.py` imports 11 `Classic*` classes |
| Present in working tree | **NO** |
| Present in any git blob | **NO** — `git rev-list --objects --all` 仅命中该 script 本身 |
| Present at Initial commit `3316a16` | **NO** |

Named imports（script-only）：

```text
ClassicDualThrustStrategy
ClassicTurtleStrategy
ClassicBollChannelStrategy
ClassicKeltnerChannelStrategy
ClassicAberrationStrategy
ClassicKeltnerChannel15m{,V2,V3}Strategy
ClassicAberration15m{,V2,V3}Strategy
```

```text
classic_*
  Referenced: YES
  Available source: NO
  → cannot bind
```

### 1.3 Deleted Strategy Families（git history · recoverable source ≠ bindable）

Deleted in `04398ef`（parent `e2bfc0c`，2026-07-20）。源码可从该 revision 检出，但**不满足** RC001-B C-BIND：

| Family | Source at `e2bfc0c` | Orthogonal Trend/MR class? | Context-independent? | Frozen S1/S2 identity package? | Bindable? |
|--------|---------------------|----------------------------|----------------------|--------------------------------|-----------|
| `pa_cta` | YES | **NO** — multi-OPP Brooks PA 单体 | **NO** — embeds `context_layers` / `regime_gate` | **NO** | **NO** |
| `pa_minimal` | YES | **NO** — same family slim | Unattested for routing roles | **NO** | **NO** |
| `brooks_scalp` | YES | At most one trend-ish scalp | Likely yes (no Context engine) | **NO** — no Closed S1 lineage for RC001-B | **NO**（缺正交对手 + 缺冻结包） |
| `smc_orderflow_vwap` | YES | **NO** — SMC + VWAP Z hybrid | Mixed filters | **NO** | **NO** |

```text
Recoverable from git
        ≠
Bindable under C-BIND

Reason: missing orthogonal pair attestation,
        missing frozen identity/version/param/hash/lineage package,
        and/or Context entanglement (pa_cta).
```

### 1.4 Research Artifacts（`research/` · `output/` · `evidence/`）

| Artifact family | Frozen code+version+hash for CTA S1/S2? | Notes |
|-----------------|------------------------------------------|-------|
| `OPP16_EXP001` | Detector identity YES；CTA pair **NO** | Closed event study；RC001-A baseline |
| `RC001_A_EXP001` | Wrapper+OPP16 for Filter；pair **NO** | Single strategy arm × CTRL/FILT；非 S1∧S2 |
| `CAP_CTX_*` / sensors | **NO** | Capability / Feature；非 CTA |
| `RC001_B_EXP001` | Bind file **UNBOUND** | Templates only；Observation **NONE** |
| `ATR_COMPRESSION` / `OI_CHANGE` / … | **NO** | Sensor experiments |

判定规则（本 Review 执行）：

```text
Artifact + Code + Version + Hash
        → candidate only if also
orthogonal Role (S1 XOR S2) + lineage + param set + Context independence

Chat mention / script import / deleted multi-setup PA
        → NOT an asset
```

### 1.5 Known Historical Strategy Families（name-level）

曾在项目话语 / 脚本名中出现：CTA Trend、Donchian、Turtle、Momentum、Boll/MACD、RBreaker、ORB、MultiCycle、TrendRegimeFramework。

本 Review 结论：

```text
Discussed / named
        ≠
frozen artifact + source available + bindable
```

仓库与 git 对象中**未找到**上述家族的冻结源码 + 身份包。

---

## 2. Bind Checklist（aggregate）

| Field | S1 | S2 |
|-------|----|----|
| strategy_id | null | null |
| version | null | null |
| source_revision | null | null |
| parameter_set | null | null |
| content hash | null | null |
| lineage | null | null |
| Context-independent attested | — | — |
| Not fabricated for RC001-B | — | — |
| Orthogonal pair attested | **false** | **false** |

```text
Valid S1: NOT FOUND
Valid S2: NOT FOUND
C-BIND: UNSATISFIED
```

---

## 3. What is explicitly NOT counted as an asset

```text
❌ 历史聊天中的策略描述
❌ 曾经跑过但没有冻结 identity 的代码
❌ 未 hash 的实验脚本
❌ 可临时改造成 S1/S2 的策略
❌ script import 而无 blob 的 classic_*
❌ 可 git checkout 但缺正交对 / 缺冻结包 / 内嵌 Context 的 deleted PA 框架
❌ 单独的 OPP16（不足以成对；且非 Contract 定义的 Trend CTA）
```

原因：会破坏 RC001-B **single variable attribution**（唯一实验变量 = Routing）。

---

## 4. Impact

| Object | Effect |
|--------|--------|
| RC001-B Contract | **UNCHANGED**（未修改） |
| RC001-B EXP001 | **remains CLOSED — BLOCKED** |
| C-BIND | **NOT SATISFIED**（确认） |
| K001 / Gate v2 / Capability / A1 / RC001-A | **UNCHANGED** |
| Strategy Research | **NOT STARTED** |

```text
Inventory COMPLETE
        ≠
Strategies recovered
        ≠
C-BIND satisfied
        ≠
Permission to write S1/S2 inside RC001-B
```

---

## 5. Recommendation

```text
Preserve EXP001 closure
Do not fabricate S1/S2 under RC001-B
```

### Next options（须另授；互斥语境）

| Option | Authorization phrase | Meaning |
|--------|----------------------|---------|
| **A** | `Authorize Historical Strategy Asset Recovery Review` | 继续在归档/外源寻找**已冻结**可恢复资产（仍禁止新写策略） |
| **B** | `Confirm RC001-B Permanent Closure` | 接受当前 Capability 验证边界；RC001-B Routing 能力验证至此终止 |
| **C** | Separate **Strategy Research Phase** | 与 RC001-B **分离**；不重新打开 EXP001；不修改 Contract |

```text
不建议：在 RC001-B 内直接“写 S1/S2”
原因：那属于 Strategy Research，破坏实验边界
```

---

## 6. Scope compliance

| Forbidden in this Phase | Honored? |
|-------------------------|----------|
| 新建策略 | ✓ |
| 修改策略逻辑 | ✓ |
| 参数优化 | ✓ |
| 回测 | ✓ |
| Strategy Research | ✓ |
| Portfolio 构建 | ✓ |
| 修改 RC001-B Contract | ✓ |

---

## 修订记录

| 日期 | 说明 |
|------|------|
| 2026-07-22 | Asset Inventory Review **COMPLETE**；Valid S1/S2 **NOT FOUND**；C-BIND **NOT SATISFIED** |
