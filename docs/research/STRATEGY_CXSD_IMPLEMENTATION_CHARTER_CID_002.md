# CXSD Implementation Charter — CID_002

> **Type**: Implementation Charter（≠ Implementation · ≠ Observation · ≠ Alpha）  
> **Status**: **CHARTERED** ✓ · **Implementation NOT AUTHORIZED**  
> **Charter ID**: `CXSDIC_CID_002_V0_1`  
> **Date**: 2026-07-22  
> **Authorization**: Delegation-50L（Theme A under Epoch 6）  
> **Contract**: `CXSD-CID_002-v0.1` **FROZEN**  
> **Design**: `CXSD_CID_002_V0_1`  
> **Parents**: `ACL_CID_002_V0_1` · `E6A_V0_1` · `E5RC_V0_1`

## Charter record

```text
================================================
CXSDIC_CID_002_V0_1

Purpose: Define how to implement CXSD-v0.1 conformance tooling
         without turning Context into Alpha.

Implementation: NOT AUTHORIZED by this charter
Code / tests / backtests: NONE under this auth
Alpha / Production: NONE / NO
================================================
```

## 1. Goal

```text
Make “CXSD-safe consumption” machine-checkable and auditable
for research runs that attach Context to CID_002 consumers.
```

## 2. In-scope modules（when Implementation later authorized）

| Module | Responsibility |
|--------|----------------|
| Interface validator | Enforce allowed API intents（`get_state` · `decide`） |
| ACL checker | Enforce Consumer Identity + call rules vs `ACL_CID_002_V0_1` / CXSD Arts 1–4 |
| Runtime audit | Emit Design §2.6 lineage fields on ALLOW/BLOCK/MONITOR |
| Violation detector | Flag F1–F8 forbidden actions / fail-open trading path |
| Evidence exporter | Write compliance evidence JSON/CSV under `research/output/evidence/` |

## 3. Evaluation criteria（ONLY）

```text
KEEP / PASS for implementation work means:
  · Contract Compliance
  · Auditability
  · Failure Safety（fail closed on trading path）

NEVER:
  · PnL ↑ · Sharpe ↑ · DD ↓ · win rate
```

## 4. Explicit out of scope

```text
❌ Context scoring / regime Alpha
❌ Position sizing from Context
❌ Entry optimization
❌ PnL optimization / parameter search
❌ Modify BROOKS_SCALP_FP / F1 rules
❌ Mutate G5 binding bytes
❌ Production Bindable auto-grant
❌ Risk Modifier（CXSD v0.1 out of scope → needs v0.2）
```

## 5. Proposed package layout（design only）

```text
strategies/paaf/cxsd/          # or scripts/cxsd/
  validate_interface.py
  check_acl.py
  audit_schema.py
  detect_violations.py
  export_evidence.py

tests/cxsd/
  test_forbidden_apis.py
  test_fail_closed.py
  test_audit_fields.py
```

```text
Layout is indicative. No files created under this charter.
```

## 6. Conformance claim rule

```text
A run may claim “CXSD-CID_002-v0.1 compliant” only if:
  1. Contract ID cited
  2. Audit lineage complete
  3. No violation detector hits on forbidden actions
  4. Surface ID（CC）named
  5. Strategy identity hashes verified（VMP/EI）
```

## 7. Gate to implement

```text
Authorize CXSD Implementation
  （implies code + tests under this charter bounds）
```

## Hard guarantees

```text
✓ No code shipped under Delegation-50L
✓ No Observation / backtest
✓ CXSD-CID_002-v0.1 not silently rewritten
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-22 | CXSDIC_CID_002_V0_1 CHARTERED · Impl NOT AUTHORIZED |
