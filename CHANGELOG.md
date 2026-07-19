# Changelog

本文件记录 **PAAF / vnpy_tq** 对用户可见的规范与重要行为变更。  
研究实验明细仍以 `research/experiments.md` 为准，不在此逐条重复。

格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。  
版本策略：规范冻结与破坏性约定用 MAJOR；文档补强用 MINOR；笔误用 PATCH。

---

## [0.1.0] — 2026-07-19

### Added（Sprint 1 / Commit 001）

- `strategies/paaf/domain.py`：纯 Domain（Direction / MarketState / Context / Signal / TradeRecord / DetectorInfo）
- `strategies/paaf/metadata.py`：Detector 元数据
- `strategies/paaf/config.py`：EMA / ATR / ADX / Risk / TickSize
- `strategies/paaf/base_detector.py`：`detect(am, context) -> Signal | None`
- `strategies/paaf/registry.py`：插件式注册
- `strategies/paaf/paaf_strategy.py`：编排骨架
- `strategies/paaf/engines/`：Context / Signal / Risk / Execution / Logger
- `DECISIONS.md`：架构决策记录
- `tests/test_paaf_foundation.py`

### Added（Sprint 1 / Commit 001.x Architecture Foundation 补强）

- `strategies/paaf/adapters/vnpy_adapter.py`：vn.py `BarData` / 行情窗口 → `PaafBar` 边界适配
- `experiments/schema.yaml`：与 `docs/06_RESEARCH_WORKFLOW.md` 对齐的可机读实验登记 schema
- `experiments/README.md`：实验登记规则
- `tests/test_paaf_adapter.py`
- Decision 007 / 008：Adapter 边界；Feature Layer 延后且不改信号主链

### Notes

- 本版本建立可运行契约；vn.py `CtaTemplate` 接入与 OPP16 实装分别在 Commit 002 / 003
- **正式 v0.1.1 仍留给 Context Engine**（本补强不发 0.1.1 版本号）
- v0.1 Context 只有 UNKNOWN / TREND / RANGE；Compression 作为 E0 假设保留
- `Signal.confidence` 默认 1.0，预留 Opportunity Score
- Feature Layer 未实现；见 ROADMAP「后续项」

---

## [3.0.0] — 2026-07-19

### 规范冻结（Frozen）

- 新增唯一总设计书 `PAAF_PROJECT_SPEC.md`
- 文档编号冻结为：
  - `01_CONSTITUTION`
  - `02_ARCHITECTURE`
  - `03_DETECTOR_SPEC`
  - `04_BACKTEST_SPEC`
  - `05_CODING_STYLE`
  - `06_RESEARCH_WORKFLOW`
  - `07_DATA_SPEC`
- 新增 Detector Registry 目标架构与 `strategies/paaf/` 目录骨架
- 新增 E0–E4 证据等级、统一 Logger 字段、统一回测验收指标
- 新增「不追逐利润」硬规则
- Detector 契约升级为不可变输入 + 显式 `PatternState`，禁止访问持仓或修改 Strategy
- 新增 Cursor 常驻规则 `.cursor/rules/paaf-core.mdc`

### Clarified

- 规范描述的是目标架构；现有 `pa_minimal` / `pa_cta` 尚未完全满足纯函数与 Registry 契约
- 单次 `PF < 1` / `Expectancy < 0` 只触发退出生产与复核；连续独立负证据且样本达标才永久 Deprecated

---

## [2.0.0] — 2026-07-19

### 规范冻结（Added）

- 建立顶层文档体系：
  - `AGENTS.md` v2（PAAF AI 开发指南）
  - v2 时代的 `docs/01`–`06` 文档组（已由 v3 编号体系取代）
  - `docs/ROADMAP.md`
  - `CHANGELOG.md`、`LICENSE`
- 明确项目一句话目标、零假设、复杂度预算、检测器生命周期、无 CSV 不 Commit 结论门禁
- 原分散在对话 / 缺失 `AGENTS_DETAIL.md` 中的细则并入 `docs/05`、`docs/06`

### Changed

- `README.md` 改为以 PAAF 研究平台为中心，并链到规范文档
- `CLAUDE.md` 指向新文档地图，保留每轮硬约束（配额、OPP、临时文件）

---

## [1.x] — 2026-07 及更早

历史以 git 提交与 `research/experiments.md` 为准（`AGENTS.md` 曾用 1.7.x 协作规则）。  
自 2.0.0 起，AI 契约以本 Changelog 与 `docs/` 为准。
