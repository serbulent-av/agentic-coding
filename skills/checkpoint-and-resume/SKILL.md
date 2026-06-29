---
name: checkpoint-and-resume
description: Use when work risks exceeding a single session or context window; persist state so it survives interruption.
---

# Checkpoint and Resume

## Purpose
Persist just enough state at natural breakpoints that work survives an interruption or context reset and can resume without relearning.

## When to use
- Work may outlast one session or exceed the context window.
- Approaching a natural breakpoint with more work remaining.
- Before a risky or long operation that could lose your place.

When NOT to use: a short task that finishes within the current context — checkpointing it is pure overhead.

## Method
1. Capture active intent. Record what you're trying to achieve and why, in a durable note — not just in context.
2. Name the next action. Write the single concrete next step, so resume starts moving immediately instead of guessing.
3. Record the essentials. Key files, decisions made, and open questions — enough to reconstruct the work, nothing more.
4. Checkpoint at breakpoints. Save at natural seams (task done, before a context reset), not mid-edit.
5. Resume from the checkpoint. On return, read the checkpoint FIRST and continue from the recorded next action.
6. Route knowledge correctly. Durable cross-task facts go to project memory; transient state stays in the checkpoint.

## Red flags
- State held only in context, lost the moment the session ends.
- A checkpoint with no concrete next action — resume stalls on "where was I?".
- Re-reading or re-deriving what's already in context.
- Dumping transient scratch values into durable memory.
- Checkpointing mid-edit, leaving an inconsistent snapshot.

## Checklist
- [ ] Active intent written to a durable note.
- [ ] Single concrete next action recorded.
- [ ] Key files, decisions, and open questions captured.
- [ ] Checkpoint taken at a natural breakpoint.
- [ ] On resume, checkpoint read before acting.
- [ ] Durable knowledge in project memory; transient state in the checkpoint.
