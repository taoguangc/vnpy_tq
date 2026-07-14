---
name: vnpy-multi-symbol
description: Run Brooks PA strategy across multiple futures symbols for generalization testing. Use for multi-symbol scans, cross-species parameter validation, or finding which symbols profit from the strategy.
version: '1.1.0'
---

# vnpy-multi-symbol 多品种泛化回测

## 触发场景

- "跑多品种回测"、"全品种扫描"、"策略泛化测试"
- "跨品种对比"、"哪些品种赚钱"、"换个品种试试"
- 新增 OPP 后验证跨品种表现

## 固定品种池

跨品种研究统一使用 `strategies/pa_cta/symbol_config.py` 中的 **`CROSS_SYMBOL_UNIVERSE`**：

`i`, `jm`, `p`, `y`, `ag`, `rb`, `hc`, `ta`（8 品种）

脚本内通过 `cross_symbol_list()` 读取（仅返回已在 `TQ_SYMBOL_ENGINE` 中配置的品种）。

## 执行方式

```bash
python scripts/multi_symbol_scan.py
python scripts/multi_symbol_scan.py --symbols i,jm,p,y,ag,rb,hc,ta
```

脚本位于 `scripts/multi_symbol_scan.py`，向无 `SYMBOL_PROFILES` 的品种注入 rb lean 模板 + `TQ_SYMBOL_PARAM_OVERRIDES` 后批量回测。

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

- 通用配置**不含** rb888 的调参结果（disabled_setups、atr_regime 等），因此 rb 在扫描中可能出现 LOSS。
- 品种若交易笔数为 0，通常是因为 `rb_min_atr` 过高拦掉了所有信号。
- 8 品种扫描约 3–5 分钟；≥10 品种使用 `run_in_background` 避免阻塞会话。
- 扫描结果写入 `backtests/multi_symbol_scan.json`。
