# CAP-CTX-001 — Independence Evidence Pre-Registration Fill（v0.2）

> **Type**: Governance Completion Document（Independence Fill · Portfolio Bar **P4**）  
> **Status**: **Confirmation PASS** ✓ — Pre-Registration COMPLETE · Eligible for Execution Authorization  
> **Version**: 0.2  
> **Date**: 2026-07-21  
> **Path**: `docs/research/CAP_CTX_001_INDEPENDENCE_PRE_REGISTRATION_FILL.md`  
> **Parent Spec**: [`CAP_CTX_001_INDEPENDENCE_SPECIFICATION.md`](CAP_CTX_001_INDEPENDENCE_SPECIFICATION.md) v0.2 **Confirmation PASS**  
> **Parent Proposal**: [`CAP_CTX_001_PHASE34_INDEPENDENCE_EVIDENCE_PROPOSAL.md`](CAP_CTX_001_PHASE34_INDEPENDENCE_EVIDENCE_PROPOSAL.md) — Confirmation PASS  
> **Parent Knowledge**: K001 (**Strengthened Qualified**)  
> **Governance**: [`CROSS_EVIDENCE_GOVERNANCE.md`](CROSS_EVIDENCE_GOVERNANCE.md) v1.2  
> **Lineage**: Original chain RUN001–004 Closed · future `run_id=CAP_CTX_001_RUN005`（仅 Auth 后）  
> **EQ**: EQ-CTX-005  
> **Prior**: Draft v0.1 → Fill Review **PASS WITH REVISION** → v0.2 → **Confirmation PASS**

### Fill Confirmation（binding）

```text
================================================
CAP_CTX_001_INDEPENDENCE_PRE_REGISTRATION_FILL v0.2

Confirmation: PASS ✓

IER Freeze:              PASS ✓
Artifact Access Control: PASS ✓
Mode:                    C → B FROZEN ✓
Residual Bias Matrix:    PASS ✓
Outcome → Knowledge Action: PASS ✓

Pre-Registration: COMPLETE ✓
Mode frozen: Mode B+C（C→B）
IER protocol: IER-CTX-005 v1.0

Execution Authorization: NOT STARTED
Observation: NONE
Evidence generation: NOT AUTHORIZED
Knowledge update: NOT AUTHORIZED

K001: UNCHANGED（Strengthened Qualified）
Gate: BLOCKED
RC001: UNCHANGED
Capability Candidate: NO
================================================
```

### Claim Boundary（binding）

> Fill freezes the Independence instance design; it does **not** authorize execution, upgrade K001, or designate Capability Candidate.

```text
Fill Confirmation PASS
        ≠
Auth / Observation
        ≠
P4 PASS → Capability Candidate
```

```text
Failure ≠ K001 false
```
---

## 1. Mode selection（proposed freeze · pending Confirmation）

### Selected Mode（order frozen）

```text
Mode B + Mode C combination
  Order FROZEN: C → B

Independent Research Specification（C）
        ↓
Seal Independent Evaluation Rubric / Record（IER）
        ↓
Independent Evaluation Path（B）
        ↓
Read-only Artifact Evaluation
```

**禁止** B→C（先评价再写独立路径 → 反馈污染）。

### Rejected for this instance

| Mode | Reason |
|------|--------|
| A | 工程成本高；非当前主风险（researcher choice） |
| D | 外部复现过重；Controlled Independence 优先 |
| B only | 缺少 IER 密封，评价仍易被原路径污染 |
| C only | 无对 Closed artifacts 的独立评价落地 |
| B→C order | 评价框架易被原路径污染；仅证明“另一 evaluator 认可” |

### Selection criteria answers（Spec §5.1）

| # | Answer |
|---|--------|
| 1 | I3 + I4（Evaluation + Research Path） |
| 2 | 见 §2.1 Residual Bias Matrix |
| 3 | 非新窗/品种/Family/参数；是证据生成路径分离 |
| 4 | RQ + Claim Boundary 保持 |
| 5 | 见 §5 Outcome → Action；失败不换 Mode |
| 6 | 非为更容易 PASS；C→B 提高证伪可见性 |
| 7 | Controlled Independence；非 External Replication |

