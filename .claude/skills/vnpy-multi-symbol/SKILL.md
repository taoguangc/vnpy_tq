---
name: vnpy-multi-symbol
description: Run Brooks PA strategy across multiple futures symbols for generalization testing. Use for multi-symbol scans, cross-species parameter validation, or finding which symbols profit from the strategy.
version: '1.0.0'
---

# vnpy-multi-symbol 多品种泛化回测

## 触发场景

- "跑多品种回测"、"全品种扫描"、"策略泛化测试"
- "跨品种对比"、"哪些品种赚钱"、"换个品种试试"
- 新增 OPP 后验证跨品种表现

## 执行方式

```bash
python scripts/multi_symbol_scan.py
```

脚本位于 `scripts/multi_symbol_scan.py`，向 `SYMBOL_PROFILES` 动态注入 19 个品种的通用配置后批量回测。

## 输出格式

单张汇总表，按 PnL/Sharpe 聚类分三档：

| 档位 | 判定条件 | 含义 |
|------|---------|------|
| PROFIT | PnL > 3000 + Sharpe > 0.8 | 可直接使用 |
| MARGINAL | PnL > 0 | 需要调参 |
| LOSS | PnL < 0 | 不适合当前参数 |

## 通用配置说明

- `rb_min_atr = max(3, tick × 5)` — 按品种最小变动价位缩放
- `slippage = max(1, min(2, int(tick)))` — 按品种流动性估算
- `risk_capital = 10,000`、`risk_pct_per_trade = 0.05` — 统一风险金

## 注意事项

- 通用配置**不含** rb888 的调参结果（disabled_setups、atr_regime 等），因此 rb888 在扫描中可能出现 LOSS。
- 品种若交易笔数为 0，通常是因为 `rb_min_atr` 过高拦掉了所有信号。
- 扫描耗时约 8–10 分钟（19 品种），使用 `run_in_background` 避免阻塞会话。
- 扫描结果写入 `backtests/multi_symbol_scan.json`。
