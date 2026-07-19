# PAAF 路线图

> 版本：3.0.0 · 更新日期：2026-07-19  
> 路线图**可变**；宪章与规格冻结后，改路线图不等于改哲学。

---

## Sprint 计划

### Sprint 1 — Framework（当前）

目标：**框架跑通，不关心收益。**

| 交付物 | 状态 |
|--------|------|
| `AGENTS.md` / `docs/` / `PAAF_PROJECT_SPEC.md` | 完成 |
| `domain.py` / `config.py` / `base_detector.py` / `registry.py` | 完成（Commit 001） |
| `paaf_strategy.py` + Engine 接口 | 完成（Commit 001 骨架） |
| Engine 可导入骨架 | 完成（Commit 001） |
| Foundation 补强：`adapters/vnpy_adapter.py` + `experiments/schema.yaml` | 完成（Commit 001.x，仍属 0.1.0） |
| Context Engine Spec（`docs/specs/CONTEXT_ENGINE_SPEC.md`） | **Accepted**（Decision 009） |
| Spec-Driven Development | **Accepted**（Decision 010） |
| Context Engine：Domain / Lifecycle / Contract Tests | **完成**（Commit 002 / 003 / 004）→ Tag `v0.1.1` |
| CSV Logger | 待做 |
| `PAAFStrategy` + vn.py 可加载 | 待做 |
| OPP16 Detector | 待做 |

#### PAAF v0.1.1 里程碑（Context Framework）

```text
PAAF v0.1.1

✓ Context API Frozen
✓ Context Lifecycle Frozen
✓ Context Contract Frozen

Market State
  Not Implemented
```

Detector 可基于冻结 Context 契约开发；Market State 另立项、证据驱动，不与 Framework 混写。

验收：

```text
vn.py BacktestingEngine → PAAFStrategy → 产生交易 → 输出 CSV
```

### Sprint 2 — Core Detector

OPP16 / OPP01 / OPP02 / OPP04 / OPP09；统一输出 Trade / WR / PF / Expectancy / MAE / MFE。

### Sprint 3 — Research

按 Context / 品种 / 时段做真正研究；积累可追溯证据链，形成 Price Action 知识库。

---

## Release

| 版本 | 含义 |
|------|------|
| v0.1.0 | Framework |
| v0.1.1 | Context Engine |
| v0.1.2 | Logger |
| v0.2.0 | 5 Core Detector |

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

- `main`：永远可运行
- 开发：`feature/context-engine`、`feature/opp16`、`feature/logger` …
- 完成：Merge 回 `main`

---

## 明确不做（在论证通过前）

- 机器学习 / 深度学习信号
- 无约束参数搜索与自动「优化到年化」
- 为证明 Brooks 正确而扭曲数据或成本
- 大爆炸式重写整个 `strategies/` 树
- 将 Feature Engine 插入冻结信号主链（见下）

## 后续项（未立项实现）

| 项 | 状态 | 说明 |
|----|------|------|
| Feature Layer（ATR/EMA/ADX 等） | E0 假设 | 若实现，只作 Context/Risk 的计算依赖；**不得**改主链为 Market→Feature→Context |
| `research/run_*.py` 三层治理 | 待治理专项 | experiments / validation / reports；不与 Foundation 补强捆绑 |

---

## 变更方式

更新本文件时：改「更新日期」，在 `CHANGELOG.md` 记一条；**不**悄悄改宪章条款。