---

## 2. §5.2 Candidate Mode Governance Table（proposed freeze）

| 项 | Fill |
|----|------|
| **Candidate Mode** | **Mode B+C**（**C→B 顺序冻结**） |
| **Independence Dimension** | **I4** Research Path + **I3** Evaluation Independence |
| **Shared Components** | Research Question；K001 Claim Boundary；Governance v1.2；Closed artifact 身份；TQ offline / 1m / CbC 数据契约；同一研究者组织（非外部机构） |
| **Removed Dependencies** | （C）IER 冻结前不打开 intermediate design / Original interpretation；（B）不改写 Closed Evidence 数值；Knowledge decision 文档在 Phase B 前 **unavailable** |
| **Residual Bias** | 见 §2.1 Matrix（不追求零 bias） |
| **Independence Argument** | 先密封评价标准再触达 Closed 细节，降低 self-confirmation；再分离 Evidence≠Evaluation |
| **Protocol delta** | sealed IER + Artifact Access Level + IER 评分；**不**改 Universe/Time/Family/Null 为实验变量 |
| **Exclusion Criteria** | ≠ P1/P2/P3 扩展；≠ Feature 调参；≠ 重跑；≠ Mode A/D；≠ B→C |
| **Failure Interpretation** | 见 §5；失败 **禁止**改 Mode / 放宽 IER |
| **Non-claim list** | Capability Candidate；Gate PASS；K001 unconditional；“K001 为假”；外部复现完成；Alpha |

### 2.1 Residual Bias Matrix（R4 · binding disclosure）

> 目的不是证明无 bias，而是证明**知道 bias 在哪里**。

| Bias | Remaining? | Impact | Note |
|------|------------|--------|------|
| Dataset selection | **Partial** | medium | 继承 Closed 宇宙/窗指纹；非本 Mode 实验变量 |
| Original RQ framing | **Yes** | high | EQ / Claim 故意保持；Independence ≠ 换问题 |
| Evidence contract | **Yes** | low | Manifest→Evaluation→Record 层保留（治理一致性） |
| Same research organization | **Yes** | medium | Controlled Independence；非 Mode D |
| Indirect memory of design | **Partial** | medium | C 密封降低；无法保证零记忆 |
| Evaluator interpretation | **Reduced** | medium | IER Freeze + Access Level 约束后验解释 |
| Implementation path（I1） | **Yes** | medium | 本实例不测 Mode A |
| Data-handling assumptions（I2） | **Yes** | low–medium | 本实例不重开数据处理假设 |

```text
Residual Bias disclosed
        ≠
Independence FAIL
        ≠
zero-bias claim
```

---

## 3. Phase C — IER Freeze（R1 · binding）

### 3.0 Before opening artifacts — Freeze Checklist

**在打开任何 Evidence artifact / Original interpretation / Knowledge decision 之前**，必须已冻结并写入执行记录：

| Freeze item | Binding content（本 Fill） |
|-------------|---------------------------|
| **Evaluator identity** | Role = `Independent Evaluator (Controlled)`；组织 = PAAF research（non-external）；须在 Manifest / Report 记名或记角色 ID |
| **Evaluation protocol version** | `IER-CTX-005 v1.0`（本 Fill §3）；变更 → 新 `run_id` |
| **Metric definitions** | IER-1…IER-5 questions + Retain/Narrow/Reject/Infeasible bands（§3.2–3.3）；**不是** E1/E2/E3 重跑参数 |
| **Interpretation rules** | Aggregate 表（§3.3）+ Outcome→Action（§5）；Failure ≠ K001 false |

```text
Independent Evaluation Requirement
        ↓
Seal Independent Evaluation Record（IER Freeze）
        ↓
Read-only Artifact Evaluation（Phase B）
```

未完成 §3.0 Freeze Checklist → **禁止**进入 Phase B artifact access。

### 3.1 Sealing rule（binding）

