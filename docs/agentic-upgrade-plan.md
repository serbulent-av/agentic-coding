# Agentic Team Upgrade Plan (v1)

> **HISTORICAL — SUPERSEDED.** This is the original research/plan written for a
> *mini-swe-agent* runtime. The repo was ultimately built on **opencode**: the team
> runs as opencode agents (`orch` → `patek` → `lange`/`philipe`/`sohne`/`gerald`),
> the orchestrator is a pure **agent** (no Python package), and skills are real
> Agent-Skills under `skills/`. Read this only for background/rationale; for what
> exists, see [orchestrator.md](orchestrator.md), [graphify.md](graphify.md), and
> the repo `README.md`.

Status: **historical draft (mini-swe-agent era), superseded by the opencode build.**
Scope (as originally written): modernize the Patek/Lange/Philipe/Sohne/Gerald team
and how it is dispatched and supervised, on the **mini-swe-agent + local-vLLM
harness** (not opencode).

> This v1 supersedes the v0 draft. Every one of the four reviewers (Lange, Philipe, Sohne,
> Gerald) returned **BLOCKED** on v0. Their must-fixes are folded in below; see the
> [Team review log](#appendix-a--team-review-log) for the raw verdicts.

---

## 0. TL;DR — what changed after review

The v0 plan was over-built and contradicted your own benchmarks. The four biggest corrections:

1. **Fix the model-allocation inversion.** v0 put weak models on the role that emits the
   patch. Your data: **gemma-4-31B 38%** is the best agentic model; Qwen3-Coder-30B-A3B is
   **14%**, GLM-4.7-Flash **18%**, phi-4 **2%**. → The **implementer must run the strongest
   model**, not the reviewers/planner.
2. **Attack the real bottleneck first: empty patches.** Failures are dominated by empty/
   malformed patches (phi-4 40/50, GLM-4.7-Flash 37/50, gemma 18/50) — a harness/tool-format
   reliability problem, **not** a planning or oversight problem. Orchestration is not the
   bottleneck.
3. **Respect the runtime.** mini-swe-agent uses a `litellm_textbased` **backticks** scaffold:
   one shell command per step, **no tool-calling, no MCP client, no skill runtime**. So
   "MCP over HTTP", "skills", and "skill-trigger-rate" do not exist here. Graphify must be a
   **bash-callable CLI**; "skills" are **prompt sections / `cat`-able files**; usage is measured
   from trajectories.
4. **Gate every added layer on evidence.** Start **flat** (dispatcher → implementer + 1 reviewer
   + deterministic gates). Add roles / oversight team / Graphify **only if an A/B beats the
   frozen single-agent baseline (gemma-4-31B, 38%)**. Plan-once already *regressed* strong
   models (−14); the review loop was +1 (within ±7–8 pt noise).

---

## 1. Context & evidence

**Repo today:** five agents defined only as prose (`agents/<name>/description.md`), `memory.md`
are 17-line stubs, nothing wired to a runtime.

**Actual runtime:** `minisweagent.run.benchmarks.swebench --model-class litellm_textbased -c
swebench_backticks.yaml`, one vLLM model on port 8000 (weights unloaded before the next),
`-w` = concurrent instances against that one endpoint, `step_limit≈40`, evaluated by the
SWE-bench Docker harness. The only proven multi-role mechanism is the out-of-band
plan→implement→review loop in `run_strategy_c.py`.

**Measured results (SWE-bench Verified, seed-0 subset of 50) — `benchmarks/.../summary.tsv`:**

| Model | resolved/50 | pass@1 | empty patches |
|---|---|---|---|
| gemma-4-31B | 19 | **38.0%** | 18 |
| GLM-4.7-Flash | 9 | 18.0% | 37 |
| gemma-4-26B-A4B | 8 | 16.0% | 30 |
| Qwen3-Coder-30B-A3B | 7 | 14.0% | 20 |
| Qwen2.5-Coder-32B | 4 | 8.0% | 28 |
| phi-4 | 1 | 2.0% | 40 |

**Orchestration experiments (benchmark §4.3):** Strategy B (Opus plan-once) took gemma-4-31B
38%→24% (**−14**) and GLM-4.7-Flash 18%→6%; Strategy C (review loop) was **+1** on the 12-subset
(7/12→8/12). **Harness dominates.**

**Measurement caveats (benchmark §4.6–4.7):** seed-50 carries **±7–8 pt** noise; the SWE-bench
verifier is **8.5% FP / 24% FN**; GLM-5.2 at **8-way concurrency** produced prefill-contention
**timeout cascades** (6/10 raw failures were timeouts, not wrong answers).

**SOTA sources informing the design:** Anthropic *Effective context engineering* (smallest
high-signal token set, compaction, note-taking, JIT retrieval, context rot); Anthropic *Multi-
agent research system* (~15× tokens, coding less parallelizable, subagents return distilled
summaries, artifacts to filesystem); Cognition *Don't build multi-agents* (parallel multi-agent
coding is fragile; share full context; prefer linear + compression model); Anthropic *Agent
Skills* (progressive disclosure; the description is the trigger). Tools: **Graphify** (local,
deterministic tree-sitter graph-of-code; ships as a skill **and** a bash/HTTP query CLI);
**Agent Orchestrator** (worktree-isolated fleet IDE — kept OUT of scope as an optional human
dashboard only).

