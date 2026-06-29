---
name: persistent-memory
description: Use at the start or end of a session, or when a durable lesson emerges, to maintain memory across sessions.
---

# Persistent Memory

## Purpose
Carry durable knowledge across sessions so each one builds on the last instead of relearning from scratch.

## When to use
- Session start: read the relevant memory before acting.
- Session end: record what is durable and worth keeping.
- A lasting lesson, recurring pattern, or non-obvious gotcha emerges mid-session.

When NOT to use: to log transient state (current branch, today's scratch values) — that is noise, not memory.

## Method
1. Read on entry. At session start, read `agents/<name>/memory.md` for the active agent.
2. Carry the context. Work with what's recorded; don't relearn what's already known.
3. Capture real learnings. When a durable lesson emerges, write one honest entry.
4. File it correctly. Place it under Sessions, Lessons Learned, or Recurring Patterns.
5. Park heuristics. Put gotchas and rules of thumb in Lessons Learned / Recurring Patterns.
6. Promote repeats. Once a lesson recurs, lift it into Recurring Patterns.

## Red flags
- Inventing sessions, dates, or history that never happened.
- Logging transient state that is stale by tomorrow.
- Duplicate entries for the same lesson instead of promoting it once.
- A wall of low-value notes that buries the signal.
- Skipping the start-of-session read, then repeating a past mistake.

## Checklist
- [ ] Read the agent's `agents/<name>/memory.md` at session start.
- [ ] Each entry reflects a real, durable learning.
- [ ] Entry placed in the right section (Sessions / Lessons Learned / Recurring Patterns).
- [ ] No fabricated sessions or history.
- [ ] Recurring items have been promoted to Recurring Patterns.
