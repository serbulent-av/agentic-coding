---
name: executing-plans
description: Use when you have a written, approved implementation plan to execute step by step with review checkpoints.
---

# Executing Plans

## Purpose
Turn an approved plan into working code by executing it faithfully, one step at a time, verifying as you go and surfacing blockers instead of improvising.

## When to use
- A written, approved implementation plan exists and is ready to build.
- The plan has discrete steps with verification or review checkpoints.
- Work will be executed deliberately rather than explored.

When NOT to use: no plan exists yet, or the direction is still unclear — write or revise the plan first.

## Method
1. Review the plan first. Read it end to end; raise questions or gaps before writing any code.
2. Execute one step at a time. Follow the current step exactly as written; don't jump ahead or batch unrelated steps.
3. Verify before moving on. Run the step's checks and confirm they pass before starting the next one.
4. Run the defined checkpoints. At each review or verification point, stop and confirm the result holds.
5. Keep the plan in sync. When reality diverges, note the deviation and update the plan deliberately — don't silently drift.
6. Stop on blockers. A failing verification, missing dependency, or unclear step — surface it and resolve it; never force through or guess.

## Red flags
- Running ahead of the plan or batching unrelated steps together.
- Skipping a step's verification to move faster.
- Silently improvising around a blocker instead of surfacing it.
- The plan and the actual code drifting apart, undocumented.
- Pushing past a repeatedly failing check by guessing.

## Checklist
- [ ] Plan reviewed end to end; concerns raised before starting.
- [ ] Steps executed one at a time, in order.
- [ ] Each step verified before moving on.
- [ ] Checkpoints run at the defined points.
- [ ] Deviations noted and the plan kept in sync.
- [ ] Blockers surfaced, not improvised around.
