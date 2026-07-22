# Execution Identity Freeze — CID_002（M1）

> **Type**: Execution Identity / Runtime Contract Freeze  
> **Status**: **FROZEN** ✓  
> **Freeze ID**: `EI_CID_002_V0_1`  
> **Date**: 2026-07-22  
> **Authorization**: Bindable Maturity Gap Closure Pack · `BMGCP_CID_002_V0_1`  
> **Parents**: `CEMB-v1` · G5 `833ae474…` · `docs/07_DATA_SPEC.md` v1.0.0 · `AMR_CID_002_V0_1` M1

## Purpose

```text
Close AMR M1: content hash alone is insufficient.
Bind: repo revision + build environment pin + runtime contract.
```

## 1. Repo identity（binding surface）

| Field | Value |
|-------|--------|
| `binding_source_revision` | `833ae4740e6da3e2e3a42899d2bd4229f61785d6`（G5） |
| MECH `source_hash` | `1877dffe2108ba4237469b52bccc589d479811d4aea82c2764900cf74ad1d4c8` |
| MECH `parameter_hash` | `3ff061891488a9d9f5641cf147efc1e70c8d4cb8410540858d8b727bd485d1ab` |
| RISK `source_hash` | `5c089251ac301cf7d5c8f72c25960d5a1e50b90907319d0e6bd54fa3880e2499` |
| RISK `parameter_hash` | `7ff1fe9976ba809dce8f38325c33e6b7bf11a0817b2dce6d372f32258a7da346` |

```text
Any consumer citing EI_CID_002_V0_1 MUST re-verify source_hash
against G5 blobs before evaluation.
Mismatch → abort（do not evaluate）.
```

## 2. Build environment pin（research workstation snapshot）

Captured at freeze time on the authorizing research host:

| Field | Frozen value |
|-------|----------------|
| `os` | Windows-10-10.0.19044-SP0 |
| `python` | 3.13.13 |
| `vnpy` | 4.4.0 |
| `vnpy_ctastrategy` | 1.4.1 |
| `interpreter` | `.venv/Scripts/python.exe`（repo-local venv） |
| `freeze_capture_commit` | `dfe679b5d9ab35073e818c4a554b870d42def570`（docs trail tip at capture） |

```text
This pin documents the research runtime used for CID_002 Closed EXPs.
It is NOT a Production deployment certificate.
Drift requires a new EI version（EI_CID_002_V0_2）or an explicit
declared independent environment experiment.
```

## 3. Runtime contract（research backtest）

```text
host:                 vn.py CtaTemplate / BacktestingEngine
                      （RolloverBacktestingEngine for CbC EXPs）
interval:             1m
data_protocol:        docs/07_DATA_SPEC.md @ 1.0.0
cost_binding:         PROJECT_FROZEN_DATA_PROTOCOL（CEMB-v1）
fill_binding:         VNPY_CTA_BACKTEST_ENGINE_DEFAULTS_AT_EXP_REGISTRATION
order_semantics:      stop entry · same-bar stop-before-target（project coding style）
market_scope:         UNBOUND_AT_ASSET（EXP must declare symbols/period/capital）
surface_selection:    MUST name CC-CID_002-v1 Surface ID（MECH | RISK）
context_adapter:      outside G5 binding bytes when used
                      （strategies/paaf/context_consumer/*）
```

### Forbidden silent assumptions

```text
❌ Live brokerage identity
❌ Zero-cost / adjusted continuous as formal baseline
❌ Merging MECH KEEP with RISK KEEP into one PnL story
❌ Treating Context Filter adapter as part of G5 source_hash
```

## 4. Closure verdict（M1）

```text
AMR M1 documentary gap: CLOSED
Bindable maturity upgrade: NOT granted by this freeze
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-22 | EI_CID_002_V0_1 FROZEN |
