---
name: test-driven-development
description: Use when implementing any new behavior or bugfix, before writing implementation code.
---

# Test-Driven Development

## Purpose
Write the test first, watch it fail, then write the minimal code to pass. If you didn't watch it fail, you don't know it tests the right thing.

## When to use
- Any new feature, behavior change, or bug fix, before writing implementation.
- Refactoring (tests must already exist and stay green).

**When NOT to use:** throwaway prototypes, generated code, or pure config. If you explored with throwaway code, delete it and restart under TDD.

## Method
**No production code without a failing test first.** Wrote code before the test? Delete it and start fresh — don't "adapt" it.

Run one behavior per cycle:
1. **RED — write one failing test.** One behavior, clear name, real code (avoid mocks unless unavoidable). Express the API you wish existed.
2. **Verify RED — run it, watch it fail.** Mandatory. Confirm it *fails* (not errors) and for the *expected reason* (feature missing, not a typo). Passes already? It tests existing behavior — fix the test.
3. **GREEN — minimal code to pass.** Simplest thing that works. No extra options, no speculative features, no refactoring other code.
4. **Verify GREEN — run it, watch it pass.** This test passes, all others still pass, output is clean (no warnings).
5. **REFACTOR — clean up while green.** Remove duplication, improve names, extract helpers. Add no behavior. Keep tests green.
6. **Repeat** with the next failing test for the next behavior.

For bugs: write a failing test that reproduces the bug first; the fix turns it green and guards against regression.

## Red flags
- Writing implementation before a failing test exists.
- A new test that passes immediately (it proves nothing).
- Can't explain *why* the test failed.
- "I'll add tests after" / "already manually tested it."
- "Keep the old code as reference" — you'll adapt it; that's testing after.
- Adding options/abstraction the test doesn't require.
- Editing the test to fit the code when GREEN fails (fix the code).

## Checklist
- [ ] A failing test existed before each piece of production code.
- [ ] Watched every test fail for the expected reason.
- [ ] Wrote the minimal code to pass.
- [ ] One behavior per test; names describe behavior.
- [ ] All tests pass; output is clean.
- [ ] Real code used (mocks only where unavoidable).
- [ ] Edge cases and error paths covered.
- [ ] Each bug fix has a regression test.
