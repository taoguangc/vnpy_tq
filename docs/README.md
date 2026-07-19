# docs/ — PAAF 规范索引

| 文件 | 内容 |
|------|------|
| [01_CONSTITUTION.md](01_CONSTITUTION.md) | 宪章：目标、零假设、复杂度预算 |
| [02_ARCHITECTURE.md](02_ARCHITECTURE.md) | 分层与目录约束 |
| [03_DETECTOR_SPEC.md](03_DETECTOR_SPEC.md) | 检测器契约与生命周期 |
| [04_BACKTEST_SPEC.md](04_BACKTEST_SPEC.md) | 回测验收指标与报告 |
| [05_CODING_STYLE.md](05_CODING_STYLE.md) | Python / vn.py 编码 |
| [06_RESEARCH_WORKFLOW.md](06_RESEARCH_WORKFLOW.md) | 单假设实验、证据晋级与 Commit 门禁 |
| [07_DATA_SPEC.md](07_DATA_SPEC.md) | 冻结数据、换月与成本 |
| [ROADMAP.md](ROADMAP.md) | 阶段目标（可变） |
| [specs/CONTEXT_ENGINE_SPEC.md](specs/CONTEXT_ENGINE_SPEC.md) | Context Engine Spec（v0.1.1 接口；**Accepted**） |
| [specs/DETECTOR_FRAMEWORK_SPEC.md](specs/DETECTOR_FRAMEWORK_SPEC.md) | Detector Framework Spec（v0.2；**Accepted**） |
| [specs/FEATURE_SENSOR_SPEC.md](specs/FEATURE_SENSOR_SPEC.md) | Feature Sensor Architecture（v0.3；**Accepted**） |
| [specs/EVIDENCE_ENGINE_SPEC.md](specs/EVIDENCE_ENGINE_SPEC.md) | Evidence Engine（v0.3；**Accepted**） |
| [specs/EVIDENCE_ENGINE_IMPL_RFC.md](specs/EVIDENCE_ENGINE_IMPL_RFC.md) | Evidence Engine Phase 0 实现切片（**Accepted**） |
| [specs/EXPERIMENT_WORKFLOW_IMPL_RFC.md](specs/EXPERIMENT_WORKFLOW_IMPL_RFC.md) | Experiment Workflow Phase 1 实现切片（**Accepted**） |
| [specs/EVIDENCE_EVALUATION_IMPL_RFC.md](specs/EVIDENCE_EVALUATION_IMPL_RFC.md) | Evidence Evaluation Phase 2 实现切片（**Accepted**） |
| [specs/EVALUATION_REPOSITORY_INTEGRATION_RFC.md](specs/EVALUATION_REPOSITORY_INTEGRATION_RFC.md) | Evaluation Persistence Phase 2.1（**Accepted**） |

AI 每轮操作契约在 [`AGENTS.md`](../AGENTS.md)，总设计书在 [`PAAF_PROJECT_SPEC.md`](../PAAF_PROJECT_SPEC.md)，架构决策见 [`DECISIONS.md`](../DECISIONS.md)。

模块级 RFC 放在 `docs/specs/`：**先改 Spec，再改对应实现。**
