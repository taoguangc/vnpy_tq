# Research Directory Policy

> **Status**: Accepted（governance；Decision 017）
> **Updated**: 2026-07-20
> **Rule priority**: `AGENTS.md` > Decision 017 > 本文件

本目录存放研究脚本、遗留实验与分析工具。  
**它不是** Active PAAF 实验的权威登记处。权威实验身份在 `docs/experiments/`，证据产物在
`research/output/`（通常 gitignore）。

---

## Archived Research

下列研究线视为 **ARCHIVED**（来自 AFF 迁移与历史优化阶段）：

| 模式 / 区域 | Origin | Status |
|-------------|--------|--------|
| `run_pa_minimal_*.py` 及同类 pa_minimal 研究脚本 | AFF / pa_minimal | **ARCHIVED** |
| `pa_cta` / `brooks_scalp` / 历史 CTA 研究入口（若仍出现在本树或 git 历史） | AFF migration | **ARCHIVED** |
| 无 `experiment_id`、无 Evidence 输出的一次性 `run_*.py` 优化脚本 | historical | **ARCHIVED** |
| 旧 `ALPHA_PROTOCOL` / 未挂 Decision 017 的研究备忘 | pre-PAAF | **ARCHIVED** |

### Rules（强制）

```text
Do not extend.
Do not create new experiments from these scripts.
Do not treat Archived scripts as Active Research.
Do not optimize them to chase backtest PnL.
```

需要延续某条历史假设时：

1. 新开 `docs/experiments/<NEW_ID>.md` + Spec（新 `experiment_id`）；
2. 可选声明 `parent = <旧实验或旧标签>`；
3. 在 PAAF `strategies/paaf/` + Evidence Domain 路径上重做；
4. 服从 Decision 017（append-only；Closed 不可原地复活）。

**本轮不移动文件**：避免巨大 diff。语义治理优先于物理搬家。日后若整理为
`research/archive/`，须另授权且保持 git 历史可追溯。

---

## Active Research

Active 研究必须同时满足：

1. 有稳定 **`experiment_id`**
2. 有可审计 **Evidence** 输出（或等价 Artifact → Evaluation → Evidence）
3. 在 **`docs/experiments/`** 登记（Run Spec / Index）
4. 服从 **Decision 017** 与 `docs/specs/EVIDENCE_DOMAIN_SPEC.md`
5. 正式数据协议默认 **Decision 001**（偏离须标独立数据实验）

推荐入口：

| 用途 | 位置 |
|------|------|
| 实验 Run Spec / Index | `docs/experiments/` |
| Domain / Engine Spec | `docs/specs/` |
| PAAF 实现 | `strategies/paaf/` |
| 授权 runners | `scripts/run_*_exp*.py`、`scripts/paaf_*.py` |
| 本地证据产物 | `research/output/`（勿提交大产物） |

AI Agent / 协作者：**优先**读 `docs/experiments/` 与 `DECISIONS.md`；**不要**把 Archived
`pa_minimal` 脚本当作当前研究主线。

---

## Portfolio 提示（概念）

Decision 017 Research Portfolio 五桶：

```text
DATA | FEATURE | PATTERN | DETECTOR | EXECUTION
```

归档脚本通常不属于 Active Portfolio 计数；Closed 实验的 Evidence 仍按 Portfolio 归档统计
（含 Negative / Inconclusive）。

---

## 修订记录

| 日期 | 说明 |
|------|------|
| 2026-07-20 | 首版：Archived vs Active 语义治理；不移动文件 |
