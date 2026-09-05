# Graph Report - agentic-coding  (2026-08-30)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 291 nodes · 287 edges · 30 communities (28 shown, 2 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ec9d3390`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Agentic Coding
- 4.7 Measured frontier-scale result: GLM-5.2 (753 B) on 8x H200 — Terminal-Bench 2
- Agentic Team Upgrade Plan (v1)
- opencode.json
- Self-Hostable Open-Weight Coding Models on a Single H100
- Lange - Planning Agent (The Strategist)
- Gerald - Red Team Agent (The Breaker)
- Patek - Main Agent (The Conductor)
- Philipe - Implementation Agent (The Builder)
- glm52
- Sohne - Oversight Agent (The Guardian)
- run_swe_verified.sh
- run_strategy_c.py
- run_pilot_planned.sh
- run_bench.sh
- test_skills.py
- Gerald - Memory Log
- Lange - Memory Log
- Patek - Memory Log
- Philipe - Memory Log
- Sohne - Memory Log
- chain_c.sh
- checkpoint_push.sh

## God Nodes (most connected - your core abstractions)
1. `Agentic Team Upgrade Plan (v1)` - 15 edges
2. `Self-Hostable Open-Weight Coding Models on a Single H100` - 12 edges
3. `8. The plan — steps in execution order` - 10 edges
4. `4.7 Measured frontier-scale result: GLM-5.2 (753 B) on 8x H200 — Terminal-Bench 2` - 9 edges
5. `Agentic Coding` - 8 edges
6. `4. Results` - 8 edges
7. `Sohne - Oversight Agent (The Guardian)` - 8 edges
8. `Lange - Planning Agent (The Strategist)` - 8 edges
9. `Gerald - Red Team Agent (The Breaker)` - 8 edges
10. `Philipe - Implementation Agent (The Builder)` - 8 edges

## Surprising Connections (you probably didn't know these)
- None detected - all connections are within the same source files.

## Import Cycles
- None detected.

## Communities (30 total, 2 thin omitted)

### Community 0 - "Agentic Coding"
Cohesion: 0.08
Nodes (21): Bash-callable usage (works in any shell-driven agent), Git, Graphify integration, Keep it fresh, Optional: serve over MCP/HTTP, What's installed, AO principles kept, Architecture (+13 more)

### Community 1 - "4.7 Measured frontier-scale result: GLM-5.2 (753 B) on 8x H200 — Terminal-Bench 2"
Cohesion: 0.08
Nodes (25): 4.1 Function-level capability (HumanEval+, MBPP+), 4.2 Serving throughput (one H100, bf16, 256 output tokens), 4.3.1 Baseline performance (all models, 50 instances), 4.3.2 Strategy B: Opus plan-once (all models, 50 instances), 4.3.3 Strategy C: Opus plan + review (12-instance pilot, phi-4 and gemma-4-31B), 4.3.4 Orchestration findings, 4.3 Agentic results (SWE-bench Verified), 4.4 Cross-harness comparison vs Claude Opus (vendor-reported) (+17 more)

### Community 2 - "Agentic Team Upgrade Plan (v1)"
Cohesion: 0.08
Nodes (24): 0. TL;DR — what changed after review, 10. Risks, 11. Open questions (need your call), 1. Context & evidence, 2. Diagnosis: what the data says the bottleneck is, 3. Locked decisions (revised), 4. Model-per-role (CORRECTED), 5. Escalation policy (cost-capped hybrid) (+16 more)

### Community 3 - "opencode.json"
Cohesion: 0.09
Nodes (21): agent, build, plan, disable, compaction, auto, tail_turns, default_agent (+13 more)

### Community 4 - "Self-Hostable Open-Weight Coding Models on a Single H100"
Cohesion: 0.11
Nodes (18): 1. Introduction & research questions, 2.1 Environment, 2.2 Models under test, 2. Experimental setup, 3.1 Function-level evaluation (sec 4.1), 3.2 Throughput measurement (sec 4.2), 3.3 Agentic evaluation (sec 4.3), 3.4 Orchestration strategies (sec 4.3) (+10 more)

### Community 5 - "Lange - Planning Agent (The Strategist)"
Cohesion: 0.12
Nodes (16): 1. What is the actual goal?, 2. What are the boundaries?, 3. What are the pieces?, 4. What depends on what?, 5. How do we know it's done?, 6. What could go wrong?, After Each Implementation Step, Common Traps Lange Avoids (+8 more)

### Community 6 - "Gerald - Red Team Agent (The Breaker)"
Cohesion: 0.13
Nodes (14): Gerald - Red Team Agent (The Breaker), Gerald's Mindset in Practice, Gerald's Report Format, Hard Rules, How Gerald Reviews, Identity, Layer 1: Plan Compliance, Layer 2: Logic Analysis (+6 more)

