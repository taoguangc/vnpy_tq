# Evidence Engine Specification（RFC）

> **Status**: Accepted（Frozen for v0.3 Evidence Engine interface）  
> **Accepted date**: 2026-07-19  
> **Target version**: PAAF v0.3.x  
> **Path**: `docs/specs/EVIDENCE_ENGINE_SPEC.md`  
> **规则优先级**: `AGENTS.md` > `PAAF_PROJECT_SPEC.md` / 宪章 > 本 Spec > 实现代码  
> **变更规则**: 先改本 Spec，再改代码；破坏性变更须 ADR。  
> **实现门禁**: Accepted **不等于**授权 ATR Sensor。首个实现切片为 Evidence Engine Core（Manifest / ArtifactReference / EvidenceRecord / Provenance）。

本文件定义 **Evidence Engine（证据引擎）**：采集、挂接、验证与晋级研究证据。  
v0.3 的核心不是交易，而是：

```text
Evidence Collection + Research Validation
```

**No detector / sensor enters production without evidence.**（Decision 011）

---

## 0. 与已冻结决策的关系

| 决策 | 约束 |
|------|------|
| Decision 001 | 正式证据默认使用冻结 TQ 离线 1m CbC 无复权真实成本 |
| Decision 011 | Production 必须有证据链 |
| Decision 013 | Opportunity / DetectionResult 已冻结；证据挂接不得破坏其 immutability |
| Decision 014 | Framework First；本 Spec 是 Alpha 之前的证据层 |
| Decision 015 | 双路径、Storage/Provenance、Production = Intent+Evidence+Enablement |
| `experiments/schema.yaml` | 实验登记最低字段继续有效 |
| `FEATURE_SENSOR_SPEC.md` | FeatureResult / Observation Key / 四层分存交叉冻结 |

---

## 1. Design Goals

### 1.1 定义

**Evidence Engine 把「观测 → 结果 → 度量」变成可审计、可复现、可晋级的证据对象。**

它回答：

> 在冻结数据与成本下，某个 Sensor / Detector / Opportunity 的假设是否得到统计支持？

它不回答：

> 现在该不该下单？

### 1.2 MUST / MUST NOT

| MUST | MUST NOT |
|------|----------|
| 登记假设、窗口、度量、数据协议指纹 | 为提高收益改成本 / 复权 / 挑品种 |
| 链接 `experiment_id` 与对象 id（OPPXX / sensor_id） | 无 CSV/等价输出宣称 KEEP / Production |
| 支持 Feature 观测与 Opportunity 观测两类证据 | 把 Compression 直接写成 Buy Breakout |
| 输出可复现结论：KEEP / REVERT / HOLD | 跳级 E0→E4；按收益自动晋级 |

### 1.3 在系统中的位置

```text
FeatureResult ──┐
                ├──► Evidence Engine ──► KEEP / REVERT / HOLD
Opportunity ────┘         │
                          ▼
                   evidence_refs / 实验档案
                          │
                          ▼
              VALIDATED / PRODUCTION 门禁
```

---

## 2. Evidence Object

### 2.1 核心形状

```python
@dataclass(frozen=True)
class EvidenceRecord:
    evidence_id: str                      # 稳定业务 ID，如 EVD-2026-001
    experiment_id: str                    # 对齐 experiments/schema.yaml
    subject_kind: str                     # "feature_sensor" | "opportunity" | "detector"
    subject_id: str                       # ATR_COMPRESSION / OPP16 / DEMO_MINIMAL
    subject_version: str
    hypothesis: str                       # 单句可证伪假设
    observation: Mapping[str, float | str]
    outcome: Mapping[str, float | str]
    window: Mapping[str, int | str]       # e.g. bars_forward=30, bar="1m"
    metrics: Mapping[str, float]
    data_protocol_version: str
    decision: str                         # KEEP | REVERT | HOLD
    feature_artifact_uri: str = ""        # 引用，不复制 Feature 表
    artifact_hash: str = ""
    schema_version: str = "1.0"
    created_at: datetime = ...
    metadata: Mapping[str, str] = ...
```

### 2.2 示例（Compression — 证据，不是交易）

```text
Subject: Feature Sensor ATR_COMPRESSION @ 0.1.0
Hypothesis: ATR ratio 低于阈值后，未来 N bar 已实现波动倾向于扩张
Observation: atr_ratio < threshold  （来自 FeatureResult.values）
Outcome: realized_volatility over forward window
Window: 30 bars, 1m, frozen TQ CbC
Metric: mean/median RV, hit-rate vs baseline, sample size
Decision: HOLD | KEEP | REVERT
```

**禁止**等价表述：

```text
Compression = Buy breakout
breakout_weight += 0.5
```

### 2.3 与 Opportunity.evidence_refs

- Opportunity / DetectorDescriptor 的 `evidence_refs` 元素必须能解析到 `experiment_id`（或未来 `evidence_id` 映射表）
- Evidence Engine **不 mutate** 已发布 Opportunity；晋级时注册新版本 Descriptor / 新 Opportunity 快照

---

## 3. Evidence Collection

### 3.1 输入源

| 源 | 用途 |
|----|------|
| `FeatureResult` | 连续或稀疏特征观测序列 |
| `DetectionResult` / `Opportunity` | 事件型机会观测 |
| 冻结行情窗口 | 前向结果（volatility、return、MAE/MFE 等） |

### 3.2 采集规则

