# Phase 3.6 — Exit Criteria Resolution（Informal）

> **Status**: **Positioned** — L1 Proposal Draft opened · execution **NOT AUTHORIZED**  
> **Version**: 0.2  
> **Date**: 2026-07-21  
> **Path**: `docs/research/PHASE_36_EXIT_CRITERIA_RESOLUTION.md`  
> **Parent**: Epoch 3 Closure — [`EPOCH_3_SUMMARY.md`](../releases/EPOCH_3_SUMMARY.md)  
> **Gate**: [`CONTEXT_CAPABILITY_GATE_V2_REVIEW.md`](CONTEXT_CAPABILITY_GATE_V2_REVIEW.md) — CONDITIONAL · Exit Criteria L1–L5  
> **L1 Proposal**: [`PHASE_36_L1_INDEPENDENCE_REPAIR_PROPOSAL.md`](PHASE_36_L1_INDEPENDENCE_REPAIR_PROPOSAL.md) — **Confirmation PASS** ✓  
> **L1 Spec**: [`CAP_CTX_001_L1_INDEPENDENCE_SPECIFICATION.md`](CAP_CTX_001_L1_INDEPENDENCE_SPECIFICATION.md) — **Draft v0.1**

### Watershed（binding）

```text
PAAF: Exploration → Capability Validation
最大不确定性 ≠ Alpha
最大不确定性 = Context 是否具备可被策略消费的可靠性
```

```text
不要直接写策略或回测
```

---

## 1. Objective

> Reduce uncertainty that keeps Gate v2 at CONDITIONAL — especially Independence coupling — so a **re-authorized Gate Re-Review** can honestly consider PASS / CONDITIONAL / BLOCK.

**不是**：再证明一次 K001。

---

## 2. Priority order

| Priority | Exit Criterion | Focus |
|----------|----------------|-------|
| **P0** | **L1 Independence** | 降低定义耦合；P4 PARTIAL → MET（或显式永久 Narrow+降权） |
| P1 | **L2 Falsification / Stress** | Negative Evidence Coverage；结构不存在时系统能否识别 |
| P1 | **L3 Engineering signal** | 非 UNKNOWN 的研究可用一级状态 |
| P2 | **L4 / L5** | Bar+Candidate 路径；RC001 另授；消费边界（Variable ≠ Signal） |

---

## 3. L1 — Independence repair（highest value）

### Problem（from RUN005）

```text
M1-derived condition / evaluation coupling
        ↓
independence robustness limited
        ↓
P4 PARTIAL → Gate CONDITIONAL
```

问题不是 Context 不存在，而是**部分评价能力依赖原始定义方式**。

### Allowed research direction（when chartered）

```text
Same Research Question
        +
Different condition construction / generation path
        →
Test whether support retains with reduced definition coupling
```

示例方向（**未选定 · 未授权**）：

- 替换 M1-derived partition  
- 完全不同的 condition construction  
- 保留 RQ，改变生成路径（Controlled Independence 深化）

### Forbidden

```text
❌ 再证明一次 K001 / 堆 P1–P3 样本
❌ 为 PASS 隐藏 Partial / Negative Evidence
❌ 未立项改 Closed RUN001–005
❌ 以 PnL 验证 Independence
```

### Success framing

```text
P4: PARTIAL → MET
  OR
explicit permanent Narrow + capability down-weight（不得静默）
        ↓
re-enter Gate Review（另授）
```

---

## 4. L2 / L3 — Falsification & Engineering

| Track | Question |
|-------|----------|
| L2 | 若 Context 结构不存在，系统是否能识别？（Negative Evidence Coverage / Stress） |
| L3 | 是否存在可研究消费的一级 published state（非仅 UNKNOWN）？ |

Null 已有 ≠ Gate 级 Falsification 已满足。

---

## 5. L4 / L5 — Consumption boundary（not trading code）

**允许（未来）**：

```text
Context → Research Variable → Strategy Hypothesis
```

**禁止**：

```text
Context → Signal → Buy/Sell
```

定义消费边界 ≠ 写 vn.py 策略 / CTA 回测 / 参数优化。

---

## 6. Strategy / offline backtest entry（hard gate）

**现在不建议**：vn.py strategy · CTA backtest · 参数优化 · PnL ranking。

**合理入口**仅当：

```text
Gate v2 PASS（或显式 Controlled Research Entry）
+
Capability Candidate
+
RC001 Accepted
```

之后策略研究形态：

```text
Context Capability + Trading Hypothesis
        ↓
Strategy Experiment → Offline Backtest → Evidence
```

**禁止**：

```text
回测赚钱 → 证明 Context 有用
```

---

## 6.1 Strategy Entry Gate（最低门槛 · binding）

**现在不建议** vn.py strategy / CTA 回测 / 参数优化 / PnL ranking。

启动 Strategy Research 前至少：

| ID | Requirement |
|----|-------------|
| **SE-G1** | Capability Candidate = **YES**（**不是**仅 K001 Qualified） |
| **SE-G2** | Context Interface Defined：decision variable（filter / risk / selection）≠ entry signal |
| **SE-G3** | RC001 Positive Evidence：Strategy vs Strategy+Context（非直接开发 PAAF Strategy） |

另需：**Gate v2 PASS**（或显式 Controlled Research Entry）作为前置；Independence 达 MET **或** Partial 经显式接受为可消费。

示例形态（未来）：Baseline PA Strategy vs PA + Context Filter（expectancy / DD / trade quality / regime）——**仅在 SE-G1…G3 后**。

---

## 6.2 Maturity snapshot（indicative）

```text
Architecture          ██████████ 100%
Evidence System       ██████████ 100%
Context Discovery     █████████░  ~90%
Capability Proof      ██████░░░░  ~60%
Strategy Integration  ██░░░░░░░░  ~20%
Trading System        ░░░░░░░░░░    0%
```

方向未偏；勿因正向 Evidence 跳过 Capability Gate。

---

## 7. Next

```text
L1 Independence Repair Proposal v0.2
        ↓
Proposal Confirmation Review
        ↓
L1 Experiment Spec（另开）
        ≠
Observation / Strategy / RUN006 sample stack
```

当前：**L1 Proposal v0.2**；**Confirmation PENDING**；**execution NOT AUTHORIZED**。

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-21 | 0.1 | Phase 3.6 定位；L1 P0；禁止扩样本默认；策略入口门槛 |
| 2026-07-21 | 0.2 | Watershed；Strategy Entry Gate；maturity snapshot；L1 Proposal pointer |
| 2026-07-21 | 0.2.1 | L1 Proposal v0.2（PASS WITH REVISION applied）；Confirmation pending |
