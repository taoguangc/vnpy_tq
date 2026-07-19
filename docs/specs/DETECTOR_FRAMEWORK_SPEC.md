# Detector Framework Specification

> **Status**: Accepted（Frozen for v0.2.x interface）  
> **Accepted date**: 2026-07-19  
> **Target version**: PAAF v0.2.x  
> **Path**: `docs/specs/DETECTOR_FRAMEWORK_SPEC.md`  
> **规则优先级**: `AGENTS.md` > `PAAF_PROJECT_SPEC.md` / 宪章 > 本 Spec > `docs/03_DETECTOR_SPEC.md`（OPP 细则）> 实现  
> **变更规则**: 先改本 Spec，再改代码；破坏性变更须 ADR。

本文件冻结 **Detector Framework 的接口与契约**，不冻结任何 OPP 形态算法。  
v0.2 **先框架、后 OPP**；Demo Detector 只验证管线，不为收益。

**Stable API, Replaceable Implementation.**  
Detector / Opportunity / Registry 的对外语言长期稳定；形态算法与证据可替换。

与 [`docs/03_DETECTOR_SPEC.md`](../03_DETECTOR_SPEC.md) 的关系：

| 文档 | 职责 |
|------|------|
| **本 Spec** | Framework：DetectionResult、Opportunity、Capability、Status、Registry、Evidence |
| `docs/03_DETECTOR_SPEC.md` | OPP 编号细则、E0–E4、命名与禁用约定 |

冲突时：本 Spec + ADR > `03` 的过时实现描述。`03` 中的 `Signal` 输出描述以本 Spec 的迁移条款为准。

---

## 0. 与已冻结决策的关系

| 决策 | 约束 |
|------|------|
| Decision 003 | Registry 为唯一发现入口；Strategy 不写 `if OPPxx` |
| Decision 005 | 评分字段使用 `confidence`，禁止平行 `score` |
| Decision 009 | Detector **只读** Context；不得 mutate / 不得调用 `update` |
| Decision 010 | Spec-Driven Development |
| Decision 011 | **No detector enters production without evidence** |
| Decision 012 | `main` 稳定；`feature/*` / `research/*` |
| Decision 013 | 本 Spec Accepted；Open Questions 决议见 §11 |

---

## 1. Design Goals

### 1.1 定义

**Detector 是确定性形态识别单元：只回答「是否出现可命名的价格行为假设」，不交易、不风控、不持仓。**

### 1.2 工程原则（强制）

> **No detector enters production without evidence.**

```text
Idea
  → Experiment（schema 登记）
  → Validation
  → Evidence（CSV / 等价审计）
  → Detector Spec 条目
  → Implementation
  → Production（须 E4 + 用户确认 + DetectorStatus.PRODUCTION）
```

### 1.3 负责 / 不负责

| MUST | MUST NOT |
|------|----------|
| 读只读窗口 + 只读 `Context` | `buy` / `sell` / 持仓 / 账户 |
| 返回 `DetectionResult \| None` | 修改 Context / Strategy / 其它 Detector |
| 显式 `PatternState`（若需跨 bar） | 未来函数；返回裸 `bool` |
| 声明 id / version / status / capability / evidence | 在 Detector 内做资金管理 |

### 1.4 研究与交易解耦

```text
Detector
    ↓
DetectionResult          # 检测（非下单）
    ↓
Opportunity（可选提升）   # 研究目录 + Evidence 链接
    ↓
Decision / Risk          # 是否可交易
    ↓
OrderIntent → Execution
```

**禁止**长期路径：`Detector → Signal（交易语义）`。  
见 §2 弃用条款。

---

## 2. DetectionResult（禁止 bool）

### 2.1 规则

禁止以 `True` / `False` 作为 Detector 主输出。  
无检测 → 返回 `None`。

`DetectionResult` 必须满足：

