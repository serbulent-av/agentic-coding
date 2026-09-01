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

## Status

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
