# PAAF 路线图

> 版本：3.1.0 · 更新日期：2026-07-20  
> 路线图**可变**；宪章与规格冻结后，改路线图不等于改哲学。  
> **研究顺序以 Decision 017 为准**；本文件不得与之冲突。

---

## Sprint 计划

### 阶段总览

```text
Phase 0  Research Chaos（AFF）              — 已结束
Phase 1  Architecture Foundation（v0.1）    — 已结束（Tag v0.1.1）
Phase 2  Detector Framework（v0.2）         — 已结束（Pipeline Verification）
Phase 3  Evidence Platform（v0.3）          — 当前（Decision 017）
Phase 4  Validation Protocol（v0.4）        — 下一
Phase 5+ Market State → Opportunity → …   — 其后
```

### Sprint 1 — Framework（已完成）

目标：**框架跑通，不关心收益。**

| 交付物 | 状态 |
|--------|------|
| Foundation + Context Spec + Context Engine | **完成** → Tag `v0.1.1` |
| CSV Logger / vn.py 可加载 Strategy | 待做（可与后续并行，非 v0.3 阻塞） |

#### PAAF v0.1.1 里程碑

```text
PAAF v0.1.1

✓ Context API Frozen
✓ Context Lifecycle Frozen
✓ Context Contract Frozen

Market State
  Not Implemented
```

### Sprint 2 — Detector Framework（已完成）

目标：**先 Framework，后 OPP；无证据不进 Production。**

| 版本 | 交付 | 状态 |
|------|------|------|
| v0.2.0 | `docs/specs/DETECTOR_FRAMEWORK_SPEC.md` | **Accepted**（Decision 013） |
| v0.2.1 | `DetectionResult` / `PatternState` / 必要类型（`Signal` Deprecated） | **完成** |
| v0.2.2 | `Opportunity` + DetectionResult 引用 + lineage | **完成** |
| v0.2.3 | Descriptor Catalog Registry + Capability Query | **完成** |
| v0.2.4 | Detector Pipeline Verification + `DEMO_MINIMAL` | **完成** |

```text
✓ Context
✓ DetectionResult
✓ Opportunity
✓ Registry
✓ Detector Pipeline Verification
✓ Minimal Opportunity Logger

Detector Framework Complete
Alpha Not Implemented
```

### Sprint 3 — Evidence Platform（当前 · Decision 017）

目标：**把已有研究能力产品化；暂停新 OPP / Alpha。**

**Done Definition（不是代码行数）：**

```text
Experiment → Evaluation → Evidence → Portfolio → Query
全部闭环可运营
```

| 范围 | 状态 |
|------|------|
| Evidence / Evaluation 切片（已跑通多轮 EXP） | **部分完成** |
| Experiment Repository 产品化 | 待做 |
| Research Portfolio 索引（DATA/FEATURE/PATTERN/DETECTOR/EXECUTION） | 待做 |
| Cross-Experiment Query | 待做 |
| Dashboard（最小版） | 待做（可后置） |

**明确不做（v0.3）：** 新 OPP、新 Market State、新 Alpha、Feature→交易主链。

### Sprint 4 — Validation Protocol（下一 · Decision 017）

目标：**验证协议**，不是 Multi-Symbol Engine。

**Done Definition：**

```text
Every Candidate Detector
  → Automatically Validated
  → Multi-Symbol
  → Roll-aware
  → Evidence Generated
```

协议须预注册：最少品种/样本量、HOLD/KEEP、E2 条件、Roll 双报。具体 Spec 另开。

---

## 已关闭研究快照（append-only；禁止原地复活）

ATR / Volume / OI / Close Location Feature EXP001 与 `OPP16_EXP001` 均 **Closed（inconclusive / Negative Evidence）**。  
Decision 016：暂停 rb「标量 Feature ↔ RV_60」同构。  
Decision 017：Closed 实验不可变；新条件 → 新 `experiment_id`（可声明 parent）。

| Spec / ADR | 状态 | 说明 |
|------|------|------|
| `ATR_COMPRESSION_EXP001` | **Closed** | inconclusive / HOLD |
| `DATA_CONTINUOUS_CONTRACT_EXP001` | **Closed** | material_annotate / HOLD；基线不变 |
| `DATA_CONTINUOUS_CONTRACT_EXP002` | **Closed** | annotate_multi / HOLD |
| `CLOSE_LOCATION_EXP001` | **Closed** | ρ_ex=-0.0046；inconclusive |
| `OPP16_EXP001` | **Closed** | mean_ex=-0.000134；Negative Evidence |
| `VOLUME_RATIO_EXP001` | **Closed** | ρ_ex=0.0646；inconclusive |
| `OI_CHANGE_EXP001` | **Closed** | ρ_ex=-0.0198；inconclusive |
| `FEATURE_ROLL_ANNOTATION_POLICY_RFC.md` | **Accepted** | 新 Feature 须双报 |
| Decision 016 | **Accepted** | 暂停 rb Feature↔RV_60 同构 |
| Decision 017 | **Accepted** | Evidence-first 路线；Portfolio；append-only |
| Decision 015 | **Accepted** | 双路径；Intent+Evidence+Enablement |
| Decision 011 | **Accepted** | 无证据不进 Production |

---

## Release（Decision 017）

| 版本 | 含义 |
|------|------|
| v0.1.0 | Framework Skeleton |
| v0.1.1 | Context Engine Foundation（**Tagged**） |
| v0.2.0–0.2.4 | Detector Framework → Pipeline Verification |
| **v0.3.x** | **Evidence Platform**（当前） |
| **v0.4.x** | **Multi-Symbol Validation Protocol** |
| v0.5.x | Market State |
| v0.6.x | Opportunity Library（真实 OPP） |
| v0.7.x | Decision Engine |
| 其后 | Execution Adapter / Production CTA |

旧表中「v0.4 Market State / v0.5 Opportunity」已被 Decision 017 **后移**。

---

## Git 约定

### Commit

```text
feat(context): add Context Engine
feat(detector): implement OPP16
feat(logger): export trade log
refactor(strategy): decouple signal engine
docs: update detector specification
test: add detector unit tests
```

禁止：`update` / `fix` / `modify` 这类无信息提交说明。

### Branch

- `main`：永远可运行（稳定点；Decision 012）
- 功能：`feature/detector-framework`、`feature/market-state` …
- 实验：`research/e0-compression`、`research/e3-transition` …
- 完成：Review 后 Merge 回 `main`；发布打 Annotated Tag

---

## 明确不做（在论证通过前）

- 机器学习 / 深度学习信号
- 无约束参数搜索与自动「优化到年化」
- 为证明 Brooks 正确而扭曲数据或成本
- 大爆炸式重写整个 `strategies/` 树
- 将 Feature Engine 插入冻结信号主链
- **v0.3 期间未经立项授权的新 OPP / Alpha 跑数**（Decision 017）
- **覆盖或原地复活 Closed 实验**（Decision 017）

## 后续项（未立项实现）

| 项 | 状态 | 说明 |
|----|------|------|
| Feature Layer（ATR/EMA/ADX 等） | E0 假设 | 若实现，只作 Context/Risk 的计算依赖；**不得**改主链为 Market→Feature→Context |
| `research/run_*.py` 三层治理 | 待治理专项 | experiments / validation / reports；纳入 v0.3 Portfolio/Query |
| Research Portfolio Dashboard | 概念已定 | UI 后置；ADR 不绑实现 |

---

## 变更方式

改本文件须同步检查 Decision 017；哲学级变更走新 ADR，不静默改路线表。
