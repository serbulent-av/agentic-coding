---
name: writing-documentation
description: Use when writing or updating a README, module docs, or docstrings.
---

# Writing Documentation

## Purpose
Let a zero-context reader set up, run, and understand the code — and grasp why it works the way it does.

## When to use
- Writing or updating a README, module overview, or docstrings.
- Behavior changed and existing docs now describe the old reality.
- A new module or file lacks a stated purpose.

When NOT to use: to restate what self-evident code already says line by line — delete that noise instead of documenting it.

## Method
1. Pass the newcomer test. A reader with zero context can set up and run it from the doc alone.
2. State purpose up front. Every file or module says what it is for in one line.
3. Document the why. Capture intent, tradeoffs, and constraints — not a paraphrase of the code.
4. Show, don't just tell. Include at least one concrete, runnable example.
5. Keep docs adjacent. Put them next to the code so they're found and updated together.
6. Update in lockstep. When behavior changes, change the doc in the same commit.

## Red flags
- Comments that restate the code ("increment i by 1").
- Setup instructions you never actually ran from a clean state.
- Docs in a separate wiki that quietly drifts from the code.
- A file or module with no stated purpose.
- "Update the docs later" — later never comes; do it in the same change.

## Checklist
- [ ] A newcomer can set up and run it using only the doc.
- [ ] Every file or module states its purpose.
- [ ] At least one concrete example is included.
- [ ] Explains why, not just what.
- [ ] Docs live beside the code and match current behavior.
