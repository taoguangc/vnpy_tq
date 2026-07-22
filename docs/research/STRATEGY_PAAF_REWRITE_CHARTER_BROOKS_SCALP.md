# PAAF Rewrite Charter — STRAT_TREND_BROOKS_SCALP_01（Design Only）

> **Type**: Rewrite Charter Design → Confirmation → Freeze as **design boundary**  
> **Status**: **CHARTER FROZEN** ✓ · **Implementation AUTHORIZED（path B）· v0.1.0 DELIVERED**  
> **Charter ID**: `PRC-BROOKS_SCALP-v1`  
> **Date**: 2026-07-22  
> **Authorization**: Twenty-round delegated decision — decisions 12–15；implementation = user path **B**  
> **Lineage parent**: CID_001 / `STRAT_CAND_001_BROOKS_SCALP_SOURCE`  
> **ADAP**: T4 REQUIRE_PAAF_REWRITE for Bindable  
> **Implementation record**: [`STRATEGY_PAAF_REWRITE_IMPLEMENTATION_BROOKS_SCALP.md`](STRATEGY_PAAF_REWRITE_IMPLEMENTATION_BROOKS_SCALP.md)  
> **Rewrite identity draft**: [`STRATEGY_CANDIDATE_IDENTITY_DRAFT_002.md`](STRATEGY_CANDIDATE_IDENTITY_DRAFT_002.md)

## Charter record

```text
================================================
PRC-BROOKS_SCALP-v1

Charter: FROZEN（design boundary）
Implementation: AUTHORIZED · v0.1.0 DELIVERED（STRAT_TREND_BROOKS_SCALP_02）
Backtest: NOT AUTHORIZED by charter alone（still requires separate auth）
================================================
```

## 1. Research intent

Preserve the **observable hypothesis class** of the admitted Candidate Source:

```text
1m trend-leg detection → pullback → stop entry → 1R + time stop
```

without carrying forward the legacy architecture that blocks Bindable status.

```text
Hypothesis continuity
        ≠
byte-identical restore
        ≠
PnL continuity claim
```

## 2. Required target architecture

```text
Market Data
  → Context（optional consumer later；not inside signal path）
  → Detector Registry（pullback / trend-leg detection）
  → Risk（stop / target / time stop / size）
  → Execution
  → Logger
```

Legacy `CtaTemplate` monolith is **out of charter** for the Bindable lineage.

## 3. Identity rules for rewrite

```text
New strategy_id required（must not reuse STRAT_TREND_BROOKS_SCALP_01
  as if it were the legacy bytes）

Recommended pattern:
  STRAT_TREND_BROOKS_SCALP_02（or _PAAF_01）
  version 0.1.0
  parent= CID_001 / STRAT_CAND_001 / source_revision e2bfc0c…

New source_manifest / parameter_manifest / hashes mandatory
```

## 4. Parameter policy

```text
Defaults may start from CID_001 observed defaults
Any change → new parameter_hash + new experiment
No optimization search authorized by this charter
```

## 5. Explicit non-authorizations（charter text；superseded in part by path B）

```text
❌（charter-era）Implement detectors / strategy code now → SUPERSEDED by path B
❌ Run backtest / Observation without separate auth
❌ Claim rewrite improves returns
❌ Skip SEVF-v1 pre-registration later
❌ Reopen RC001-B
```

## 6. Implementation gate

```text
Authorize PAAF Rewrite Implementation for PRC-BROOKS_SCALP-v1
→ GRANTED 2026-07-22（user path B）
→ Delivery: STRATEGY_PAAF_REWRITE_IMPLEMENTATION_BROOKS_SCALP.md
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-22 | Rewrite Charter frozen as design boundary; implementation withheld |
| 2026-07-22 | Path B · implementation v0.1.0 delivered |
