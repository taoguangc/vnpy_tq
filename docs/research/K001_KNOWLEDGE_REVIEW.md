# K001 — Knowledge Review

> **Type**: Knowledge Review（Qualified → Strengthen → Cross-sectional → Family → Independence Narrow → **L1 Independence Repair**）  
> **Knowledge ID**: K001  
> **Evidence Sources**: `CAP_CTX_001_RUN001` … `RUN005` + **`CAP_CTX_001_L1_RUN001`**  
> **Date**: 2026-07-21  
> **Path**: `docs/research/K001_KNOWLEDGE_REVIEW.md`  
> **Prior Evidence**:  
> - [`CAP_CTX_001_RUN001_EVIDENCE_REVIEW.md`](CAP_CTX_001_RUN001_EVIDENCE_REVIEW.md)  
> - [`CAP_CTX_001_RUN002_EVIDENCE_REVIEW.md`](CAP_CTX_001_RUN002_EVIDENCE_REVIEW.md)  
> - [`CAP_CTX_001_RUN003_EVIDENCE_REVIEW.md`](CAP_CTX_001_RUN003_EVIDENCE_REVIEW.md)  
> - [`CAP_CTX_001_RUN004_EVIDENCE_REVIEW.md`](CAP_CTX_001_RUN004_EVIDENCE_REVIEW.md)  
> - [`CAP_CTX_001_RUN005_EVIDENCE_REVIEW.md`](CAP_CTX_001_RUN005_EVIDENCE_REVIEW.md)（Evidence PASS · Independence **Partial**）  
> - [`CAP_CTX_001_L1_RUN001_EVIDENCE_REVIEW.md`](CAP_CTX_001_L1_RUN001_EVIDENCE_REVIEW.md)（Evidence PASS · Independence **Qualified PASS**）

### Layer Distinction（强制）

```text
Experiment Result ≠ Evidence Finding ≠ Accepted Knowledge ≠ Gate / RC001 / Alpha
```

**Not in scope（本 L1 Knowledge Review）**: Gate Re-evaluation · RC001 · Alpha · Capability Candidate · Strategy / Backtest.

---

## Current Knowledge Decision（authoritative）

```text
================================================
K001 L1 INDEPENDENCE REPAIR KNOWLEDGE REVIEW

Decision:
ACCEPT STRENGTHENED QUALIFIED KNOWLEDGE ✓
+ Independence Qualified PASS（L1）
+ ADDITIONAL QUALIFICATION（residual Price Family）

Registered Action consumed: STRENGTHEN（Independence / P4-facing）✓

Independence update vs RUN005:
  M1 label-generation dependency: REMOVED（structure survives GEN≠LER）
  Residual Price Family coupling: RETAINED（N2 SMD_M2 ≫ SMD_FWD）
  Full independence: NO
  Independent market regime claim: NO

Not:
  Capability Candidate
  ACCEPT (unconditional)
  Downgrade / NARROW（L1）
  Gate PASS / P4 full MET
  “K001 false” / “完全独立”
  Alpha / trading signal

Status:
  K001 (Strengthened Qualified
        + Independence Qualified
        + residual Price Family qualification)

Gate v2: CONDITIONAL（Re-evaluation COMPLETE · G6 PASS WITH QUALIFICATION；G2/E1 still block）
RC001: UNCHANGED / DEFERRED
Strategy: NOT STARTED
================================================
```

### Citation form（current）

```text
K001 (Strengthened Qualified + Independence Qualified)
  — RUN001–RUN005 + L1_RUN001
  — universe {rb, i, MA, TA}
  — families: Volatility + Price + Liquidity Structure
  — Independence: M1 label-coupling repaired（Qualified PASS）;
                  residual Price Family dependency remains
  — Not: independent market regime · full independence · Capability Candidate
```

Allowed：

> Under registered CAP-CTX-001 conditions, descriptive condition structure remains Strengthened Qualified; after L1 Independence Repair, the structure persists with reduced M1 label-generation dependency（Qualified PASS）. Residual Price Family coupling remains material. K001 is a descriptive context structure, not an independent market-regime variable, not Capability Candidate, not Alpha.

Forbidden：

```text
❌ Capability Candidate / Gate PASS / P4 full MET
❌ fully independent / zero residual dependency
❌ independent market regime / predictive alpha
❌ K001 false / unconditional ACCEPT
❌ direct buy/sell signal from K001
```
---

## Historical Decision #1 — Initial Promotion（2026-07-21）

