---
name: writing-plans
description: Use when turning an agreed direction or spec into a reviewable, step-by-step implementation plan before touching code.
---

# Writing Plans

## Purpose
Convert an agreed design into a concrete, reviewable plan: small tasks, each with exact files, acceptance criteria, and dependencies — so anyone can execute or review it.

## When to use
- A design or spec is agreed and the work spans multiple steps or files.
- Before touching code on a non-trivial change.
- When work will be handed to another agent/engineer (or future you).

**When NOT to use:** a single-file, single-step change with an obvious approach — just do it. If the direction itself is unclear, brainstorm first.

## Method
1. **State objective and scope.** One sentence on what this builds. List what's in scope and, explicitly, what's out.
2. **Map the files first.** Name each file to create/modify and its single responsibility. Files that change together live together. Lock decomposition here.
3. **Decompose into small, reviewable tasks.** Each task is a self-contained change that makes sense on its own. Write for someone with zero context for this codebase.
4. **Give every task acceptance criteria.** Concrete, testable done-conditions: exact commands to run and expected output. Favor TDD — failing test, then minimal code.
5. **Map dependencies.** State task order and what blocks what. Independent tasks can run in parallel.
6. **List risks + mitigations.** For each notable risk, name the mitigation or fallback.
7. **Keep the plan living.** As reality diverges, update the plan deliberately and log what changed and why — don't silently drift.

## Red flags
- Placeholders: "TBD", "handle edge cases", "add error handling", "write tests" with nothing concrete.
- Tasks too big to review (touch many files, do many things at once).
- Acceptance criteria you can't test or verify.
- Inconsistent names/signatures across tasks.
- No scope boundary — unclear what's deliberately excluded.
- Plan never updated as the work reveals new facts.

## Checklist
- [ ] Objective in one sentence; in-scope and out-of-scope listed.
- [ ] File map written, each with one responsibility.
- [ ] Tasks are small and independently reviewable.
- [ ] Every task has concrete, testable acceptance criteria.
- [ ] Dependencies and order explicit.
- [ ] Risks paired with mitigations.
- [ ] No placeholders anywhere.
- [ ] Plan is updatable and changes get logged.
