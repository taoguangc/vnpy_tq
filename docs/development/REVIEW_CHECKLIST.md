# Pre-Merge / Sprint Gate Checklist

**Status:** Active  
**Authority:** Engineering practice (not an ADR)  
**Applies from:** `architecture-baseline-v1`

## Pre-Merge Checklist

Before merge（含单人本地提交视为 merge 门禁时），回答下列三问。

```text
□ Does this change require a new Decision?

□ Does this change violate any Accepted Contract?

□ Does this change modify Architecture Baseline v1?
```

Default answers: `No` / `No` / `No`.  
If any Yes → **Stop merge.**

## Sprint Start Check

Before starting any Platform Construction Sprint:

```text
1. What existing Contract does this consume?

2. What Evidence/Capability gap does it solve?

3. Why cannot this wait?

4. Does it modify Baseline?
```

Ideal answers:

```text
Consumes existing Contract: Yes
Solves identified gap: Yes
Cannot wait: Explained
Baseline change: No
```

If item 4 is Yes → Decision / Contract flow first; do not open the Sprint.

## Notes

- Does **not** authorize new foundation Contracts.
- Cursor rules may remind; **this document is the source of truth**.
- Epoch 1 Stable Checkpoint: `docs/releases/EPOCH_1_SUMMARY.md`
