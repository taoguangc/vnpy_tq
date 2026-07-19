# 稳定 Alpha 研究协议（ALPHA_PROTOCOL_V1）

> 本文件为计划落地文档；**不要**把开发窗结果标为「稳定 alpha」或 `CONFIRMED_ALPHA`。  
> 服从 `docs/01_CONSTITUTION.md` 零假设与 `docs/06_RESEARCH_WORKFLOW.md` 晋级门禁。

## 1. 不可变冻结项

| 项 | 值 |
|----|-----|
| 版本 | `ALPHA_PROTOCOL_V1` |
| 开发窗 | 2021-07-01 → 2026-06-30 |
| 品种池 | `i, jm, p, y, ag, rb, hc, ta` |
| OPP 候选库 | OPP02 / 08 / 12 / 13 / 15 / 16 / 17 / 19（阈值冻结） |
| 成本 | 品种 profile 滑点 tick + `rate=0.00003`；经济边际按 **1 手** |
| 主退出视野 | 40 根 1m；辅 10/20/80；折间 embargo=80 分钟 |
| Forward holdout | **2026-07-01 起**（未见数据） |

指纹写入：`research/output/alpha_discovery/alpha_protocol_manifest.json`  
（`opp_code_fingerprint` / `param_fingerprint` / 各 detector 文件 hash）。

## 2. 路由审计结论（阶段 0）

已证实（代码路径）：

1. **OPP13** `day_high` 首次触达（`FIRST_TEST`）在 live 路径返回 `True`，会**提前结束**同 bar 其他 OPP 扫描；shadow 模式不提前返回。
2. **OPP19** `_process_opening_drive` 在调用 `_arm_fast_track` 后**恒返回 True**，即使门禁未过（arm 内部失败）；shadow 通过 `alpha_shadow_mode` 拦截 `_try_production_arm` / `_try_opp15_direct_entry`。
3. **OPP15 / OPP13** 状态推进与 `detectors/*` 并存：状态机负责武装副作用，检测器负责只读命中记账。
4. **DIRECT**（OPP15 B'）与 `FAST_TRACK` / `PENDING_CONFIRM` 成交语义不同；shadow 用 `_shadow_entry_price` / trigger 估计入场价。
5. 信号在 5m 产生，候选 forward 自信号时刻**下一根 1m**起算；不把组合路径依赖当成形态 alpha。

本阶段**不改**任何形态阈值；仅增加 `alpha_shadow_mode` 与账本字段。

## 3. 标签三档（禁止第四档「稳定」）

| 标签 | 含义 |
|------|------|
| `REJECT` | 未过时间/品种/集中度门禁 |
| `PROVISIONAL` | 部分通过；开发窗暂定，**不是**稳定 alpha |
| `PROMOTE_TO_CTA` | 可进入 1 手 CTA 含成本验证 |

## 4. PROVISIONAL → CONFIRMED_ALPHA

| 条件 | 要求 |
|------|------|
| 数据 | 仅使用 **≥ 2026-05-17** 的新行情（forward holdout） |
| 样本量 | 累计 OOS round-trip **≥ 30** |
| 时间覆盖 | 至少 **6 个自然月** |
| 前置 | 该 OPP 已分别通过候选门禁 + CTA KEEP（含成本 OOS PnL>0、PF≥1.15、RT≥30，时间/品种不反转） |
| 禁止 | 用 2025–2026 开发窗「再优化」后回填 CONFIRMED |

晋级记录模板（追加 `research/experiments.md`）：

```
| 日期 | pa_minimal | multi | EXP-ALPHA-CONFIRM | {OPP} dir={±1} holdout≥2026-05-17 | … | CONFIRMED_ALPHA / FAIL |
```

## 5. 运行入口

```powershell
Set-Location C:\projects\vnpy_tq
$env:PYTHONIOENCODING='utf-8'
.\.venv\Scripts\python.exe -m research.run_pa_minimal_alpha_discovery
.\.venv\Scripts\python.exe -m research.run_pa_minimal_alpha_promote
```

产出目录：`research/output/alpha_discovery/`。
