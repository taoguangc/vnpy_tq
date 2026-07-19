# 数据规范（Data Spec）

> 版本：1.0.0 · 冻结日：2026-07-19  
> 本文件定义正式研究的冻结数据基线。

---

## 1. 冻结基线

| 项 | 冻结值 |
|----|--------|
| Source | 天勤 TQSDK Offline Data |
| Bar | 1 Minute |
| Continuous | Auto Roll（CbC 自动换月） |
| Price | Unadjusted（无复权） |
| Commission | Real（真实手续费） |
| Slippage | Real（真实滑点） |

未经用户明确批准，任何 AI 不得把复权连续、其它数据源、零成本或更短区间替代为正式基线。

偏离只能作为**独立数据实验**，必须：

- 明确实验 ID；
- 与冻结基线并列；
- 标注不可直接比较的部分；
- 不覆盖生产 profile 或历史结论。

---

## 2. 文件与主链路

```text
data/tq/{prefix}/
├── {prefix}_{yymm}.parquet
├── rollover_map.parquet
├── rollover_cost_detail.parquet   # 完整构建时
├── dominant_windows.json
├── manifest.json
└── oi_daily/
```

主链路：

```text
分月原始合约 → rollover_map → CbC 1m Bar 流 → 回测引擎
```

不生成或依赖后复权主连作为正式研究输入。

---

## 3. 无复权与换月

- 分月 OHLCV 保持交易所原始价格；
- 换月边界保留真实价差；
- Detector / Context 必须意识到换月跳空可能产生假信号；
- 不得用未来主力合约信息回填过去；
- 合约切换规则与 map 版本必须可追溯。

---

## 4. 成本验证分层

| 层级 | 验证 |
|------|------|
| 数据层 | `rollover_map` 与成本明细存在且字段非空 |
| 引擎层 | 换月滑点 / 手续费按手数与乘数计入 |
| 触发层 | 切点有持仓并实际产生换月成交 |

仅有成本文件不等于回测已计成本；PnL 不变也不等于成本数据失败。

---

## 5. 数据质量门禁

正式实验前至少检查：

- datetime 单调、无重复；
- 交易时段内无大面积缺口；
- OHLC 关系合法；
- volume / open_interest 类型与缺失值合理；
- 合约规格、tick、乘数与交易所一致；
- 起止区间落在实际数据范围；
- manifest / rollover map 与数据版本匹配。

数据质量失败时停止研究结论，先修数据链路。

---

## 6. 时间与会话

- 统一时区与交易日口径；
- 中国期货夜盘跨自然日但属于相应交易日；
- Context 与 Detector 的 session key 必须使用同一规则；
- 合成 5m / 15m / 60m Bar 只能在周期收盘后发布；
- 禁止把未完成大周期 Bar 用于当前决策。

---

## 7. 数据版本与指纹

每次正式实验应记录：

- 数据协议版本；
- 品种与区间；
- manifest hash；
- rollover map hash；
- 合约规格版本；
- 缺失 / 修复说明。

数据被修复后，旧实验不自动失效，但必须保留旧数据指纹并标注不可直接复现的风险。

---

## 8. 禁止事项

- 未来函数与 look-ahead；
- 后复权价格替换冻结基线；
- 零成本结果冒充正式结果；
- 只下载或保留盈利品种；
- 为提高回测收益修改换月点；
- 未披露的数据清洗；
- 把 Parquet、密钥或大体积输出提交到 git。
