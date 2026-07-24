# Delegation-25BH Execution Log

> Status: **STOP** · Date: 2026-07-24 · Authorization: bare grant `授权你决定25次` → agent Option **H_EDGE after H_MECH KEEP (CID_014)**

## Decision

Post-`STRAT_SZL_EXP001` KEEP → run H_EDGE EXP002 (rb/2024) + EXP003 (rb/2025 OOS) under frozen hashes/gates.

## Executed

1. Scripts `scripts/run_strat_szl_exp002.py` / `scripts/run_strat_szl_exp003.py`
2. Hash gate MATCH both runs
3. EXP002 **REVERT** (n_gate=105, share=0.276, mean_net=-45.14)
4. EXP003 **REVERT** (n_gate=77, share=0.402, mean_net=-28.38)
5. Docs: H_EDGE design · SEVF · AERC Alpha NONE · CPD Pause
6. Campaign pointers updated (CID_003–014 PAUSED)

## Not executed

- Retune · Alpha claim · reopen Closed EXP · merge with CID_013

## STOP boundary

CID_014 closed Alpha NONE + Paused. Next bare grant ≠ auto new Spec; prefer NSAD or explicit resume only.

Timestamp (UTC): 2026-07-24T02:13:48Z
