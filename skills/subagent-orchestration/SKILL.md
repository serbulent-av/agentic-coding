---
name: subagent-orchestration
description: Use when work splits into independent tasks that can run in parallel without shared state or sequential dependencies.
---

# Subagent Orchestration

## Purpose
Split work into independent units, dispatch a focused subagent per unit, and integrate the results — trading coordination effort for parallel speed and clean context.

## When to use
- 2+ tasks (failures, features, investigations) with different root causes.
- Each unit can be understood and finished without the others' state.
- You want to preserve your own context by delegating self-contained work.

When NOT to use: tasks are coupled (fixing one changes another), they edit the same files / share state, the work is exploratory and you don't yet know the boundaries, or one unit's output feeds the next — sequence those instead.

## Method
1. Decompose into independent domains. Group the work by what's actually separable. If two units touch the same code or depend on a shared outcome, they are one unit or a sequence — not parallel.
2. Brief each subagent fully. It does NOT inherit your history. Hand it exactly: a narrow scope, the acceptance criteria, the context/errors it needs, constraints ("don't touch X"), and the expected return format. Self-contained or it will guess wrong.
3. Dispatch the independents in parallel. Send one call per domain in a single turn. Sequence only the genuine dependents — spawn the dependent after its prerequisite returns.
4. Keep implementation single-writer per file. Parallel subagents must not edit the same file concurrently; partition the work so their changes can't collide.
5. Integrate centrally. Read each return, verify the changes don't conflict, resolve overlaps yourself, then run the full suite/build to confirm the merged result holds.
6. Verify, don't trust. Spot-check each subagent's claim against the actual diff/output; agents make systematic errors.

## Red flags
- Parallelizing coupled work and getting merge conflicts or clobbered edits.
- "Fix all the tests" — scope too broad; the agent gets lost.
- Dispatching without the error text, file paths, or acceptance criteria.
- Multiple subagents writing the same file at once.
- Accepting "done" summaries without checking the combined result builds/passes.
- Forcing into parallel work that's really sequential (output feeds input).

## Checklist
- [ ] Units confirmed independent — no shared files, state, or ordering.
- [ ] Each subagent given scope, acceptance criteria, context, and constraints.
- [ ] Independent units dispatched in parallel; dependents sequenced.
- [ ] No two concurrent agents writing the same file.
- [ ] Returns read, conflicts resolved centrally.
- [ ] Full suite/build run on the integrated result.
- [ ] Each agent's claim spot-checked against real output.
