# Orchestrator (agentic)

The orchestrator is an **agent** — `.opencode/agent/orch.md` (primary) — not a
framework. It holds the orchestration intelligence: plan the fleet, lead each
Patek team, apply gates, escalate, and supervise. It draws on the Agent
Orchestrator's *ideas* (worktree isolation, derived status, durable facts) but the
reasoning is done by the model, not re-implemented in code.

## Why an agent, not a big script

An earlier version built a ~1,200-line Python state machine (custom gates,
escalation engine, board, store). That was over-engineering: the agents already
know how to plan/review/escalate. The code's only job is to **launch** teams.

## The thin launcher (`orchestrator/`)

~150 lines, stdlib only:

- `index.py` — **Graphify-first**: `ensure_indexed(repo)` builds/refreshes
  `graphify-out/graph.json` before any team runs on that repo.
- `dispatch.py` — `dispatch(repo, tasks, max_parallel)` spawns one `orch` agent
  session per task (via `opencode run --agent orch`), each in its own git worktree
  when the target is a git repo.
- `cli.py` — `python -m orchestrator dispatch <repo> "<task...>"`.

Everything else — planning, delegation, gating, review, escalation, logging — is
the `orch` agent + `patek` team + the `skills/`.

## Running it

Interactive (opencode TUI): the default agent is `orch`, so you start there and it
orchestrates. Headless:

```bash
python -m orchestrator dispatch . "add health-check endpoint" "write tests for X" \
    --max-parallel 4
```

## Team + skills

`orch` → `patek` (team lead) → `lange` / `philipe` / `sohne` / `gerald`.
Shared skills in `skills/`: `graphify` (code graph), `memory` (per-agent lessons at
`agents/<name>/memory.md`), `plan-doc`, `code-review`, `red-team-review`,
`activity-log`.