---

## 2. Diagnosis: what the data says the bottleneck is

Rank-ordered by measured impact:

1. **Patch-emission reliability** (empty/malformed patches) — the dominant failure mode.
2. **Base model capability on the implementer role** — gemma-4-31B ≫ the others.
3. **Verifier/measurement noise** — big enough to hide any small orchestration gain.
4. **Context/harness format** — everything else.

Orchestration elaborateness (multi-role teams, oversight teams) is **not** in the top tier of
measured impact. The plan is sequenced accordingly: reliability and the right model first;
orchestration only where it earns its keep.

---

## 3. Locked decisions (revised)

- **Control plane:** a **minimal custom asyncio/subprocess scheduler** extending
  `run_strategy_c.py`. **Not** LangGraph (adds a framework onto a harness that already dominates,
  for no throughput gain). AO desktop is out of scope.
- **Concurrency model:** one GPU-bound endpoint is the reality. Default is **role-batched
  scheduling** (load model M, run that stage for all active tasks, swap) — **not** N independent
  GPU jobs. "N teams" means `-w N` sized to measured throughput, or partitioned endpoints **only
  if explicitly funded**. "10 teams concurrently" is treated as batched/multiplexed, not 10
  parallel GPU jobs (your §4.7 shows 8-way already saturates).
- **Models:** cost-capped hybrid — local-first; Opus 4.8 **only** on ambiguous escalation.
- **Team structure:** the five roles are retained as the design, but the **MVP execution graph
  is flat** and roles are switched on incrementally, each gated by an A/B beating baseline.

---

## 4. Model-per-role (CORRECTED)

| Role | Model (revised) | Rationale (from your data) |
|---|---|---|
| **Implementer (Philipe)** | **gemma-4-31B** (38%); escalate hard cases to GLM-5.2 | The patch-emitter must be the strongest agentic model. This single swap likely beats the whole orchestration effort. |
| **Reviewer (Gerald/Sohne)** | GLM-5.2 or gemma-4-31B (**reviewer ≥ implementer**); contested → Opus 4.8 | GLM-4.7-Flash (18%) reviewers miss subtle defects and make the conflict-escalation signal unreliable. |
| **Planner (Lange)** | Lightweight/local, **A/B-gated, off by default** | Plan-once *hurt* strong models (−14). Do not force a heavy planner on a strong implementer. |
| **Summarizer / compaction** | phi-4 or gemma-4-26B-A4B | Cheap, frequent. **Never compact requirement/acceptance fields; keep a pointer to the full artifact.** |
| **Orchestrator / oversight (Patek)** | GLM-5.2 local; Opus on escalation | Runs rarely, on compact inputs. |

