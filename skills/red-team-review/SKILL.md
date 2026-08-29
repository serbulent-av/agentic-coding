---
name: red-team-review
description: Adversarial correctness review. Use when hunting bugs, edge cases, plan deviations, and security risks in an implementation (Gerald's pass). Read-only — reports findings, does not edit.
---

# Red-team review

Interrogate the code for what it does NOT do:

1. **Plan compliance** — every requirement/acceptance criterion implemented; flag
   deviations and scope creep.
2. **Logic** — control/data flow, state, boundaries (0/1/many, empty/max/overflow),
   error propagation.
3. **Integration** — input validation, API contracts, filesystem, DB.
4. **Security** — injection, authn/authz, data exposure, dependency risk.
5. **Future problems** — implicit assumptions, tight coupling, perf time bombs,
   missing observability. Use `graphify path`/`affected` to trace impact.

## Severity (accurate — never inflate/deflate)

- **CRITICAL** broken/insecure/data-loss → blocks.
- **MAJOR** real gap, likely failure → blocks.
- **MINOR** low risk → may defer. Label theoretical risks as theoretical.

End with `LGTM` (zero CRITICAL/MAJOR) or `BLOCKED` + the must-fix list. Re-reviews
are full reviews: verify each fix resolved the finding and added nothing new.
