---
name: task-tracking
description: Use when work spans three or more steps or multiple sessions; track it as discrete tasks with explicit status.
---

# Task Tracking

## Purpose
Make multi-step work visible and recoverable: register it as discrete tasks with explicit status so nothing is dropped and progress stays legible.

## When to use
- Work has three or more steps, or spans multiple sessions.
- A larger effort needs breaking into small, reviewable pieces.
- You want a durable record of what's done, in progress, and blocked.

When NOT to use: a single trivial action with an obvious result — just do it; a task entry is pure overhead.

## Method
1. Register before starting. Capture each work item as a task up front, so the full scope is visible before you touch code.
2. One in progress at a time. Working solo, keep exactly one task in-progress; finish it before starting the next.
3. Break work down. Split large items into small tasks that can each be reviewed and verified on their own.
4. Mark done immediately. The moment a task is complete and verified, mark it done — never batch completions for later.
5. Block with a reason. When stuck, mark the task blocked and record what you're waiting on; don't leave it silently in-progress.
6. Never close partial work. A task stays open while tests fail or the change is incomplete — "done" means done.

## Red flags
- Starting work with no task registered — scope invisible, steps forgotten.
- Several tasks in-progress at once while working solo.
- Batching: finishing five things, then marking them done together.
- Marking done while tests fail or the implementation is partial.
- A stuck task left in-progress with no blocker recorded.
- One giant task that can't be reviewed in pieces.

## Checklist
- [ ] Every work item registered as a task before starting.
- [ ] Exactly one task in-progress (solo work).
- [ ] Large work broken into small, reviewable tasks.
- [ ] Each task marked done immediately on completion.
- [ ] Blocked tasks carry an explicit reason.
- [ ] No task marked done while tests fail or work is partial.
