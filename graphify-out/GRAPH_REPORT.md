# Graph Report - agentic-coding  (2026-08-29)

## Corpus Check
- 56 files · ~38,788 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 511 nodes · 729 edges · 46 communities (40 shown, 6 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 39 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `80987439`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- run_swe_verified.sh
- run_pilot_planned.sh
- run_bench.sh
- run_strategy_c.py
- test_orchestrator.py
- chain_c.sh
- checkpoint_push.sh
- TaskFacts
- opencode.json
- What You Must Do When Invoked
- Agentic Coding
- 4.7 Measured frontier-scale result: GLM-5.2 (753 B) on 8x H200 — Terminal-Bench 2
- Agentic Team Upgrade Plan (v1)
- run_gates
- Self-Hostable Open-Weight Coding Models on a Single H100
- Lange - Planning Agent (The Strategist)
- Gerald - Red Team Agent (The Breaker)
- Patek - Main Agent (The Conductor)
- Workspace
- Philipe - Implementation Agent (The Builder)
- EscalationPolicy
- Sohne - Oversight Agent (The Guardian)
- GitWorkspace
- index.py
- graphify reference: extra exports and benchmark
- graphify reference: query, path, explain
- Gerald - Memory Log
- Lange - Memory Log
- Patek - Memory Log
- Philipe - Memory Log
- Sohne - Memory Log
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native AGENTS.md integration
- graphify reference: incremental update and cluster-only
- graphify reference: GitHub clone and cross-repo merge
- graphify reference: transcribe video and audio
- extraction-spec.md
- adapters/__init__.py

## God Nodes (most connected - your core abstractions)
1. `TaskFacts` - 38 edges
2. `run_team()` - 22 edges
3. `EscalationPolicy` - 21 edges
4. `Store` - 21 edges
5. `Workspace` - 18 edges
6. `Role` - 16 edges
7. `derive_status()` - 15 edges
8. `Supervisor` - 15 edges
9. `Agentic Team Upgrade Plan (v1)` - 15 edges
10. `Stage` - 12 edges

## Surprising Connections (you probably didn't know these)
- `TestDerivedStatus` --uses--> `TaskFacts`  [INFERRED]
  tests/test_orchestrator.py → orchestrator/domain.py
- `TestDispatch` --uses--> `EscalationPolicy`  [INFERRED]
  tests/test_orchestrator.py → orchestrator/escalation.py
- `FakeRunner` --uses--> `Role`  [INFERRED]
  tests/test_orchestrator.py → orchestrator/domain.py
- `TestDerivedStatus` --uses--> `Stage`  [INFERRED]
  tests/test_orchestrator.py → orchestrator/domain.py
- `TestDerivedStatus` --uses--> `Status`  [INFERRED]
  tests/test_orchestrator.py → orchestrator/domain.py

## Import Cycles
- None detected.

## Communities (46 total, 6 thin omitted)

### Community 0 - "run_swe_verified.sh"
Cohesion: 0.26
Nodes (11): ckpt(), HF_HOME, log(), MSWEA_COST_TRACKING, OPENAI_API_KEY, PATH, run_model(), run_swe_verified.sh script (+3 more)

### Community 1 - "run_pilot_planned.sh"
Cohesion: 0.24
Nodes (10): ckpt(), HF_HOME, log(), MSWEA_COST_TRACKING, OPENAI_API_KEY, PATH, serve(), run_pilot_planned.sh script (+2 more)

### Community 2 - "run_bench.sh"
Cohesion: 0.36
Nodes (8): free_weights(), HF_HOME, log(), PATH, run_ds(), run_bench.sh script, TOKENIZERS_PARALLELISM, VLLM_LOGGING_LEVEL

### Community 3 - "run_strategy_c.py"
Cohesion: 0.29
Nodes (9): chat(), Programmatic Opus 4.8 via the GitHub Copilot API (token reused from OpenCode…, _token(), log(), main(), opus_review(), push(), run_agent() (+1 more)

### Community 4 - "test_orchestrator.py"
Cohesion: 0.07
Nodes (38): Enum, OpencodeRunner, opencode adapter. Runs one role headlessly via the opencode CLI. opencode run…, Pull the last assistant text out of opencode's JSON event stream., board(), Read-model / board. Derives the AO-style Kanban from stored durable facts.…, render(), _build_supervisor() (+30 more)

### Community 9 - "TaskFacts"
Cohesion: 0.13
Nodes (19): Any, Artifact, A compact handoff between stages (a file reference, not inline content)., Durable facts about one dispatched task. This is ALL that is persisted., TaskFacts, Store, _blocked(), _current_patch_text() (+11 more)

### Community 10 - "opencode.json"
Cohesion: 0.07
Nodes (27): compaction, auto, tail_turns, default_agent, api, apiKey, models, name (+19 more)

### Community 11 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native AGENTS.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 12 - "Agentic Coding"
Cohesion: 0.08
Nodes (21): Bash-callable usage (works in any shell-driven agent), Git, Graphify integration, Keep it fresh, Optional: serve over MCP/HTTP, What's installed, AO principles kept, Architecture (+13 more)

### Community 13 - "4.7 Measured frontier-scale result: GLM-5.2 (753 B) on 8x H200 — Terminal-Bench 2"
Cohesion: 0.08
Nodes (25): 4.1 Function-level capability (HumanEval+, MBPP+), 4.2 Serving throughput (one H100, bf16, 256 output tokens), 4.3.1 Baseline performance (all models, 50 instances), 4.3.2 Strategy B: Opus plan-once (all models, 50 instances), 4.3.3 Strategy C: Opus plan + review (12-instance pilot, phi-4 and gemma-4-31B), 4.3.4 Orchestration findings, 4.3 Agentic results (SWE-bench Verified), 4.4 Cross-harness comparison vs Claude Opus (vendor-reported) (+17 more)

### Community 14 - "Agentic Team Upgrade Plan (v1)"
Cohesion: 0.08
Nodes (24): 0. TL;DR — what changed after review, 10. Risks, 11. Open questions (need your call), 1. Context & evidence, 2. Diagnosis: what the data says the bottleneck is, 3. Locked decisions (revised), 4. Model-per-role (CORRECTED), 5. Escalation policy (cost-capped hybrid) (+16 more)

### Community 15 - "run_gates"
Cohesion: 0.13
Nodes (9): GateReport, looks_like_unified_diff(), Deterministic gates. Cheap, objective checks run BEFORE any LLM judgment.…, Run all deterministic gates on a candidate patch. Returns a report., run_gates(), test_integrity_violations(), touched_files(), FakeWorkspace (+1 more)

### Community 16 - "Self-Hostable Open-Weight Coding Models on a Single H100"
Cohesion: 0.11
Nodes (18): 1. Introduction & research questions, 2.1 Environment, 2.2 Models under test, 2. Experimental setup, 3.1 Function-level evaluation (sec 4.1), 3.2 Throughput measurement (sec 4.2), 3.3 Agentic evaluation (sec 4.3), 3.4 Orchestration strategies (sec 4.3) (+10 more)

### Community 17 - "Lange - Planning Agent (The Strategist)"
Cohesion: 0.12
Nodes (16): 1. What is the actual goal?, 2. What are the boundaries?, 3. What are the pieces?, 4. What depends on what?, 5. How do we know it's done?, 6. What could go wrong?, After Each Implementation Step, Common Traps Lange Avoids (+8 more)

### Community 18 - "Gerald - Red Team Agent (The Breaker)"
Cohesion: 0.13
Nodes (14): Gerald - Red Team Agent (The Breaker), Gerald's Mindset in Practice, Gerald's Report Format, Hard Rules, How Gerald Reviews, Identity, Layer 1: Plan Compliance, Layer 2: Logic Analysis (+6 more)

### Community 19 - "Patek - Main Agent (The Conductor)"
Cohesion: 0.13
Nodes (14): Hard Rules, How Patek Thinks, Identity, Log Entry Structure, Orchestration Protocol, Patek - Main Agent (The Conductor), Patek's Relationship With Each Agent, Phase 1: Intake (+6 more)

### Community 20 - "Workspace"
Cohesion: 0.13
Nodes (8): Manages an isolated git worktree per task. Production impl:…, Create a worktree + branch; return (worktree_path, branch)., Apply a unified diff; return (applied_cleanly, message)., Return the current unified diff of the worktree vs its base., Run the repo's test gate; return (passed, output)., Alias-friendly teardown (defaults to remove)., Workspace, Protocol

### Community 21 - "Philipe - Implementation Agent (The Builder)"
Cohesion: 0.14
Nodes (13): Build incrementally, not all at once, Coding Standards (The Non-Negotiables), Handle the unhappy path, Hard Rules, How Philipe Thinks, Identity, Implementation Philosophy, No gold-plating (+5 more)

### Community 22 - "EscalationPolicy"
Cohesion: 0.21
Nodes (4): EscalationEvent, EscalationPolicy, Pop the highest-severity pending escalation if budget allows., TestEscalation

### Community 23 - "Sohne - Oversight Agent (The Guardian)"
Cohesion: 0.17
Nodes (11): Hard Rules, How Sohne Reviews, Identity, Pass 1: The Newcomer Test (Documentation), Pass 2: The Simplicity Check (Anti-Bloat), Pass 3: The Craft Check (Best Practices), Sohne - Oversight Agent (The Guardian), Sohne's Relationship With Over-Engineering (A Deeper Look) (+3 more)

### Community 24 - "GitWorkspace"
Cohesion: 0.23
Nodes (3): GitWorkspace, Git worktree adapter. One worktree + branch per task (AO's workspace…, Default test gate: run the repo's unittest suite if one exists. This is…

### Community 25 - "index.py"
Cohesion: 0.26
Nodes (9): ensure_indexed(), graph_path(), graphify_available(), IndexResult, is_indexed(), Graphify-first precondition. ``ensure_indexed(repo)`` builds or refreshes…, Ensure ``repo`` has a graphify index. Builds it if missing (code-only, local…, Graphify-index the repo, then run one team per prompt to completion. (+1 more)

### Community 26 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 27 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 28 - "Gerald - Memory Log"
Cohesion: 0.40
Nodes (4): Gerald - Memory Log, Lessons Learned, Recurring Patterns, Sessions

### Community 29 - "Lange - Memory Log"
Cohesion: 0.40
Nodes (4): Lange - Memory Log, Lessons Learned, Recurring Patterns, Sessions

### Community 30 - "Patek - Memory Log"
Cohesion: 0.40
Nodes (4): Lessons Learned, Patek - Memory Log, Recurring Patterns, Sessions

### Community 31 - "Philipe - Memory Log"
Cohesion: 0.40
Nodes (4): Lessons Learned, Philipe - Memory Log, Recurring Patterns, Sessions

### Community 32 - "Sohne - Memory Log"
Cohesion: 0.40
Nodes (4): Lessons Learned, Recurring Patterns, Sessions, Sohne - Memory Log

### Community 33 - "graphify reference: add a URL and watch a folder"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 34 - "graphify reference: commit hook and native AGENTS.md integration"
Cohesion: 0.50
Nodes (3): For git commit hook, For native AGENTS.md integration, graphify reference: commit hook and native AGENTS.md integration

### Community 35 - "graphify reference: incremental update and cluster-only"
Cohesion: 0.50
Nodes (3): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only

## Knowledge Gaps
- **224 isolated node(s):** `chain_c.sh script`, `PATH`, `checkpoint_push.sh script`, `PATH`, `PATH` (+219 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Self-Hostable Open-Weight Coding Models on a Single H100` connect `Self-Hostable Open-Weight Coding Models on a Single H100` to `Agentic Coding`, `4.7 Measured frontier-scale result: GLM-5.2 (753 B) on 8x H200 — Terminal-Bench 2`?**
  _High betweenness centrality (0.068) - this node is a cross-community bridge._
- **Why does `4. Results` connect `4.7 Measured frontier-scale result: GLM-5.2 (753 B) on 8x H200 — Terminal-Bench 2` to `Self-Hostable Open-Weight Coding Models on a Single H100`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Why does `TaskFacts` connect `TaskFacts` to `index.py`, `test_orchestrator.py`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `TaskFacts` (e.g. with `board()` and `Store`) actually correct?**
  _`TaskFacts` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `run_team()` (e.g. with `Role` and `Stage`) actually correct?**
  _`run_team()` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `EscalationPolicy` (e.g. with `Supervisor` and `TestDispatch`) actually correct?**
  _`EscalationPolicy` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `Store` (e.g. with `board()` and `render()`) actually correct?**
  _`Store` has 4 INFERRED edges - model-reasoned connections that need verification._