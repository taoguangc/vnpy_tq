# PAAF 项目总设计书

> 版本：1.0.0  
> 状态：Frozen（冻结）  
> 冻结日：2026-07-19  
> 规则优先级：`AGENTS.md` > 本文件 > `docs/*`

本文件固定 PAAF 的项目目标、系统架构、开发规范与研究规范。它描述**目标架构**；现有代码未满足之处属于待迁移项，不得宣称已经完成。

---

# 第一部分：项目目标（Mission）

## 1.1 定义

PAAF（Price Action Alpha Framework，价格行为 Alpha 框架）是一个中国商品期货量化研究平台。

PAAF：

- 研究具有统计显著性的价格行为 Alpha；
- 使用接近生产环境的数据与成本；
- 把每个 Detector 视为待证伪的研究假设；
- 产出可审计、可解释、可复现的证据。

PAAF 不是：

- Brooks 书籍的软件复刻；
- 交易策略合集；
- 追逐漂亮回测曲线的优化器；
- 未经验证便自动上线的信号工厂。

## 1.2 核心目标

> **研究 Alpha，而不是复刻 Brooks。**

Brooks 或其它理论只能提供候选假设，不能提供证据。最终结论由冻结数据协议、真实成本、可复现实验与统计结果决定。

## 1.3 研究价值函数

PAAF 不以「更高回测收益」作为开发价值函数。优先级为：

1. 研究质量；
2. 统计有效性；
3. 可复现性；
4. 可解释性；
5. 生产真实性。

收益变化是观察值，不是优化目标。

---

# 第二部分：系统架构（Architecture）

## 2.1 唯一允许的信号流

```text
Market Data
    ↓
Context Engine
    ↓ immutable Context
Detector Registry
    ↓ Signal | None
Risk Engine
    ↓ OrderIntent
Execution Engine
    ↓ Fill / Position Event
Research Logger
```

任何绕过这条链路的生产路径都必须登记为技术债。

## 2.2 Market Data

职责：

- 提供冻结口径的 1 分钟 Bar；
- 执行 CbC 自动换月；
- 保留无复权价格与真实换月跳空；
- 提供手续费、滑点与合约规格。

禁止：

- 为改善回测结果偷偷复权；
- 在加载层注入策略信号；
- 用未来主力信息修正过去。

## 2.3 Context Engine

只负责计算：

- Unknown（未知）；
- Trend（趋势）；
- Range（区间）。

Compression 是待验证假设，不属于 v0.1 基础 Context。输出必须是不可变 `Context`。Context 不允许买卖、访问仓位或产生交易建议。

## 2.4 Detector

Detector 是确定性计算单元：

```text
(Bars, Context, PatternState) -> DetectorResult
DetectorResult = Signal | None + next PatternState
```

约束：

- 不下单；
- 不访问账户、持仓、订单；
- 不修改 Strategy 或 Context；
- 不读取未来数据；
- 不使用隐藏全局状态；
- 同一输入必须产生同一输出。

跨 bar 形态允许显式 `PatternState`，但状态必须可序列化、可重放、可单测。纯函数要求不等于「所有形态只能看一根 Bar」。

## 2.5 Detector Registry

Registry 是 Detector 的唯一发现入口，负责：

- 注册 `detector_id` 与版本；
- 校验 ID 唯一性；
- 按时间框架 / 状态 / profile 选择 Detector；
- 固定执行顺序；
- 输出启用清单与代码指纹；
- 禁止重复注册与隐式覆盖。

目标使用方式：

```python
registry.register(OPP21Detector)
detectors = registry.build(profile="research")
```

Strategy 不逐个 import Detector，不写 `if OPPxx` 分发逻辑。

Registry 不负责：

- 判断买卖；
- 更改证据等级；
- 自动晋级；
- 根据收益动态启停 Detector。

## 2.6 Risk Engine

输入 `Signal`，输出 `OrderIntent`。职责包括：

- 结构止损有效性；
- 风险上限；
- 仓位；
- 同 bar 保守撮合规则；
- 生产 profile 门禁。

Risk 不得重新定义 Pattern。

## 2.7 Execution Engine

职责：

- 委托、撤单与成交；
- 最小执行周期风控；
- 换月；
- 日终平仓；
- 滑点与手续费。

Execution 不得修改 Detector 语义。

## 2.8 Research Logger

Logger 记录候选、信号、订单、成交、出场和归因。v0.1 冻结字段：

`run_id`、`experiment_id`、`version`、`symbol`、`detector`、`context`、`direction`、`entry`、`exit`、`stop`、`target`、`bars`、`mfe`、`mae`、`pnl`、`reason`。

`experiment_id` 采用 `YYYYMMDD_symbol_vX.Y.Z`，例如 `20260719_rb_v0.1.0`。

禁止仅记录盈利成交而丢弃未成交候选或失败门禁；漏斗研究需要完整事件链。

---

# 第三部分：开发规范（Development Rules）

## 3.1 目录目标

```text
strategies/paaf/
├── domain.py
├── config.py
├── base_detector.py
├── detectors/
├── engines/
│   ├── context_engine.py
│   ├── risk_engine.py
│   ├── signal_engine.py
│   ├── execution_engine.py
│   └── logger.py
├── registry/
└── profiles/
```

Domain 不依赖 vn.py、Engine 或 Strategy；Engine 依赖 Domain。

现有 `pa_minimal` / `pa_cta` 不做大爆炸迁移。每次迁移必须是单一、可验证、保持行为对照的小步变更。

