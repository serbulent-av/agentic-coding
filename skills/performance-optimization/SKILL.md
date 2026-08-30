---
name: performance-optimization
description: Use when there is a stated performance concern or a measured bottleneck — not by default.
---

# Performance Optimization

## Purpose
Make proven-slow code faster through measurement, without guessing or trading away clarity for unproven gains.

## When to use
- A real, stated performance requirement is at risk.
- Profiling or metrics point to a specific, measured bottleneck.
- A scaling time bomb has been identified (see Red flags).

When NOT to use: routine code with no measured problem — leave it readable. "This feels slow" with no numbers is not a trigger; measure first, then decide.

## Method
1. Measure first. Profile to find where time and memory actually go.
2. Confirm the hotspot. Verify it is a meaningful share of total cost and worth the effort.
3. Prefer algorithmic wins. Better complexity or fewer calls beats micro-tuning.
4. Change one thing. Keep behavior intact and the test suite green.
5. Measure again. Keep the change only if before/after numbers prove a real gain.
6. Record the numbers. Leave evidence so the next person isn't guessing.

## Red flags
- Optimizing without a profile — you'll speed up the wrong thing.
- Trading readability for a speedup that was never measured.
- Unbounded loops or queries over input that grows without limit.
- Missing pagination or batch limits on collections and queries.
- Caches with no eviction or TTL — a memory leak in waiting.
- N+1 queries or per-row network calls hidden inside a loop.

## Checklist
- [ ] A measurement justified doing the work.
- [ ] Only the proven hotspot was changed.
- [ ] Algorithmic options were considered before micro-tuning.
- [ ] Before/after numbers are recorded and show real improvement.
- [ ] Behavior is unchanged; tests are green.
- [ ] No new unbounded growth was introduced.
