# ATR Compression EXP001 — Experiment Run Specification

> **Status**: Accepted（Frozen for ATR_COMPRESSION_EXP001 Feature Run）
> **Accepted date**: 2026-07-19
> **Experiment ID**: `ATR_COMPRESSION_EXP001`
> **Parent**: `docs/specs/ATR_COMPRESSION_SENSOR_EXPERIMENT_RFC.md`（Accepted）
> **Sensor**: `atr_compression@1.0`（EXPERIMENT；commit `37baf45`）
> **规则优先级**: `AGENTS.md` > Parent RFC > 本 Run Spec > 运行脚本
> **运行门禁**: 本文件 **已 Accepted**；仍须用户明确授权「跑 EXP001」才可生成 Feature Artifact。Accepted ≠ 自动跑数；**不**授权 Evaluation / Evidence。

本文件冻结 **第一次真实运行** 的实验身份、数据、参数、产物与评估计划。
它不是新的 Sensor RFC，也不授权交易。

**一句话**：在已实现的 ATR Feature Sensor 上，登记一次可审计的 Experiment Run；本 Spec 授权范围仅到 Feature Artifact；Evaluation / Evidence 须另授权。

---

## 0. Identity Freeze

| 字段 | 冻结值 |
|------|--------|
| `experiment_id` | `ATR_COMPRESSION_EXP001` |
| `run_id` | 运行时由调用方注入（建议 `ATR_COMPRESSION_EXP001_RUN001`）；不得自动 UUID |
| `subject_kind` | `feature_sensor` |
| `sensor_id` | `atr_compression` |
| `sensor_version` | `1.0` |
| `feature_schema_version` | `2.0` |
| Sensor governance | `EXPERIMENT`（本 Run 不晋级） |

禁止：

- 改 `experiment_id` 覆盖历史
- 同 id 重跑覆盖 artifact / evidence（append-only；重跑须新 `run_id` 或新 experiment）

---

## 1. Hypothesis（预注册，不得事后改）

```text
H0:
  atr_ratio 与未来已实现波动无统计关联。

H1:
  atr_ratio 与未来 N-bar realized volatility 存在可检出关联。
```

本 Run 只验证上述单一假设。
发现相关性变强 **不是** 调参或扩样本的理由。

---

## 2. Universe & Dataset

| 项 | 冻结值 |
|----|--------|
| symbol | `rb`（连续合约身份按数据目录 `data/tq/rb/`） |
| timeframe | `1m` |
| Source | 天勤 TQSDK Offline |
| Continuous | CbC 自动换月 |
| Price | 无复权 |
| Cost | 数据流保持真实成本口径；本 Run **不**做成交 / PnL |

### 2.1 日历区间（RQ1 Accepted）

基于当前 `data/tq/rb/manifest.json` 可用跨度约 `2020-01-15`–`2026-07-06`，本实验冻结：

```yaml
data_period:
  start: 2024-01-01
  end: 2025-12-31
```

| 项 | 冻结值 |
|----|--------|
| `start_date` | `2024-01-01` |
| `end_date` | `2025-12-31` |
| 时区 | bar timestamp timezone-aware（与数据一致） |

规则：

- Accepted 后允许报告缺失数据、报告样本数量变化
- **禁止**根据结果缩短 / 拉长 / 换年份
- 改区间 → 新 `experiment_id`，不是本 EXP001

### 2.2 Dataset Fingerprint（RQ2 Accepted）

`data_fingerprint` **不是**目录路径字符串。

```text
Dataset Fingerprint =
  source_id
  + file_manifest
  + file_hashes
  + construction_metadata
```

#### source_id

```text
tqsdk_offline / rb / 1m / CbC
```

#### file_manifest

对本次 Run 实际读取的每个文件记录：

```text
relative_path
size
hash
modified_time (optional)
```

至少包含（相对 `data/tq/rb/`）：

