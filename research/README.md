# Research Directory Policy

> **Status**: Accepted（governance；Decision 017）  
> **Updated**: 2026-07-20  
> **Rule priority**: `AGENTS.md` > Decision 017 > 本文件

本目录存放研究治理说明与**本地**证据产物。  
**它不是** Active PAAF 实验的权威登记处。权威实验身份在 `docs/experiments/`。

---

## Layout（当前树）

```text
research/
├── README.md          # 本文件
├── __init__.py
└── output/            # 本地 Evidence 产物（gitignore；勿提交大文件）
    └── evidence/<experiment_id>/
```

AFF / `pa_minimal` / `pa_cta` / `event_engine` / 历史 `run_*.py` 等 **Archived 源码已从工作树移除**（仍可在 git 历史检索）。  
**禁止**从历史提交复活为 Active Research。

---

## Archived Research（语义仍有效）

| 模式 / 区域 | Origin | Status |
|-------------|--------|--------|
| `run_pa_minimal_*.py` 及同类 | AFF / pa_minimal | **ARCHIVED**（源码已移除） |
| `pa_cta` / `brooks_scalp` / 历史 CTA | AFF migration | **ARCHIVED**（源码已移除） |
| `research/event_engine/` | historical | **ARCHIVED**（源码已移除） |
| 无 `experiment_id`、无 Evidence 的一次性优化脚本 | historical | **ARCHIVED** |

### Rules（强制）

```text
Do not extend.
Do not create new experiments from archived history.
Do not treat Archived scripts as Active Research.
Do not optimize them to chase backtest PnL.
Do not delete research/output/evidence/ — Negative Evidence is first-class.
```

需要延续某条历史假设时：

1. 新开 `docs/experiments/<NEW_ID>.md` + Spec（新 `experiment_id`）；
2. 可选声明 `parent = <旧实验或旧标签>`；
3. 在 PAAF `strategies/paaf/` + Evidence Domain 路径上重做；
4. 服从 Decision 017（append-only；Closed 不可原地复活）。

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
| 本地证据产物 | `research/output/evidence/`（勿提交大产物） |

AI Agent / 协作者：**优先**读 `docs/research/PAAF_RESEARCH_METHOD.md`（PRM）、`docs/experiments/` 与 `DECISIONS.md`。

---

## 修订记录

| 日期 | 说明 |
|------|------|
| 2026-07-20 | 首版：Archived vs Active 语义治理 |
| 2026-07-20 | 清理：移除 Archived 源码与 `__pycache__`；保留 `output/evidence/` |
