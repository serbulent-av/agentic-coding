# Orchestrator (pure agent — no scripts)

The orchestrator is an **agent**: `.opencode/agent/orch.md` (primary), with its
canonical persona at `agents/orch/description.md`. There is **no orchestrator code
package** — an earlier ~150-line launcher and, before that, a ~1,200-line state
machine were both removed as over-engineering. The orchestration intelligence
(planning, delegation, gating, escalation, supervision) is done by the model.

## How it orchestrates (agentic, via the Task tool)

`orch` is the entry point and the only selectable primary. On a goal or batch:

1. **Graphify-first** — index each target repo (`graphify update/extract`) before
   any team touches it.
2. **Plan the fleet** — split into bounded, independent tasks.
3. **Dispatch teams as subagents** — spawn a `patek` team per task via the Task
   tool, in parallel when independent. Each Patek then runs its own team
   (`lange` → `philipe` → `sohne` + `gerald`) as nested subagents.
4. **Supervise** — read each team's compact structured result; apply gates
   (patch applies, tests pass, tests untouched) and the cost-capped escalation
   policy; surface blocked teams to the user.
5. **Close out** — log events (`activity-log`), record lessons (`memory`).

"Dispatch 10 teams as subagents, orchestrator manages them" = one `orch` session
issuing 10 `task(subagent_type="patek", …)` calls in parallel and managing their
structured results.

## Why this guarantees orchestrator-first

- `default_agent: orch` → a fresh session starts on the orchestrator.
- Built-in `build`/`plan` disabled; `patek` is a **hidden subagent** → users can't
  bypass `orch` by selecting a raw agent.
- Capability routing: `orch` may invoke only `patek`; `patek` may invoke only the
  four workers. No agent escapes the tree.

## Layout

- Personas + per-agent memory: `agents/<name>/{description,memory}.md` (incl. `orch`).
- Runnable opencode agents (thin wrappers): `.opencode/agent/*.md`.
- Shared, tool-agnostic skills: `skills/` (graphify, memory, plan-doc, code-review,
  red-team-review, activity-log).

## Note on isolation

opencode's Task subagents share the working directory, so parallel teams editing
the *same* repo can collide. For parallel work on the same repo, prefer independent
tasks, or extend later with per-task git worktrees if it becomes a real need.
