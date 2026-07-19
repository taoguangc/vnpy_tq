# PAAF

**Price Action Alpha Framework**

## Mission

用接近生产环境的中国商品期货数据，发现、验证并积累具有统计意义的价格行为 Alpha。

PAAF 是可复现、可解释、可审计的量化研究平台，不是单一交易策略。

## Architecture

```text
Market Data → Context → Detector Registry → Risk → Execution → Logger
```

当前主路径：天勤离线 1 分钟数据、CbC 自动换月、无复权、真实手续费与滑点。

## 当前 Sprint

**Sprint 1 — Framework**：框架跑通（不关心收益）。  
地基：`strategies/paaf/{domain,metadata,base_detector,registry,paaf_strategy}.py`。
下一步：Context Engine → Logger → PAAFStrategy → OPP16。

详见 [`docs/ROADMAP.md`](docs/ROADMAP.md)。

---

## 先读规范（所有贡献者与 AI）

| 文档 | 作用 |
|------|------|
| [`AGENTS.md`](AGENTS.md) | AI 开发契约（必读） |
| [`PAAF_PROJECT_SPEC.md`](PAAF_PROJECT_SPEC.md) | 项目唯一总设计书 |
| [`docs/01_CONSTITUTION.md`](docs/01_CONSTITUTION.md) | 项目宪章 |
| [`docs/02_ARCHITECTURE.md`](docs/02_ARCHITECTURE.md) | 架构与目录边界 |
| [`docs/03_DETECTOR_SPEC.md`](docs/03_DETECTOR_SPEC.md) | 检测器规格与生命周期 |
| [`docs/04_BACKTEST_SPEC.md`](docs/04_BACKTEST_SPEC.md) | 回测与验收指标 |
| [`docs/05_CODING_STYLE.md`](docs/05_CODING_STYLE.md) | 编码风格 |
| [`docs/06_RESEARCH_WORKFLOW.md`](docs/06_RESEARCH_WORKFLOW.md) | 研究流程与证据晋级 |
| [`docs/07_DATA_SPEC.md`](docs/07_DATA_SPEC.md) | 冻结数据规范 |
| [`docs/ROADMAP.md`](docs/ROADMAP.md) | 路线图 |
| [`CHANGELOG.md`](CHANGELOG.md) | 变更记录 |
| [`DECISIONS.md`](DECISIONS.md) | 架构决策记录 |
| [`program_trading.md`](program_trading.md) | 自治实验编排 |

---

## 目录结构（摘要）

```text
data/tq/{prefix}/     天勤离线分月 1m + 换月表
strategies/           CTA 策略；paaf/ 为冻结目标架构
research/             实验脚本、协议、输出 CSV
scripts/              回测加载、扫描、单文件构建
tools/                数据下载与质量审计
tests/                单元测试
docs/                 PAAF 规范文档
```

更细的数据文件说明见下文「数据与回测」。

---

## 环境准备

默认使用仓库根目录 **`.venv`**。

```powershell
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
copy .env.example .env
# 编辑 .env，填入 TQ_USER / TQ_PASSWORD
```

```powershell
python -c "import vnpy, vnpy_ctastrategy, tqsdk; print('ok')"
```

---

## 数据与回测（三步走）

### 1. 下载分月合约（原始无复权）

```powershell
.venv\Scripts\python.exe tools\download_rb_monthly.py -s SHFE.rb -y 2021 2026
```

落盘：`data/tq/{prefix}/`。两阶段下载会生成 `rollover_map.parquet`。

### 2. 换月映射（全量模式或补图）

```powershell
.venv\Scripts\python.exe tools\build_rollover_map.py -s rb --map-only
```

完整构建（去掉 `--map-only`）可生成移仓成本明细；行情本身不做复权。

### 3. 跑回测

```powershell
Set-Location C:\projects\vnpy_tq
$env:PYTHONIOENCODING='utf-8'
.venv\Scripts\python.exe scripts\run_backtest.py --prefix rb --start 2023-07-01 --end 2026-06-30
```

PA 最小集 / 研究臂请用 `strategies/pa_minimal/` 与 `research/run_pa_minimal_*.py`（见 `docs/04`、`docs/07` 与 skill `vnpy-cta-backtest`）。

---

## 关于数据口径

- **下载**：分月原始合约，非天勤 `KQ.m@` 后复权主连
- **回测主路径（CbC）**：分月 raw + `rollover_map` 拼接，**无复权**
- **成本**：手续费、滑点；换月成本须按数据/引擎/触发分层验证（见 `docs/07_DATA_SPEC.md`）

---

## 许可证

见 [`LICENSE`](LICENSE)。