- **Stable**：字段语义由本 Spec 与 `schema_version` 管理；
- **Immutable**：发布后不得修改字段或 `metadata`；
- **Serializable**：统一提供 `to_dict()` / `from_dict()`；
- **Traceable**：记录 `opportunity_id`、`evidence_refs` 与 `created_at`。

### 2.2 冻结形状

```python
@dataclass(frozen=True)
class DetectionResult:
    detector_id: str
    detector_version: str
    opportunity_id: str
    status: DetectorStatus
    direction: Direction
    confidence: float = 1.0              # [0, 1]；Decision 005
    tags: tuple[DetectorTag | str, ...] = ()
    entry: float | None = None
    stop: float | None = None
    target: float | None = None
    reason: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)  # 发布后只读
    pattern_state: PatternState | None = None
    evidence_refs: tuple[str, ...] = ()
    schema_version: str = "1.0"
    created_at: datetime = field(default_factory=utc_now)
```

约束：

- `confidence` 必须为 `float` 语义且在 `[0.0, 1.0]`；禁止 `85` / `92` / `100` 百分制；
- `created_at` 必须是带时区时间戳，默认 UTC；
- `to_dict()` 只返回 JSON 友好值（Enum → value，datetime → ISO 8601）；
- `from_dict()` 按 `schema_version` 分派；v0.2.1 仅接受 `"1.0"`，未知版本明确失败；
- `to_dict → from_dict` 必须保持对象等价；
- `status=PRODUCTION` 时 `evidence_refs` 不得为空；
- `tags` **只用于分类、检索与统计，不得参与业务逻辑**；业务状态读取 `PatternState` / 稳定字段；
- `pattern_state` 是唯一形态状态入口；禁止在 DetectionResult 增加几十个 pattern bool。

### 2.3 `Signal` 弃用路径（已决议）

| 版本 | 策略 |
|------|------|
| **v0.2** | 引入 `DetectionResult`；`Signal` 标记 **Deprecated**（可薄包装/适配，不得新写依赖） |
| **v0.3** | **删除** Domain `Signal`（破坏性；须迁移笔记） |

语义：

- `DetectionResult` = **检测**
- 交易意图 = Risk / Decision 之后的 `OrderIntent`
- 不得把 DetectionResult 直接当成下单指令

---

## 3. PatternState（独立 dataclass）

```python
@dataclass(frozen=True)
class PatternState:
    name: str                            # 形态/相位名，如 "armed" / "Compression"
    confidence: float = 1.0              # [0, 1]
    metadata: Mapping[str, Any] = field(default_factory=dict)  # 只读
```

- **禁止**以自由 `dict` / `Mapping` 作为跨 bar 主状态类型
- 需要扩展时改 dataclass 字段或经 ADR 增字段；`metadata` 仅诊断

---

## 4. Tags（小枚举 + 扩展）

### 4.1 冻结小枚举 `DetectorTag`

```text
COMPRESSION
TREND
BREAKOUT
REVERSAL
PULLBACK
LIQUIDITY
DEMO                         # 仅框架验证
```

### 4.2 自定义扩展

允许额外字符串，**必须**使用前缀：

```text
custom:<slug>
```

例：`custom:asia_session_fade`。  
禁止无前缀的自由拼写（避免 `Compression` / `compress` / `COMP` 并存）。

统计与搜索：标准枚举可聚合；`custom:*` 单独桶。

---

## 5. Opportunity Model

### 5.1 定义

**Opportunity 是目录中的可审计交易机会定义**（研究资产），不是单笔下单，也不是 UUID 瞬时事件。

单 bar 检出 → `DetectionResult`；目录条目 → `Opportunity`（稳定业务 ID）。

### 5.2 `Opportunity.id`（已决议：固定业务 ID）

**禁止**自动 UUID。

格式（与现有 OPP 编号对齐）：

```text
OPPXX          # 推荐主形式，如 OPP03、OPP16
```

可选文档展示：`PAAF-OPP-03`（等价于 `OPP03`）。

Demo / 非 OPP 目录项：

