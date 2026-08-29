---
name: code-review
description: Oversight review for quality, simplicity, and documentation. Use when reviewing an implementation for over-engineering, readability, and docs quality (Sohne's pass). Read-only — reports findings, does not edit.
---

# Code review (oversight)

Three passes, calibrated to context (prototype vs production vs library):

1. **Newcomer test (docs)** — README/module docs/why-comments let a fresh reader
   understand what + why. Missing or insider-only docs are findings.
2. **Simplicity (anti-bloat)** — unnecessary abstraction, premature generalization,
   layer-cake architecture, over-built error handling, dead code. Unnecessary
   complexity is a defect.
3. **Craft** — readability, single responsibility, proportionate error handling,
   idiomatic, consistent.

## Report format (specific + actionable)

```
[Critical|Warning|Suggestion] <file:line> — <problem> — <concrete fix>
```

Block only on Critical/Warning. Pragmatism over perfection — sign off (`LGTM`) when
the code is good enough for its goal. Use `graphify query` to check coupling/structure.
