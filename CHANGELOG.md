# Changelog

本文件记录 **PAAF / vnpy_tq** 对用户可见的规范与重要行为变更。  
研究实验明细仍以 `research/experiments.md` 为准，不在此逐条重复。

格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。  
版本策略：规范冻结与破坏性约定用 MAJOR；文档补强用 MINOR；笔误用 PATCH。

---

## [Unreleased]

### Docs（Spec Accepted — 未授权 ATR 实现）

- Phase 0 Evidence Foundation + Phase 1 Experiment Workflow：**已实现**
- `EVIDENCE_EVALUATION_IMPL_RFC.md` v1.0.0：**Accepted** — EQ1–EQ6 关闭
- 当前切片：`feat(paaf): add evaluation models`
- 仍禁止：ATR Sensor、FeaturePipeline、Promotion Automation；禁止用 ATR 反向塑形 Evaluation

---

## [0.2.4] — 2026-07-19

### Added（Commit 011 — Detector Pipeline Verification）

- `DetectorPipeline`：Context → Descriptor Factory → DetectionResult → Opportunity → Logger
- `DEMO_MINIMAL`：仅 `close > open`，状态 `EXPERIMENT`，无 Alpha 声明
- `OpportunityLogger`：最小 JSONL Opportunity 消费与审计
- Decision 014：**Framework First, Alpha Later**

### Added（Commit 012 — Pipeline Tests）

- `tests/test_paaf_detector_pipeline.py`：七步 Pipeline、空结果、Capability Gate 与契约失败测试

### Notes

- 不含 Risk / Execution / Market State / OPP
- Demo 是 Pipeline 载体，不进入 Production

---

## [0.2.3] — 2026-07-19

### Added（Commit 009 — Detector Catalog Registry）

- `DetectorDescriptor`：不可变目录项，按 factory 延迟实例化
- `DetectorCapability`：requires / produces / states / directions / timeframe
- Registry 核心 API：`register / unregister / get / list / find / exists`
- 唯一键 `(detector_id, detector_version)`；多版本可共存
- Deprecated 默认可见；Capability 子集查询

### Added（Commit 010 — Registry Tests）

- `tests/test_paaf_registry.py`：复合键、多版本、查询、不可变、Deprecated 与 factory Contract

### Notes

- Registry 只存 Descriptor，不存 Detector 实例
- v0.2 暂留旧实例注册与迭代兼容层；v0.3 删除
- Demo / OPP / Risk / Execution 不在本版本实现

---

## [0.2.2] — 2026-07-19

### Added（Commit 007 — Opportunity Domain）

- `Opportunity`：引用 `DetectionResult` 的不可变机会描述对象
- `OpportunityDirection`：`LONG / SHORT / BOTH / UNKNOWN`
- `lineage`：`DET:<id>@<version>` 与 `EXP:<experiment_id>` 血缘
- schema `1.0`、UTC `created_at`、深度只读 `metadata`
- `to_dict()` / `from_dict()` JSON 友好往返

### Added（Commit 008 — Opportunity Tests）

- `tests/test_paaf_opportunity.py`：引用一致性、血缘、不可变、序列化与证据门禁

### Notes

- Opportunity 不是订单；状态变化产生新对象
- Registry / Demo Detector 不在本版本实现

---

## [0.2.1] — 2026-07-19

### Added（Commit 005 — DetectionResult Domain）

- `DetectionResult`：不可变、可追踪的 Detector 唯一输出契约
- `PatternState`：独立、不可变、可序列化的显式形态状态
- `DetectorTag`：标准小枚举 + `custom:<slug>` 扩展
- `DetectorStatus`：`EXPERIMENT / VALIDATED / PRODUCTION / DEPRECATED`
- `to_dict()` / `from_dict()`：schema `1.0` JSON 友好往返
- `schema_version` / UTC `created_at` / `opportunity_id` / `evidence_refs`

### Deprecated

- `Signal`：v0.2 迁移期保留；新 Detector 禁止依赖；v0.3 删除

### Added（Commit 006 — DetectionResult Tests）

- `tests/test_paaf_detection_result.py`：Immutable / Serialization / Schema Version / Evidence Gate Contract Tests

### Notes

- tags 只作分类、检索和统计，不参与业务逻辑
- Registry / Opportunity / Capability / Demo Detector 不在本版本实现

---

## [0.1.1] — 2026-07-19

### Added（Commit 002 — Domain + Spec freeze）

- `docs/specs/CONTEXT_ENGINE_SPEC.md` v1.0.0：**Accepted**（接口与契约冻结；算法不冻结）
- Decision 009：Context Engine Spec Accepted
- Decision 010：Spec-Driven Development（RFC → Review → Accepted → Implementation → Contract Test → Merge）
- Domain：`Session`（`DAY` / `NIGHT` / `UNKNOWN`）
- Domain：扩展 `Context`（`symbol` / `datetime` / `session` / `market_state` / `extras`）
- Domain：`extras` 发布后为 `MappingProxyType`（只读）
- Domain：文档化 extras 键 `trend_bias` / `state_confidence` / `compression_score`

### Added（Commit 003 — ContextEngine lifecycle）

- `ContextEngine`：`update` / `freeze` / `publish` / `get_context` / `reset`
- 生命周期：`update → freeze → publish → readonly`
- **无** Market State 算法：发布后 `market_state` 恒为 `UNKNOWN`（Context Framework only）
- `framework_version` → `0.1.1`

### Added（Commit 004 — Contract / Lifecycle tests）

- `tests/test_paaf_context.py`：Domain 纯度、生命周期、只读契约、Detector 不可写 Context
- ROADMAP：v0.1.1 里程碑（API / Lifecycle / Contract Frozen；Market State Not Implemented）

### Notes

- **Stable API, Replaceable Implementation**；Context 是 Semantic Layer，不是 Feature Layer
- v0.1.1 基线 `MarketState` 仍为 `UNKNOWN` / `TREND` / `RANGE`；**Market State Not Implemented**
- 下一阶段：v0.2 Detector Framework（建立在已冻结 Context 契约之上）

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

- 本版本建立可运行契约；vn.py `CtaTemplate` 接入与 OPP16 实装分别在后续 Commit
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
