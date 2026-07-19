# Context Engine Specification

> **Status**: Accepted（Frozen for v0.1.1 interface）  
> **Accepted date**: 2026-07-19  
> **Target version**: PAAF v0.1.1  
> **Path**: `docs/specs/CONTEXT_ENGINE_SPEC.md`  
> **规则优先级**: `AGENTS.md` > `PAAF_PROJECT_SPEC.md` / 宪章 > 本 Spec > 实现代码  
> **变更规则**: 任何 Context 行为或对外接口变更，必须先改本 Spec，再改代码，并在 `DECISIONS.md` 留 ADR（破坏性变更）。

本文件冻结 **接口与契约**，不冻结 **状态判定算法**。

**Stable API, Replaceable Implementation.**  
Context API 长期稳定；内部如何计算 Trend / Range /（未来）Compression 等允许替换，Detector 读取方式不变。

---

## 0. 与已冻结决策的关系

| 决策 | 对本 Spec 的约束 |
|------|------------------|
| Decision 002 | v0.1.x 基线状态仅为 `UNKNOWN` / `TREND` / `RANGE`；Compression 不得作为基线事实 |
| Decision 004 | Domain 对象纯净；指标周期在 `config.py`，不进 Domain |
| Decision 007 | vn.py 类型只经 Adapter；Context 对外类型不得暴露 `BarData` / `ArrayManager` |
| Decision 008 | Feature Layer 未实现；若内部计算指标，仅作 Context 私有依赖，不得改信号主链 |
| Decision 009 | 本 Spec Accepted；Session 为 Enum；性能 &lt;100μs 为 Design Target |

本 Spec 若与上表冲突，以已 Accepted ADR 为准，除非新 ADR 明确覆盖。

---

## 1. Design Goals（设计目标）

### 1.1 定义与总原则

**Context 是市场状态的统一语义层（Semantic Layer），而不是指标计算层（Feature Layer）。**

**Context 是 PAAF 对「当前可交易时刻之市场状态」的统一、只读抽象。**

它是 Detector、Logger 与研究归因共享的**市场语言**，不是交易引擎。  
以后 ATR、ADX、Slope、ER 等属于 Feature；Context 负责组织和发布语义，不负责发明指标。

### 1.2 负责（MUST）

- 在每根（合成）信号 Bar 更新后，发布一份**不可变** `Context`
- 表达当前 `market_state`（见 §4）
- 携带 Detector / Logger 所需的只读身份与时间信息（symbol、datetime、session 等，见 §3）
- 保证同一输入窗口下输出确定性（无隐藏全局可变状态）

### 1.3 不负责（MUST NOT）

- 下单、撤单、持仓、账户
- 风险计算、仓位 sizing、止损止盈决策（属 Risk）
- 成交撮合、换月执行、日终平仓（属 Execution）
- 写 CSV / 改实验结论（属 Logger / Research）
- 定义 OPP 形态（属 Detector）
- 充当 Feature Engine（计算并对外承诺 ATR/ADX 等指标 API）
- 读磁盘、网络、数据库、模型推理（见 §7）

### 1.4 设计原则

1. **Stable API, Replaceable Implementation**：对外字段冻结；内部判定 TREND/RANGE 的算法可升级版本。
2. **只读发布**：`update` 完成后，下游只读；禁止任何下游模块写回 Context。
3. **单状态主枚举**：用一个 `market_state`，禁止散落的 `is_trend` / `is_range` 布尔丛林。
4. **一级语义**：`MarketState` 只表达一级市场状态，不编码方向、强度及实验性信息（见 §4）。
5. **扩展不破坏**：新状态或新诊断字段走 Enum 扩展或 `extras` 策略（见 §5），默认不改编排层。

---

## 2. Lifecycle（生命周期）

### 2.1 在信号流中的位置

```text
Market Data
    ↓
Adapter（vn.py → PaafBar / 只读窗口）
    ↓
ContextEngine.update(...)
    ↓
immutable Context（published）
    ↓
Detector Registry（只读 Context）
    ↓
Risk → Execution → Logger
```

### 2.2 每根信号 Bar 的时序

```text
1. Adapter 准备只读行情窗口（am / bars）
2. ContextEngine.update(window, meta) → 计算并构造新 Context
3. 引擎用新 Context 替换上一份（旧对象可丢弃；不得原地 mutate）
4. Detector.detect(am, context) 只读 context
5. 本 bar 结束；下一根 bar 重复 1–4
```

**Hard rule:**

