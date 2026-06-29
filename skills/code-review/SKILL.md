---
name: code-review
description: Use when reviewing a diff or pull request before sign-off; checks correctness, readability, tests, and scope.
---

# Code Review

## Purpose
Catch defects, unclear code, and scope creep in a change before it lands, while issues are still cheap to fix.

## When to use
- Reviewing a diff, branch, or PR before approving or merging.
- After an agent or teammate reports a task complete and hands off work.
- Before refactoring, as a baseline check on current behavior.

When NOT to use: while code is still actively being written (review whole units, not keystrokes), or for changes you must verify by running them — use verification-before-done for evidence.

## Method
1. Anchor on intent. Read the acceptance criteria / task / PR description first. Review the diff against what it was supposed to do, not against your own design taste.
2. Correctness. Trace the logic. Hunt edge cases: empty input, nulls, boundaries, concurrency, error paths. Ask "what input breaks this?"
3. Readability. Names say what they mean; control flow is followable; no surprising indirection. If you have to reverse-engineer intent, that is a finding.
4. Tests. Confirm tests exist for the new behavior and actually assert it (not just smoke). A passing test that can't fail is a gap.
5. Scope discipline. Flag work beyond the stated goal — speculative abstractions, unrequested features, gold-plating. Less code that meets the spec wins.
6. Write findings. Each comment names a location (`file:line`), the problem, and a concrete fix or question. No vague "this feels off".
7. Assign severity and decide. Block on Critical/Important; record Minor as suggestions. State a clear verdict: approve, or what must change.

## Red flags
- Approving because "it's simple" or "looks fine" without reading the logic.
- Comments with no location or no actionable fix ("improve this").
- Rewriting to your personal style instead of reviewing against the spec.
- Letting scope creep through because the extra code "might help later".
- Passing a change whose tests don't actually exercise the new behavior.
- Nitpicking style while missing a correctness or security defect.

## Checklist
- [ ] Reviewed the diff against explicit acceptance criteria.
- [ ] Correctness and edge cases traced, not assumed.
- [ ] Naming and control flow are clear to a fresh reader.
- [ ] Tests exist, are meaningful, and cover the new behavior.
- [ ] Out-of-scope / gold-plated additions flagged.
- [ ] Every comment has a location and an actionable fix.
- [ ] Severity assigned; explicit verdict given (block vs. suggest).
