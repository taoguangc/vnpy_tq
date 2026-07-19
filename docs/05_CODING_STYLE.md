# 编码风格（Coding Style）

> 版本：2.0.0 · 冻结日：2026-07-19  
> 架构边界见 `02_ARCHITECTURE.md`。AI 操作约束见 `AGENTS.md`。

---

## 1. 语言与类型

- Python 3 + **PEP 8**：函数/变量 `snake_case`，类 `PascalCase`。
- 优先：`dataclass`、`Enum`、**类型标注**（公开函数与检测器返回值）。
- 一模块一职责；检测器**一文件一主形态家族**（可含多空对称函数）。
- 禁止为抽象而抽象；禁止与任务无关的重构。

### 1.1 冻结命名

| 类别 | 允许 | 禁止 |
|------|------|------|
| MarketState | `UNKNOWN` `TREND` `RANGE` | COMPRESSION / SIDEWAY / BOX / FLAT |
| Direction | `LONG` `SHORT` `NONE` | BUY / SELL / OPENLONG |
| Detector 文件 | `oppXX_<slug>.py` | `h2_detector.py` / `pattern.py` |
| Signal.score / confidence | 使用 `confidence`，默认 `1.0`，范围 `[0, 1]` | 平行字段 `score` |

交易日志 CSV 冻结为：`run_id,experiment_id,version,symbol,detector,context,direction,entry,exit,stop,target,bars,mfe,mae,pnl,reason`（见 `strategies/paaf/domain.py`）。

---

## 2. vn.py CTA 底线

- 策略继承 `CtaTemplate`：`from vnpy_ctastrategy import CtaTemplate, ...`
- **禁止**已废弃的 `vnpy.app.cta_strategy`
- 策略内禁止 `print()`，用 `self.write_log()`  
  （`if __name__ == "__main__"` 调 `run_parquet_backtest()` 除外）
- 参数：类属性 + `parameters` 列表
- `ArrayManager` 在 `__init__` 创建；在对应回调里 **`am.update_bar(bar)` 之后**再读指标
- `BarGenerator`：先 `super().__init__`，再创建；周期参数经 `add_strategy(..., setting)` 注入

---

## 3. 出场撮合（真实性）

- 止损 / 止盈在**最小可执行周期**检查（1m 时在 `on_bar`，不在信号 K 回调里假撮合）
- 挂单价：多头止损跳空用 `min(open, stop)`，止盈用 `max(open, target)`（空头对称）
- 同 bar 止损与止盈均触发 → **止损优先**
- 禁止用信号 K 收盘价代替边界成交价

---

## 4. Detector、Registry 与 Strategy 边界

```text
# Detector：(Bars, Context, PatternState) → Signal | None + next state
# Registry：注册 / 发现 / 固定排序 / profile 选择
# Strategy：update context → registry → risk → execute → log
```

- Detector 禁止访问持仓、订单和 Strategy 可变状态
- PatternState 使用显式、可序列化模型；禁止隐藏全局状态
- Detector 行为变更必须升级 `detector_version`
- Strategy 不得逐个硬编码新 OPP import；新架构通过 Registry
- 不要把 500 行无关逻辑塞进单个检测器「方便」
- 不要在策略里复制粘贴第二套形态定义（应以 detectors 为准）
- 单文件包由构建脚本生成，手改无效且易漂移

现有遗留代码允许渐进迁移；禁止为一次性「合规」重写整个策略。

---

## 5. 日志与诊断

- 长期诊断脚本放 `scripts/test_*.py` 或 `research/`
- 根目录 `_tmp_*` / `_tem_*` 仅临时，当轮删除（见 `AGENTS.md`）
- 禁止提交密钥、`.env`、实盘账号

---

## 6. 外来代码接入

接入教程 / 外部策略前须检查：

1. 是否有未来函数或信号 K 假撮合
2. 成本与仓位是否与本仓库一致
3. 是否引入隐藏全局状态
4. 是否违背检测器 / 策略分层

可疑结果走 skill：`quant-backtest-validation-tool`。

---

## 7. AI 改码原则（摘要）

- 小步增量；禁止无关模块大重构
- **One Commit, One Concept**：一次提交只引入一个架构概念
- 无强理由不改公共接口
- 不重写整个项目「顺便现代化」
- 用户未要求不 Commit
