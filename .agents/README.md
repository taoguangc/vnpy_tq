# .agents 目录说明

## 用途

`.agents/` 目录用于存放 AI 助手（Agent）的 Skills，这些 Skills 可以被 **Cursor** 和 **Trae** 同时读取。

## 目录结构

```
.agents/
└── skills/
    ├── vnpy-quant-python/              # scripts/ 等仓库内 Python 补充（非通用规范）
    ├── vnpy-cta-backtest/               # vn.py CTA 回测
    ├── vnpy-rqdata-data-pipeline/       # 数据下载
    └── quant-backtest-validation-tool/  # 回测校验
```

## Skills 列表

| Skill | 用途 | 适用场景 |
|-------|------|---------|
| `vnpy-quant-python` | `scripts/` 路径/日志/venv 约定 | 改加载器、诊断脚本等非 CTA 策略文件 |
| `vnpy-cta-backtest` | vn.py CTA Parquet 回测 | 回测、策略开发 |
| `vnpy-rqdata-data-pipeline` | RQData 数据下载 | 下载历史数据 |
| `quant-backtest-validation-tool` | 回测审计清单 | 结果可疑、零成交、外来教程、未来函数排查 |

**选用顺序**：数据问题 → `vnpy-rqdata-data-pipeline`；跑/改回测 → `vnpy-cta-backtest`；结果审计 → `quant-backtest-validation-tool`；改 `scripts/` 工具 → `vnpy-quant-python`。核心流程见 **`AGENTS.md`**；回测标准/工程细则见 **`AGENTS_DETAIL.md`**（按需）。
