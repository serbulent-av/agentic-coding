---
name: refactoring
description: Use when restructuring code without changing its observable behavior.
---

# Refactoring

## Purpose
Improve internal structure — readability, naming, duplication — while keeping observable behavior identical.

## When to use
- Splitting a large function, renaming for clarity, or removing duplication.
- Cleaning up messy code before adding a feature (refactor first, then change).
- Untangling structure so a later change becomes easy.

When NOT to use: when you intend to change behavior — that is a feature or bugfix, do it as a separate step. Also stop if there is no test coverage and no cheap way to add it; build the safety net first.

## Method
1. Go green first. Run the test suite; it MUST pass before you touch anything.
2. Pick one transformation. Choose a single move — rename, extract, inline, relocate.
3. Take the smallest step. Apply that one change in the most reversible way.
4. Re-verify. Re-run tests: green keeps the step, red reverts it immediately.
5. Commit the step. Lock in each small win before starting the next.
6. Repeat one at a time. Never batch unrelated transformations together.

## Red flags
- Tests were red or absent when you started — stop and fix the net first.
- "While I'm here I'll just tweak this behavior" — that is scope creep.
- Restructuring and changing logic in the same step — you can't tell which broke it.
- A large multi-file rewrite with no intermediate green checkpoint.
- Public signatures, return shapes, or side effects shifting — callers will break.

## Checklist
- [ ] Tests were green before starting.
- [ ] Each step was a single transformation, verified on its own.
- [ ] Public contract (signatures, return shapes, side effects) is unchanged.
- [ ] Tests are green after, with no assertions loosened to pass.
- [ ] Behavior is observably identical to before.
