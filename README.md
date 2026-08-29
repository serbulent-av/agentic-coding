# Agentic Coding

A multi-agent system for software development. Each agent has a specialized role, and together they form a complete workflow from planning through implementation to quality assurance.

## Agents

| Agent | Role | Description |
|-------|------|-------------|
| **Patek** | Main / Orchestrator | Coordinates all agents, delegates tasks, and logs every action into an activity log. The central hub of the system. |
| **Philipe** | Implementation | Analyzes requirements, plans the implementation, and writes the code. Iterates based on review feedback. |
| **Lange** | Planning | Creates and maintains the project plan. Monitors progress and expands the plan when new information emerges. |
| **Sohne** | Oversight | Ensures best practices are followed without over-engineering. Reviews documentation quality (README, module docs, inline comments). |
| **Gerald** | Red Team | Adversarial reviewer. Hunts for bugs, edge cases, plan deviations, and potential problems. Does not sign off until all critical issues are resolved. |

## Workflow

```
User Prompt
    |
    v
 [Patek] -- delegates to --> [Lange] (creates plan)
    |
    v
 [Patek] -- delegates to --> [Philipe] (implements step by step)
    |
    v  (after each step)
 [Patek] -- triggers --> [Sohne] (oversight review)
 [Patek] -- triggers --> [Gerald] (red team review)
    |
    v  (if issues found)
 [Patek] -- routes feedback to --> [Philipe] (fixes)
    |
    v  (repeat until sign-off)
 [Patek] -- compiles final log and delivers result
```

## Repository Structure

```
.opencode/
  agent/                 # the team, as opencode agents (single source of truth)
    orch.md              #   orchestrator / dispatcher (primary) — starts runs
    patek.md             #   team lead (primary) — coordinates one team
    lange.md             #   planner (subagent, hidden)
    philipe.md           #   implementer (subagent) — the only role that edits
    sohne.md             #   oversight review (subagent, hidden)
    gerald.md            #   red-team review (subagent, hidden)
agents/                  # canonical personas + per-agent memory
  patek/{description,memory}.md    # ... lange, philipe, sohne, gerald
skills/                  # tool-agnostic Agent Skills (shared, not owned by opencode)
  graphify/SKILL.md      #   queryable code knowledge graph
  memory/SKILL.md        #   append/retrieve lessons in agents/<name>/memory.md
  plan-doc/ code-review/ red-team-review/ activity-log/
orchestrator/            # thin launcher that spawns orch teams (the agent orchestrates)
docs/                    # upgrade plan + integration docs
graphify-out/            # this repo's knowledge graph (graph.json + report)
```

## How to Use

**The orchestrator is always the top agent.** When you open this repo in opencode
(or any Agent-Skills-compatible tool), `orch` is the only selectable primary:
`default_agent: orch`, the built-in `build`/`plan` agents are disabled, and `patek`
is demoted to a *hidden* subagent that only `orch` may invoke
(`permission.task: { "*": deny, patek: allow }`). So you can't accidentally start in
a raw agent and bypass the orchestrator — every prompt lands on `orch`, which
indexes the repo and dispatches team(s).

1. **Start with the orchestrator (`orch`)**: give it a task (or a batch). It first
   Graphify-indexes the repo, then spins up one **Patek** team per task in an
   isolated git worktree, and supervises them. (`python -m orchestrator dispatch
   <repo> "<task...>"` for the headless path.)
2. **Patek leads each team**: coordinates and delegates; never writes code.
3. **Lange plans** → **Philipe builds** → **Sohne + Gerald review** in parallel →
   feedback loops to Philipe until both sign off.
4. **Gates + escalation** (deterministic, then cost-capped frontier) decide done/blocked.
5. **Memory**: each agent appends durable lessons to its own `agents/<name>/memory.md`
   (via the `memory` skill) and greps it back just-in-time.

## Agent & skill files

- **Canonical personas + memory** live in `agents/<name>/` — `description.md` (the
  full role instruction manual) and `memory.md` (that agent's running lesson log).
- **Runnable opencode agents** live in `.opencode/agent/` — thin wrappers
  (frontmatter: mode/permissions/model + a compact prompt) that point at the
  canonical persona in `agents/<name>/description.md`.
- Skills live once in the tool-neutral `./skills/` dir (Agent Skills format — the
  same `SKILL.md` works with opencode, Claude Code, Cursor, Codex, etc.; each tool
  just points at the path). They are **pinned per agent** (frontmatter allows them
  and the prompt states they are already available), so agents use them directly
  rather than re-discovering them each run. opencode loads them via
  `"skills": { "paths": ["skills"] }` in `opencode.json`.

## Integrations

This repo wires the team to two tools:

- **Graphify** — a queryable knowledge graph of the codebase (`graphify-out/graph.json`)
  so agents answer architecture questions by querying the graph instead of grepping.
  See [docs/graphify.md](docs/graphify.md). Skill lives at `skills/graphify/`.
- **Headless Orchestrator** — dispatches and supervises teams of these agents
  (worktree-per-task, deterministic gates, cost-capped escalation), templated on the
  Agent Orchestrator. **Graphify-first:** every repo is indexed before a team runs on
  it; **active on dispatch:** `python -m orchestrator dispatch <repo> <task...>` *is*
  the orchestrator. See [docs/orchestrator.md](docs/orchestrator.md).

The five agents are wired as opencode agents under `.opencode/agent/` (Patek primary;
Lange/Philipe/Sohne/Gerald hidden subagents). Quick start:

```bash
python -m orchestrator dispatch . "add a health-check endpoint" "write tests for X"
python -m orchestrator board     # derived Kanban from durable facts
```

## Benchmarks

- [Local LLM Coding Benchmark](benchmarks/local-llm-coding-benchmark.md) — HumanEval+ / MBPP+ pass@1 for open-weight coding models that fit on a single NVIDIA H100 80GB, served with vLLM and scored with EvalPlus. Includes the reproduction script (`benchmarks/run_bench.sh`) and raw run logs.
