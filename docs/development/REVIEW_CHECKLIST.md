# Pre-Merge Review Checklist

**Status:** Active  
**Authority:** Engineering practice (not an ADR)  
**Applies from:** `architecture-baseline-v1`

Before merge（含单人本地提交视为 merge 门禁时），回答下列三问。

## Checklist

```text
□ Does this change require a new Decision?

□ Does this change violate any Accepted Contract?

□ Does this change modify Architecture Baseline v1?
```

## Default answers

```text
No
No
No
```

## If any answer is Yes

**Stop merge.** Re-open Decision / Contract / ABR scope before continuing.

## Notes

- This checklist does **not** authorize new foundation Contracts.
- Cursor rules may automate reminders; **this document is the source of truth**.
- Baseline reference: `docs/releases/architecture-baseline-v1.md`
