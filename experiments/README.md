# Experiments

PAAF 实验登记入口。研究结论进入证据链前，必须按 [`schema.yaml`](schema.yaml) 登记。

字段对齐：`docs/06_RESEARCH_WORKFLOW.md` §3。

## 规则

1. **一次实验只验证一个主要假设**（`single_variable`）。
2. **无 CSV（或等价可审计输出）→ 不得 KEEP / 不得晋级证据等级**。
3. `decision` 只能是 `KEEP` / `REVERT` / `HOLD`；`KEEP` 不是 Production。
4. **禁止**用 `run_final.py`、`run_final2.py`、`run_xxx_real.py` 这类一次性命名冒充实验登记。

## 建议布局（治理目标，渐进迁移）

```text
experiments/
├── schema.yaml          # 本 schema（冻结字段）
├── README.md
└── EXP-YYYY-NNN/        # 可选：单实验目录（假设、配置、结果指针）
```

历史 `research/run_*.py` 不在本轮 bulk 回填；新实验从本 schema 开始登记。
