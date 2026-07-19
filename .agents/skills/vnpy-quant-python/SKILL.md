---
name: vnpy-quant-python
description: vnpy_quant repo-only Python conventions for scripts/ and shared utilities. Use when editing parquet loaders, diagnose scripts, or non-CTA Python—not for general style (see AGENTS.md) or backtest workflow (see vnpy-cta-backtest).
version: '2.0.0'
---

# vnpy_quant Python 补充规范

本 skill **不重复** 通用工程原则（最小 diff、避免过度抽象、先根因再改代码等）——以 **Cursor 用户规则** 与 **`AGENTS.md`** / **`docs/`** 为准。冲突时：**宪章 / AGENTS.md > docs/* > 本 skill**。

## 何时读本 skill

| 任务 | 应优先使用的文档 |
|------|------------------|
| 策略逻辑、回测、风控 | `AGENTS.md` + `vnpy-cta-backtest` |
| 数据下载、Parquet | **本 skill**（见 §TQ 数据） |
| 回测结果审计 | `quant-backtest-validation-tool` |
| `scripts/`、`configs/`、加载器、诊断脚本 | **本 skill** |

## 运行环境

- 解释器：项目 **`.venv`**（版本以 `.venv/pyvenv.cfg` 为准，当前为 Python 3.13）。
- 命令前缀：

```powershell
.\.venv\Scripts\python.exe scripts\<脚本名>.py
```

- 仓库根目录注入（与策略内回测一致）：

```python
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent  # scripts/ 下文件
# strategies/xxx.py 则为 .parent.parent
import sys
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
```

## 日志与输出

| 位置 | 约定 |
|------|------|
| `strategies/*.py`（`CtaTemplate`） | **禁止** `print()`；用 `self.write_log()`（见 `AGENTS.md` §2） |
| `scripts/*.py` 工具/回测报告 | 可用 `print()` 输出表格与统计；长期维护的脚本优先 `logging` |
| 禁止 | 在策略中留调试 `print` 提交 |

## 类型与风格（仅本仓库补充）

- **新写**的 `scripts/` 模块：推荐类型注解 + `from __future__ import annotations`（与 `backtest_trade_analysis.py` 一致）。
- **既有策略文件**：不要求为旧代码批量补注解；修改时局部保持原风格即可。
- 路径一律 **`pathlib.Path`**，数据/配置路径相对 `ROOT`，勿硬编码用户盘符。
- 密钥：天勤账号 `.env` / 环境变量 **勿提交**；示例用 `.env.example`。

## TQ 数据下载（Parquet）

| 用途 | 路径/命令 |
|------|-----------|
| 分月 1m 下载 | `tools/download_rb_monthly.py -s SHFE.rb -y 2020 2026 --rebuild-continuous` |
| 批量新品种 | `scripts/download_new_symbols_1m.py` |
| 换月表/连续合约 | `tools/build_rollover_map.py -s {prefix}` |
| 数据目录 | `data/tq/{prefix}/`（分月 parquet、rollover_map、rollover_cost_detail） |
| CbC 回测加载 | `scripts/tq_rollover_data.py` |

- 回测母版为 **TQ 分月 Parquet**，不存其它格式副本。
- Phase-1 日频 OI → Phase-2 分月 1m；`dominant_windows.json` 须先于 1m 下载存在。

## 修改边界

- 只改与任务相关的文件；**禁止**顺带大规模格式化无关策略。
- 不新增「一层抽象」除非用户明确要求；工具函数放 `scripts/`，策略逻辑留在 `strategies/`。
- 性能：数据加载/回测瓶颈优先查 Parquet 区间与 `history_data` 规模，勿在未测量前上 async/缓存。

## 与其它 skill 的分工

- 未来函数、成本、乘数、回测可信度 → **quant-backtest-validation-tool**，不在此重复。
- `engine.set_parameters`、`load_bar_data_from_parquet` → **vnpy-cta-backtest**，不在此重复。
