# Bindable Designation Docket — CID_002（pre-packaged）

> **Type**: Designation Docket（≠ Bindable grant）  
> **Status**: **PACKAGED** ✓ · **Designation GRANTED** via `BDR_CID_002_V0_1`  
> **Docket ID**: `BDD_CID_002_V0_1`  
> **Date**: 2026-07-22  
> **Authorization**: Delegation-100F  
> **Designation**: [`STRATEGY_BINDABLE_DESIGNATION_CID_002.md`](STRATEGY_BINDABLE_DESIGNATION_CID_002.md)  
> **Parents**: `BRN_CID_002_V0_1` · `BPR_CID_002_V0_2` · `E5P_V0_1`

## Purpose

When G5 clears and user authorizes designation review, this docket is the
single intake package — so the review does not rediscover the ledger.

```text
PACKAGED ≠ GRANTED
```

## Proposed designation objects（must stay dual-surface）

| Object | Identity | Proposed class if granted later |
|--------|----------|----------------------------------|
| Mechanism surface | `STRAT_TREND_BROOKS_SCALP_02@0.1.1` · `SIF_CID_002_V0_1_1` | Bindable **Research Mechanism Asset**（H_MECH Verified · E2） |
| Risk surface | `STRAT_TREND_BROOKS_SCALP_02@0.2.0` · `SIF_CID_002_V0_2_0` | Bindable **Capital-Gated Research Consumer**（not Alpha） |

```text
Do not collapse into one Bindable blob.
CC-CID_002-v1 remains mandatory.
```

## Intake checklist

| # | Item | Pointer | Pre-G5 |
|---|------|---------|--------|
| 1 | MECH Verified | `VR_CID_002_MECH_V0_1_1` | ✓ |
| 2 | RISK capital portable | EXP009 · EXP010 | ✓ |
| 3 | Consumer Contract | `CC-CID_002-v1` | ✓ |
| 4 | Pipeline attestation | `CPA_CID_002_V0_1` | ✓ |
| 5 | SAC fields @0.2.0 | `SIF_CID_002_V0_2_0` amended | ✓ |
| 6 | Gap board G0–G4/G6/G7 | closed/mitigated | ✓ |
| 7 | **G5 commit + source_revision update** | user | ✓ `833ae47…` |
| 8 | Explicit designation auth | user | ✓ `BDR_CID_002_V0_1` |

## G5 commit checklist（user-owned）

Binding paths（LF · hashes must still match after commit）:

| path | expected sha256 |
|------|-----------------|
| `strategies/paaf/brooks_scalp_paaf_strategy.py` | `5cdc3c4fa47e70ae524e3225cbce04787341f227f0c47ad7d9fc95fccb3dfaef` |
| `strategies/paaf/brooks_scalp_paaf_strategy_v011.py` | `dec3b51eb326e3bfeb9930752fb945aee9275f58375bee1dc48b7d58843b2bd5` |
| `strategies/paaf/brooks_scalp_paaf_strategy_v020.py` | `3723f01a24b139495587744b77f4b031751926e1fbca2c588b4c8347c9e79b1c` |
| `strategies/paaf/detectors/brooks_scalp_first_pullback.py` | `3ffd6a027d92a914e438ccc0e6cc797aa319c9d2a79ec779a29fc74ec8126fad` |

Aggregate freezes to re-check after commit:

| Freeze | source_hash |
|--------|-------------|
| `@0.1.1` `SIF_CID_002_V0_1_1` | `1877dffe2108ba4237469b52bccc589d479811d4aea82c2764900cf74ad1d4c8` |
| `@0.2.0` `SIF_CID_002_V0_2_0` | `5c089251ac301cf7d5c8f72c25960d5a1e50b90907319d0e6bd54fa3880e2499` |

```text
After commit:
  • If recomputed source_hash == frozen → MAY set source_revision = full git SHA
  • If hash drifts → new version + new freeze（do not silently edit）
```

Verified at packaging time（2026-07-22）: all four files exist · LF-only · sha256 match table above.

## Explicit non-grants in this docket（historical at packaging）

```text
At packaging time: Bindable WITHHELD.
Superseded 2026-07-22 by BDR_CID_002_V0_1（GRANTED dual-surface）.
Still not granted by docket alone: Alpha · Production · Context routing permission.
```

## Wake

```text
Authorize Bindable Designation Review  → DONE（BDR_CID_002_V0_1）
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-22 | Docket packaged under Delegation-100F |
| 2026-07-22 | Designation GRANTED · linked to BDR_CID_002_V0_1 |