```text
After Context is published,
no downstream module may mutate Context.
```

### 2.3 创建 / 更新 / 销毁

| 事件 | 行为 |
|------|------|
| Strategy / 编排启动 | 创建 `ContextEngine` 实例；初始 Context 为 `market_state=UNKNOWN`，`session=UNKNOWN` |
| 每根信号 Bar | 调用 `update`；返回**新的** frozen Context |
| 品种切换 / 换月重置编排 | 允许 `reset()` 回到 UNKNOWN；须在日志中可审计 |
| Strategy 结束 | Engine 可销毁；无跨 run 持久化义务（v0.1.1） |

### 2.4 禁止的生命周期反模式

- Detector / Risk / Execution / Logger 调用 `context_engine.update`
- 在 `update` 未完成时把半成品 Context 交给 Detector
- 对已发布 Context 做字段赋值（`ctx.market_state = ...`）或 mutate `extras`
- 跨 bar 隐藏可变缓存却不反映在可序列化状态中（若需跨 bar 记忆，必须显式、可测试）

---

## 3. Context Object（对外接口）

### 3.1 v0.1.1 冻结形状（目标 Domain）

实现落在 `strategies/paaf/domain.py`（frozen dataclass + Enum）。  
下列字段为 **v0.1.1 对外契约**（实现阶段可从当前极简 Context 增量扩展，但不得引入可变对象）：

```python
class Session(str, Enum):
    DAY = "DAY"
    NIGHT = "NIGHT"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class Context:
    # --- identity / time ---
    symbol: str                      # 逻辑品种键，如 "rb"
    datetime: datetime | None        # 当前信号 Bar 时间；未知则为 None
    session: Session                 # DAY | NIGHT | UNKNOWN

    # --- market language (single source of truth) ---
    market_state: MarketState        # 见 §4

    # --- extension bag (versioned keys only) ---
    extras: Mapping[str, Any]        # 只读；键名与 schema 见 §5
```

### 3.2 字段语义

| 字段 | 含义 | Detector 可读 | 备注 |
|------|------|---------------|------|
| `symbol` | 当前研究/交易品种键 | 是 | 不含交易所前缀亦可，但 run 内须一致 |
| `datetime` | 信号 Bar 时间戳 | 是 | 来自 Adapter；AM 无时间则允许 None |
| `session` | 交易时段抽象（Enum） | 是 | 判定算法不冻结；未知用 `Session.UNKNOWN` |
| `market_state` | 统一市场状态 | 是 | **唯一**主状态字段 |
| `extras` | 诊断与试验字段 | 是（约定键） | 不得把必需主语义只放 extras |

### 3.3 关于 `ctx.bar` / 结构子对象

**v0.1.1 不冻结** `ctx.bar`、`ctx.trend`、`ctx.range`、`ctx.compression` 等嵌套对象。

理由：

- 当前链路为 vn.py → ArrayManager → Adapter；过早冻结 `ctx.bar` 会耦合未来 backtrader / vectorbt 适配
- Detector 契约仍是 `detect(am, context)`；Bar 窗口由 `am` / Adapter 提供
- Compression 等结构信息若需试验，放入 `extras` 且标明研究假设

只读 `PaafBar` 进入 Context：**延期**；须新 ADR + 本 Spec 修订后方可纳入后续版本。

### 3.4 引擎接口（ContextEngine）

```text
update(
    window,
    *,
    symbol: str,
    datetime: datetime | None = None,
    session: Session = Session.UNKNOWN,
) -> Context
get_context() -> Context
reset() -> Context   # 回到 market_state=UNKNOWN；session/symbol 策略由实现定义且须可测
```

- `window`：只读行情窗口（可为 Adapter 包装后的结构或 `am: Any`）；Engine 不得假设可变
- `update` **必须**返回新 Context；`get_context()` 返回最近一次发布的实例
- ContextEngine **可以**依赖 `PAAFConfig` 与纯计算；**不可以** import 策略持仓或下单 API
- vn.py 类型转换在 Adapter；Engine 优先消费 `PaafBar` / 抽象序列（实现细节不冻结）

---

## 4. State Model（状态模型）

### 4.0 一级语义原则

**MarketState 表示一级市场状态，不编码方向、强度及实验性信息。**

方向、强度、Compression 分数等一律进入 `extras`（或未来独立 Feature），不得膨胀主枚举。

一级状态示例形态（语义类别，非全部进入本版基线）：

```text
UNKNOWN | TREND | RANGE | (future first-level e.g. TRANSITION)
```

