# 检测器规格（Detector Spec）

> 版本：2.0.0 · 冻结日：2026-07-19  
> 架构边界见 `02_ARCHITECTURE.md`。研究晋级见 `06_RESEARCH_WORKFLOW.md`。

---

## 1. 检测器契约

检测器**只**回答：当前 bar / 上下文下，是否出现某形态？

```text
输入：Bars + Context（只读）+ PatternState（显式）
输出：Signal | None + next PatternState
```

### 允许

- 读取不可变历史窗口、ATR、tick、会话键与 `Context`
- 返回结构化信号（方向、标签、建议止损参考、元数据）
- 返回显式 `next PatternState`；状态须可序列化、可重放、可单测

### 禁止

- `buy()` / `sell()` / `cancel_order()` / 直接改仓位
- 访问账户、仓位、订单
- 读取未来 bar
- 修改 Strategy / Context / 其它 Detector 状态
- 把 arm / consume 状态隐藏在 Strategy 属性或全局变量
- 在检测器内做资金管理或「顺手过滤」未写入规格的门禁（门禁属 Risk / Strategy）

同一输入必须产生同一输出。需要跨 bar 记忆不违反纯函数原则，但状态必须是**显式输入/输出**。

---

## 2. OPP 编号与命名

- 新入场按 **OPP01–99 递增**。
- **文件名冻结**：`oppXX_<english_slug>.py`  
  例：`opp01_h2.py`、`opp02_ema_pullback.py`、`opp04_wedge.py`、`opp16_two_bar_reversal.py`。  
  禁止：`h2_detector.py`、`test.py`、`pattern.py`。
- 参数：`oppXX_<描述>`（如 `opp13_wide_range_cutoff_hour`）。
- `disabled_setups`：`OPPXX_<描述>`（如 `OPP09_5M_BP_LONG`）。
- **对称多空共享同一 OPP 编号**，用方向字段区分；缺一侧须标注「单向架构」或补齐。
- 新增时检查：`always_in` 对称、LATE 相位是否适用、exit tag 对称、时间框架已声明。

术语须与量化定义一致（例：OPP03 为均线二次入场，不得误称为 measured move）。

---

## 3. Detector Registry

Detector 由统一 Registry 注册，Strategy 不逐个 import 或写 `if OPPxx` 路由。

每个注册项至少声明：

- `detector_id`
- `detector_version`
- `timeframe`
- `lifecycle`
- `evidence_level`
- `enabled_profiles`
- `definition_fingerprint`

Registry 必须拒绝重复的 `(detector_id, detector_version)`，并保持固定执行顺序。Registry 不得根据回测收益自动启停或晋级。

现有 `pa_minimal` / `pa_cta` 是遗留路径，按 `PAAF_PROJECT_SPEC.md` 渐进迁移；本规范不声称当前代码已完成 Registry。

---

## 4. 生命周期（每个 Pattern 的身份）

```text
Candidate（候选）
    ↓
Testing（测试中）
    ↓
Verified（已验证）
    ↓
Production（生产）
    ↓
Deprecated（弃用）
```

| 状态 | 含义 | 允许 |
|------|------|------|
| Candidate | 有书面定义，未跑或仅冒烟 | 写检测器 + 单测；不进默认生产臂 |
| Testing | 固定协议下对照/归因中 | 进 research 臂；结论标「样本内/待 OOS」 |
| Verified | 跨样本或跨品种证据达到门禁 | 可写入推荐 profile，仍可关 |
| Production | 用户确认的默认交易集合 | 改逻辑视为新假设，须新实验 |
| Deprecated | 证据失败或被替代 | 保留代码路径与注释，勿静默删除历史标签 |

**禁止**：无生命周期标注就把新 Pattern「直接当成生产 Alpha」。

---

## 5. 证据等级

| 等级 | 名称 | 最低含义 |
|------|------|----------|
| E0 | Idea | 有可证伪定义，无 Alpha 结论 |
| E1 | Single Symbol | 单品种冻结协议 + CSV |
| E2 | Multi Symbol | 参数冻结后的多品种验证 |
| E3 | Multi Year / OOS | 多年份或严格样本外通过 |
| E4 | Production Ready | E3 + 成本/执行/日志审计 + 用户确认 |

证据等级与生命周期是两个维度。`Testing/E2` 合法；`Production/E1` 非法。

---

## 6. 登记表示例（须随实验更新）

> 下表为规范冻结时的**工作快照**，不是永久真理。更新登记表本身不算「优化收益」。

| OPP | 简述 | 时间框架 | 生命周期 | 证据 | 备注 |
|-----|------|----------|----------|------|------|
| OPP01 | L1 回调 | 5m | Testing | E0 | 多空应对称 |
| OPP03 | 均线二次入场 | 5m | Testing | E0 | 术语已更正 |
| OPP04 | 楔形旗形等 | 5m | Testing | E0 | 新门禁后当前对照 0 笔 |
| OPP05 | II / IOI 突破 | 5m | Testing | E1 | 仍未达到生产证据 |
| OPP08 | 突破相关 | 5m | Testing | E0 | 空侧对称默认 |
| OPP13 | 日极值反转 | 5m | Testing | E1 | 标签 `DAY_EXTREME_REV_*` |
| OPP14 | 双底/双顶类 | 60m | Testing | E0 | 真二次测试状态机 |
| OPP15 | 楔形 B′ 等 | 5m | Testing | E0 | Path A / 多空 |
| OPP16 | 两棒反转 | 5m | Testing | E2（暂定） | 多品种有证据，但尚非 E3/E4 |
| OPP17–20 | 高潮/形态/夜盘等 | 5m | Testing | E0 | 见各检测器文档字符串 |

完整证据以 `research/experiments.md` 与输出 CSV 为准。

---

> 暂定等级只用于迁移起点；没有可追溯 CSV 的条目应降回 E0。

---

## 7. 废弃规范

- 单个窗口 `PF < 1` 或 `Expectancy < 0`：从 Production 降到 Testing，并退出生产 profile。
- 两个预登记的独立证据单元连续为负，且达到样本门槛：标记 Deprecated。
- 样本不足：HOLD，不永久废弃。
- Deprecated 保留实现版本、指纹、实验记录与历史标签；默认 Registry 不注册。

禁止因单次抽样噪声直接永久删除 Detector。

---

## 8. 软禁 vs 硬禁

| 层级 | 机制 | 使用 |
|------|------|------|
| 软禁 | `always_in`、`trend_phase == LATE` 等 | 优先；结构反转可自启 |
| 硬禁 | `disabled_setups` | 证据表明难救且跨品种同病；标注 `# 品种特定` 与恢复条件 |

被软禁替代的硬禁项**保留注释**，不直接删历史。

---

## 9. 规格文档最低要求（新 OPP）

提交新检测器前，规格须写清：

1. Brooks / 内部定义（可检验句子，非鸡汤）
2. 多空是否对称
3. 触发 bar、失效条件、建议结构止损
4. 时间框架与路由函数
5. 生命周期初始状态 = Candidate，证据等级 = E0
6. `detector_id`、版本、Registry 元数据与定义指纹
7. 单测：确定性、镜像、跨会话、边界 tick、状态序列化（若适用）
