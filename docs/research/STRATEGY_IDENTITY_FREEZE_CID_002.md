# Strategy Identity Freeze — CID_002 / STRAT_TREND_BROOKS_SCALP_02

> **Type**: Candidate Identity Freeze（≠ Bindable · ≠ Testing · ≠ Backtest · ≠ Alpha）  
> **Status**: **FROZEN** ✓  
> **Freeze ID**: `SIF_CID_002_V0_1`  
> **Draft ID**: `CID_002_BROOKS_SCALP_PAAF_V0_1`  
> **Date**: 2026-07-22  
> **Authorization**: `Authorize CID_002 Identity Freeze`  
> **Contracts**: `SAC-v1` · `CEMB-v1` · `ADAP-v1` · `PRC-BROOKS_SCALP-v1`  
> **Implementation**: [`STRATEGY_PAAF_REWRITE_IMPLEMENTATION_BROOKS_SCALP.md`](STRATEGY_PAAF_REWRITE_IMPLEMENTATION_BROOKS_SCALP.md)

## Freeze record

```text
================================================
STRATEGY IDENTITY FREEZE — CID_002

strategy_id:     STRAT_TREND_BROOKS_SCALP_02
version:         0.1.0
lifecycle:       Testing（H_MECH evidence Closed KEEP；not Verified/Bindable）
Identity:        FROZEN ✓

Bindable:        NO
Testing:         ACTIVE（mechanism claim under rb/2024）
Verified:        NO
Evidence:        STRAT_BS02_EXP001 Closed KEEP（H_MECH）
Backtest:        EXP001 Observation executed（not Alpha EXP）
Alpha claim:     NONE
================================================
```

## 1. Frozen StrategyIdentity

| Field | Frozen value |
|-------|--------------|
| `strategy_id` | `STRAT_TREND_BROOKS_SCALP_02` |
| `version` | `0.1.0` |
| `source_revision` | `833ae4740e6da3e2e3a42899d2bd4229f61785d6`（G5 commit；source_hash unchanged） |
| `git_anchor_head` | `833ae4740e6da3e2e3a42899d2bd4229f61785d6`（binding bytes first committed） |
| `source_manifest` | see §2 |
| `source_hash` | `3ba12893e43db6805e5af2012d811a7f0034143dbedb102637afd7a5819b9589` |
| `parameter_manifest` | see §3 |
| `parameter_hash` | `3ff061891488a9d9f5641cf147efc1e70c8d4cb8410540858d8b727bd485d1ab` |
| `market_scope` | `UNBOUND_AT_ASSET`（CEMB-v1；every Testing EXP must declare symbols/session/period/data_protocol） |
| `execution_model` | see §4 |
| `evidence_lineage` | `["STRAT_BS02_EXP001","STRAT_BS02_EXP002","STRAT_BS02_EXP003","STRAT_BS02_EXP004"]` |
| `class_tags` | `["trend"]` |
| `context_independence` | `true`（signal path ignores Context v0.1；ContextEngine called for orchestration only） |
| `not_fabricated_for_context` | `true`（rewrite of pre-RC001-B admitted Candidate Source；not built to force Context result） |
| `architecture_attestation` | see §5 |
| `lineage_parent` | `CID_001_BROOKS_SCALP_V0_1` / `STRAT_CAND_001_BROOKS_SCALP_SOURCE` @ `e2bfc0cf390a0a059fc04dce182082009e685a5b` |
| `detector_binding` | `BROOKS_SCALP_FP@0.1.0` |

### Revision pointer rule（uncommitted sources）

```text
Binding modules were untracked at freeze time.
Identity is pinned by source_hash + parameter_hash + manifests.

When the exact same bytes are first committed:
  • source_revision MAY be updated to the full git commit SHA
  • ONLY if recomputed source_hash == frozen source_hash
  • Any byte change → new version + new Identity Freeze（not an in-place edit）
```

## 2. Frozen `source_manifest`

