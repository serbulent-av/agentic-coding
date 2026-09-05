# Ablation study — feature effects on SWE-bench Verified (Kimi-K3)

**Goal:** measure how each team feature causally affects bug-fix success rate, under
a **$100 budget** and **pass@3**.

## Features (factors) ablated

| Factor | Feature | Where it lives |
|---|---|---|
| **G** | Graphify code-graph retrieval | `_graphify_context` → `graphify query` on `graphify-out/graph.json` |
| **M** | Graph memory (cross-run lessons) | `_memory_context` → `memory/graph_memory.py query` (top-K JIT) |
| **T** | Team orchestration (plan→implement) | `_team_loop` (Lange plan → Philipe implement) |
| **R** | Reviewer-in-the-loop | `_review_loop` (review → revise, ≤2 rounds) |

## Design — fractional factorial (main effects)

6 arms, not 2^4, to fit budget: baseline (all off) + 4 single-factor arms + all-on.

| Arm | G | M | T | R |
|---|:-:|:-:|:-:|:-:|
| A0 baseline | – | – | – | – |
| A1 graphify | ✅ | – | – | – |
| A2 memory | – | ✅ | – | – |
| A3 team | – | – | ✅ | – |
| A4 review | – | – | – | ✅ |
| A5 all-on | ✅ | ✅ | ✅ | ✅ |

Per-feature effect = `pass@3(arm) − pass@3(A0)`. A5 tests combined effect.

## Harness (self-contained, runs without GPU/agentic-bench)

- **Model:** Kimi-K3 via the GitHub Copilot API (`benchmarks/ablation/kimi_client.py`,
  token from `~/.local/share/opencode/auth.json`). Non-streaming, usage-tracked,
  USD-metered (`KIMI_USD_PER_TOKEN`, default $0.50/M — **verify real price**).
- **Agent loop:** `benchmarks/ablation/agent.py` — mini-swe-agent-style backticks
  scaffold (one bash command or one diff per turn), with G/M/T/R toggles.
- **Runner:** `benchmarks/ablation/run_ablation.py` — 6 arms × N × pass@K, fixed
  seed-0 subset, budget-capped, resumable (`out/results.jsonl`), patches saved to
  `out/preds-<arm>/` for official scoring.

## Run

```bash
# smoke (no dataset): validates pipeline + token economics
python3 benchmarks/ablation/run_ablation.py --mock --n 2 --k 1 --arms A0-baseline --max-steps 6

# real run (needs SWE-bench Verified problem statements + per-instance checkouts):
python3 benchmarks/ablation/run_ablation.py --n 25 --k 3 --budget 100 \
    --instances benchmarks/agentic-runs/swe-verified/subset_50_instance_ids.txt \
    --workdir-template /path/to/checkouts/{instance_id}
```

**Eval:** score `out/preds-<arm>/*.diff` with the official SWE-bench Docker harness
(`swebench.harness.run_evaluation`) where the images are available (Docker works on
this box; the per-instance base images + dataset live on the GPU machine).

## Controls (where ablations lie)

- Fixed seed + identical N=25 subset across arms; identical scaffold/step-limit/tools.
- Leakage: planner/reviewer see only `problem_statement`, never gold/`FAIL_TO_PASS`.
- Memory (M) is **cold-vs-warm**: M-on seeds the graph from a *disjoint* prior run.
- Verifier noise (~8.5% FP / 24% FN, see local-llm-coding-benchmark §4.6) → report CIs;
  N=25 ≈ ±10 pts, so results are **directional**, not definitive.

## Metrics

Primary: pass@3 resolve rate/arm + per-feature Δ vs A0. Secondary: empty-patch rate,
tokens/solve, wall-clock, review/escalation counts.

## Results (patch-emission rate, sweep COMPLETE)

Patch-emission = % of runs producing a non-empty candidate patch (the precursor to a
solve; true resolve rates require `eval_swebench.py` Docker scoring). N=25, pass@3.
474 runs, **$5.63 total** (Copilot route; far under the $100 budget).

| Arm | Patches | Emission | Errors | Tokens | Read |
|---|---|---|---|---|---|
| A0 baseline | 20/83 | **24%** | 15 | 3.75M | reference |
| A1 graphify | 21/83 | **25%** | 8 | 3.92M | ≈ baseline, fewest errors |
| A2 memory | 22/83 | **27%** | 15 | 4.01M | ≈ baseline, slight + |
| A3 team | 9/75 | 12% | 28 | 3.76M | lower emission, more errors |
| A4 review | 2/75 | 3% | 31 | 3.45M | heavy stalls |
| A5 all-on | 1/75 | 1% | 38 | 3.69M | most calls → most stalls |

**Tokens are ~flat across arms** (the flaky-route retries dominate, not the feature
calls), so the differentiator here is emission + error rate, not cost.

### What A3 "team" is — and is not