### 4.1 v0.1.1 冻结枚举（基线）

与 Decision 002 / 现有 Domain 对齐：

```text
MarketState =
    UNKNOWN
  | TREND
  | RANGE
```

| 状态 | 含义（语义，非算法） |
|------|----------------------|
| `UNKNOWN` | 信息不足、预热中、或无法可靠分类 |
| `TREND` | 判定为趋势环境（方向不进入基线枚举） |
| `RANGE` | 判定为区间环境 |

### 4.2 明确不采用的反模式

禁止作为主 API：

```python
is_trend: bool
is_range: bool
is_compression: bool
```

禁止在 v0.1.1 基线中加入：

```text
COMPRESSION | EXPANSION | TREND_UP | TREND_DOWN | VOLATILITY_CLUSTER | TRANSITION
```

`TRANSITION` 等可作为**未来一级状态**候选，须走 §5 扩展流程，不得默认加入。

### 4.3 方向与结构细节（非基线状态）

| extras 键 | 类型建议 | 说明 |
|-----------|----------|------|
| `trend_bias` | `"UP" \| "DOWN" \| "NONE"` | 仅当 `market_state==TREND` 时有意义；**v0.1.1 正式采用此通道表达方向** |
| `state_confidence` | `float ∈ [0,1]` | 分类置信；默认可不提供 |
| `compression_score` | `float` | **研究假设**；不得单独把状态改成 COMPRESSION |

**已关闭**：不拆 `TREND_UP` / `TREND_DOWN`；若未来需要，走 RFC + ADR。

### 4.4 状态转换（测试须覆盖的语义）

合法转换（任意 → 任意）在 v0.1.1 **均允许**；不强制马尔可夫约束。  
但单测至少覆盖典型路径的可观测性：

```text
UNKNOWN → TREND
UNKNOWN → RANGE
TREND → RANGE
RANGE → TREND
TREND → UNKNOWN
RANGE → UNKNOWN
```

转换由 `update` 的输入决定；禁止无输入的自发跳变。

---

## 5. Extension Policy（扩展策略）

**新字段优先进入 `extras`，只有经过 RFC 与验证后才进入稳定（顶级）接口。**

### 5.1 扩展 MarketState

新增一级枚举值必须同时满足：

1. 独立实验立项（`experiments/schema.yaml`）与假设登记  
2. 证据达到约定等级前，不得进入 production profile  
3. 本 Spec 修订 + ADR Accepted  
4. 旧 Detector：对未知枚举值必须安全退化（见 §5.3）

### 5.2 扩展 Context 字段

| 变更类型 | 要求 |
|----------|------|
| 新增可选 `extras` 键 | **默认路径**；文档化键名；Detector 可忽略 |
| 新增 Context 顶级字段 | Spec + ADR + 验证；尽量带默认值；CSV/Logger 同步 |
| 删除或改名顶级字段 | **破坏性**；须升框架次版本并提供迁移说明 |
| 把算法阈值写进 Domain | **禁止**；放 `config.py` |

### 5.3 Detector 对未知状态的契约

```text
若 market_state 不在 Detector 声明的支持集合内：
    → 返回 None（不交易），不得抛异常中断整条管线
```

推荐 Detector metadata 将来可声明 `supported_states`；v0.1.1 不强制。

### 5.4 Reserved 未来状态（非基线）

```text
TREND_UP, TREND_DOWN, COMPRESSION, EXPANSION, VOLATILITY_CLUSTER, TRANSITION
```

方向表达：**保持 `TREND` + `extras["trend_bias"]`**（已决议）。

---

## 6. Concurrency & Thread Safety

- v0.1.1：Context / ContextEngine **不保证线程安全**。
- 约定编排为**单线程 per strategy instance**。
- **One Symbol → One Context（Engine）**：多品种时每个 symbol / 策略实例独立 Engine；禁止跨品种共享可变 Engine 状态。
- 禁止在多线程中无锁地 `update` 同一 Engine。

---

## 7. Performance Budget

| 约束 | v0.1.1 |
|------|--------|
| `update` 每信号 Bar | **Design Target**：&lt; 100 μs（不含 Adapter 拉数）。**不是 Acceptance Criteria**；略超但可维护性更好时允许，须可解释 |
| I/O | **禁止**在 ContextEngine 内读磁盘 / 网络 / 数据库（硬约束） |
| ML | **禁止**在 ContextEngine 内做模型推理（硬约束） |
| 分配 | 允许每 bar 构造新 frozen Context；禁止无界历史缓存（硬约束） |

