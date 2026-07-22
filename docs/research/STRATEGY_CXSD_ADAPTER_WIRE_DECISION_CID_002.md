# CXSD Adapter Wire Decision — Epoch 6

> **Type**: Scoped decision under `授权你来决定`  
> **Status**: **COMPLETE** ✓ · **STOP**  
> **Date**: 2026-07-22  
> **Choice**: Wire CXSD into Context Filter adapter · **not** Production Bindable Re-review

## Path

```text
1. Wire CXSD-v0.1 gate + audit into BrooksScalpCtxFilterV011
2. Unit tests PASS（11）
3. Self-check PASS
4. STOP

NOT done:
  ❌ Production Bindable grant
  ❌ Backtest Observation
  ❌ G5 binding byte mutation
  ❌ Alpha claim
```

## Result

```text
Adapter emits _cxsd_audit_events with full lineage.
F1 rule unchanged（expansion-only）.
G5 strategy/detector bytes untouched.
```

## Next（须另授）

```text
Production Bindable Re-review
  — OR — Pause Epoch 6
```

## Revision record

| Date | Change |
|------|--------|
| 2026-07-22 | Wire COMPLETE · STOP |