- 单次实验单主假设（对齐 docs/06）
- 必须落盘：配置指纹、代码指纹、CSV/JSONL、schema 版本
- 前视禁止：outcome 窗口不得使用未完成 bar

### 3.3 最小输出物

无以下任一，不得 KEEP：

1. 实验登记（`experiments/schema.yaml` 字段）  
2. 可审计观测/结果表  
3. 预登记度量与停止条件  
4. 明确 decision  

---

## 3.4 Storage and Provenance（与 Feature Spec Q5 对齐）

Evidence Engine 是 **Evidence Object + Validation Protocol**，不只是存储。

四层存储：

```text
Registry | Feature Artifact | Experiment Manifest | Evidence Store
```

Observation Key（定位 Feature 观测；`parameter_fingerprint` 在 Envelope，不进 FeatureResult）：

```text
sensor_id + sensor_version + parameter_fingerprint
+ symbol + timeframe + timestamp
```

Artifact Provenance：

```text
experiment_id + run_id + code_revision
+ data_fingerprint + environment_fingerprint
```

Experiment Manifest（示例）：

```json
{
  "experiment_id": "exp_20260719_001",
  "sensor_id": "atr_compression",
  "sensor_version": "1.0",
  "parameters": {"atr_window": 14, "baseline_window": 100},
  "parameter_fingerprint": "...",
  "code_revision": "...",
  "data_fingerprint": "...",
  "environment_fingerprint": "...",
  "artifact_refs": [
    {"uri": "runs/run_001/feature_results.parquet", "hash": "..."}
  ]
}
```

目录：

```text
research/output/evidence/<experiment_id>/
├── manifest.json
├── runs/<run_id>/feature_results.parquet
├── outcomes.parquet
├── metrics.json
└── evidence.json
```

规则：进入 Evidence 的 FeatureResult 必须先持久化；临时 Pipeline 可 memory-only；
Artifact append-only；Evidence 用 URI/hash 引用，禁止复制整表；Evidence 不回写 FeatureResult；
Replay 必须恢复五元组（sensor_version、parameter_fingerprint、code、data、environment）。

---

## 4. Validation & Promotion

```text
E0 Idea
 → E1 Single Symbol + CSV
 → E2 Multi Symbol
 → E3 Multi Year / OOS
 → E4 Production Ready（+ 用户确认）
```

| 动作 | 含义 |
|------|------|
| KEEP | 证据支持保留假设；**不**自动 Production |
| REVERT | 证据反对；关闭实验臂；可 VALIDATED（过程可审计）后转 DEPRECATED |
| HOLD | 样本不足或冲突 |

Sensor 治理状态机见 Feature Spec §4：`EXPERIMENT → VALIDATED → CANDIDATE → PRODUCTION → DEPRECATED`。  
PRODUCTION 必须 **Intent + Evidence + Explicit Enablement**。

---

## 5. 与 Feature Sensor / Opportunity 的关系

| 对象 | Evidence 角色 |
|------|----------------|
| Feature Sensor | 提供 observation 数值；本身不是交易信号 |
| Opportunity | 事件假设的载体；可挂多实验 |
| Evidence Engine | 唯一「是否够格晋级」的审计中枢（逻辑上） |

Feature Spec（`FEATURE_SENSOR_SPEC.md`）定义 **如何测**；  
本 Spec 定义 **如何证**。

---

## 6. Engine 职责边界（实现时）

### 6.1 Evidence Engine 可做

- 绑定观测与前向结果  
- 计算预登记度量  
- 写出证据档案  
- 校验 Production 门禁所需 refs  

### 6.2 不可做

- 下单 / 改仓  
- 按收益搜索阈值  
- 改写历史 CSV 语义  
- 自动把 KEEP 写成 PRODUCTION  

---

## 7. v0.3 Removal Window（配合）

Evidence 层落地同期或紧前，执行 Detector Framework 已声明的删除：

1. Registry legacy adapter  
2. Domain `Signal`  
3. Feature 路径 Direction leakage（由 Feature Spec 约束）  

详细清单写入 Decision 015。

---

## 8. Testing Requirements（Accepted 后）

- EvidenceRecord frozen + 序列化往返  
- 无审计输出不得 KEEP  
- Production 门禁：缺 evidence_refs 失败  
- 前视窗口边界单测  
- 不依赖「收益好看」作为断言  

---

## 9. Open Questions — **CLOSED**

| ID | 决议 |
|----|------|
| Q1 | 初版 `evidence_id`:`experiment_id` = 1:1；后期可一对多报告 |
| Q2 | 统一 `EvidenceRecord` + `subject_kind` |
| Q3 | 初版最小度量：RV + `sample_n`；其余扩展 |
| Q4 | 查询 API 延后；先落盘 + schema |
| Q5 | 目录见 §3.4；与 Feature Spec Storage 交叉冻结 |

---

## 10. Freeze Criteria

- [x] Open Questions 关闭或推迟  
- [x] 与 Decision 001/011/013/014/015 一致  
- [x] 明确：Compression 证据 ≠ Breakout 交易规则  
- [x] Feature Spec Accepted 交叉引用无矛盾  
- [x] `docs/README.md` 已索引  

---

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-19 | 0.1.0-draft | 首版 Draft：EvidenceRecord、采集/晋级、与 Feature/Opportunity 边界 |
| 2026-07-19 | 1.0.0 | **Accepted**：Storage/Provenance；Validation Protocol；Open Questions 关闭 |