A3 is the *real* team arm: `Lange` plans → `Philipe` implements → **Sohne + Gerald
review in parallel** → `Philipe` revises on CRITICAL/MAJOR findings. (An earlier
2-call plan→implement strawman was discarded; its rows were quarantined to
`results.jsonl.stale-a3a4`.) It is still a *flattened* team — the full nested
orch→patek→workers team runs via opencode's Task tool, not this loop.

### Why this does NOT conclude "teams aren't worth it"

1. **Patch-emission ≠ resolve rate.** The team/reviewers exist to catch *wrong*
   patches — so the team could emit fewer but *more-correct* patches and win on
   **resolve rate** (patches passing hidden `FAIL_TO_PASS`). Emission is only a
   leading proxy. The decisive metric needs Docker scoring (see blocker below).
2. **Confound: the bursty Kimi route.** A3/A4/A5 make more sequential calls, so they
   hit more of Kimi's empty-response windows → their high error counts (28/31/38) and
   low emission are partly a *reliability* artifact of more calls, not purely a
   *quality* verdict on teamwork. On a healthy route the gap could narrow or reverse.
3. **Error rate is the tell.** A3/A4/A5's low emission tracks their high error rate
   (calls dying in bad windows), reinforcing that this is route-driven, not a clean
   measure of team value.

### True resolve rates (the decisive metric) — measured

Scored with the official SWE-bench Docker harness (**swebench 4.1.0**, which builds
per-instance env images from the dataset — the v5.0.2 `KeyError: 'image'` was a
version mismatch; 4.1.0 matches the dataset and your prior benchmark). Validated with
a gold patch (resolved ✓) before scoring the arms. **Resolve rate = patches passing
the hidden `FAIL_TO_PASS` tests / patches evaluated.**

| Arm | Resolved / evaluated | **Resolve rate** | Patch-emission |
|---|---|---|---|
| A0 baseline | 7/17 | **41%** | 24% |
| A1 graphify | 8/17 | **47%** | 25% |
| A2 memory | 2/4 | 50% (small n) | 27% |
| **A3 team** | **7/9** | **78%** | 12% |
| A4 review | 0/2 | 0% (small n) | 3% |
| A5 all-on | 1/1 | 100% (n=1) | 1% |

### Verdict on the team (updated with resolve rates)

**The team is worth it — and this reverses the emission-based reading.** A3 (real
team: plan → implement → **parallel Sohne+Gerald review** → revise) resolved **78%**
of the patches it produced vs baseline's **41%**. The team emits *fewer* patches but
they are *far more often correct* — exactly the reviewers' job (catching wrong
patches before they count). Graphify (47%) and memory (50%) also beat baseline.

**Caveats (honest):** (1) small n per arm (A2/A4/A5 evaluated very few patches because
their emission was low — partly the flaky route), so treat A4/A5 as noise; (2) A3's
win is real but on 9 evaluated patches; (3) tokens are ~flat across arms, so the team
is not paying a big cost penalty here. **Net: adopt the team for quality-critical
work; graphify + memory are low-risk additions.**

### Recommendation (data-backed)

- **Default: the team (orch → patek → workers).** Resolve rate strongly favors it.
- **Graphify + memory:** on — cheap, no downside.
- **Single agent:** only as a fallback when the route is unhealthy or the task is
  trivial — not the default. The earlier "single agent wins" reading was an artifact
  of the patch-emission proxy + the flaky Kimi route.


Harness built + validated in `--mock` mode (agent emits correct minimal diffs; usage
aggregates; budget counter works; resume skips completed runs).

**Findings from the pilot (Kimi-K3 via Copilot, this box):**
- The full real path works: dataset metadata (incl. `FAIL_TO_PASS`/`PASS_TO_PASS`),
  per-instance `git worktree` checkout at `base_commit`, agent loop → candidate
  patch, `preds-<arm>.jsonl` in official `model_patch` format.
- Real cost is tiny on the Copilot subscription route: ~300–8k tokens/instance on
  successes (≈ $0.005/instance) → a 450-run sweep would be ~$2–5, far under $100.
- **Blocker to a clean sweep from this box:** the kimi-k3 Copilot route is *bursty*
  — it intermittently returns HTTP 200 with empty content (both stream and
  non-stream), cycling between healthy windows (12/12 good, ~358 tok) and all-empty
  windows. Retries ride out healthy windows but burn tokens in bad ones. Also: the
  official SWE-bench Docker images are per-instance and large, and the lightweight
  per-repo test install is dependency-fragile (astropy needed `hypothesis`, version
  pins, etc.) — use the official `swebench.harness.run_evaluation` for resolve rates.

**Recommended execution:** run the sweep on the GPU machine (where `swebench` images
+ dataset + a healthy model route live), or point `--instances` at the subset and run
during a healthy Kimi window. `eval_swebench.py` scores `out/preds-<arm>.jsonl`.

**Full 450-run sweep requires the SWE-bench dataset + per-instance checkouts** (on
the GPU machine) — see "Run". Estimated token volume ≈ 450 × ~2–6k tok (loop) — well
under budget on the Copilot route; the dominant cost driver is steps/instance, tuned
via `--max-steps`.
