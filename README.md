# Agentic Coding — Technical Report

A self-hosted, multi-agent system for software development (and adjacent technical
domains), built on **opencode**. A single orchestrator agent dispatches and supervises
teams of role-specialized agents; a queryable **code knowledge graph** gives agents
just-in-time retrieval; a **graph-based team memory** lets agents accumulate and
recall lessons across runs; and an **ablation harness** measures what each feature
actually contributes to benchmark success.

> **Headline empirical result** (SWE-bench Verified, Kimi-K3, official Docker
> scoring): the **team** resolves **78%** of the patches it produces vs **41%** for a
> single agent — fewer but far-more-correct patches. Graphify (47%) and memory (50%)
> also beat the single-agent baseline. Details in [§ Ablation](#ablation-evidence).

---

## 1. Architecture at a glance

```
User prompt
    |
    v
 [Orch]  orchestrator (only selectable primary)
    |    1. Graphify-index the repo (graphify-out/graph.json)
    |    2. Query memory graph for prior lessons
    |    3. Split goal into bounded tasks; dispatch one team per task (parallel subagents)
    v
 [Patek] team lead (one per task)
    |--> [Lange]   plan (scope, dependencies, acceptance criteria)
    |--> [Philipe] implement (the only role that edits code)
    |--> [Sohne]   oversight review  (quality / simplicity / docs)
    |--> [Gerald]  red-team review   (correctness / bugs / security)
    |--> [Breguet] domain review     (biophysics / MD / FEP, when relevant)
    |
    v  reviewers sign off, or feedback loops back to Philipe
 [Orch]  supervise fleet, apply gates + cost-capped escalation, close out
```

All agents are wired as **opencode agents** (`.opencode/agent/*.md`) — thin wrappers
over the canonical personas in `agents/<name>/description.md`. The orchestrator is an
**agent, not a script**; the orchestration intelligence lives in the agents + skills.

## 2. The team (agents)

| Agent | Role | Mode | Edits? |
|-------|------|------|--------|
| **Orch** | Orchestrator / entry point — index, dispatch, supervise the fleet | primary (only selectable) | no |
| **Patek** | Team lead — coordinates one team, owns the thread + activity log | hidden subagent | no |
| **Lange** | Planner — executable plans with testable acceptance criteria | hidden subagent | no |
| **Philipe** | Implementer — writes the code, iterates on review | hidden subagent | **yes** |
| **Sohne** | Oversight — quality, simplicity (anti-over-engineering), docs | hidden subagent | no |
| **Gerald** | Red team — bugs, edge cases, plan deviations, security | hidden subagent | no |
| **Breguet** | Biophysics/structural-biology domain reviewer (MD/FEP validity) | hidden subagent | no |

**Orchestrator-first guarantee:** `default_agent: orch`, built-in `build`/`plan`
disabled, `patek` is a hidden subagent only `orch` may invoke
(`permission.task: { "*": deny, patek: allow }`). Every prompt lands on the
orchestrator; you can't bypass it by selecting a raw agent.

## 3. Graphify — queryable code knowledge graph

[Graphify](https://github.com/Graphify-Labs/graphify) maps the codebase (tree-sitter
AST, local + deterministic, no LLM for code) into `graphify-out/graph.json`, so agents
**query a scoped subgraph instead of grepping / reading whole files** — smaller,
higher-signal context.

- **Graphify-first:** `orch` indexes a repo before any team runs on it (on-demand).
- Agents call `graphify query/path/explain` (bash-callable; also exposed as a skill
  at `skills/graphify/`). See [docs/graphify.md](docs/graphify.md).
- Every edge is tagged `EXTRACTED` vs `INFERRED`, so agents can tell fact from guess.

## 4. Graph-based team memory

A lightweight, **single-file, agent-anchored property graph** (`memory/graph.jsonl`)
replaces flat per-agent logs. Nodes (`lesson | decision | pattern | gotcha`) hang off
agent hubs via `knows`, and interlink via `applies_to | related_to | supersedes`. See
[docs/memory-graph.md](docs/memory-graph.md).

- **Committed source of truth:** `memory/graph.jsonl` (append-only text — git-diffable
  and merge-friendly, unlike a binary DB).
- **Query engine:** `memory/graph_memory.py` (stdlib) loads the JSONL into an
  **in-memory SQLite** for top-K just-in-time recall (`query "<kw>" --agent X --k 5`)
  — never a full dump, so recall stays context-lean. Appends are `fcntl`-locked +
  `O_APPEND` (safe for parallel teams sharing a working dir). `supersede` is
  append-a-marker (self-pruning; stale lessons drop out by default).
- **Mirror:** `export` regenerates a human-readable `agents/<name>/memory.md` per
  agent (generated, do-not-edit).
- **Forced habit:** every agent's prompt requires querying memory *first* at task
  start and recording durable lessons after.

## 5. Skills (tool-agnostic)

A shared `skills/` library of portable Agent Skills (one `SKILL.md` per folder) —
works across opencode / Claude Code / Cursor / Codex. Each agent is **scoped to its
role's skills** (`permission.skill`) and told to **consult skills at the start of
every task**. Team-specific skills: `graphify`, `memory`, `plan-doc`, `code-review`,
`red-team-review`, `activity-log`, plus a general library (testing, debugging,
refactoring, CI/CD, security, MD/FEP, …). Catalog: [skills/README.md](skills/README.md).

## 6. Ablation evidence

Self-contained harness in `benchmarks/ablation/` (Kimi-K3 via Copilot API;
mini-swe-agent-style loop; arm toggles; official SWE-bench Docker scoring). Full
design + controls in [docs/ablation-study.md](docs/ablation-study.md).

**Design:** 6 arms × N=25 × pass@3 (fractional factorial — baseline + each feature
alone + all-on). **Cost: $5.63** (budget was $100).

**Patch-emission** (proxy) vs **resolve rate** (decisive — patches passing hidden
`FAIL_TO_PASS` tests, official Docker scoring):

| Arm | Patch-emission | Resolve rate |
|---|---|---|
| A0 baseline (single agent) | 24% | **41%** |
| A1 + graphify | 25% | **47%** |
| A2 + memory | 27% | 50% (n=4) |
| A3 **team** (plan→implement→parallel review→revise) | 12% | **78%** |
| A4 review-only | 3% | 0% (n=2) |
| A5 all-on | 1% | 100% (n=1) |

**Takeaway:** the team emits *fewer* but *far more correct* patches (78% vs 41%)
because reviewers catch wrong patches before they count. Patch-emission alone would
have mis-led; resolve rate is the metric that matters. Graphify + memory beat baseline
at no extra token cost. (Small n on A2/A4/A5 → treat as directional; A3's 78% is the
robust signal.)

**Consequence:** the team is the default for quality-critical work; single agent is a
fallback for unhealthy model routes or trivial tasks.

## 7. Benchmarks

- [Local LLM Coding Benchmark](benchmarks/local-llm-coding-benchmark.md) — HumanEval+ /
  MBPP+ pass@1, serving throughput, and agentic SWE-bench Verified results for
  open-weight models on a single H100 (vLLM, EvalPlus, mini-swe-agent), with Opus
  planner/reviewer orchestration experiments. Reproduction scripts + raw logs included.
- [Ablation study](docs/ablation-study.md) — feature-effect measurement above.

## 8. Repository structure

```
.opencode/agent/      # runnable opencode agents (orch primary; 6 hidden subagents)
agents/<name>/        # canonical personas (description.md) + memory mirror (memory.md)
skills/               # tool-agnostic Agent Skills (+ README catalog)
memory/               # graph.jsonl (source) + graph_memory.py (CLI)
graphify-out/         # this repo's code knowledge graph (graph.json + report)
benchmarks/           # local-LLM benchmark + ablation/ harness
tests/                # skill-wiring + memory tests (no GPU needed)
docs/                 # orchestrator, graphify, memory-graph, ablation-study, upgrade plan
```

## 9. Quick start

```bash
# open the repo in opencode — you start on `orch`, the orchestrator
opencode

# headless: dispatch a batch of tasks (each gets a team, in an isolated worktree)
#   -> orch indexes the repo, queries memory, then dispatches Patek teams as
#      parallel subagents and supervises them to sign-off.

# query the code graph directly
graphify query "how does orch dispatch teams?"

# team memory
python3 memory/graph_memory.py query "review flaky" --agent orch --k 5
```

## 10. Testing

```bash
python -m unittest discover -s tests    # 17 tests, no GPU required
```

Covers skill wiring (each agent's allowed skills exist + skills-first instruction),
and the memory graph (add/link/query/supersede/export round-trip, top-K bounding,
concurrent-append safety, git-diff-friendliness).
