# Campaign Pause Decision — CID_014

> Status: **PAUSED** · Date: 2026-07-24 · ID: `CPD_CID_014`
> Authorization: **Delegation-25BH Observation**
> Campaign: CID_014 · Asset: `STRAT_SMC_ZSCORE_LONG_01@0.1.0`

## Pause reason

H_EDGE REVERT ×2 after H_MECH KEEP ? `AERC_CID_014` Alpha NONE.

## Frozen ledger

| Item | Value |
|------|-------|
| Morph Spec | `SMC_ZSCORE_LONG_MS_V0_1` |
| Freeze | `SIF_CID_014_V0_1` |
| source_hash | `d7b25017…c55830ec14` |
| parameter_hash | `de4e92d2…59109836` |
| H_MECH | STRAT_SZL_EXP001 KEEP |
| H_EDGE | EXP002 REVERT · EXP003 REVERT |
| Alpha | NONE (`AERC_CID_014`) |

## Closed experiment_ids (immutable)

`STRAT_SZL_EXP001` · `STRAT_SZL_EXP002` · `STRAT_SZL_EXP003`

## Resume conditions (explicit only)

- New NSAD with distinct asset identity / Spec, **or**
- User-authorized new campaign with new `experiment_id`s
- **Not** retune of zscore/VWAP under Closed ids

## STOP

Delegation-25BH Observation complete. No further CID_014 runs under this grant.