- 区间内参与 CbC 拼接的分月 parquet（由 `rollover_map` 决定）
- `rollover_map.parquet`
- `manifest.json`
- 若使用：`dominant_windows.json`、`rollover_cost_detail.parquet`

#### file_hashes

每个文件内容的确定性 hash（与 Evidence hashing 工具一致）。

#### construction_metadata

```json
{
  "continuous_contract": "CbC",
  "adjustment": "unadjusted",
  "bar": "1m",
  "roll_rule": "dominant_oi",
  "data_spec": "docs/07_DATA_SPEC.md@1.0.0",
  "period_start": "2024-01-01",
  "period_end": "2025-12-31"
}
```

`roll_rule` 以实际 `rollover_map` 的 `method` 字段为准（当前数据为 `dominant_oi`）；写入 Manifest 时记录实测值。

禁止：仅 fingerprint `data/tq/rb/` 路径而无 file hash / construction metadata。

### 2.3 其它 Provenance（运行时填写）

| 字段 | 规则 |
|------|------|
| `code_revision` | 运行时 `git rev-parse HEAD`（须含 `37baf45` 或其后代） |
| `data_fingerprint` | 按 §2.2 计算 |
| `environment_fingerprint` | Python + 关键依赖版本的 canonical fingerprint |
| `parameter_fingerprint` | 由扁平 parameters 计算（见 §3） |

---

## 3. Parameter Set（扁平标量）

```yaml
parameters:
  atr_period: 14
  baseline_window: 100
```

规则：

- 改任一参数 → **新实验**（新 `experiment_id`），不是本 EXP001 的调参续跑
- 参数 **不**写入 FeatureResult；只进 Manifest
- **禁止**本 Run 内 grid / 扫描

---

## 4. Feature Observation Plan

```text
every 1m bar in [2024-01-01, 2025-12-31]
    → ATRCompressionSensor.observe(...)
    → FeatureResult{ atr_ratio: float | null }
```

规则：

- always-emit；warmup → `atr_ratio=null` + `warmup_state=insufficient`
- `rollover_flag` 只诊断，Sensor 不 drop
- Evaluation 可排除 `rollover_flag=true` 与 `atr_ratio=null` 样本（须预注册，见 §6；**本 Spec 不授权执行 Evaluation**）

---

## 5. Expected Artifacts

布局（对齐 Evidence Repository）：

```text
research/output/evidence/ATR_COMPRESSION_EXP001/
├── manifest.json
├── artifacts/
│   └── ATR_COMPRESSION_EXP001_FEATURES/
│       └── feature_results.jsonl
├── evaluation/          # 本 Spec 不授权写入
└── evidence/            # 本 Spec 不授权写入
```

| Artifact | `artifact_id`（建议） | 本 Spec 授权？ | 内容 |
|----------|----------------------|----------------|------|
| Feature | `ATR_COMPRESSION_EXP001_FEATURES` | **是**（须另有「跑 EXP001」指令） | FeatureResult JSONL（append-once） |
| Evaluation | — | **否** | 另授权后生成 |
| Evidence | — | **否** | 另授权后生成 |

FeatureResult **不得**含 experiment_id / metric / conclusion。

---

## 6. Evaluation Plan（预注册；执行未授权）

> **RQ3 Accepted**：EXP001 Run authorization covers Feature Artifact generation only. Evaluation requires separate explicit authorization.

本节仅预注册契约，防止事后择优；**不**因本 Spec Accepted 而授权计算 RV / Spearman / Evidence。

### 6.1 Primary Outcome

```text
RV_N = std(log_return[t+1 : t+N])
N = 60
```

### 6.2 Primary Metric

```text
Spearman(atr_ratio, future_RV_N)
```

报告（未来 Evaluation 授权后）：

- Spearman ρ
- effective sample size `n`
- 可选：confidence interval

### 6.3 Sampling

| 层 | 规则 |
|----|------|
| Feature | every bar |
| Outcome sample | **non-overlapping**，`sampling_interval = 60` |

### 6.4 Sample filters（预注册）

