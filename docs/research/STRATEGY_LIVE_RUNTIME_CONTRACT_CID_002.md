# Live Runtime Contract — Freeze（CID_002）

> **Type**: Contract Freeze  
> **Status**: **FROZEN** ✓ · **≠ Live trading auth** · **≠ Production Bindable** · **≠ Alpha**  
> **Contract ID**: `LRC-CID_002-v0.1`  
> **Date**: 2026-07-23  
> **Authorization**: `授权你来决定`（chose LRC freeze over container / RISK OOS）  
> **Design/Draft**: [`STRATEGY_LIVE_RUNTIME_CONTRACT_DRAFT_CID_002.md`](STRATEGY_LIVE_RUNTIME_CONTRACT_DRAFT_CID_002.md) · **SUPERSEDED**  
> **Parents**: `DID_CID_002_V0_1` · `EI_CID_002_V0_2` · `CEMB-v1` · `docs/07_DATA_SPEC.md`

## Freeze record

```text
================================================
LRC-CID_002-v0.1

Purpose: Separate research/backtest execution bindings
         from any future live/simulation brokerage path.

Live trading: NOT AUTHORIZED by this freeze
Production Bindable: STILL WITHHELD
Venue evidence pack: STILL REQUIRED before Production Bindable
================================================
```

## Article 1 — Dual path

```text
1.1 Research / backtest path（default for Closed EXPs）:
      CEMB-v1
      docs/07_DATA_SPEC.md @ 1.0.0
      fill_binding = VNPY_CTA_BACKTEST_ENGINE_DEFAULTS_AT_EXP_REGISTRATION

1.2 Live / simulation brokerage path:
      MUST use a distinct declared binding（Article 2）
      MUST NOT silently inherit 1.1 fill/cost assumptions
```

## Article 2 — Live binding MUST declare

```text
When a live/sim path is claimed, pre-declare at minimum:
  · venue / broker identity
  · account class（sim vs funded）
  · order types & session calendar
  · fee / slippage schedule source
  · failover / disconnect policy
  · mapping to EI / DID artifact set（if deployed）
```

## Article 3 — Evidence misuse

```text
3.1 Citing backtest KEEP / Verified stamps as live performance: FORBIDDEN
3.2 Merging MECH Verified + RISK Verified + backtest PnL into “live edge”: FORBIDDEN
3.3 Production Bindable requires:
      this contract cited
      AND a venue binding evidence pack
      AND remaining PBDR residuals addressed
```

## Article 4 — Modification

```text
4.1 This contract is FROZEN.
4.2 Rule changes → LRC-CID_002-v0.2（new freeze）· no silent rewrite.
4.3 Freeze ≠ go-live permission.
```

## P5 verdict

```text
P5 documentary contract: CLOSED（this freeze）
P5 venue evidence pack:  OPEN（blocks Production Bindable）
```

## Explicit non-grants

```text
❌ Live trading / sim go-live
❌ Production Bindable / E4
❌ Alpha
❌ Container digest
❌ RISK OOS Observation
```

## Next（须另授）

```text
Venue binding evidence pack
  — OR — Container/image digest
  — OR — RISK OOS E3
  — OR — remain paused
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-23 | LRC-CID_002-v0.1 FROZEN from draft |