```text
Decision: ACCEPT WITH QUALIFICATION
Source: RUN001 only
Status superseded for “current citation” by Strengthen Review below;
historical record retained.
```

详见原 §1–§9 结构；下文以 Strengthen Review 为当前权威。

---

## Strengthen Review — KR-S1…S4

### KR-S1 — Evidence Accumulation

| Run | Window | E1 | E2 | E3 | Evidence Review |
|-----|--------|----|----|----|-----------------|
| RUN001 | 2024–2025 | PASS | PASS | 2/2 supported | PASS |
| RUN002 | 2022–2023 | PASS | PASS | 2/2 supported | PASS · SUPPORTED |

协议：RUN002 = RUN001 inheritance；唯一覆盖 = temporal scope。

累计含义：

```text
Single-window Qualified Evidence
        +
Independent Temporal OOS Cross Evidence
        =
Stronger support chain than RUN001 alone
```

解释权重仍以 **E2 + E3 + SMD_M2** 为主；E1 为 supporting。

**Verdict KR-S1: PASS — accumulation justifies Strengthen（confidence），not Expand.**

---

### KR-S2 — Scope

**Chosen path**：

```text
Strengthen:
  same scope family / universe / descriptive nature
  higher confidence via temporal reproducibility
```

**Rejected path**：

```text
Expand:
  all instruments / all markets / new families
```

Scope 更新（相对初版）：注册条件从「仅 RUN001 窗口」扩展为「RUN001 + RUN002 两个已注册非重叠时间窗」；**品种宇宙与观测族不变**。

**Verdict KR-S2: PASS — same scope, higher confidence.**

---

### KR-S3 — Limitations（still binding）

| ID | Limitation | After Strengthen |
|----|------------|------------------|
| L1 | E1 definition coupling（M1→Partition→SMD_M1） | **RETAINED** |
| L2 | Single Run / no Cross Evidence | **CLEARED**（RUN002 Temporal OOS） |
| L3 | Family = Volatility + Price only | **RETAINED** |
| L4 | Universe = `{rb, i, MA}`；transfer 未饱和 | **RETAINED** |
| L5 | Single period only | **PARTIALLY CLEARED**（2022–2023 + 2024–2025）；更远时期/制度冲击仍开放 |
| L6 | Descriptive ≠ Predictive | **RETAINED** |

```text
Strengthen MUST NOT remove Qualification.
```

因此：不是 unconditional ACCEPT；也不是「额外新资格」（无新增限制种类）→  
选用 **ACCEPT STRENGTHENED QUALIFIED KNOWLEDGE**，而非 STRENGTHEN WITH ADDITIONAL QUALIFICATION。

**Verdict KR-S3: PASS — Qualification retained.**

---

### KR-S4 — Falsification Boundary

K001（Strengthened Qualified）**仍可被降级 / 收窄 / 撤回**，例如：

| Condition | Effect |
|-----------|--------|
| 新时间窗在同等协议下 E2/E3 系统性失败 | Downgrade / Narrow |
| 扩展 universe 后 transfer 系统性失败 | 收窄 transferable 用语 |
| 修正 definition-coupling 后独立分离不再成立 | 修订 claim 或降级 |
| Null 协议复现后显著性消失 | 降级 / 撤回 |

```text
K001 is not permanent truth.
Strengthened ≠ irreversible.
```

**Verdict KR-S4: PASS — falsifiable.**

---

## Cross-sectional Review — KR-CX1…CX4（RUN003）

> **Trigger**: RUN003 Evidence Review PASS · `registered_knowledge_action = STRENGTHEN`  
> **Evidence type**: Cross-sectional · Universe expansion only

### KR-CX1 — Evidence Accumulation

| Run | Variable | Window | E1 | E2 | E3 | Evidence Review |
|-----|----------|--------|----|----|----|-----------------|
| RUN001 | Discovery | 2024–2025 | PASS | PASS | 2/2 | PASS |
| RUN002 | Temporal OOS | 2022–2023 | PASS | PASS | 2/2 | PASS · SUPPORTED |
| RUN003 | Cross-sectional | 2024–2025† | 4/4 PASS | PASS | 3/3（i,MA,TA） | PASS · SUPPORTED |

† 时间窗为 execution condition（继承 RUN001 协议），非 RUN003 实验变量。

累计含义：

```text
Temporal chain (RUN001+RUN002)
        +
Cross-sectional universe expansion (RUN003)
        =
Stronger descriptive support on registered expanded universe
        ≠
Capability Candidate
```

