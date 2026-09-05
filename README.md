# Agentic Coding

A multi-agent system for software development. Each agent has a specialized role, and together they form a complete workflow from planning through implementation to quality assurance.

## Agents

| Agent | Role | Description |
|-------|------|-------------|
| **Orch** | Orchestrator / entry point | The top agent. Graphify-indexes the repo, splits the goal into bounded tasks, and dispatches one Patek team per task as parallel subagents, then supervises them. The only user-selectable primary. |
| **Patek** | Team lead | Coordinates one team: delegates to the workers, keeps the thread, logs every handoff. Never writes code. |
| **Lange** | Planning | Turns the ask into an executable plan — explicit scope, dependencies, testable acceptance criteria. |
| **Philipe** | Implementation | Writes the code, step by step; the only role that edits. Iterates on review feedback. |
| **Sohne** | Oversight | Reviews for quality, simplicity, and docs; hunts over-engineering as hard as sloppiness. |
| **Gerald** | Red Team | Adversarial reviewer. Hunts bugs, edge cases, plan deviations, security. Won't sign off until critical issues are resolved. |
| **Breguet** | Biophysics / Structural Biology | Domain expert for computational structural biology. Validates molecular-dynamics and free-energy work for scientific correctness, convergence, and reproducibility. Joins reviews for MD/FEP tasks. |

## Skills

The team shares a `skills/` library of portable, Claude-Code-format Agent Skills
(each a folder with a single `SKILL.md`). Each agent loads the skills relevant to
its role on demand when a task matches a skill's trigger, rather than carrying
every procedure inline. See [`skills/README.md`](skills/README.md) for the catalog
and the per-agent skill mapping.

## Workflow

```
User Prompt
    |
    v
 [Orch] -- graphify-index repo, split into tasks, dispatch teams (parallel subagents)
    |
    v  (one team per task)
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
    v  (repeat until both sign off)
 [Patek] -- delivers result --> [Orch] -- supervises fleet, closes out
```

## Repository Structure

```
.opencode/
  agent/                 # runnable opencode agents (thin wrappers over the personas)
    orch.md              #   orchestrator / dispatcher (primary) — starts runs
    patek.md             #   team lead (hidden subagent) — coordinates one team
    lange.md             #   planner (hidden subagent)
    philipe.md           #   implementer (subagent) — the only role that edits
    sohne.md             #   oversight review (hidden subagent)
    gerald.md            #   red-team review (hidden subagent)
    breguet.md           #   biophysics domain review (hidden subagent)
agents/                  # canonical personas + per-agent memory (source of truth)
  orch/{description,memory}.md     # ... patek, lange, philipe, sohne, gerald, breguet
skills/                  # tool-agnostic Agent Skills (shared, not owned by opencode)
  README.md              #   catalog + per-agent mapping
  graphify/ memory/ plan-doc/ code-review/ red-team-review/ activity-log/  # team-specific
  subagent-orchestration/ writing-plans/ test-driven-development/ ...       # general library
tests/                   # skill-wiring guard (test_skills.py)
docs/                    # integration docs (+ historical upgrade plan)
graphify-out/            # this repo's knowledge graph (graph.json + report)
```

> The orchestrator is an **agent** (`orch`), not a script — there is no
> `orchestrator/` code package. Orch dispatches teams as **parallel subagents** via
> opencode's Task tool; the orchestration intelligence lives in the agents + skills.

## How to Use

**The orchestrator is always the top agent.** When you open this repo in opencode
(or any Agent-Skills-compatible tool), `orch` is the only selectable primary:
`default_agent: orch`, the built-in `build`/`plan` agents are disabled, and `patek`
is demoted to a *hidden* subagent that only `orch` may invoke
(`permission.task: { "*": deny, patek: allow }`). So you can't accidentally start in
a raw agent and bypass the orchestrator — every prompt lands on `orch`, which
indexes the repo and dispatches team(s).

1. **Start with the orchestrator (`orch`)**: give it a task (or a batch). It first
   Graphify-indexes the repo, then **dispatches one Patek team per task as parallel
   subagents** (via the Task tool) and supervises them to completion.
2. **Patek leads each team**: coordinates and delegates; never writes code.
3. **Lange plans** → **Philipe builds** → **Sohne + Gerald review** in parallel →
   feedback loops to Philipe until both sign off. For computational structural
   biology work, **Breguet** also reviews for scientific validity, convergence, and
   reproducibility.
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
  just points at the path). opencode loads them via `"skills": { "paths": ["skills"] }`.
  Each agent is **scoped to its role's skills** (frontmatter `permission.skill`) and
  its prompt says **"at the start of every task, consult your skills first"** — so
  agents use the right skills up front instead of discovering them mid-task.

## Integrations

This repo wires the team to two tools:

- **Graphify** — a queryable knowledge graph of the codebase (`graphify-out/graph.json`)
  so agents answer architecture questions by querying the graph instead of grepping.
  See [docs/graphify.md](docs/graphify.md). Skill lives at `skills/graphify/`.
- **Orchestrator** — an *agent* (`orch`), not a script. Templated on the Agent
  Orchestrator's ideas (worktree isolation, derived status, durable facts) but the
  reasoning is done by the model. **Graphify-first:** every repo is indexed before a
  team runs on it; **active on dispatch:** `orch` spawns Patek teams as parallel
  subagents via the Task tool and supervises them. See
  [docs/orchestrator.md](docs/orchestrator.md).

The six agents are wired as opencode agents under `.opencode/agent/` — thin wrappers
over the canonical personas in `agents/<name>/description.md`. `orch` is the only
selectable primary; Patek + the four workers are hidden subagents it invokes.
Quick start: open the repo in opencode (starts on `orch`) and give it a task or a
batch — it indexes, dispatches teams, and supervises.

## Benchmarks

- [Local LLM Coding Benchmark](benchmarks/local-llm-coding-benchmark.md) — HumanEval+ / MBPP+ pass@1 for open-weight coding models that fit on a single NVIDIA H100 80GB, served with vLLM and scored with EvalPlus. Includes the reproduction script (`benchmarks/run_bench.sh`) and raw run logs.
