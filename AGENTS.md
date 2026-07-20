# PAAF AI 开发规范（AGENTS.md）

> **Every detector is guilty until proven innocent.**
> **每一个 Detector 默认都是无效的，直到数据证据证明它有效。**
>
> version: 3.0.0 · 规范冻结日：2026-07-19 · author: taoguang
> 本文件为所有 AI（Cursor / Claude Code / 其它 Agent）的**每轮必读操作契约**。
> **规则优先级最高**。总设计书 → `PAAF_PROJECT_SPEC.md`；细则按任务读取 `docs/01`–`07`。

---

## 项目一句话

**PAAF 不是为了证明 Brooks 正确；PAAF 是为了在中国商品期货上，用接近实盘的数据，发现具有统计显著性的价格行为 Alpha。**

---

## 1. 项目使命（Mission）

本仓库实现 **PAAF**（Price Action Alpha Framework，价格行为 Alpha 框架）。

PAAF 是量化研究平台。它**不是** Brooks 书籍的软件实现，也**不是**交易策略集合。

| PAAF 是 | PAAF 不是 |
|---------|-----------|
| 量化**研究平台** | 单一「圣杯」策略 |
| 每个检测器 = **研究假设** | 每个检测器 = 已证实 Alpha |
| 证据驱动晋级 | 叙事驱动上线 |

在统计证据之前，**默认每个检测器无 Alpha**（零假设）。

**研究 Alpha，而不是复刻 Brooks。**

---

## 必读文档地图

| 顺序 | 文档 | 何时读 |
|------|------|--------|
| 0 | **本文件 `AGENTS.md`** | 每轮 |
| 1 | `PAAF_PROJECT_SPEC.md` | 新会话 / 改方向 / 架构决策 |
| 2 | `docs/01_CONSTITUTION.md` | 项目哲学与不可谈判原则 |
| 3 | `docs/02_ARCHITECTURE.md` | 改分层、目录、信号流 |
| 4 | `docs/03_DETECTOR_SPEC.md` | 改 / 新增 OPP |
| 5 | `docs/04_BACKTEST_SPEC.md` | 回测、验收指标、报告 |
| 6 | `docs/05_CODING_STYLE.md` | 写 Python / vn.py |
| 7 | `docs/06_RESEARCH_WORKFLOW.md` | 实验、证据晋级、Commit 前 |
| 8 | `docs/07_DATA_SPEC.md` | 数据、换月、成本口径 |
| — | `docs/ROADMAP.md` | 排期与「现阶段不做」 |
| — | `program_trading.md` | 用户授权自治实验时 |
| — | `CHANGELOG.md` | 发版 / 规范变更 |
| — | `DECISIONS.md` | 架构决策与“为什么”（含 Decision 017/018） |

原 `AGENTS_DETAIL.md` 已废弃，勿再引用。

---

## 2. 研究哲学

- **数据 > 理论**
- **证据 > 意见**
- **研究质量 > 优化结果**
- **生产真实性 > 回测好看**
- **在理解之前，禁止优化**

### 不追逐利润（Don't Chase Profit）

**禁止以提高回测收益为优化目标。**

只优化：

- 研究质量
- 可解释性
- 可复现性
- 统计有效性

发现收益变高只是实验结果，不是准许继续调参的理由。

### 复杂度预算（Complexity Budget）

新模块必须先证明其**研究价值**（可检验假设、可审计、可复现）。

若功能不能提升研究能力 → **不实现**。

Kelly / 贝叶斯 / XGBoost / Transformer 等：先回答「为什么」；无研究价值 → 拒绝。

---

## 3. 当前数据规格（冻结）

所有正式研究始终使用：

- 天勤 TQSDK **离线**数据
- **1 分钟** K 线
- **自动换月（CbC）**
- **无复权**价格
- **真实手续费 + 真实滑点**

任何偏离都必须由用户明确批准，并标为**独立数据实验**，不得替代冻结基线。
细节 → `docs/07_DATA_SPEC.md`。

---

## 4. Detector（检测器）原则