**Verdict KR-CX1: PASS — accumulation justifies scope expansion, not Capability.**

---

### KR-CX2 — Scope（registered expansion only）

**Chosen path**：

```text
Remain Strengthened Qualified
  + expand evaluated universe to {rb, i, MA, TA}
  + TA = pre-registered expansion instrument（C-UNIV）
```

**Rejected path**：

```text
Capability Candidate
all futures markets
ad-hoc symbol substitution
new observation families
```

**Verdict KR-CX2: PASS — registered universe expansion only.**

---

### KR-CX3 — Limitations（still binding）

| ID | Limitation | After RUN003 |
|----|------------|--------------|
| L1 | E1 definition coupling | **RETAINED** |
| L2 | No Cross Evidence | **CLEARED** |
| L3 | Family = Volatility + Price only | **RETAINED** |
| L4 | Universe = initial `{rb,i,MA}` only | **PARTIALLY CLEARED** → expanded registered set `{rb,i,MA,TA}`；**非**全市场 |
| L5 | Single period only | **PARTIALLY CLEARED**（两时间窗）；截面窗与 RUN001 重叠但变量不同 |
| L6 | Descriptive ≠ Predictive | **RETAINED** |

```text
Universe expansion MUST NOT remove Qualification.
RUN003 PASS MUST NOT imply Capability Candidate.
```

**Verdict KR-CX3: PASS — Qualification retained; L4 narrowed to registered expansion.**

---

### KR-CX4 — Falsification Boundary

新增/强化可证伪路径：

| Condition | Effect |
|-----------|--------|
| 新 expansion instrument 在同等协议下系统性失败 | 不得换品种；须新 `run_id` |
| Observation Expansion（新 Family）失败 | 不自动削弱截面结论；独立 Review |
| Gate v2 未通过 | 仍 BLOCKED |

**Verdict KR-CX4: PASS — falsifiable; C-UNIV binding.**

---

## Historical Decision #2 — Temporal Strengthen（2026-07-21）

```text
Decision: ACCEPT STRENGTHENED QUALIFIED KNOWLEDGE
Source: RUN001 + RUN002
Status: retained; superseded for citation scope by RUN003 review below
```

---

## 1. Knowledge Claim（current）

### 1.1 Strengthened Qualified claim（current）

> Under CAP_CTX_001 registered conditions spanning two non-overlapping temporal windows (RUN001: 2024–2025; RUN002: 2022–2023) and one registered cross-sectional universe expansion (RUN003: +TA on 2024–2025 execution window), volatility and price observations demonstrated cumulative evidence consistent with persistent and transferable descriptive condition structure across the evaluated universe `{rb, i, MA, TA}`, subject to retained methodological qualifications.

### 1.2 Forbidden claims（unchanged class）

```text
❌ Market conditions exist (as a general fact)
❌ Context is a stable model
❌ Predictive power established
❌ Trading / Alpha value established
❌ Context Capability Gate PASS
❌ Universal property of futures markets
❌ Qualification removed by Strengthen
```

---

## 2. Supporting Evidence（cumulative）

| Source | Contribution |
|--------|----------------|
| CAP_CTX_001_RUN001 | Initial Qualified Evidence（E1/E2/E3 + Nulls） |
| CAP_CTX_001_RUN002 | Temporal OOS Cross Evidence；SUPPORTED → STRENGTHEN Action |
| CAP_CTX_001_RUN003 | Cross-sectional Evidence；universe +TA；SUPPORTED → STRENGTHEN Action |
| Evidence Reviews | All PASS；方法学限制持续披露 |
| E2 vs block null（两窗 + RUN003 窗） | 非随机持续结构（高解释权重） |
| E3 transfer（RUN001/002: 2/2；RUN003: 3/3） | 含 expansion instrument TA |
| Reproducibility | Fingerprints · Manifests · Pre-registration · Scripts |

---

## 3. Evidence Limitations（current）

见 KR-S3 / KR-CX3 表。**Qualification 因 L1/L3/L6（及 L5 残余）而保留。**

---

## 4. Scope Boundary（Frozen — Strengthened + RUN003 expansion）

```text
K001 Scope (Strengthened Qualified)

Applies ONLY:
  - under CAP_CTX_001_RUN001, RUN002, and RUN003 registered conditions
  - to volatility + price observation families as registered
  - to evaluated universe {rb, i, MA, TA}
    (TA = pre-registered expansion instrument; C-UNIV binding)
  - as descriptive structure evidence (not predictive / trading)
  - with temporal reproducibility across 2022–2023 and 2024–2025 windows

Does NOT apply:
  - all futures markets
  - unregistered symbols / ad-hoc universe expansion
  - unregistered observation families
  - Context Engine / Market State Model claims
  - Opportunity evaluation (RC001)
  - Capability Candidate / Gate PASS
  - unconditional / universal confirmation
```