## 3.2 接口优先

开发顺序：

```text
Interface → Unit Test → Implementation → Integration Test
→ Backtest → CSV → Research Report
```

## 3.3 版本不可覆盖

每个 Detector 必须有：

- 稳定 `detector_id`；
- 明确 `detector_version`；
- 生命周期；
- 证据等级；
- 定义指纹。

行为语义变化必须升级版本。不得用同一版本号覆盖旧算法，也不得回写历史 CSV 使旧结论看似来自新算法。

## 3.4 复杂度预算

新模块必须说明：

1. 它回答哪个研究问题；
2. 为什么现有模块不能回答；
3. 如何验收成功或失败；
4. 如何审计与复现。

无法回答则不实现。Kelly、贝叶斯、机器学习、组合优化与大参数搜索默认不获批准。

## 3.5 兼容与迁移

- 公共接口无强理由不改；
- CSV 增列优于改名或删列；
- 破坏性 schema 变更必须升级版本；
- 禁止为符合目标架构一次性重写现有策略。

---

# 第四部分：研究规范（Research Rules）

## 4.1 零假设

每个 Detector 默认无 Alpha。理论正确、代码可运行、单品种盈利均不足以推翻零假设。

## 4.2 生命周期与证据等级

生命周期表示工程状态：

```text
Candidate → Testing → Verified → Production → Deprecated
```

证据等级表示证据覆盖：

| 等级 | 含义 | 最低要求 |
|------|------|----------|
| E0 | Idea | 可证伪定义，无收益结论 |
| E1 | Single Symbol | 单品种固定协议 + CSV |
| E2 | Multi Symbol | 冻结参数、多品种验证 |
| E3 | Multi Year / OOS | 多年份或严格样本外通过 |
| E4 | Production Ready | E3 + 成本/执行/日志审计 + 用户确认 |

生命周期与证据等级不可混用。例如 `Testing/E2` 是合法状态；`Production/E1` 不合法。

## 4.3 单假设工作流

```text
Design
  ↓
Implement
  ↓
Unit Test
  ↓
Backtest
  ↓
CSV
  ↓
Analysis
  ↓
Conclusion
  ↓
Commit（仅用户明确要求）
```

一次实验只允许一个主要变量。没有 CSV 或等价可审计输出，不得称为已证实。

## 4.4 回测验收指标

正式报告必须至少输出：

- Trade Count（交易数）；
- Win Rate（胜率）；
- PF（盈亏因子）；
- Expectancy（期望值）；
- Avg Trade（平均每笔）；
- MAE（最大不利波动）；
- MFE（最大有利波动）；
- Sharpe（夏普比率）；
- Max Drawdown（最大回撤）。

缺失指标必须标 `N/A` 并说明数据链路缺口，不得静默省略。

## 4.5 废弃规则

`PF < 1` 或 `Expectancy < 0` 是负证据，但**单一窗口不足以永久废弃**，否则会把抽样噪声误当事实。

规则：

1. Production Detector 在冻结验收窗出现任一负条件：立即降级到 `Testing`，从生产 profile 移除；
2. 在预先登记的独立窗口 / 品种复核；
3. 若连续两个独立证据单元仍 `PF < 1` 或 `Expectancy < 0`，且样本量达到协议门槛：标为 `Deprecated`；
4. 样本不足：标 `HOLD`，不晋级、不永久删除；
5. Deprecated 保留版本、代码指纹与历史 CSV，不再默认注册。

## 4.6 禁止追逐利润

禁止以下行为：

- 为提高回测收益连续加过滤器；
- 看到好结果后继续扩参；
- 只报告盈利品种；
- 缩短区间或移除成本；
- 用生产 profile 反复试错；
- 将样本内结果写成稳定 Alpha。

## 4.7 Commit 门禁

实验代码允许在用户授权范围内开发，但研究结论进入 Commit 前必须具备：

- 实验 ID；
- 固定配置；
- CSV 或等价输出；
- 分析结论；
- KEEP / REVERT / HOLD；
- 用户明确要求 Commit。

---

# 第五部分：冻结数据基线

正式研究基线：

| 项 | 冻结值 |
|----|--------|
| Source | TQSDK Offline Data |
| Bar | 1 Minute |
| Continuous | Auto Roll（CbC） |
| Price | Unadjusted |
| Commission | Real |
| Slippage | Real |

偏离冻结值只能作为独立实验，不得替代基线或与基线混报。

---

# 第六部分：规范治理

## 6.1 优先级

```text
AGENTS.md
  > PAAF_PROJECT_SPEC.md / 01_CONSTITUTION.md
  > docs/02–07
  > Skills / 工具提示
  > 临时聊天建议
```

## 6.2 变更程序

冻结规范不能静默修改。变更必须：

1. 提出明确问题与影响；
2. 说明是否改变研究结论；
3. 更新文档版本；
4. 写入 `CHANGELOG.md`；
5. 经用户明确确认。

## 6.3 当前技术债声明

规范冻结不等于现有代码已合规。当前重点技术债包括：

- 部分 Detector 仍依赖 Strategy 可变状态；
- Strategy 仍有逐个 OPP 路由；
- Registry 尚未正式实现；
- Logger 尚未覆盖所有统一字段；
- 旧实验的 MAE/MFE/Expectancy 可能不完整。

这些项目应按路线图渐进迁移，不得用一次大重构解决。
