# Architecture Deviation Acceptance Protocol — `ADAP-v1`

> **Type**: Protocol Design → Confirmation → Freeze（combined under delegated authority）  
> **Status**: **FROZEN** ✓  
> **Protocol ID**: `ADAP-v1`  
> **Date**: 2026-07-22  
> **Authorization**: Twenty-round delegated decision — decisions 1–4  
> **Applies to**: Candidate Identity Drafts with `architecture_status = declared_deviation`

## Freeze record

```text
ADAP-v1: FROZEN ✓
Confirmation: PASS ✓
Implementation / Restore / Backtest: NONE
```

## Purpose

Decide how a legacy architecture deviation may be accepted **without** pretending the asset conforms to the PAAF target boundary.

```text
declared_deviation acceptance
        ≠
architecture conformity
        ≠
Bindable
```

## Acceptance tiers（frozen）

| Tier | Label | Meaning | Allowed later states |
|------|-------|---------|----------------------|
| **T0** | `REJECT` | Deviation incompatible（e.g. embedded Context in signal path） | none |
| **T1** | `ACCEPT_CANDIDATE_ONLY` | Deviation disclosed; Candidate / Identity Draft allowed | Candidate · Draft |
| **T2** | `ACCEPT_TESTING_LEGACY` | Legacy may enter Testing under SEVF-v1 with deviation locked in attestation | Testing · Verified（scope-limited） |
| **T3** | `ACCEPT_BINDABLE_LEGACY` | Explicit user acceptance that Bindable may remain non-conformant | Bindable（rare；must be user-explicit） |
| **T4** | `REQUIRE_PAAF_REWRITE` | No Bindable on legacy bytes; rewrite required for Bindable path | rewrite lineage only |

Default for legacy `CtaTemplate` encapsulating pattern + risk + execution:

```text
Maximum without new user auth: T2 ACCEPT_TESTING_LEGACY
Bindable on legacy bytes: FORBIDDEN unless user grants T3
Recommended Bindable path: T4 REQUIRE_PAAF_REWRITE
```

## CID_001 application（decision 4）

```text
Object: STRAT_TREND_BROOKS_SCALP_01 / CID_001
Deviation: legacy CtaTemplate FSM encapsulates pattern + entry + exits
Context: independent（SCAP）

ADAP outcome:
  T2 ACCEPT_TESTING_LEGACY
  + T4 REQUIRE_PAAF_REWRITE for Bindable

Therefore:
  Identity Draft: allowed
  Future Testing（if Identity Freeze later）: allowed with deviation locked
  Bindable on these exact bytes: BLOCKED
  Bindable requires PAAF rewrite lineage（new strategy_id / hashes）
```

## Forbidden

```text
❌ Silent upgrade T2 → T3
❌ Treat T2 as architecture conformity
❌ Use ADAP to authorize restore / rewrite / backtest
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-22 | `ADAP-v1` frozen; CID_001 rated T2 + T4 |