```text
DEMO_<SLUG>    # 如 DEMO_CONTEXT_PASSTHROUGH
```

同一 `id` 在论文、实验、Git、报告中必须可引用。

### 5.3 冻结形状

```python
@dataclass(frozen=True)
class Opportunity:
    id: str                              # OPPXX 或 DEMO_*
    symbol_scope: str                    # 如 "rb" / "multi" / "*"
    direction: Direction | None          # None = 多空均可能
    setup: str                           # 人类可读短名
    detector_id: str
    detector_version: str
    status: DetectorStatus               # 见 §7
    tags: tuple[DetectorTag | str, ...] = ()
    evidence_refs: tuple[str, ...] = ()  # 见 §6；一对多实验引用
    context_requirements: tuple[str, ...] = ()  # 如 ("TREND",)
```

### 5.4 原则

- Opportunity **不是**订单
- `status=PRODUCTION` 时 `evidence_refs` **不得为空**
- Library 检索/UI 可后置；本 Spec 先冻字段

---

## 6. Evidence Reference（Opportunity ↔ Experiment）

```text
Opportunity
    ↓ 1 : N
evidence_refs[]
    ↓
EXP-021, EXP-035, EXP-044, ...
```

| 规则 | 说明 |
|------|------|
| 元素格式 | 与 `experiments/schema.yaml` 的 `experiment_id` 对齐 |
| 一对多 | 同一 Opportunity 可挂多次实验 |
| 可追溯 | 打开 Opportunity 应能列出全部关联实验 |
| 晋级 | 无合格 `evidence_refs` 不得 `DetectorStatus.PRODUCTION` |

---

## 7. Detector Status

Registry / Opportunity / metadata 使用统一状态（证据可见）：

```text
DetectorStatus =
    EXPERIMENT
  | VALIDATED
  | PRODUCTION
  | DEPRECATED
```

| 状态 | 含义 | 生产 profile |
|------|------|--------------|
| `EXPERIMENT` | 想法或试验中 | 禁止默认启用 |
| `VALIDATED` | 证据达到约定门槛，尚未用户确认生产 | 禁止默认启用 |
| `PRODUCTION` | E4 + 用户确认 + 显式启用 | 允许 |
| `DEPRECATED` | 被替代或证伪 | 禁止 |

与 `docs/03` 生命周期映射（迁移用）：

| docs/03 | 本 Spec |
|---------|---------|
| Candidate / Testing | `EXPERIMENT` |
| Verified | `VALIDATED` |
| Production | `PRODUCTION` |
| Deprecated | `DEPRECATED` |

---

## 8. Detector Capability

Registry 不仅注册实例，还声明**能力**，供发现、门禁与未来 Agent 组合：

```python
@dataclass(frozen=True)
class DetectorCapability:
    market_states: tuple[MarketState, ...]   # 所需/适用 Context 状态；空 = 不限制
    directions: tuple[Direction, ...]        # 可产出方向
    requires: tuple[str, ...] = ()           # 所需 Context.extras 键等，如 ("trend_bias",)
    produces: tuple[DetectorTag | str, ...] = ()  # 产出标签
    timeframe: str = "5m"
```

规则：

- Context 不满足 `market_states` / `requires` 时：Registry **不得**将该 Detector 纳入本 bar 的可运行集（或 Detector 必须返回 `None`；推荐 Registry 侧拒绝加载进 scan 列表）
- `produces` 用于检索与组合，不代替 Evidence
- Capability 变更若改变可运行语义 → 升 `detector_version`

---

## 9. Registry（升级）

### 9.1 注册键（已决议）

**唯一键：`(detector_id, detector_version)`**

允许同时存在：

```text
(OPP03, 1.0.0)  DEPRECATED
(OPP03, 2.0.0)  PRODUCTION
```

禁止仅用 `detector_id` 覆盖旧版本。

### 9.2 API 目标