```text
Phase C drafting constraint：
  DO NOT open for rubric design:
    - RUN001–004 metric recipes / threshold notes
    - Family selection rationales beyond public Claim/EQ
    - post-hoc narrative in Evidence Reviews（Original interpretation）
    - Knowledge decision documents（K001 Review body）
  MAY open:
    - EQ-CTX-005 / Claim Boundary / Governance
    - Closed status labels（SUPPORTED / CLOSED）without metric tables
```

Fill Confirmation 后，IER 条款不可为提高 PASS 而修改；修改 → 新 `run_id`。

### 3.2 IER — Core questions（sealed）

| ID | Question |
|----|----------|
| **IER-1** | 在注册 Claim Boundary 下，是否仍有足够证据支持「存在 descriptive condition structure」——**不**要求 Capability / Alpha？ |
| **IER-2** | 时间维（Temporal）支持是否可在不依赖原 Discovery 叙事的前提下被保留？ |
| **IER-3** | 截面维（Cross-sectional）支持是否可被保留？ |
| **IER-4** | 观察域扩展（Observation Family）支持是否可被保留？ |
| **IER-5** | 原链结论是否明显依赖未披露的 researcher degrees of freedom（若是，列出）？ |

### 3.3 IER — Scoring bands（sealed）

| Band | Meaning |
|------|---------|
| **Retain** | 独立评价下仍支持该维 |
| **Narrow** | 仅在更窄条件下支持（须写收窄项） |
| **Reject** | 独立评价下不支持该维 |
| **Infeasible** | 证据不足以下判（artifact/文档缺口） |

**Aggregate**：

| Aggregate | Result |
|-----------|--------|
| IER-1 Retain，且 IER-2…4 均非 Reject，且 IER-5 无阻断性路径依赖 | **PASS** |
| IER-1 Retain，但 IER-2…4 出现 Narrow，或范围须收窄 | **Partial** |
| IER-1 Reject，或关键维 Reject 且不可收窄保留核心主张，或 IER-5 路径依赖主导 | **FAIL** |
| 关键维 Infeasible 无法裁决 | **INFEASIBLE** |

```text
IER scoring ≠ re-running E1/E2/E3 with new parameters ≠ PnL / Alpha
```

### 3.4 What IER deliberately does not do

```text
❌ 新 Universe / Time / Family / 参数搜索
❌ 要求 Mode A 代码重写
❌ 要求外部机构签字
❌ 以“再证明一次 Robustness”替代 Independence
❌ 打开 artifact 后再改 metric / interpretation rules
```

---

## 4. Artifact Access Level（R2 · binding）

| Artifact | Access Level | Rule |
|----------|--------------|------|
| **Raw data** | **restricted** | 默认不打开；仅当 IER 某维 Infeasible 且身份核验必要时，经 Auth 条件允许只读指纹/覆盖率核验；**禁止**探索性重算冒充 Independence |
| **Evidence artifact**（Manifest / evaluation.json / EvidenceRecord） | **read-only** | 仅 Phase B（IER Freeze 完成之后）；禁止编辑 |
| **Original interpretation**（Evidence Review 叙事、事后解释） | **sealed until Phase B**；Phase B = **read-only / cite-sparingly** | Phase C **不可用**；Phase B 引用须标注“原叙事”，不得当作 IER 前提 |
| **Knowledge decision**（K001 Review 决策正文 / Citation 包装） | **unavailable until after IER scoring draft** | 防止继承原作者 Knowledge packaging；评分完成后方可对照 Claim Boundary 做一致性检查 |

```text
Purpose:
  prevent unintentional inheritance of original-author narrative
```

### 4.1 Phase B procedure（with Access Level）

```text
1. Complete §3.0 IER Freeze Checklist（recorded）
2. Open Evidence artifacts read-only（per table）
3. Apply IER-1…5 with written justifications
4. Assign aggregate Outcome
5. Only then：optional Knowledge-decision对照（Claim Boundary check）
6. Complete Residual Bias Matrix runtime notes
7. Write EvidenceRecord + Report（若 RUN005 授权）
```

### 4.2 Integrity

