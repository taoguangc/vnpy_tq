# PAAF 系统架构

> 版本：3.0.0 · 更新日期：2026-07-20  
> 哲学见 `01_CONSTITUTION.md`。编码细节见 `05_CODING_STYLE.md`。  
> **架构基线**：`docs/reviews/ABR-001_ARCHITECTURE_FREEZE_REVIEW.md`（ABR-001）。  
> 研究顺序见 Decision 017；Evidence Domain 合同见 `docs/specs/EVIDENCE_DOMAIN_SPEC.md`。

---

## 0. 顶层架构（Architecture Baseline）

PAAF 同时包含 **研究证据链** 与 **检测器框架**。二者经 Evidence Gate 衔接；Projection
（Portfolio / Timeline / Dashboard）只读投影 Domain，不得回写。

```text
                    Data Layer
                         │
                         ▼
                 Experiment Layer
                         │
                         ▼
                 Evaluation Layer
                         │
                         ▼
                  Evidence Layer
                         │
                  Evidence Gate
                (Decision 011)
                         │
────────────────────────────────────────────
             Detector Framework
────────────────────────────────────────────
Context
    │
    ▼
Detector
    │
    ▼
DetectionResult
    │
    ▼
Opportunity
    │
    ▼
Decision（future）
    │
    ▼
Execution（future）
```

### Architecture Principles

**Principle 1 — Evidence Gate precedes Detector Promotion.**  
无 Evidence（或等价可审计证据链）不得将 Detector 晋级 Production。引用 Decision 011；
Decision 017 §G 重申。

**Principle 2 — Projection never mutates Domain.**  
Portfolio / Timeline / Dashboard / Knowledge Graph 等均为 **Projection**：只读观察方式，
不得调用写路径改写 Experiment / Evaluation / Evidence。引用 Decision 017（Research
append-only；Portfolio 为治理视图而非交易层）。

| 层 | 职责 | 禁止 |
|----|------|------|
| Data | 冻结协议行情（Decision 001） | 为收益改复权/成本 |
| Experiment | 假设与条件身份（Manifest） | 写入结果/PnL |
| Evaluation | Assessment（按协议判断） | mutate Evidence；冒充 Truth |
| Evidence | 结论归档（append-only） | 原地改 decision |
| Evidence Gate | 晋级门禁 | 跳级 Production |
| Context | Unknown / Trend / Range | 下单、产生交易 |
| Detector | 形态识别 → `DetectionResult \| None` | 下单、持仓、改 Strategy |
| Opportunity | 研究机会目录 | 自动下单 |
| Decision / Execution | 未来 | 在无 Evidence 时启用 Production |
| Projection | Portfolio 等只读视图 | 回写 Domain |

**策略（Strategy）只做编排，不做形态识别。**  
**检测器只做形态识别，不做交易。**  
**Feature Sensor 与 Opportunity Detector 双路径**（Decision 015）；Feature 不得插入
`Market → Feature → Context` 交易捷径。

---

## 1. Detector Framework 信号流（细节）

```text
Market Data
        ↓
Context Engine → immutable Context
        ↓
Detector Registry → DetectionResult | None
        ↓
   Opportunity（可选提升）
        ↓
   风控（Risk）          ← 须经 Evidence Gate 才进 Production
        ↓
   执行（Execution）
        ↓
   日志（Logger）
```

新代码禁止以遗留 `Signal` 作为主输出（v0.2 Deprecated；v0.3 Removal Window，见 CLEANUP
与 Decision 013/015）。

| 层 | 职责 | 禁止 |
|----|------|------|
| Context | Unknown / Trend / Range | 下单、产生交易 |
| Detector | 纯计算识别形态，返回 DetectionResult 或空 | 下单、持仓、修改 Strategy |
| Registry | 注册、发现、排序、profile 启停 | 按收益自动晋级 |
| Risk | 止损止盈、仓位、门禁、软禁/硬禁 | 发明新形态 |
| Execution | 挂单撮合、换月、EOD | 改写检测语义 |
| Logger | 候选、成交、归因、CSV | 改变交易结果 |

---

## 2. 仓库目录约束

