# Headless Orchestrator

A minimal, headless orchestrator that dispatches and supervises agentic **teams**
on this repo. Design template: [Agent Orchestrator](../README.md)
(`Untrivial-ai/agent-orchestrator`), reduced to its durable core and re-implemented
in Python (stdlib only) for headless operation.

## AO principles kept

| AO principle | Here |
|---|---|
| Durable facts, derived status | `store.py` persists only `TaskFacts`; `board.py` derives status at read time — never stored |
| Port-based design | `ports.py` (`AgentRunner`, `Workspace`); core logic never touches concrete impls |
| Worktree isolation | `adapters/git_workspace.py` — one git worktree + branch per task |
| Lifecycle / observation | `team.py` stages + `supervisor.py` persist facts after every change |
| CLI over daemon | per-dispatch supervisor (no Electron/tmux/SSE/HTTP) |

## Architecture

```
orchestrator/
  domain.py      # Role, Stage, Status (derived), Artifact, TaskFacts
  ports.py       # AgentRunner, Workspace interfaces (+ RunResult)
  store.py       # JSONL durable fact store (source of truth, resumable)
  board.py       # derive + render the Kanban from facts (read time)
  gates.py       # deterministic gates: apply / tests / test-integrity / diff lint
  escalation.py  # cost-capped hybrid policy (priority queue, budget, kill-switch)
  index.py       # graphify-first precondition (ensure_indexed)
  team.py        # role pipeline: Lange -> Philipe -> Sohne||Gerald -> gates -> fix
  supervisor.py  # per-dispatch supervisor (the active orchestrator)
  cli.py         # python -m orchestrator {dispatch,status,board}
  adapters/
    opencode_runner.py  # opencode run --agent <role> --dir <worktree> --format json
    git_workspace.py    # git worktree add/remove, apply, diff, tests
```

## Your two requirements, mapped

1. **Graphify-first.** `Supervisor.dispatch()` calls `ensure_indexed(repo)` before
   starting any team, building/refreshing `graphify-out/graph.json` on demand for
   whatever repo you dispatch against. Role prompts instruct agents to query the
   graph before reading files. (Use `--require-index` to hard-fail if indexing is
   impossible.)

2. **Orchestrator is active when you dispatch.** `python -m orchestrator dispatch
   <repo> <task...>` *is* the active orchestrator for the run: it creates isolated
   worktrees, runs each team through the role pipeline, persists durable facts after
   every change, enforces gates + escalation, and is resumable (re-running skips
   already-terminated tasks). No daemon to remember to start.

## Usage

```bash
# dispatch 10 teams (one per task) on this repo, 4 at a time
python -m orchestrator dispatch . "task 1" "task 2" ... "task 10" \
    --max-parallel 4 \
    --models philipe=glm52/glm-5.2 sohne=glm52/glm-5.2

# inspect durable facts + derived status
python -m orchestrator status
python -m orchestrator board
```

## Team pipeline (role-batched, compact handoffs)

`Lange` plans → `Philipe` implements → `Sohne` + `Gerald` review → deterministic
**gates** (`git apply` clean, tests non-regress, test-integrity guard, diff lint) →
fix loop → **escalation** (cost-capped; frontier model only on contested-CRITICAL
or repeated gate-fail) → `done`. Each stage runs with fresh context; handoffs are
compact summaries + artifact file references, not full transcripts.

## Tests

```bash
python -m unittest discover -s tests -v
```

Covers gates, derived status, escalation caps, the graphify-first precondition,
resume, and a 10-team dispatch on a small task (faked runner/workspace — no GPU).
