# PAAF 系统架构

> 版本：2.0.0 · 冻结日：2026-07-19  
> 哲学见 `01_CONSTITUTION.md`。编码细节见 `05_CODING_STYLE.md`。

---

## 1. 分层总览

```text
Market Data
        ↓
Context Engine → immutable Context
        ↓
Detector Registry → Signal | None
        ↓
   风控（Risk）
        ↓
   执行（Execution）
        ↓
   日志（Logger）
```

| 层 | 职责 | 禁止 |
|----|------|------|
| Context | Unknown / Trend / Range | 下单、产生交易 |
| Detector | 纯计算识别形态，返回信号或空 | 下单、持仓、修改 Strategy |
| Registry | 注册、发现、排序、profile 启停 | 按收益自动晋级 |
| Risk | 止损止盈、仓位、门禁、软禁/硬禁 | 发明新形态 |
| Execution | 挂单撮合、换月、EOD | 改写信号语义 |
| Logger | 成交、归因、CSV | 改变交易结果 |

**策略（Strategy）只做编排，不做形态识别。**  
**检测器只做形态识别，不做交易。**

---

## 2. 仓库目录约束

| 目录 | 只允许 | 不允许 |
|------|--------|--------|
| `strategies/*/detectors/` | 形态识别、返回 Signal | 下单、风控、仓位 |
| `strategies/*/engines/` 或计算子模块 | 纯计算（楔形、VSA、摆动等） | 策略状态机耦合交易 |
| `strategies/*/strategy.py` 等 | 编排 Context→Detector→Risk→Execution | 把数百行形态逻辑塞进策略 |
| `research/` | 分析脚本、实验协议、报告产物 | 改生产默认参数冒充「分析」 |
| `tests/` | 单测 / 镜像 / 边界 | 依赖真实 Parquet 全量回测当单测 |
| `scripts/`、`tools/` | 加载、下载、扫描、构建 | 根目录一次性 `_tmp_*` 诊断堆积 |
| `data/tq/` | TQ 离线数据 | 写入策略逻辑 |

检测器文件宜**单一职责、可单测**；禁止把无关 OPP 堆进同一巨型函数而不声明边界。

---

## 3. 当前主战场包

| 包 | 角色 |
|----|------|
| `strategies/paaf/` | **生产 / 研究主框架**（Domain / Registry / Engines / Adapters） |
| `scripts/tq_data_loader.py` / `rollover_*` | CbC 数据与换月引擎对接 |
| `research/` | 对照臂、OOS、归因、实验日志 |
| `experiments/` | 实验登记（`schema.yaml`）；新实验按 schema 登记 |

遗留包（`pa_minimal` / `pa_cta` 等）仅作对照与渐进迁移来源，**不再**作为新功能主战场。禁止以此为由一次性重写；每次只迁移一个接口或模块，并做行为对照。

其它策略包（如 `smc_orderflow_vwap`）服从同一分层原则，但**不默认**套用全部 OPP 编号规则。

### 目标包（`strategies/paaf/`）

```text
strategies/paaf/
├── domain.py
├── config.py
├── base_detector.py
├── adapters/          # vn.py 边界；Domain 禁止直接 import vn.py
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

`domain.py` 是依赖中心，不依赖 vn.py、Engine 或 Strategy。vn.py 类型只经 `adapters/` 进入 PAAF。

---

## 4. 信号与时间框架路由

信号在**合成 K**上计算，风控在 **1 分钟 `on_bar`** 上执行（见 `04_BACKTEST_SPEC.md`）。

| 时间框架 | 典型 OPP | 说明 |
|----------|----------|------|
| 5m | OPP01–05, OPP08–13, OPP15–20 | 主力信号层 |
| 15m | OPP06, OPP07 | 更大周期假突破相对更少 |
| 60m | OPP14 | 双顶/双底类更适合 1H |

新增 OPP **必须声明**目标时间框架；迁移须在 `disabled_setups` 或规格表中留注释。

---

## 5. Logger 与 CSV

- 每个候选信号与每笔成交须可追溯。
- 统一字段：`run_id,experiment_id,version,symbol,detector,context,direction,entry,exit,stop,target,bars,mfe,mae,pnl,reason`。
- 研究输出 CSV（`research/output/` 等）在增列时**尽量向后兼容**；破坏性改列须改版本并在实验记录说明。
- Agent 不得为「好看」删改历史 CSV 语义而不留痕。

---

## 6. 单文件 vs 包路径

- **生产 / 对照默认**：`strategies/paaf/` 包路径。
- 遗留单文件（如历史 `pa_minimal.py`）仅研究便携；须由构建脚本重生，禁止手改后当作源真相。
- 遗留包与 `paaf` 对照回测应对齐；不一致时以 `paaf` + 迁移缺陷排查为准。
