---
name: plan-doc
description: Produce an executable project plan. Use when planning a feature/change — decomposing scope, ordering tasks by dependency, and writing concrete acceptance criteria. Used by the planner (Lange) and the orchestrator before implementation starts.
---

# Plan document

Write a plan that an implementer can execute without guessing. Keep it compact —
this is a handoff, so high-signal only.

## Format

```
# Plan: <name>
## Objective        (1-2 sentences: what + why)
## Scope
  In:    <explicit>
  Out:   <explicit — prevents creep>
## Tasks (ordered by dependency)
  1. <task> — acceptance: <testable condition> — depends on: <ids|none>
  2. ...
## Risks            <risk — mitigation>
## Open questions   <unknowns -> spike or user question>
```

## Rules
- Every task has a **testable acceptance criterion**; no criterion → not ready.
- Scope is explicit (in AND out). First milestones detailed; later ones can be coarse.
- Ground the plan in the real code: run `graphify query` before naming files/components.
- Surface unknowns as spikes or open questions; never bury assumptions.