| 目录 | 只允许 | 不允许 |
|------|--------|--------|
| `strategies/paaf/detectors/` | 形态识别、返回 DetectionResult | 下单、风控、仓位；依赖 Evidence 写路径 |
| `strategies/paaf/sensors/` | Feature 观测（FeatureResult） | Direction / Opportunity / 下单 |
| `strategies/paaf/evidence/` | Evidence Domain / Repository | Dashboard；交易语义 |
| `strategies/paaf/evaluation/` | Evaluation 合同 | mutate Evidence |
| `strategies/*/strategy.py` 等 | 编排 Context→Detector→Risk→Execution | 把数百行形态逻辑塞进策略 |
| `research/` | 分析脚本；**Archived 勿扩展**（见 `research/README.md`） | 把 AFF/`pa_minimal` 当 Active |
| `docs/experiments/` | Active 实验登记 | 覆盖 Closed 结论 |
| `docs/reviews/` | ABR 等架构基线审计 | 用 Review 替代 Spec |
| `tests/` | 单测 / 契约 | 依赖真实 Parquet 全量回测当单测 |
| `scripts/`、`tools/` | 加载、下载、扫描、授权 runners | 根目录一次性 `_tmp_*` 堆积 |
| `data/tq/` | TQ 离线数据 | 写入策略逻辑 |

---

## 3. 当前主战场包

| 包 | 角色 |
|----|------|
| `strategies/paaf/` | **生产 / 研究主框架** |
| `scripts/tq_*` / `paaf_*` | 数据与授权实验 runners |
| `docs/experiments/` | Active 实验权威登记 |
| `research/` | 遗留脚本（多为 Archived）+ 本地 `output/` |

遗留包（`pa_minimal` / `pa_cta` 等）仅作对照与渐进迁移来源，**不再**作为新功能主战场。

### 目标包（`strategies/paaf/`）

```text
strategies/paaf/
├── domain.py
├── config.py
├── base_detector.py
├── adapters/
├── detectors/
├── sensors/
├── evidence/
├── evaluation/
├── data_audit/
├── engines/
└── registry.py
```

`domain.py` 是交易/检测领域依赖中心，不依赖 vn.py。Evidence / Evaluation 合同分册存放，
不把研究归档对象塞进交易 Domain 丛林。vn.py 类型只经 `adapters/` 进入 PAAF。

---

## 4. 信号与时间框架路由

信号在**合成 K**上计算，风控在 **1 分钟 `on_bar`** 上执行（见 `04_BACKTEST_SPEC.md`）。

| 时间框架 | 典型 OPP | 说明 |
|----------|----------|------|
| 5m | OPP01–05, OPP08–13, OPP15–20 | 主力信号层 |
| 15m | OPP06, OPP07 | 更大周期假突破相对更少 |
| 60m | OPP14 | 双顶/双底类更适合 1H |

新增 OPP **必须声明**目标时间框架；迁移须在规格表中留注释。v0.3 期间未经立项不新开
OPP/Alpha（Decision 017）。

---

## 5. Logger 与 CSV

- 每个候选信号与每笔成交须可追溯。
- 统一字段：`run_id,experiment_id,version,symbol,detector,context,direction,entry,exit,stop,target,bars,mfe,mae,pnl,reason`。
- 研究输出在增列时**尽量向后兼容**；破坏性改列须改版本。
- Evidence / Evaluation 归档服从 append-only（见 Evidence Domain Spec）。

---

## 6. 架构治理（ABR）

大版本阶段完成须通过 **Architecture Baseline Review（ABR）** 方可进入下一阶段：

```text
Spec → Implementation → Tests → ABR → Next Phase
```

- 基线：`docs/reviews/ABR-001_ARCHITECTURE_FREEZE_REVIEW.md`
- 后续：`ABR-002` … 与上一份可比；发现问题进 Backlog，Review 本身默认不改代码

---

## 7. 单文件 vs 包路径

- **生产 / 对照默认**：`strategies/paaf/` 包路径。
- 遗留单文件仅研究便携；禁止手改后当作源真相。
- 不一致时以 `paaf` + 迁移缺陷排查为准。