纳入评估的样本必须同时满足：

1. `atr_ratio is not None`
2. `warmup_state == "ready"`
3. `rollover_flag == false`（排除换月诊断为 true 的观测点）
4. 未来窗口 `[t+1, t+N]` 完整存在

### 6.5 Secondary（可选，不得替代 Primary）

分桶 low / medium / high `atr_ratio` → 比较 mean `RV_N`。
必须标注 `secondary`；禁止事后选最好桶作结论。

### 6.6 Decision vocabulary（RQ4 Accepted）

Evidence `conclusion` 仅允许：

```text
reject_h1 | accept_h1 | inconclusive
```

**不**定义：

```text
rho > x
p < 0.05
```

作为晋级或通过条件。本阶段目标是可审计 Evidence，不是 pass/fail 门禁。

禁止：「有效 Alpha」「可上线」「应加仓」。
Sensor 状态保持 `EXPERIMENT`；本 Run **不**触发 PRODUCTION。

---

## 7. Execution Gate

| 步骤 | 需要 | 本 Spec |
|------|------|---------|
| 1. 本 Run Spec Accepted | RQ1–RQ4 关闭 | ✅ |
| 2. 用户明确说「跑 EXP001」 | 禁止自作主张跑数 | 待指令 |
| 3. Feature Artifact + Manifest | 单次探索；完整四段复盘 | 待指令 |
| 4. Evaluation | **单独明确授权** | ❌ 未授权 |
| 5. Evidence | **单独明确授权** | ❌ 未授权 |

**禁止**本 Spec Accepted 后顺带：

- 参数搜索
- 多品种扩展
- 交易回测 / PnL 验收
- compression_score
- Strategy / Opportunity 接入
- 自动 Evaluation / Evidence

---

## 8. Success Criteria（过程）

Feature Run 成功 = 可审计 Feature Artifact 完成，**不是** Spearman 显著：

1. Manifest 持久化且 fingerprint 可核验（含 §2.2）
2. Feature artifact hash 稳定、可 replay
3. 区间严格为 `2024-01-01`–`2025-12-31`
4. 全过程无交易语义泄漏
5. Evaluation / Evidence **未**因本 Run 自动产生

---

## 9. Open Questions — CLOSED

| ID | Accepted 决议 |
|----|---------------|
| RQ1 | 冻结 `start=2024-01-01`，`end=2025-12-31`；禁止因结果改区间 |
| RQ2 | Dataset Fingerprint = source_id + file_manifest + file_hashes + construction_metadata；禁止仅路径 |
| RQ3 | 本 Spec 仅覆盖 Feature Artifact；Evaluation / Evidence 须另授权 |
| RQ4 | 报告 ρ 与 n（可选 CI）；不设显著性 pass/fail / 晋级门槛 |

---

## 10. Freeze Criteria

- [x] RQ1–RQ4 关闭
- [x] 与 Parent ATR Sensor RFC / Decision 015 无矛盾
- [x] H0 / Outcome / Metric / N / sampling / filters 预注册完整
- [x] 明确日期 `2024-01-01`–`2025-12-31`
- [x] 明确：Accepted ≠ 自动跑数；须用户「跑 EXP001」
- [x] Evaluation 未隐含授权
- [x] `docs/README.md` 已索引

---

## 11. Relation

```text
ATR Sensor RFC            ✅ Accepted
ATR Sensor Implementation ✅ 37baf45
ATR EXP001 Run Spec       ✅ Accepted ← 本文件
    → (explicit) 跑 EXP001
    → Feature Artifact only
    → (separate auth) Evaluation
    → (separate auth) Evidence
```

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-19 | 0.1.0-draft | 首版 EXP001 Run Spec；开列 RQ1–RQ4 |
| 2026-07-19 | 1.0.0 | **Accepted**：冻结 2024-01-01–2025-12-31；Dataset Fingerprint 完整定义；Feature-only 授权；无显著性门槛 |
