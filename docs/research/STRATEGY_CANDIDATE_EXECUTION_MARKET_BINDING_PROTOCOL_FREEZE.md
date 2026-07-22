# Candidate Execution and Market-Scope Binding Protocol — `CEMB-v1`

> **Type**: Protocol Design → Confirmation → Freeze  
> **Status**: **FROZEN** ✓  
> **Protocol ID**: `CEMB-v1`  
> **Date**: 2026-07-22  
> **Authorization**: Twenty-round delegated decision — decisions 5–8  
> **Parents**: `SAC-v1` · `SCIDR-v1` · `docs/07_DATA_SPEC.md`

## Purpose

Complete Candidate Identity Draft fields that must not invent symbol universes or fee numbers, while still binding formal research to the frozen data baseline.

## Frozen rules

### Market scope

```text
Asset-level market_scope may be:
  UNBOUND_AT_ASSET

Meaning:
  Identity Draft / even Identity Freeze（if later granted）must require
  every Testing experiment to pre-declare:
    symbols · session · period · data_protocol_version

Inventing a preferred symbol list for CID_001: FORBIDDEN
```

### Cost / fill / slippage

```text
execution_model.cost_binding =
  PROJECT_FROZEN_DATA_PROTOCOL

Pointers（immutable references）:
  • docs/07_DATA_SPEC.md — TQ offline · 1m · CbC · unadjusted · real costs
  • Engine profile costs resolved at experiment registration from project
    symbol cost tables / backtest harness（not invented in this draft）

Strategy module need not embed fee constants.
Identity Freeze still requires this binding to be present and version-pinned.
```

### Fill assumptions

```text
fill_binding = VNPY_CTA_BACKTEST_ENGINE_DEFAULTS_AT_EXP_REGISTRATION
Must be named in Run Spec; not silently assumed after the fact.
```

## CID_001 application（decision 8）

| Field | Updated draft value |
|-------|---------------------|
| `market_scope` | `UNBOUND_AT_ASSET`（EXP must declare） |
| `execution_model.cost_binding` | `PROJECT_FROZEN_DATA_PROTOCOL` → `docs/07_DATA_SPEC.md` v1.0.0 |
| `execution_model.fill_binding` | `VNPY_CTA_BACKTEST_ENGINE_DEFAULTS_AT_EXP_REGISTRATION` |
| fee/slippage numeric constants | **not invented** |

## Revision record

| Date | Change |
|------|--------|
| 2026-07-22 | `CEMB-v1` frozen; applied to CID_001 |
