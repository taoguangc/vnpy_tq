# Context eXecution Safety Contract — Freeze（CID_002）

> **Type**: Contract Freeze  
> **Status**: **FROZEN** ✓ · **NOT IMPLEMENTED** · **≠ Alpha** · **≠ Production**  
> **Contract ID**: `CXSD-CID_002-v0.1`  
> **Date**: 2026-07-22  
> **Authorization**: `Authorize Context Safety Definition Contract Freeze`  
> **Design**: [`STRATEGY_CONTEXT_EXECUTION_SAFETY_DEFINITION_CID_002.md`](STRATEGY_CONTEXT_EXECUTION_SAFETY_DEFINITION_CID_002.md) · `CXSD_CID_002_V0_1`  
> **Supersedes draft**: [`STRATEGY_CONTEXT_EXECUTION_SAFETY_CONTRACT_DRAFT_CID_002.md`](STRATEGY_CONTEXT_EXECUTION_SAFETY_CONTRACT_DRAFT_CID_002.md) · `CXSD-CID_002-v0.1-DRAFT`  
> **Parents**: `LCF_CID_002_V0_1` · `ACL_CID_002_V0_1` · `CC-CID_002-v1` · Decision 019

## Freeze record

```text
================================================
CXSD-CID_002-v0.1

Status:     FROZEN
Purpose:    Consumption-constraint rules for Context execution
Applies:    When Context is attached to CID_002 consumers
Alpha:      NONE
Production: NO
Impl:       NOT mandated by this freeze
================================================
```

## Article 1 — Identity

```text
1.1 Only listed Consumer IDs may read ContextState
    （CXSD_CID_002_V0_1 Design §2.1）.
1.2 Detector MUST NOT read ContextState for detection logic.
1.3 Strategy orchestrators MUST NOT read ContextState directly;
    they may only receive ALLOW/BLOCK from a Filter adapter.
1.4 Every claim MUST cite CC-CID_002-v1 Surface ID（MECH|RISK）.
```

## Article 2 — Permissions

```text
2.1 Legal permissions: ALLOW | BLOCK | MONITOR.
2.2 Filter / Permission roles emit ALLOW or BLOCK on an existing
    DetectionResult path only.
2.3 MONITOR never alters orders, size, stops, or targets.
2.4 Unknown permission → BLOCK on trading path.
```

## Article 3 — Forbidden actions

```text
3.1 Context stack MUST NOT generate signals, orders, or sizing.
3.2 Context stack MUST NOT modify DetectionResult fields.
3.3 Context stack MUST NOT mutate G5 binding bytes.
3.4 Reports MUST NOT merge Context effects into unlabeled Alpha/PnL claims.
```

## Article 4 — Interfaces

```text
4.1 Allowed read API intent: context.get_state() → ContextState.
4.2 Allowed gate API intent: filter.decide(signal, state) → permission.
4.3 Forbidden API intents include:
      modify_signal · modify_position · generate_order · set_size
4.4 Risk Modifier role is OUT OF SCOPE for v0.1
    （requires CXSD-CID_002-v0.2 or later）.
```

## Article 5 — Failure

```text
5.1 invalid / missing / degraded / unsupported → BLOCK trading path.
5.2 MONITOR streams may record gaps without enabling entries.
5.3 Strategy identity hash mismatch → ABORT（no outcome evaluation）.
```

## Article 6 — Audit

```text
6.1 Every ALLOW/BLOCK/MONITOR event MUST write Design §2.6 fields,
    including cxsd_version = CXSD-CID_002-v0.1 when claiming compliance.
6.2 Absence of audit lineage invalidates CXSD-compliance claims.
6.3 PnL / Sharpe MUST NOT be primary CXSD compliance gates.
```

## Article 7 — Modification

```text
7.1 This contract is FROZEN.
7.2 Any rule change → CXSD-CID_002-v0.2（new freeze）· no silent rewrite.
7.3 Freeze does not authorize implementation, Observation, or Production.
```

## Normative binding

```text
When a research run claims CXSD compliance under CID_002:
  MUST satisfy Articles 1–6 and cite this Contract ID.

Non-compliance → cannot claim CXSD-safe Context consumption.
```

## Explicit non-grants

```text
❌ Implementation mandate
❌ Production Bindable / Production Readiness
❌ Strategy / F1 / Detector / Alpha changes
❌ Backtest / Observation authorization
❌ Risk Modifier in-scope for v0.1
❌ Capability upgrade of Context tags
```

## Next（须另授 · optional）

```text
A. Pause / Epoch 5 closure（recommended default）
B. CXSD implementation charter（adapter conformance only · still no Alpha）
C. Production Bindable Re-review（still blocked on other residuals）
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-22 | CXSD-CID_002-v0.1 FROZEN from v0.1-DRAFT |