> **Serving note:** GLM-5.2 (753B) is TP=8 across all 8×H200 — it cannot co-serve with other
> models. Mixed-model roles therefore require **role-batched swapping** or **partitioned
> endpoints** (capacity spike, §7). gemma-4-31B fits far smaller, so an implementer+reviewer
> two-endpoint split may be feasible if GPUs are partitioned.

---

## 5. Escalation policy (cost-capped hybrid)

Default all roles local. Escalate to Opus 4.8 **only** when:
- (a) deterministic gates fail after **K=2** local revision rounds **with no-progress/oscillation
  detection** (escalate on detected non-convergence, not merely on round count); or
- (b) a **contested CRITICAL** review (reviewer/implementer disagreement on a real defect).

Controls (replacing v0's fixed `≤N/2`): **soft budget + priority queue keyed by severity**;
defer-and-retry in the next window; **alarm when demand > budget** (signals a mis-specified
batch → human triage); global **token/$ ceiling with a fleet kill-switch**; **log every
escalation with reason** for threshold tuning.

---

## 6. Out of scope (v0/v1)

AO desktop dashboard; model fine-tuning; multi-repo fleets; full (non-seed) SWE-bench runs;
LangGraph/any orchestration-framework migration; real-production **destructive** DevOps
execution; native tool-calling / MCP scaffold (until/unless the harness is replaced).

---

## 7. Spikes (time-boxed, gating — do these before the steps they gate)

| Spike | Question | Gates | Exit criterion |
|---|---|---|---|
| **S1 Token accounting** | Does `litellm_textbased` populate `usage` for local vLLM, or must we tokenize `.traj`? (`MSWEA_COST_TRACKING=ignore_errors` today) | ALL token criteria | tokens/solve extractable per run |
| **S2 Capacity/concurrency** | p95 TTFT + throughput at concurrency 1/4/8 per endpoint | sets **N** for Step 6 | measured `N_max` (start from n=4; 8 timed out) |
| **S3 Control-plane** | asyncio/subprocess role-batched scheduler over the agent CLI | Step 3 | runs a 2-stage loop on 5 instances |
| **S4 Graphify-vs-grep** | Does a bash `graphify query` beat `ripgrep` on tokens-to-localization? | Step 5 | ≥25% median token cut on a named 15-task set, else drop |
| **S5 Skill/tool selection** | Do local models reliably pick the right `cat`-able reference? | Step 5 skills | trigger-rate ≥80% on a labeled 20-case eval |

---

## 8. The plan — steps in execution order

Each step lists atomic tasks, a **numeric** acceptance bar (tied to the Step 0 baseline), and a
**kill criterion**. Experiment protocol (all steps): fixed seeds, report CIs; **seed-50 is a
smoke test only** — decisions require a power-justified N.

### Step 0 — Instrumentation & frozen baseline (prerequisite)
- 0.1 Land token accounting (S1).
- 0.2 Freeze `baseline.json` on seed-50: per-model resolved-rate, **tokens/solve**, empty-patch
  rate, wall-clock. (Resolved-rate exists; add tokens + wall-clock.)
- 0.3 Capacity spike (S2) → record `N_max`.
- 0.4 Control-plane spike (S3).
- **Accept:** committed `baseline.json` + scheduler runs a 5-instance smoke; go/no-go logged.
- **Kill:** if tokens can't be extracted, stop — no efficiency claim is falsifiable without it.

### Step 1 — Patch-emission reliability (attack the real bottleneck)
- Format-adherence hardening for the backticks scaffold; **apply-and-retry** on `git apply`
  failure; patch-format lint; per-command timeout (600s wrapper already used).
- **Accept:** empty-patch rate on seed-50 **reduced ≥1/3** vs baseline (e.g. gemma 18→≤12) with
  resolved-rate **not lower** (within CI).
- **Kill:** if reliability fixes don't move empty-rate, re-diagnose before any orchestration.

### Step 2 — Prompt distillation & context discipline (Problem 5)
- Distill the five 80–140-line personas to right-altitude prompts; move formats to **`cat`-able
  reference files**; wire the summarizer for handoffs (**never** compact requirement/acceptance
  fields; keep a pointer to the full artifact); bound tool output.
- **Accept:** **≥30% fewer prompt tokens/role** vs baseline **and** resolved-rate within CI
  (confirm on > seed-50 before believing "no regression"); summarizer **requirement-retention
  ≥95%** on a labeled handoff set.
- **Kill:** if distillation drops a weak model's solve beyond CI, roll back per-model.

### Step 3 — Minimal team MVP (Problem 1), flat & gates-first
- `dispatcher → implementer (gemma-4-31B) + ONE reviewer (GLM-5.2) + gates`, role-batched.
- **Legitimate gates only:** `git apply` clean **+** pre-existing suite does not regress **+**
  agent-written tests **+ test-integrity guard** (flag/reject diffs touching test files/oracle).
  **Never gate on hidden `FAIL_TO_PASS`** (eval leak). Slow verifiers: let them complete;
  separate "timeout" from "fail". Treat the gate as **noisy evidence (≈32% wrong), not truth.**
- Escalation per §5.
- **Accept:** team resolved-rate **≥ gemma-4-31B single-agent baseline (38%)** at **≤ baseline
  tokens/solve** (report CIs).
- **Kill:** if the flat team doesn't beat single-agent, **stop and do not add layers** — the
  orchestration doesn't pay (consistent with your data).

### Step 4 — Add roles incrementally, each A/B-gated (full team)
- Add planner (Lange) only if it lifts a *strong* implementer (expected marginal/negative — keep
  it lightweight or skip). Add the second reviewer (Sohne vs Gerald split) only if it adds
  solves. Each addition gated vs the Step 3 result.
- **Accept:** each added role shows **+solves beyond CI**, else it is cut.

### Step 5 — Graphify retrieval + reference "skills" (Problems 2 + 4)
- Graphify as a **bash-callable CLI/HTTP baked into the instance Docker image** (`graphify
  query …` / `curl localhost:PORT`) — **not** MCP. **Version the graph to the commit**; rebuild
  or mark stale per worktree; return **provenance + confidence**; **fall back to grep** on low
  confidence. "Skills" = reference files with sharp trigger descriptions; measure usage from
  trajectories (S5).
- **Accept:** A/B **beats a ripgrep baseline** on tokens-to-localization **and** resolved-rate on
  a named ≥15-task set (S4).
- **Kill:** if grep ties, don't build the graph path.

### Step 6 — Scale to N teams + oversight (the hard one) — only after Step 3/4 beat baseline
- Fan out **N (= `N_max` from S2, not "10")** teams, role-batched; per-team checkpoint/resume.
- **Oversight is not card-only.** It triages on fixed-schema status cards **but performs
  risk-weighted + random FULL-diff audits** and runs **defect-injection canaries** to *measure*
  its own recall (cards are self-reported and phi-4-compacted → structurally blind to the 8.5%
  "tests-pass-but-wrong" defects).
- **Status-card schema (deliverable):** `team_id, task_id, stage, gate_results, blockers,
  token_spend, escalation_flag, artifact_pointer` — with a max token size.
- **Accept:** oversight **defect-recall ≥ target on injected canaries**; fleet throughput +
  accuracy documented at the measured N; total token/$ within ceiling.
- **Kill:** low canary recall = false assurance → fix or cut the oversight layer.

### Step 7 — DevOps / non-coding generalization (Problem 3)
- Domain-agnostic role prompts; **runbook reference files**; **scoped allow-list with dry-run +
  rollback in reversible sandboxes** (blanket deny blocks autonomy; most ops actions are stateful)
  and human-gating for irreversible actions.
- **Accept:** **≥3** non-coding tasks (e.g. Terminal-Bench DevOps) pass a defined checklist with
  human-gated destructive actions.

### Continuous — experiment protocol
Fixed seeds; power-justified N; report CIs/variance; attribute each change; seed-50 = smoke only.

---

## 9. The "10 teams + oversight" architecture (honest version)

- **Efficiency** comes from: context isolation per task, **role-batched model scheduling** on the
  single endpoint, compact status cards for *triage*, and **deterministic gates doing the cheap
  filtering** — not from 10 parallel GPU jobs (infeasible on your box today).
- **Accuracy** comes from: the **strongest model on the implementer**, **reviewer ≥ implementer**,
  **test-integrity-guarded gates treated as noisy evidence**, **full-diff + canary oversight**
  (not card-only), and **strong-but-rare Opus adjudication**.
- **N is measured, not assumed** (S2). If you need genuine parallel throughput, that's a funded
  decision to **partition the 8×H200 into multiple endpoints or add replicas** — recorded as an
  open question, not baked in.

---

## 10. Risks

- Local models are weak at reference/tool selection (Tool-Decathlon −11.7) → sharper descriptions
  + S5 measurement.
- Correlated batch difficulty can exceed the escalation budget → priority queue + alarm (§5).
- Graphify staleness/wrong-edge feeding bad context → version-to-commit + confidence + grep
  fallback (Step 5).
- Distillation can strip scaffolding weak models depend on → per-model rollback (Step 2).
- `websearch-cited` plugin is misconfigured (`Missing web search model configuration`) → blocks
  grounded search; fix separately.

---

## 11. Open questions (need your call)

1. Confirm **gemma-4-31B as primary implementer** (fixes the inversion).
2. GPU budget: may we **partition 8×H200** for ≥2 concurrent endpoints (implementer + reviewer
   diversity), or must everything **role-batch** on one endpoint?
3. Confirm **"N teams" = throughput-bounded**, not literally 10 concurrent GPU jobs.
4. Fix the `websearch-cited` plugin now (to enable grounded search for S4/comparisons)?

---

## Appendix A — Team review log

Reviewers ran concurrently as subagents on the v0 draft; all returned **BLOCKED**. Consensus
must-fixes (folded into v1):

- **Lange (planning):** no out-of-scope section; §5 bundles not decomposed; acceptance criteria
  untestable; **no frozen baseline** (added Step 0); convert risks → time-boxed spikes (§7);
  drop "reorderable"; `docs/` didn't exist.
- **Philipe (implementation):** runtime mismatch — **no MCP/skill runtime** in the backticks
  scaffold (Graphify → bash CLI; skills → files); **single-model serving** contradicts mixed
  per-role (→ role-batched); token accounting disabled today (S1); gate must be non-leaking;
  git worktrees redundant with Docker-per-instance isolation.
- **Sohne (oversight):** **3-level layer cake built before evidence**; flatten to dispatcher →
  implementer + 1 reviewer, gates-first; **implementer-model inversion**; commit to minimal
  asyncio (drop LangGraph); gate Graphify/oversight/extra roles behind A/B + a **kill criterion**.
- **Gerald (red team):** single-endpoint concurrency vs 10-team claim (measured timeouts); gate
  is **noisy/gameable/vacuous** (32% wrong, test-editing, no-test tasks); **oversight blind to
  card-invisible defects** → full-diff audits + canaries; escalation `≤N/2` breaks under
  correlated difficulty; phi-4 summarizer is a lossy single point; reviewers weaker than
  implementer make the escalation signal unreliable.

## Appendix B — Sources

Anthropic: *Effective context engineering for AI agents*; *How we built our multi-agent research
system*; *Equipping agents for the real world with Agent Skills*. Cognition: *Don't build
multi-agents*. Tools: Graphify (`Graphify-Labs/graphify`), Agent Orchestrator
(`Untrivial-ai/agent-orchestrator`). Internal: `benchmarks/local-llm-coding-benchmark.md`,
`benchmarks/.../summary.tsv`.