---

## 5. Reproducibility Status

| Item | RUN001 | RUN002 | RUN003 |
|------|--------|--------|--------|
| Dataset Fingerprint | ✓ | ✓（same rb/i/MA） | ✓（+TA） |
| Run Manifest | ✓ | ✓ | ✓ |
| Pre-Registration | ✓ | ✓ | ✓ |
| Evaluation Contract + Nulls | ✓ | inherited | inherited |
| Script | `run_cap_ctx_001_run001.py` | `run_cap_ctx_001_run002.py` | `run_cap_ctx_001_run003.py` |

---

## 6. Decision Rationale Summary（RUN003）

| Option | Verdict |
|--------|---------|
| ACCEPT（unconditional） | **No** — L1/L3/L6 仍在 |
| Capability Candidate | **No** — Portfolio Bar **NOT MET**（P3/P4） |
| **REMAIN STRENGTHENED QUALIFIED + UNIVERSE EXPANSION** | **Yes** — RUN003 SUPPORTED；C-UNIV 绑定 |
| DOWNGRADE / NARROW | **No** — RUN003 SUPPORTED |
| 换品种继续 Run | **No** — 违反 C-UNIV |

---

## 6b. Decision Rationale Summary（RUN002 · historical）

| Option | Verdict |
|--------|---------|
| ACCEPT（unconditional） | **No** — L1/L3/L4/L6 仍在 |
| **ACCEPT STRENGTHENED QUALIFIED KNOWLEDGE** | **Yes** — Temporal OOS 累积支持；Qualification 保留 |
| STRENGTHEN WITH ADDITIONAL QUALIFICATION | **No** — 无新增限制种类；L2/L5 部分解除而非新限制 |
| REMAIN QUALIFIED (NO STATUS CHANGE) | **No** — 会低估独立时间外证据链 |
| DOWNGRADE | **No** — RUN002 SUPPORTED |

---

## 7. Status After RUN003 Knowledge Review

```text
K001:
  Strengthened Qualified Knowledge
  (REMAIN + REGISTERED UNIVERSE EXPANSION)

Citation:
  K001 (Strengthened Qualified)
  — RUN001 + RUN002 + RUN003 — Scope §4

Evaluated universe:
  {rb, i, MA, TA}

Gate:
  BLOCKED (unchanged)
  — RUN003 SUPPORTED ≠ Gate PASS ≠ Capability Candidate

RC001:
  unchanged

CAP-CTX-001:
  PROMOTED (campaign unchanged)

Phase 3.2 RUN003:
  CLOSED ✓
```

---

## 7b. Status After Strengthen Review（historical）

```text
K001:
  Strengthened Qualified Knowledge
  (ACCEPT STRENGTHENED QUALIFIED KNOWLEDGE)

Citation:
  K001 (Strengthened Qualified)
  — RUN001 + RUN002 — Scope §4

Gate:
  BLOCKED (unchanged)

RC001:
  unchanged
```

---

## 8. KR / KR-S Checklist Summary

| ID | Focus | Verdict |
|----|-------|---------|
| KR1–KR5 | Initial promotion | ACCEPT WITH QUALIFICATION（historical） |
| **KR-S1** | Evidence Accumulation | **PASS** |
| **KR-S2** | Scope（same / higher confidence） | **PASS** |
| **KR-S3** | Limitations / Qualification retained | **PASS** |
| **KR-S4** | Falsification | **PASS** |
| **Strengthen Decision（RUN002）** | | **ACCEPT STRENGTHENED QUALIFIED KNOWLEDGE** |
| **KR-CX1** | RUN003 accumulation | **PASS** |
| **KR-CX2** | Registered universe expansion | **PASS** |
| **KR-CX3** | Limitations retained | **PASS** |
| **KR-CX4** | Falsification / C-UNIV | **PASS** |
| **RUN003 Decision** | | **REMAIN STRENGTHENED QUALIFIED + UNIVERSE EXPANSION** |
| **KR-OF1** | RUN004 Liquidity Family | **PASS**（Evidence SUPPORTED） |
| **RUN004 Decision** | | **REMAIN STRENGTHENED QUALIFIED + FAMILY EXPANSION** |
| **KR-IND1** | RUN005 Controlled Independence | **PASS**（Evidence PASS · Outcome Partial） |
| **RUN005 Decision** | | **REMAIN STRENGTHENED QUALIFIED + INDEPENDENCE NARROW**（superseded for Independence citation by L1） |
| **KR-L1-1** | L1 Evidence accumulation | **PASS** |
| **KR-L1-2** | M1 dependency removal vs residual Price | **PASS**（Qualified） |
| **KR-L1-3** | Claim ceiling / non-regime | **PASS** |
| **KR-L1-4** | Falsification retained | **PASS** |
| **L1 Decision** | | **ACCEPT STRENGTHENED QUALIFIED + Independence Qualified PASS + Price residual qualification** |

