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