检测器是确定性纯计算：输入只读行情窗口 `am` 与 `Context`，只返回 `Signal` 或 `None`。

禁止：

- `buy()` / `sell()` / `cancel_order()`
- 访问持仓、账户、订单
- 修改 Strategy / Context / 其它 Detector 状态
- 读取未来数据

跨 bar 记忆若需要，必须显式、可序列化，不得隐藏在策略对象中。

生命周期：`Candidate → Testing → Verified → Production → Deprecated`。
证据等级：`E0 Idea → E1 Single Symbol → E2 Multi Symbol → E3 Multi Year/OOS → E4 Production Ready`。
完整规则 → `docs/03_DETECTOR_SPEC.md`。

### Detector Registry

策略不得逐个硬编码 Detector 列表。统一：

```python
registry.register(OPP16Detector())
```

新增 Detector 只注册，不改 Strategy。

---

## 5. Context Engine 原则

Context 只计算并发布：

- Trend（趋势）
- Range（区间）
- Unknown（未知）

Context 不产生交易、不访问订单、不调用买卖。

Compression 属于待验证研究假设，不是 v0.1 基础事实。

---

## 6. Strategy 原则

策略**不**识别形态。策略只编排：

```text
Context → Detector → Risk → Execution → Logger
```

Strategy 中禁止出现形态定义，例如 `if H2: buy()`；形态必须进入 Detector。

---

## 7. Logger 原则

每个候选信号与每笔交易必须可审计。统一事件至少包含：

`run_id`、`experiment_id`、`version`、`symbol`、`detector`、`context`、`direction`、`entry`、`exit`、`stop`、`target`、`bars`、`mfe`、`mae`、`pnl`、`reason`。

CSV / 研究输出保持向后兼容；破坏性字段变更须升级 schema 版本。

---

## 8. 研究与版本规则

- 每个版本 / 每次实验只验证 **一个** 假设
- 禁止一次塞入多个无关新想法
- 工作流：设计 → 实现 → 回测 → **CSV** → 分析 → 结论 →（用户要求时）Commit
- **无 CSV（或等价可审计输出）→ 不得把结论当已证实，不得为此请求 Commit**
- 已发布 Detector 版本不可原地覆盖；行为变化必须生成新版本号
- 历史实现可 Deprecated，但不得抹去其版本、实验记录与输出定义
- **Decision 017（Evidence-first）**：研究顺序以 ADR 为准——先 Evidence Platform（v0.3），再 Validation Protocol（v0.4）；Closed 实验不可变；Research append-only；Negative Evidence 一等公民；无用户单独立项授权时，v0.3 期间不新开 OPP/Alpha 跑数
- **ABR**：大架构阶段完成须通过 Architecture Baseline Review（见 `docs/reviews/`；ABR-001 为基线）后方可进入下一阶段

编码工作流：接口优先 → 实现 → 单测 → 回测 → 研究报告。

---

## 目录约束（摘要）

| 目录 | 只做 |
|------|------|
| `detectors/` | 形态识别 |
| 计算 / engines 类模块 | 纯计算 |
| `strategy` 编排文件 | 编排与风控调用 |
| `research/` | 分析与实验 |
| `tests/` | 测试 |

---

## 禁止清单

- 未来函数 / 前视偏差
- 曲线拟合导向、擅自参数搜索
- 机器学习（v0.9 前，除非用户单独立项授权）
- 隐藏全局状态
- 讨好型、煽动性措辞
- 未经用户同意的连跑回测 / 自动优化到目标年化
- 擅自 `git commit` / `push`
- 覆盖或原地复活 Closed 实验（Decision 017；须新 `experiment_id`）

---

## AI 回复与改码规则

- 面向用户：**通俗中文**；术语首次可附中文；代码标识保持原文
- 只陈述可验证事实；区分「已证实」与「待验证假设」
- 数据与预期冲突时以数据为准，写明「未证实 / 与预期不符」
- 改码：**小步增量**；禁止无关重构、禁止无必要改接口、禁止整仓重写
- 优先改任务所需的最小文件集合