---

## 9. L1 Independence Repair Knowledge Review（authoritative for Independence）

> **Trigger**: L1 Evidence Review PASS · Independence claim Qualified PASS  
> **Consumed Action preview**: STRENGTHEN（Independence / P4-facing）  
> **Gate / Candidate**: **NOT** decided here

### KR-L1-1 — Evidence accumulation — PASS

| Layer | Result |
|-------|--------|
| Execution | VALID |
| Metric aggregate | PASS（E1/E2/E3 Retain） |
| Independence claim（Evidence） | Qualified PASS |
| C-DEP | M1 label dependency removed；Price/universe/structure/time retained |

```text
RUN005: Independence Partial（M1-label coupling Narrow）
        +
L1:     structure survives less-coupled process（GEN≠LER）
        =
Independence support strengthened with residual Price qualification
```

### KR-L1-2 — Outcome selection — PASS

| Candidate | Selected? | Reason |
|-----------|-----------|--------|
| **A — ACCEPT STRENGTHENED QUALIFIED + Independence Qualified PASS** | **Yes（primary）** | E1–E3 Retain；M1 label-coupling repaired under freeze |
| **B — ADDITIONAL QUALIFICATION（residual Price / not regime）** | **Yes（addendum）** | N2 `SMD_M2 ≫ SMD_FWD`；descriptive structure ≠ independent market regime |
| **C — NARROW** | **No** | Evidence does not support “Context ≈ price transformation artifact only” |

### KR-L1-3 — Claim boundary — PASS

```text
K001 = descriptive context structure
        ≠
independent market regime variable
        ≠
Alpha / buy-sell signal
```

消费边界（Knowledge 层预告，**非** Gate PASS）：

| May eventually consume（after Gate/Candidate） | Must not claim now |
|-----------------------------------------------|--------------------|
| context filter / regime selector / allocator modifier | direct signal · PnL proof |

### KR-L1-4 — Falsification — PASS

| Future condition | Action |
|------------------|--------|
| L1-class process FAIL under same freeze | NARROW / DOWNGRADE Independence |
| Residual coupling shown to fully explain E1（N1 non-separation） | NARROW |
| Claim Migration / Anti-Opt violation | INVALID（no Knowledge Action） |

### L1 Decision（binding）

```text
ACCEPT STRENGTHENED QUALIFIED KNOWLEDGE
+ Independence Qualified PASS（M1 label-generation dependency reduced）
+ ADDITIONAL QUALIFICATION:
    residual Price Family dependency remains material;
    not independent market regime;
    not fully independent capability
```

```text
Knowledge updated
        ≠
Gate v2 Re-evaluation performed
        ≠
Capability Candidate
        ≠
Strategy authorized
```

---

## 修订记录

| 日期 | 说明 |
|------|------|
| 2026-07-21 | Formal Knowledge Review：ACCEPT WITH QUALIFICATION |
| 2026-07-21 | Confirmation；优先 Cross Evidence（Route A） |
| 2026-07-21 | **Strengthen Review**：ACCEPT STRENGTHENED QUALIFIED KNOWLEDGE |
| 2026-07-21 | Knowledge Review Confirmation 归档 |
| 2026-07-21 | Cross Evidence Governance v1.0 引用 |
| 2026-07-21 | Portfolio Bar Review：BAR NOT MET；P3/P4 缺口 |
| 2026-07-21 | **RUN004 Family Review**：REMAIN + Liquidity Structure；STRENGTHEN consumed |
| 2026-07-21 | **RUN005 Independence Review**：REMAIN + NARROW qualification；Partial；NARROW consumed |
| 2026-07-21 | **L1 Knowledge Review**：STRENGTHEN Independence Qualified PASS + Price residual qualification；Gate 未重评 |
