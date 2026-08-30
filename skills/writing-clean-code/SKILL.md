---
name: writing-clean-code
description: Use when writing or modifying any code; enforces minimal, readable, intention-revealing implementations.
---

# Writing Clean Code

## Purpose
Keep implementations minimal, readable, and intention-revealing. Write for the next person who reads it — not for the compiler, and not for an imagined future.

## When to use
- Any time you write or modify code.
- Reviewing your own diff before committing.

**When NOT to use:** as an excuse to refactor untouched code mid-task, or to chase "perfect" structure on a throwaway spike. Stay focused on the change at hand.

## Method
1. **KISS.** Choose the simplest design that solves the actual problem. Three plain lines beat a clever abstraction.
2. **YAGNI.** Build only what's needed now. No speculative parameters, hooks, or config for futures that may never come.
3. **Name for intent.** Names say what a thing *is* or *does*. `data`, `tmp`, `processStuff`, `doIt` are not names. A good name removes the need for a comment.
4. **Small, single-responsibility units.** A function does one thing at one level of abstraction. If you need "and" to describe it, split it.
5. **Rule of three before generalizing.** Duplication is cheaper than the wrong abstraction. Extract a shared helper only after the third real occurrence.
6. **Handle the unhappy path consciously.** Decide what happens on bad input, empty, and failure at system boundaries. Don't validate what internal guarantees already ensure.
7. **Delete, don't comment out.** Remove dead code, unused vars, and stale branches. Version control is the history — commented-out code is just noise.

## Red flags
- A function you can't describe without "and".
- Abstraction with a single caller, added "for later".
- Comments explaining *what* badly-named code does (rename instead).
- Commented-out blocks or `_unused` kept "just in case".
- Defensive checks for states internal code can't reach.
- Copy-pasted logic in three+ places left un-factored.
- Refactoring unrelated code the task never asked you to touch.

## Checklist
- [ ] Simplest approach that solves the real problem (KISS).
- [ ] Nothing built for hypothetical future needs (YAGNI).
- [ ] Names reveal intent; no `data`/`tmp`/`processStuff`.
- [ ] Functions are small and single-purpose.
- [ ] No abstraction introduced before the third occurrence.
- [ ] Unhappy paths handled at boundaries, not over-validated within.
- [ ] Dead code deleted, not commented out.
- [ ] Diff is scoped to the task — no drive-by refactors.