```json
[
  {
    "path": "strategies/paaf/brooks_scalp_paaf_strategy.py",
    "sha256": "5cdc3c4fa47e70ae524e3225cbce04787341f227f0c47ad7d9fc95fccb3dfaef"
  },
  {
    "path": "strategies/paaf/detectors/brooks_scalp_first_pullback.py",
    "sha256": "3ffd6a027d92a914e438ccc0e6cc797aa319c9d2a79ec779a29fc74ec8126fad"
  }
]
```

## 3. Frozen `parameter_manifest`

```json
{
  "atr_period": {"type": "int", "unit": "bars", "value": 20},
  "ema_period": {"type": "int", "unit": "bars", "value": 20},
  "fixed_size": {"type": "int", "unit": "contracts", "value": 1},
  "max_hold_bars": {"type": "int", "unit": "bars", "value": 10},
  "pullback_atr": {"type": "float", "unit": "atr_multiple", "value": 0.2},
  "risk_reward": {"type": "float", "unit": "dimensionless", "value": 1.0},
  "trend_leg_atr": {"type": "float", "unit": "atr_multiple", "value": 1.0}
}
```

Defaults match CID_001 observed defaults（no re-optimization）.

## 4. Frozen `execution_model`

```text
signal_timeframe:     1m
order_style:          stop entry after first-pullback DetectionResult
stop / target:        structural stop + risk_reward·R target（from Detector）
time_stop:            max_hold_bars（Strategy orchestration）
sizing_rule_class:    fixed_size
cost_binding:         PROJECT_FROZEN_DATA_PROTOCOL → docs/07_DATA_SPEC.md v1.0.0
fill_binding:         VNPY_CTA_BACKTEST_ENGINE_DEFAULTS_AT_EXP_REGISTRATION
fee/slippage numbers: not invented at asset freeze（resolved at EXP registration）
```

## 5. Architecture attestation

```text
Target boundary:
  Context → Detector Registry → Risk → Execution → Logger

Attested for this identity:
  ✓ Morphology in Detector（BROOKS_SCALP_FP）
  ✓ Explicit PatternState FSM
  ✓ Strategy orchestrates only（BrooksScalpPaafStrategy）
  ✓ Context not in signal path（v0.1）
  ✓ ADAP T4 rewrite path satisfied for PAAF shape
  ✗ Registry catalog wiring not required for this orchestrator
    （strategy constructs the admitted detector directly）
  ✗ Bindable not claimed（market_scope unbound · evidence empty ·
     git commit of sources pending）
```

## 6. What this Freeze is / is not

```text
IS:
  Frozen Candidate identity for STRAT_TREND_BROOKS_SCALP_02@0.1.0
  Prerequisite for SEVF pre-registration / Observation

IS NOT:
  Bindable Strategy Asset
  Testing / Verified / Production
  Permission to backtest without separate auth
  Alpha / PnL claim
  market_scope symbol selection
```

## 7. Hard guarantees

```text
✓ Identity fields frozen to documented manifests/hashes
✓ No parameter search
✓ No backtest / Observation under this authorization
✓ No Bindable designation
✓ No RC001-B reopen
✓ Legacy CID_001 / strategies/brooks_scalp/ unchanged as reference
```

## Machine record

`research/output/evidence/STRATEGY_IDENTITY_FREEZE_CID_002/identity_freeze.json`

## Next（须另授）

```text
• SEVF Fill / Pre-registration for CID_002（under SEVF_SPEC_CID_002_V0_1）
• SEVF Authorization + Observation
• Commit binding sources without byte drift（optional hygiene）
• Pause Epoch 5
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-22 | CID_002 Candidate Identity Freeze authorized and recorded |
| 2026-07-22 | SEVF Spec `SEVF_SPEC_CID_002_V0_1` specified（Fill/Run still NO） |
| 2026-07-22 | EXP001 Closed KEEP · Evidence Review PASS · Asset Review COMPLETE（Testing · H_MECH retained） |
| 2026-07-22 | G5：`source_revision` → `833ae4740e6da3e2e3a42899d2bd4229f61785d6` |