---

## 角色与资金语境

资深量化工程师；VNPY 4.4.0+（`vnpy_ctastrategy`）；中国商品期货；日内低频、约 **20 万**资金。
年化 >30% 为**方向性**目标；**单轮回测不以达标为停止条件**，禁止为凑指标扩参连跑。

---

## 编码底线（操作摘要）

完整条款 → `docs/05_CODING_STYLE.md`。

- PEP 8；`CtaTemplate`；禁用 `vnpy.app.cta_strategy`
- 禁止策略内 `print()` → `self.write_log()`
- `ArrayManager`：`__init__` 创建，`update_bar` 后再读
- 止损止盈在 1m `on_bar`；挂单价撮合；同 bar **止损优先**
- 信号在合成 K，风控在 1m

---

## 回测配额（必须遵守）

完整说明 → `docs/04_BACKTEST_SPEC.md`。

| 类型 | 上限 | 复盘 | 等确认 |
|------|------|------|--------|
| 探索 / 调参 | **3** 次 | 完整四段 | 是 |
| 排障 / 修 bug | 改代码+回测合计 **3** | 轻量 | 否 |
| 授权批量 | 按指令 | 并列汇总 | 完成后 |
| `--compare` 等 | **1** 次（整命令） | 并列汇总 | 视情况 |
| `--all` | 1 次脚本 | 并列汇总 | 完成后 |

- 须用户明确要求才跑回测
- 配额用尽立即停止；只改代码不回测不计入
- 排障禁止顺带优化

### 回测后输出

- **完整四段**：摘要 → 问题 → 下一步（默认 1 个）→ 等待确认
- **轻量**：指标变化 + 通过/未通过 + 1 原因
- **并列汇总**：一表 + 1 句结论

---

## OPP 编号（操作摘要）

完整 → `docs/03_DETECTOR_SPEC.md` 与 `CLAUDE.md`。

- OPP01–99 递增；参数 `oppXX_*`；禁用表 `OPPXX_*`
- 多空对称共享编号；声明时间框架（5m/15m/60m）
- 软禁优先于硬禁；硬禁须标注品种特定与恢复条件

---

## Windows 终端与临时文件

1. 回测前 `$env:PYTHONIOENCODING='utf-8'`
2. PowerShell 多句用 `;`，禁止 `cd ... && $env:...`
3. 根目录 `_tmp_*` / `_tem_*`：**当轮读完必须删除**；提交前清理
   `Remove-Item .\_tmp_* , .\_tem_* -ErrorAction SilentlyContinue`
4. 长期诊断放 `scripts/test_*.py`，禁止根目录堆积

路径模板（仓库为 `vnpy_tq`）：

```powershell
Set-Location C:\projects\vnpy_tq; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe <入口> 2>&1 | Select-Object -Last 40
```

---

## Token / 上下文约定

- 大文件定位后局部读（`Read` 建议 ≤150 行）；禁把 Parquet / `.log` / `backtests/` / `.venv` / agent-transcripts 读进对话
- 默认假定免费层 TPM 有限；Rate Limit 时暂停等用户「继续」
- 多品种扫描（≥10）可用后台

---

## 项目技能

| 技能 | 场景 |
|------|------|
| `vnpy-cta-backtest` | CTA 回测 / 策略 |
| `vnpy-quant-python` | `scripts/`、TQ、非策略工具 |
| `quant-backtest-validation-tool` | 可疑结果、未来函数、外来代码 |

冲突时：**宪章 / `AGENTS.md` > `docs/*` > skill > 临时聊天话术**。

---

## 规范冻结与变更

规范变更须：

1. 明确提出变更理由；
2. 更新本文件或对应文档版本；
3. 写入 `CHANGELOG.md`；
4. 不得静默削弱配额、数据冻结、零假设或禁止追逐利润条款。

冲突优先级：**`AGENTS.md` > `PAAF_PROJECT_SPEC.md` / 宪章 > `docs/*` > skill > 临时聊天话术**。