### Community 7 - "Patek - Main Agent (The Conductor)"
Cohesion: 0.13
Nodes (14): Hard Rules, How Patek Thinks, Identity, Log Entry Structure, Orchestration Protocol, Patek - Main Agent (The Conductor), Patek's Relationship With Each Agent, Phase 1: Intake (+6 more)

### Community 8 - "Philipe - Implementation Agent (The Builder)"
Cohesion: 0.14
Nodes (13): Build incrementally, not all at once, Coding Standards (The Non-Negotiables), Handle the unhappy path, Hard Rules, How Philipe Thinks, Identity, Implementation Philosophy, No gold-plating (+5 more)

### Community 9 - "glm52"
Cohesion: 0.15
Nodes (13): models, name, npm, options, limit, name, context, output (+5 more)

### Community 10 - "Sohne - Oversight Agent (The Guardian)"
Cohesion: 0.17
Nodes (11): Hard Rules, How Sohne Reviews, Identity, Pass 1: The Newcomer Test (Documentation), Pass 2: The Simplicity Check (Anti-Bloat), Pass 3: The Craft Check (Best Practices), Sohne - Oversight Agent (The Guardian), Sohne's Relationship With Over-Engineering (A Deeper Look) (+3 more)

### Community 11 - "run_swe_verified.sh"
Cohesion: 0.26
Nodes (11): ckpt(), HF_HOME, log(), MSWEA_COST_TRACKING, OPENAI_API_KEY, PATH, run_model(), run_swe_verified.sh script (+3 more)

### Community 12 - "run_strategy_c.py"
Cohesion: 0.29
Nodes (9): chat(), Programmatic Opus 4.8 via the GitHub Copilot API (token reused from OpenCode…, _token(), log(), main(), opus_review(), push(), run_agent() (+1 more)

### Community 13 - "run_pilot_planned.sh"
Cohesion: 0.24
Nodes (10): ckpt(), HF_HOME, log(), MSWEA_COST_TRACKING, OPENAI_API_KEY, PATH, serve(), run_pilot_planned.sh script (+2 more)

### Community 14 - "run_bench.sh"
Cohesion: 0.36
Nodes (8): free_weights(), HF_HOME, log(), PATH, run_ds(), run_bench.sh script, TOKENIZERS_PARALLELISM, VLLM_LOGGING_LEVEL

### Community 15 - "test_skills.py"
Cohesion: 0.36
Nodes (4): agent_allowed_skills(), Skill wiring checks (no GPU): every skill has a valid name+description, and…, skill_names(), TestSkills

### Community 16 - "Gerald - Memory Log"
Cohesion: 0.40
Nodes (4): Gerald - Memory Log, Lessons Learned, Recurring Patterns, Sessions

### Community 17 - "Lange - Memory Log"
Cohesion: 0.40
Nodes (4): Lange - Memory Log, Lessons Learned, Recurring Patterns, Sessions

### Community 18 - "Patek - Memory Log"
Cohesion: 0.40
Nodes (4): Lessons Learned, Patek - Memory Log, Recurring Patterns, Sessions

### Community 19 - "Philipe - Memory Log"
Cohesion: 0.40
Nodes (4): Lessons Learned, Philipe - Memory Log, Recurring Patterns, Sessions

### Community 20 - "Sohne - Memory Log"
Cohesion: 0.40
Nodes (4): Lessons Learned, Recurring Patterns, Sessions, Sohne - Memory Log

## Knowledge Gaps
- **186 isolated node(s):** `Bash-callable usage (works in any shell-driven agent)`, `Git`, `Keep it fresh`, `Optional: serve over MCP/HTTP`, `What's installed` (+181 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Self-Hostable Open-Weight Coding Models on a Single H100` connect `Self-Hostable Open-Weight Coding Models on a Single H100` to `Agentic Coding`, `4.7 Measured frontier-scale result: GLM-5.2 (753 B) on 8x H200 — Terminal-Bench 2`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Why does `4. Results` connect `4.7 Measured frontier-scale result: GLM-5.2 (753 B) on 8x H200 — Terminal-Bench 2` to `Self-Hostable Open-Weight Coding Models on a Single H100`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **What connects `Bash-callable usage (works in any shell-driven agent)`, `Git`, `Keep it fresh` to the rest of the system?**
  _186 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Agentic Coding` be split into smaller, more focused modules?**
  _Cohesion score 0.08 - nodes in this community are weakly interconnected._
- **Should `4.7 Measured frontier-scale result: GLM-5.2 (753 B) on 8x H200 — Terminal-Bench 2` be split into smaller, more focused modules?**
  _Cohesion score 0.08 - nodes in this community are weakly interconnected._
- **Should `Agentic Team Upgrade Plan (v1)` be split into smaller, more focused modules?**
  _Cohesion score 0.08 - nodes in this community are weakly interconnected._
- **Should `opencode.json` be split into smaller, more focused modules?**
  _Cohesion score 0.09090909090909091 - nodes in this community are weakly interconnected._