# PAAF 架构决策记录（ADR）

> 本文件记录“为什么这样设计”。Accepted 决策如需变更，新增决策覆盖，不改写历史。

---

## Decision 001 — 正式研究使用 TQSDK 离线数据

- **日期**：2026-07-19
- **状态**：Accepted
- **背景**：PAAF 面向中国商品期货，需要分月原始合约、1 分钟数据和可审计换月链路。
- **决策**：冻结 TQSDK Offline / 1m / CbC 自动换月 / 无复权 / 真实手续费与滑点。
- **原因**：接近生产环境；分月与换月可追溯；避免复权连续价格掩盖真实执行跳空。
- **后果**：其它数据只能作为独立实验，不得替代冻结基线。

---

## Decision 002 — PAAF v0.1 不引入 AFF

- **日期**：2026-07-19
- **状态**：Accepted
- **背景**：AFF 来自遗留策略与不同研究阶段，包含 Compression 等尚未在新数据协议下重新验证的假设。
- **决策**：PAAF v0.1 Context 只有 `UNKNOWN / TREND / RANGE`；不迁移 AFF，不把 Compression 当既定市场状态。
- **原因**：Commit 001 只证明框架契约；未经新协议验证的因子不能进入基线。
- **后果**：AFF 或 Compression 以后只能以独立 E0 假设重新立项，不能从旧策略直接继承证据。

---

## Decision 003 — Detector Registry 为唯一发现入口

- **日期**：2026-07-19
- **状态**：Accepted
- **背景**：Strategy 硬编码 Detector 列表会让新增 OPP / ICT / Volume 插件都改编排代码。
- **决策**：使用 `registry.register(...)`；Strategy 只依赖 Registry / SignalEngine。
- **原因**：插件式扩展、启停与版本追溯更清晰。
- **后果**：新增 Detector 只需注册，不得在 Strategy 写 `if OPPxx`。

---

## Decision 004 — Commit 001 采用 DDD 领域模型

- **日期**：2026-07-19
- **状态**：Accepted
- **背景**：`Direction / MarketState / Context / Signal / TradeRecord / DetectorInfo` 是项目通用语言。
- **决策**：使用 `domain.py`；抽象基类为 `base_detector.py / BaseDetector`；指标周期只放 `config.py`。
- **原因**：Domain 保持纯净，不混入 EMA/ATR 定义。
- **后果**：Engine 依赖 Domain；Domain 不依赖 vn.py、Engine 或 Strategy。

---

## Decision 005 — Signal 使用 confidence 预留

- **日期**：2026-07-19
- **状态**：Accepted
- **背景**：未来 Opportunity Score 需要可升级字段，但不能破坏接口。
- **决策**：`Signal.confidence` 默认 `1.0`，范围 `[0, 1]`。
- **原因**：后续替换评分算法无需改字段名。
- **后果**：禁止另起 `score` / `opportunity_score` 平行字段。

---

## Decision 006 — 开发顺序 Domain → Interface → Engine → Strategy → Detector

- **日期**：2026-07-19
- **状态**：Accepted
- **背景**：从 config 或策略细节起步容易返工。
- **决策**：严格按 Domain、Interface、Engine、Strategy、Detector 顺序推进 Commit。
- **原因**：契约稳定后再写实现，减少接口抖动。
- **后果**：Commit 001 不做 OPP16 实装与收益优化。

---

## Decision 007 — vn.py 仅经 Adapter 进入 PAAF

- **日期**：2026-07-19
- **状态**：Accepted
- **背景**：Domain 若直接依赖 `BarData` / `ArrayManager`，换回测引擎或审计边界时会推倒契约。
- **决策**：vn.py 类型只允许出现在 `strategies/paaf/adapters/`；Domain / Detector / Context 契约保持框架无关。
- **原因**：固化边界，便于单测与未来替换执行后端。
- **后果**：新增 vn.py 依赖必须经 Adapter；禁止在 `domain.py` 中 `import vnpy`。

---

## Decision 008 — Feature Layer 延后；不改冻结信号主链

- **日期**：2026-07-19
- **状态**：Accepted
- **背景**：架构审计建议拆出 Feature Engine；冻结主链仍是 Market Data → Context → Detector → Risk → Execution → Logger。
- **决策**：v0.1.0 Foundation 补强不实现 `features/`；Feature Layer 记为 E0 后续假设。
- **原因**：复杂度预算；指标周期已在 `config.py`；Context Engine（v0.1.1）落地前过早拆层无验收价值。
- **后果**：若将来实现 Feature，只作 Context/Risk 计算依赖，不得改写宪章主链或宣称已改变架构。

---

## Decision 009 — Context Engine Spec Accepted（v0.1.1 接口冻结）

- **日期**：2026-07-19
- **状态**：Accepted
- **背景**：v0.1.1 实现前需冻结 Context 对外语言与模块契约，避免算法迭代破坏 Detector。
- **决策**：采纳 `docs/specs/CONTEXT_ENGINE_SPEC.md` v1.0.0。要点：Semantic Layer 非 Feature Layer；`MarketState` 仅一级语义 `UNKNOWN|TREND|RANGE`；`Session` 为 Enum `DAY|NIGHT|UNKNOWN`；方向用 `extras.trend_bias`；`ctx.bar` 延期；`&lt;100μs` 为 Design Target；强制 Contract Test；原则 **Stable API, Replaceable Implementation**。
- **原因**：接口稳定、实现可替换；与 Decision 002/007/008 一致。
- **后果**：Context 接口变更必须先改 Spec；实现阶段严格按 Spec 编码；算法桩可替换且不改 Detector 读法。

---

## Decision 010 — Spec-Driven Development（SDD）自 v0.1.1 起

- **日期**：2026-07-19
- **状态**：Accepted
- **背景**：聊天决策无法长期审计；核心模块需要可回溯契约。
- **决策**：自 v0.1.1 起，核心模块统一流程：`RFC → Architecture Review → Accepted → Implementation → Contract Test → Merge`。模块 Spec 放在 `docs/specs/`。
- **原因**：几年后仍能回答「代码为何如此」；AI Agent 与人类共享同一边界。
- **后果**：Detector Engine / Risk / Opportunity Library 等均先 Spec 后实现；无 Accepted Spec 不得宣称接口已冻结。
