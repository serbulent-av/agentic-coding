---
name: systematic-debugging
description: Use when encountering any bug, test failure, or unexpected behavior, before proposing a fix.
---

# Systematic Debugging

## Purpose
Find the root cause before touching a fix. Random patches waste time, mask the real issue, and spawn new bugs. Symptom fixes are failure.

## When to use
- Any bug, test failure, crash, or unexpected behavior.
- Especially under time pressure, when "one quick fix" looks obvious, or after a previous fix didn't hold.

**When NOT to use:** never skip it because a bug "looks simple" — simple bugs have root causes too. Only stop once investigation has actually proven the cause is environmental or external.

## Method
**No fix without a reproduction and a root cause first.**
1. **Reproduce reliably.** Find exact steps that trigger it every time. Read the full error and stack trace — they often name the cause. Not reproducible? Gather more data; don't guess.
2. **Isolate — one variable at a time.** Check what recently changed (diff, commits, deps, config). Compare against similar working code; list every difference. Bisect the input/commit/component space; change one thing per step.
3. **Trace to the root, not the symptom.** Follow the bad value backward: where did it originate, what passed it in? Keep going up the call stack until you reach the true source. State one hypothesis: "X is the cause because Y."
4. **Fix at the source + add a regression test.** Write a failing test that reproduces the bug first. Make the single smallest change that addresses the root cause — no bundled refactors or "while I'm here" edits.
5. **Verify.** New test passes, no other tests break, the original symptom is gone. Still broken after 3 tries? Stop guessing — question the architecture/assumptions, don't pile on fix #4.

## Red flags
- "Quick fix now, investigate later."
- Proposing a fix before reproducing or tracing the data flow.
- Changing several things at once ("run tests and see").
- Editing at the symptom site because that's where the error surfaced.
- "Skip the test, I'll verify manually."
- A second or third fix stacked on top without new understanding.
- Each fix reveals a new problem elsewhere (architecture smell).

## Checklist
- [ ] Reproduced the issue reliably.
- [ ] Read the full error/stack trace.
- [ ] Identified what changed; isolated by one variable at a time.
- [ ] Traced to the root cause, stated as a hypothesis.
- [ ] Wrote a failing regression test before fixing.
- [ ] Made one minimal fix at the source.
- [ ] Verified: test passes, nothing else broke, symptom gone.
- [ ] After 3 failed fixes, stopped and questioned the architecture.