| API | 职责 |
|-----|------|
| `register(detector)` | 按 `(id, version)` 注册；冲突则失败 |
| `discover(profile=..., status=...)` | 过滤可运行集 |
| `priority()` | 固定显式优先级（**禁止**按收益动态排序） |
| `capability(id, version)` | 返回 `DetectorCapability` |
| `get(id, version)` | 精确取版本 |

继承 Decision 003：不得按回测收益自动启停或晋级。

---

## 10. Detector Contract

| | |
|--|--|
| Read Context / window | ✓ |
| Return `DetectionResult \| None` | ✓ |
| Emit / update PatternState（显式） | ✓ |
| Write Context | ✗ |
| Call ContextEngine.update/reset | ✗ |
| Orders / position | ✗ |
| Return bool | ✗ |
| Hidden global state | ✗ |

---

## 11. Open Questions — Resolved

| ID | 决议 |
|----|------|
| Q1 Signal | **新类型 `DetectionResult` + 弃用期**；v0.3 删除 `Signal` |
| Q2 Opportunity.id | **固定业务 ID**（`OPPXX` / `DEMO_*`）；禁止 UUID |
| Q3 Registry Key | **`(detector_id, detector_version)`** |
| Q4 tags | **`DetectorTag` 小枚举 + `custom:<slug>`** |
| Q5 PatternState | **独立 frozen dataclass** |

---

## 12. 长期机制（本版一并冻结）

1. **Detector Capability** — §8  
2. **Detector Status** — §7  
3. **Evidence Reference** — §6  

---

## 13. Demo Detector（非 OPP）

v0.2.4：

- `detector_id = "DEMO_CONTEXT_PASSTHROUGH"`（目录 id：`DEMO_CONTEXT_PASSTHROUGH`）
- `status = EXPERIMENT`；**禁止** PRODUCTION profile
- 验证：Registry → DetectionResult →（可选 Opportunity）→ Logger
- **禁止** ADX/ATR 假装 Trend；**禁止** OPP 编号

---

## 14. 实现顺序

| 版本 | 交付 |
|------|------|
| **v0.2.0** | 本 Spec Accepted（本文件） |
| **v0.2.1** | Domain：`DetectionResult` + `PatternState` + `DetectorTag` + 必要 `DetectorStatus`；序列化与版本契约；`Signal` Deprecated |
| **v0.2.2** | Registry：`(id, version)` + `discover` / `priority` / `capability` |
| **v0.2.3** | Domain：`Opportunity` + `evidence_refs` 目录关联 |
| **v0.2.4** | Demo Detector + Contract Tests |

分支：`feature/detector-framework`；验证后 Merge `main`。  
每个切片一个 Commit。

---

## 15. Testing Requirements

- DetectionResult / PatternState / Opportunity frozen；extras/metadata 只读
- DetectionResult `to_dict → from_dict` 完全一致；未知 `schema_version` 明确失败
- `created_at` 保留时区与 ISO 8601 语义
- confidence 接受 `[0.0, 1.0]`，越界失败
- tags 只验证分类格式，不作为业务分支输入
- 返回 `None` vs Result；禁止 bool 路径单测
- Registry 同 id 不同 version 可并存；同 `(id, version)` 重复注册失败
- Capability 门禁：缺 `requires` 时不进入 discover 结果
- PRODUCTION 且 `evidence_refs` 为空 → 校验失败
- Detector 不可写 Context（Contract Test）
- Domain 无 vnpy/numpy/pandas/talib

---

## 16. Freeze Criteria（已满足）

- [x] Open Questions 已关闭（§11）  
- [x] Capability / Status / Evidence Reference 已写入  
- [x] 与 Decision 003/005/009–013 一致  
- [x] 先 Framework、后 OPP；Demo ≠ Alpha  
- [x] `docs/README.md` 索引更新  

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-19 | 0.1.0-draft | 首版 RFC |
| 2026-07-19 | 1.0.0 | Review 合入；五问关闭；Capability/Status/Evidence；Status → Accepted |
