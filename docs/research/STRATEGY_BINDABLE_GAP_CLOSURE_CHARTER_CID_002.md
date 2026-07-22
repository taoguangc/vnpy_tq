# Bindable Gap-Closure Charter — CID_002

> **Type**: Gap-Closure Charter（≠ Bindable designation · ≠ Implementation of new risk code · ≠ Backtest）  
> **Status**: **FROZEN** ✓ · **Execution under Delegation-50D** ✓  
> **Charter ID**: `BGC-CID_002-v1`  
> **Date**: 2026-07-22  
> **Authorization**: Delegation-50D（`授权50轮由你决定`）  
> **Parent**: `BPR_CID_002_V0_1` · `VR_CID_002_MECH_V0_1_1` · `SAR_CID_002_V0_7`

## Intent

Close **documentation / contract** gaps that block a reusable consumption interface,
without chasing KEEP or granting Bindable.

```text
Testing Asset  →  Reusable Asset bridge（docs）
        ≠
Bindable stamp
        ≠
Alpha
```

## In scope

```text
• Restate @0.2.0 SAC fields（parameter_manifest · execution_model · architecture）
• Freeze Consumer Contract（dual-surface citation）
• Standing market_scope consumer rule
• Consumption pipeline attestation（Input→…→Execution）
• Design note: Strategy Component vs Risk Controller（no code split yet）
```

## Out of scope

```text
❌ Bindable auto-grant
❌ git commit（user-owned）
❌ New capital multi-symbol Observation（unless later auth）
❌ Detector / exit retune
❌ Context Consumer Experiment
```

## Priority（inherited）

```text
P0  execution_model / architecture / pipeline
P1  repo revision（acknowledge only · no commit）
P2  dual-surface / component split clarity
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-22 | Charter frozen · executed under Delegation-50D |