```text
No edit to Closed evaluations.
No silent Mode swap / order swap（C→B frozen）.
No post-hoc IER amendment for PASS.
No Phase C access to Original interpretation / Knowledge decision.
```

---

## 5. Outcome → Interpretation → Knowledge Action（R5 · binding）

```text
Outcome
    ↓
Interpretation
    ↓
Registered Knowledge Action
    ↓
Knowledge Decision（另授 Review）
```

| Outcome | Meaning（Interpretation） | Registered Action | Knowledge Decision（另授） |
|---------|---------------------------|-------------------|---------------------------|
| **PASS** | Independence support increases；当前证据链在 Controlled Independence 下仍支持核心主张 | STRENGTHEN（Independence / P4-facing） | **Maintain K001** Strengthened Qualified（可加 Independence 范围注记）；**≠** Capability Candidate |
| **Partial** | Independence limited；支持仅在更窄资格下成立 | NARROW（qualification） | Narrow qualification；tier 默认仍 Strengthened Qualified unless Review 另裁 |
| **FAIL** | Current evidence chain insufficiently independent for present claim packaging | NARROW 或 DOWNGRADE | Remain Strengthened Qualified with heavier qualification **或** Downgrade；**≠** “K001 false” |
| **INFEASIBLE** | Protocol cannot be executed as filled | 无 Action | 新 `run_id`；禁止换 Mode 凑 PASS |

```text
Registered Action
        ≠
Knowledge Decision
        ≠
Portfolio Bar MET automatic
        ≠
Capability Candidate
```

```text
FAIL
  =
insufficient independence support for current claim packaging
  ≠
automatic “descriptive structure does not exist”
```

---

## 6. Dataset / Protocol identity（non-experimental）

| Item | Status |
|------|--------|
| Data baseline | TQ offline · 1m · CbC · 无复权（继承；**非**实验变量） |
| Universe / Time / Family | 继承 Closed；**不**作为 Independence 实验变量 |
| Fingerprint | 仅身份核验（若 Raw data restricted 触达）；≠ Evaluation evidence |
| Null N1/N2 | 非本 Mode 主判据；IER 为主协议 |

---

## 7. Non-goals / Conditions preview

```text
❌ Auth / Observation in this document
❌ Mode A/D 替换；B→C 顺序
❌ Gate / Capability Candidate / RC001
❌ 失败后改 IER / 换 Mode 凑 PASS
❌ 零 Residual Bias 宣称
```

未来 Auth 条件预览（非授权）：**C-IER** · **C-ART**（Access Level）· **C-ORDER**（C→B）· **C-SCOPE** · **C-CLAIM** · **C-GATE** · **C-NO-DRIFT** · **C-K001** · **C-BIAS**（Matrix 披露）。

---

## 8. Fill checklist（v0.2）

| ID | Check | Verdict |
|----|-------|---------|
| IF1 | Mode B+C；C→B **frozen** | **PASS** |
| IF2 | Governance Table + Residual Bias Matrix | **PASS** |
| IF3 | IER Freeze（identity / protocol / metrics / interpretation）before artifacts | **PASS** |
| IF4 | Artifact Access Level table | **PASS** |
| IF5 | Outcome → Interpretation → Knowledge Action | **PASS** |
| IF6 | Failure ≠ K001 false；Non-goals；no Auth | **PASS** |

> Checklist PASS ≠ Fill Confirmation PASS。Confirmation 须另轮。

---

## 9. Next

```text
Fill Confirmation PASS ✓
        ↓
Execution Authorization Draft
        ↓
Authorization Review
        ≠
Observation until GRANTED + explicit execution instruction
```

当前：**Pre-Registration COMPLETE**；Auth **NOT STARTED**；Observation **NONE**。

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-21 | 0.1 | 首版：Mode B+C；Governance Table；IER sealed；Phase C→B；Failure mapping |
| 2026-07-21 | 0.2 | PASS WITH REVISION：IER Freeze；Artifact Access Level；Residual Bias Matrix；Outcome→Action；C→B frozen |
| 2026-07-21 | 0.2.1 | **Confirmation PASS**；Eligible for Execution Authorization；Observation still NONE |
