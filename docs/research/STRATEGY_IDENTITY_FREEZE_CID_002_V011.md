# Strategy Identity Freeze — STRAT_TREND_BROOKS_SCALP_02@0.1.1

> **Type**: Candidate Identity Freeze（repair lineage）  
> **Status**: **FROZEN** ✓  
> **Freeze ID**: `SIF_CID_002_V0_1_1`  
> **Date**: 2026-07-22  
> **Authorization**: Delegation-50B  
> **Parent**: `SIF_CID_002_V0_1` / `@0.1.0`（immutable）  
> **Engineering**: [`STRATEGY_ENGINEERING_REVIEW_CID_002_ROLLOVER.md`](STRATEGY_ENGINEERING_REVIEW_CID_002_ROLLOVER.md)

## Freeze record

```text
================================================
SIF_CID_002_V0_1_1

strategy_id: STRAT_TREND_BROOKS_SCALP_02
version:     0.1.1
lifecycle:   Verified（H_MECH auditability · E3 · see VR_CID_002_MECH_V0_1_1 + A1）
change:      on_rollover_adjust only
Bindable:    NO
Alpha:       NONE
================================================
```

## Identity fields

| Field | Value |
|-------|--------|
| `strategy_id` | `STRAT_TREND_BROOKS_SCALP_02` |
| `version` | `0.1.1` |
| `source_revision` | `833ae4740e6da3e2e3a42899d2bd4229f61785d6`（G5；source_hash unchanged） |
| `source_hash` | `1877dffe2108ba4237469b52bccc589d479811d4aea82c2764900cf74ad1d4c8` |
| `parameter_hash` | `3ff061891488a9d9f5641cf147efc1e70c8d4cb8410540858d8b727bd485d1ab`（unchanged vs 0.1.0） |
| `market_scope` | `UNBOUND_AT_ASSET` |
| `detector_binding` | `BROOKS_SCALP_FP@0.1.0` |
| `lineage_parent` | `SIF_CID_002_V0_1` |
| `evidence_lineage` | `["STRAT_BS02_EXP005","STRAT_BS02_EXP006","STRAT_BS02_EXP007","STRAT_BS02_EXP011"]` |

### `source_manifest`

```json
[
  {
    "path": "strategies/paaf/brooks_scalp_paaf_strategy.py",
    "sha256": "5cdc3c4fa47e70ae524e3225cbce04787341f227f0c47ad7d9fc95fccb3dfaef"
  },
  {
    "path": "strategies/paaf/brooks_scalp_paaf_strategy_v011.py",
    "sha256": "dec3b51eb326e3bfeb9930752fb945aee9275f58375bee1dc48b7d58843b2bd5"
  },
  {
    "path": "strategies/paaf/detectors/brooks_scalp_first_pullback.py",
    "sha256": "3ffd6a027d92a914e438ccc0e6cc797aa319c9d2a79ec779a29fc74ec8126fad"
  }
]
```

## What this is / is not

```text
IS: Candidate repair identity for rollover price continuity
IS: Mechanism Surface lifecycle Verified（H_MECH · E3）
    after VR_CID_002_MECH_V0_1_1 + A1（EXP011 OOS）
IS NOT: replacement that erases 0.1.0 evidence
IS NOT: Bindable / Alpha / Production / E4 / Capital Surface Verified
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-22 | 0.1.1 Candidate Identity Freeze |
| 2026-07-22 | Lifecycle → Verified（H_MECH · E2）via `VR_CID_002_MECH_V0_1_1` |
| 2026-07-22 | Evidence → E3 via EXP011 / `VR_CID_002_MECH_V0_1_1_A1` |
| 2026-07-22 | G5：`source_revision` → `833ae4740e6da3e2e3a42899d2bd4229f61785d6` |