无法在合理热路径内完成的复杂特征，应降级为离线研究或独立 Feature 实验（Decision 008）。

---

## 8. Testing Requirements

### 8.1 单元测试（必测）

- Domain：`Context` frozen；`Session` 仅 `DAY` / `NIGHT` / `UNKNOWN`
- `MarketState` 仅含 `UNKNOWN` / `TREND` / `RANGE`
- `update` 返回新对象；连续两次 `update` 不共享可变内部状态
- §4.4 列出的状态转换路径均有单测（可用注入/桩算法，不依赖真实 Parquet）
- Engine 不 import `vnpy`（边界测走 Adapter）

### 8.2 Contract Test（必测）

除单元测试外，须有契约测试，至少包括：

- 已发布 `Context`：下游（含 Detector 桩）**不能**成功 mutate 字段或 `extras`
- Detector / Risk / Execution / Logger **不得**调用 `ContextEngine.update` / `reset`（可用类型边界或编排测试断言）
- 未知 `market_state`（若用测试替身注入）时 Detector 返回 `None` 且不抛异常

### 8.3 每新增一种基线 State

- 更新本 Spec §4  
- 新增转换单测 + 契约回归  
- 更新 Logger / CSV 枚举文档（如有）

### 8.4 非目标

- 证明某种 TREND 算法有 Alpha  
- 全品种 Parquet 回测作为 Context 单测  
- `&lt;100μs` 作为 CI 硬失败门禁

---

## 9. Contracts（模块契约）

> **Contract**：模块允许依赖的只读表面 + 明确禁止的副作用。  
> 后续 Risk / Logger / Feature 等模块均应采用同一写法。

### 9.1 ContextEngine Contract

| | |
|--|--|
| Read window / config | ✓ |
| Publish new frozen Context | ✓ |
| Mutate published Context | ✗ |
| Orders / position / I/O / ML | ✗ |

### 9.2 Detector Contract（相对 Context）

| | |
|--|--|
| Read Context fields / documented extras | ✓ |
| Read `am` / Adapter window | ✓ |
| Write / mutate Context | ✗ |
| Call `update` / `reset` | ✗ |

### 9.3 Risk Contract（相对 Context）

| | |
|--|--|
| Read Context for audit / sizing inputs | ✓ |
| Redefine patterns from Context | ✗ |
| Mutate Context | ✗ |

### 9.4 Execution Contract（相对 Context）

| | |
|--|--|
| Read Context for audit fields | ✓ |
| Bypass Risk using Context | ✗ |
| Mutate Context | ✗ |

### 9.5 Logger Contract（相对 Context）

| | |
|--|--|
| Persist `market_state` / session 等 | ✓ |
| Alter trading path for logging | ✗ |
| Call `update` | ✗ |

---

## 10. Implementation Plan（实现阶段，本 Spec 已冻结）

v0.1.1 代码增量：

1. Domain：新增 `Session`；扩展 `Context` 字段（保持 frozen）  
2. `ContextEngine.update`：可先用**可测规则桩**证明管线（算法可后续替换）  
3. 单测 + Contract Test 覆盖 §8  
4. **不**在同 Commit 混入 OPP16 实装、Feature Engine、或 `ctx.bar`

纪律：**严格按照本 Spec 编码；任何接口变更先改 Spec，再改代码。**

---

## 11. Open Questions — Resolved

| ID | 决议 | 说明 |
|----|------|------|
| Q1 Session | **Enum**：`DAY` / `NIGHT` / `UNKNOWN` | 稳定领域模型，非实验对象 |
| Q2 Trend direction | **`TREND` + `extras.trend_bias`** | 不拆 `TREND_UP`/`TREND_DOWN` |
| Q3 `ctx.bar` | **延期** | 不纳入 v0.1.1 |
| Q4 100μs | **Design Target** | 非 Acceptance Criteria |

---

## 12. Freeze Criteria（已满足）

- [x] §1–§9 无未决议内部矛盾  
- [x] 与 Decision 002/007/008 一致；Decision 009 记录本 Spec Accepted  
- [x] Open Questions 已关闭（§11）  
- [x] `docs/README.md` 已索引本 Spec  
- [x] 同意：「先改 Spec，再改 Context 代码」  
- [x] 原则写入：**Stable API, Replaceable Implementation**

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-19 | 0.1.0-draft | 首版 RFC |
| 2026-07-19 | 1.0.0 | Final Review 合入；Open Questions 关闭；Status → Accepted |
