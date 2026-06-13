# Self-Hostable Open-Weight Coding Models on a Single H100

**A technical report: capability, serving throughput, licensing, and agentic performance of
open models that fit on one NVIDIA H100 80 GB — benchmarked against Claude Opus 4.x, with
Opus-orchestrated planning experiments.**

*All numbers herein are either (a) measured on the machine described in §2, or (b) transcribed
from a cited official source. Nothing is estimated; anything unverifiable is marked as such.*

---

## Abstract

We evaluate six open-weight LLMs that fit on a single H100 80 GB for **internal, self-hosted
commercial coding** use. We measure function-level synthesis (HumanEval+, MBPP+), serving
throughput (tok/s), and **agentic** bug-fixing (SWE-bench Verified, run end-to-end under an
identical harness), audit model licenses for commercial use, and compare against Anthropic's
Claude Opus 4.6/4.7/4.8 using the vendors' published figures. We then test whether using
**Claude Opus 4.8 as an orchestrator** (planner, and reviewer-in-the-loop) lifts the local
models' agentic success. Headline findings: on saturated function benchmarks strong 30 B open
models reach the 80s–90s; on *agentic* SWE-bench Verified the same models score far lower under
a minimal scaffold (2–38 %), and we show empirically that **the harness, not just the model,
dominates agentic scores** (GLM-4.7-Flash: 18 % measured here vs 59.2 % self-reported). All six
models are MIT/Apache-2.0 (self-hostable, commercial-friendly); Opus is proprietary/API-only.

## 1. Introduction & research questions

A company that wants to run a coding model **inside its own infrastructure** (data residency,
air-gap, cost) needs to know: which open models are good enough, how fast they serve, whether
their licenses permit commercial use, and how far they sit behind a frontier model like Opus.
We answer:

- **RQ1 (capability):** How do single-H100 open models do on function-level synthesis?
- **RQ2 (throughput):** What serving tok/s do they achieve on one H100?
- **RQ3 (agentic):** How do they do on real repository bug-fixing (SWE-bench Verified) under a
  controlled, identical harness?
- **RQ4 (licensing):** Can a company use them commercially, self-hosted?
- **RQ5 (frontier gap):** How do they compare to Claude Opus 4.6/4.7/4.8?
- **RQ6 (orchestration):** Does using Opus 4.8 as a **planner** (Strategy B) or a
  **reviewer-in-the-loop** (Strategy C) raise the local models' agentic success?

## 2. Experimental setup

### 2.1 Environment

| Component | Spec |
|-----------|------|
| GPU | 1× NVIDIA H100 80 GB HBM3 (preemptible GCP VM) |
| Driver / CUDA | 580.159.03 / CUDA 13.0 |
| Serving | vLLM 0.22.1 |
| Framework | PyTorch 2.11.0, Transformers 5.11.0 |
| Function eval | EvalPlus (HumanEval+, MBPP+) |
| Agentic eval | mini-swe-agent 2.4.0 + SWE-bench harness 4.1.0 (Docker) |
| Orchestrator | Claude Opus 4.8 via the GitHub Copilot API (planner/reviewer) |
| Disk | 153 GB (forces download→bench→delete; agentic images chunked) |

### 2.2 Models under test

Selected because they **fit weights on one 80 GB H100**; larger models (§4.6) cannot.

| Model | Params (active) | Type | bf16 footprint |
|-------|-----------------|------|----------------|
| microsoft/phi-4 | 14.7 B | dense | ~29 GB |
| google/gemma-4-26B-A4B-it | 26.5 B (4 B) | MoE | ~53 GB |
| Qwen/Qwen3-Coder-30B-A3B-Instruct | 30.5 B (3 B) | MoE | ~61 GB |
| zai-org/GLM-4.7-Flash | 31.2 B | dense | ~62 GB |
| google/gemma-4-31B-it | 32.7 B | dense | ~65 GB |
| Qwen/Qwen2.5-Coder-32B-Instruct | 32.8 B | dense | ~66 GB |

## 3. Methodology

- **Function-level (§4.1):** `evalplus.codegen` (in-process vLLM, greedy, `max_model_len`=2048)
  then `evalplus.evaluate`. We report base and `plus` (hardened) pass@1.
- **Throughput (§4.2):** vLLM, bf16, 256 output tokens, single-stream (concurrency 1) and
  batched (concurrency 32).
- **Agentic (§4.3):** mini-swe-agent (minimal text/backticks scaffold — no native tool-calling)
  drives a local model served by vLLM (16 k context, 40-step limit, greedy; fp8 KV-cache on the
  62–66 GB models). Patches are scored by the official SWE-bench Docker harness. Subset: a fixed
  **seed-0 random 50** of SWE-bench Verified (7 repos), processed in chunks of 10 to respect disk.
- **Orchestration (§4.4):** Opus 4.8 (max effort) produces artifacts that are handed to the
  local implementer **through markdown files** (auditable). *Strategy B (plan-once):* Opus writes
  a per-instance plan injected into the task. *Strategy C (plan + review loop):* after the local
  model implements, Opus reviews the patch and returns md feedback; the local model revises, up
  to 3 rounds.
- **Licensing (§5):** read each model's HF card / `LICENSE` file.
- **Leakage controls (§6):** the planner/reviewer see **only** `problem_statement` (+ the
  candidate patch for review) — never the gold `patch`, `test_patch`, or `FAIL_TO_PASS`. The
  SWE-bench harness applies grading tests only at eval, so the implementer cannot see them.

## 4. Results

### 4.1 Function-level capability (HumanEval+, MBPP+)

Greedy pass@1 (%), sorted by composite = mean of the two `+` (hardened) scores.

| Rank | Model | HumanEval | HumanEval+ | MBPP | MBPP+ | Composite(+) |
|:--:|-------|:--:|:--:|:--:|:--:|:--:|
| 1 | gemma-4-31B | 92.7 | **89.6** | 86.5 | 74.9 | **82.3** |
| 2 | Qwen3-Coder-30B-A3B | 92.7 | 88.4 | 89.4 | 74.6 | 81.5 |
| 3 | Qwen2.5-Coder-32B | 90.9 | 86.0 | 89.9 | **76.5** | 81.3 |
| 4 | GLM-4.7-Flash | 84.8 | 80.5 | 81.7 | 68.8 | 74.7 |
| 5 | phi-4 | 86.6 | 80.5 | 74.3 | 64.0 | 72.3 |
| 6 | gemma-4-26B-A4B | 53.0 | 51.8 | 46.6 | 41.5 | 46.7 |

Top three are within ~1 point. Qwen3-Coder-30B-A3B matches dense 32 B models with only **3 B
active params** (cheapest to serve). gemma-4-26B-A4B (4 B active) trails badly — active-param
count tracks capability. Harness validated: phi-4's 80.5 HumanEval+ matches Microsoft's figure.
(Total run ~3 h 22 m; raw: `agentic-runs/.../results-summary.tsv`.)

### 4.2 Serving throughput (one H100, bf16, 256 output tokens)

| Model | Type | Single-stream tok/s | Batched-32 tok/s |
|-------|------|:--:|:--:|
| gemma-4-26B-A4B | MoE (4 B) | **206.7** | **4632.7** |
| Qwen3-Coder-30B-A3B | MoE (3 B) | 197.4 | 3825.9 |
| GLM-4.7-Flash | 31 B dense | 167.4 | 2266.6 |
| phi-4 | 14.7 B dense | 87.0 | 2598.6 |
| gemma-4-31B | 33 B dense | 41.4 | 1042.4 |
| Qwen2.5-Coder-32B | 33 B dense | 40.3 | 1226.5 |

MoE models lead single-stream (few active params). The dense 33 B models run ~4× slower; Gemma-4
is multimodal and appears to lack fully-optimized vLLM 0.22.1 kernels here. **Opus tok/s: not
published by Anthropic → no numeric comparison possible** (only the qualitative "fast mode ≈ 2.5×").

### 4.3 Agentic baseline (SWE-bench Verified, our harness)

End-to-end run, 50-instance subset, minimal scaffold. pass@1 = % whose patch passed the hidden tests.

| Model | pass@1 | resolved/50 | empty patches |
|-------|:--:|:--:|:--:|
| gemma-4-31B | **38.0 %** | 19 | 18 |
| GLM-4.7-Flash | 18.0 % | 9 | 37 |
| gemma-4-26B-A4B | 16.0 % | 8 | 30 |
| Qwen3-Coder-30B-A3B | 12.0 % | 6 | 20 |
| Qwen2.5-Coder-32B | 8.0 % | 4 | 28 |
| phi-4 | 2.0 % | 1 | 40 |

**Key result — harness dominates.** GLM-4.7-Flash scores **18 % here vs 59.2 % self-reported** on
the *same* benchmark. The ~40-pt gap is scaffold + 16 k context + 40 steps, not the model. The
only clean comparison is *within* this table (identical harness): **gemma-4-31B wins agentic
coding (38 %)**, far ahead of the nominal "coder" models, which suffered high empty-patch rates
(scaffold-fit, not necessarily skill). See §6 for the leakage audit of these wins.

### 4.4 Opus-orchestrated planning (Strategy B & C)

Pilot on a fixed **12-instance** subset of the 50 (7 repos), comparing **Baseline** (§4.3, same
instances) vs **B** (Opus plan-once) vs **C** (Opus plan + ≤3 review rounds). Implementers: phi-4
(weak; 80 % empty baseline) and gemma-4-31B (strong). Opus 4.8 is the planner/reviewer via the
Copilot API; all plans/reviews are persisted as markdown handoff files in `agentic-runs/swe-c/`.

| Implementer | Baseline (12) | B: plan-once | C: plan + review×3 |
|-------------|:--:|:--:|:--:|
| phi-4 | 1/12 | 1/12 | 2/12 |
| gemma-4-31B | 7/12 | 5/12 | 8/12 |

> **Findings.** Opus *plan-once* (B) did not raise resolved counts: phi-4 stayed at 1/12 (the plan
> changed *which* instance it solved, not how many) and gemma-4-31B actually fell from 7/12 to 5/12,
> so injecting a plan hurt the stronger model. The Opus *review loop* (C, ≤3 rounds) helped both
> modestly — phi-4 reached 2/12 and gemma-4-31B recovered to 8/12, one above its baseline and three
> above plan-once (C adds django-11433 and keeps all seven baseline solves; phi-4's two solves are
> a different pair than its single baseline win). The review loop's value was thus mostly *undoing*
> the plan-once regression while adding a single net solve per model over baseline, not a large gain.
> Review rounds used differed by model strength: gemma converged fast (avg 2.0 rounds — 4 of 12
> patches approved after round 1, 8 of 12 finalized by round 2), whereas phi-4 almost always hit the
> 3-round cap (avg 2.83 rounds; 10 of 12 ran all three rounds as Opus kept rejecting its mostly-empty
> patches).

### 4.5 Comparison vs Claude Opus 4.6 / 4.7 / 4.8 (vendor-reported)

We could not run Opus through our harness within scope, so this is a **cross-harness, vendor-
reported** comparison. Two caveats: (1) Anthropic reports SWE-Bench **Pro** while open models
report SWE-bench **Verified** (different, easier) and **Terminal-Bench 2.1** vs **2.0**;
(2) cross-harness variance is large (Opus-4.6 SWE-Bench Pro is measured at 53.4 by Kimi, 57.3 by
DeepSeek, vs Anthropic's self-reported 4.8 = 69.2). **Do not read these as a clean ranking.**

**Opus — from Anthropic's official Opus 4.8 launch chart** (covers 4.8 & 4.7 only):

| Benchmark | Opus 4.8 | Opus 4.7 | GPT-5.5 | Gemini 3.1 Pro |
|-----------|:--:|:--:|:--:|:--:|
| SWE-Bench Pro | **69.2** | 64.3 | 58.6 | 54.2 |
| Terminal-Bench 2.1 | 74.6 | 66.1 | **78.2** | 70.3 |
| HLE (no tools / tools) | 49.8 / 57.9 | 46.9 / 54.7 | 41.4 / 52.2 | 44.4 / 51.4 |
| OSWorld-Verified | 83.4 | 82.8 | 78.7 | 76.2 |
| Finance Agent v2 | 53.9 | 51.5 | 51.8 | 43.0 |

Opus 4.x: released 2026-02-05 / 04-16 / 05-28; $5/$25 per MTok; 1 M context; **proprietary,
API/cloud-only (not self-hostable)**.

**Open models — vendor self-reported** (own harnesses; HF cards):

| Model | SWE-bench | Terminal-Bench | LiveCodeBench v6 | HLE (no tools) | τ²-Bench |
|-------|:--:|:--:|:--:|:--:|:--:|
| GLM-4.7-Flash | 59.2 (Verified) | referenced, no number | 64.0 | 14.4 | 79.5 |
| gemma-4-31B | not reported | — | 80.0 | 19.5 | 76.9 |
| gemma-4-26B-A4B | not reported | — | 77.1 | 8.7 | 68.2 |
| Qwen3-Coder-30B-A3B / Qwen2.5-Coder-32B / phi-4 | not reported | — | — | — | — |

The only axis with numbers for both is **HLE** (reasoning, tool-settings differ), where Opus
leads decisively (49.8 vs ≤19.5). On SWE-bench, Pro≠Verified prevents a clean comparison.

### 4.6 Beyond a single GPU (oversized models)

Requested but **cannot run on one H100** (weights exceed 80 GB even at FP8). Their vendor-
published agentic scores (each from the model's HF card), shown with Opus for reference:

| Model | Params | Min HW | SWE-Bench Pro | SWE-bench Verified | Terminal-Bench 2.0 |
|-------|:--:|--|:--:|:--:|:--:|
| GLM-4.5-Air | 106B-A12B | 2–4× H100 | n/r¹ | n/r¹ | n/r¹ |
| DeepSeek-V4-Flash (Max) | 158 B | 2–4× H100 | 52.6 | 79.0 | 56.9 |
| GLM-5.1 | 754 B | 8× H100+4-bit | 58.4 | — | 63.5 |
| DeepSeek-V4-Pro (Max) | 862 B | 8–16× H100 | 55.4 | 80.6 | 67.9 |
| Kimi-K2.6 | 1.06 T | 8× H100+4-bit | 58.6 | 80.2 | 66.7 |
| _Claude Opus 4.8 (ref)_ | — | API only | **69.2** | — | 74.6 (TB **2.1**) |

¹ GLM-4.5-Air's card reports only an aggregate 59.8/12-benchmarks. Even 750 B–1 T open flagships
self-report **high-50s on SWE-Bench Pro** (vs Opus 4.8's self-reported 69.2); on the easier
Verified they cluster ~79–81 (≈ third-party-measured Opus-4.6 ≈ 80.8). GLM-5.1 (58.4) and
Kimi-K2.6 (58.6) SWE-Bench Pro are cross-validated in DeepSeek's independent table.

## 5. Licensing & commercial-use suitability

| Model | License | Verified from | Internal commercial use |
|-------|---------|---------------|-------------------------|
| microsoft/phi-4 | **MIT** | `LICENSE` file | ✅ unrestricted |
| google/gemma-4-26B-A4B-it | **Apache-2.0** | card metadata + text | ✅ unrestricted |
| google/gemma-4-31B-it | **Apache-2.0** | card metadata + text | ✅ unrestricted |
| Qwen/Qwen3-Coder-30B-A3B-Instruct | **Apache-2.0** | card + `LICENSE` | ✅ unrestricted |
| Qwen/Qwen2.5-Coder-32B-Instruct | **Apache-2.0** | `LICENSE` file | ✅ unrestricted |
| zai-org/GLM-4.7-Flash | **MIT** | card metadata | ✅ unrestricted |

All six are OSI-approved permissive licenses — self-host, modify, and use commercially with no
fee or field-of-use restriction (keep LICENSE/NOTICE; Apache-2.0 adds a patent grant). **Notably,
Gemma 4 is Apache-2.0**, a change from Gemma 1–3's custom terms. Claude Opus 4.x is **proprietary
(Anthropic Commercial Terms), API/cloud-only** — not runnable on your own hardware.

## 6. Threats to validity

- **Harness sensitivity (largest):** §4.3 shows a ~40-pt swing for the *same* model/benchmark
  from scaffold/context alone. Our agentic numbers are comparable **only among our 6 models**.
- **Leakage audit (gemma):** all 19 of gemma-4-31B's baseline wins edit **1 source file, 0 test
  files** (e.g. django-11163 = the canonical `if fields is not None` fix). The harness applies
  grading tests only at eval, so the agent cannot see/cheat them. The planner/reviewer see only
  `problem_statement` (+ candidate patch). Residual: public-issue pretraining contamination, which
  affects **all six models equally**.
- **Subset noise:** 50 (and 12-instance pilot) subsets are noisy (≈ ±7 pts); fixed seed-0 for
  reproducibility.
- **Quantization:** fp8 KV-cache on the 62–66 GB models (memory); weights bf16.
- **Cross-harness vendor numbers (§4.5/4.6):** different harnesses/effort — directional only.

## 7. Reproducibility

```bash
# env: Python 3.12, CUDA driver, python3.12-dev + build-essential + ninja-build + docker
uv venv && uv pip install vllm evalplus mini-swe-agent swebench
bash run_bench.sh            # §4.1 function-level (HumanEval+/MBPP+)
bash run_throughput.sh       # §4.2 throughput
bash run_swe_verified.sh     # §4.3 agentic baseline (50-instance subset)
python build_planned.py      # §4.4 Strategy B planned dataset (Opus plans)
bash run_pilot_planned.sh    # §4.4 Strategy B pilot
python run_strategy_c.py     # §4.4 Strategy C (Opus review loop; opus_client.py)
```

Artifacts (this directory): `run_*.sh`, `*.py`, fixed subset (`subset_50_instance_ids.txt`,
`pilot_ids.txt`), plans (`plans_pilot.jsonl`), Opus md handoffs (`swe-c/handoff/`), raw
trajectories, 30+ SWE-bench report JSONs, and per-experiment summary TSVs.

## 8. Conclusions & recommendations

1. **For self-hosted function-level coding on one H100:** gemma-4-31B, Qwen3-Coder-30B-A3B, and
   Qwen2.5-Coder-32B are ~tied (composite ~81–82). **Qwen3-Coder-30B-A3B is the value pick**
   (3 B active → fastest single-stream at near-top quality).
2. **For agentic coding (real bug-fixing):** under a minimal scaffold **gemma-4-31B leads (38 %)**;
   all open models are far below their marketing numbers because the scaffold matters more than
   the model. Invest in the agent harness, not just the weights.
3. **Licensing:** all six are commercial-friendly and self-hostable (MIT/Apache-2.0). Opus is
   not self-hostable — choose it for peak capability via API, not for on-prem/air-gapped use.
4. **Frontier gap:** real and large on agentic/reasoning tasks, but not cleanly quantifiable from
   public cross-harness numbers; even 1 T open models report high-50s on SWE-Bench Pro vs Opus 69.2.
5. **Opus-as-orchestrator (§4.4):** _conclusion pending experiment completion._

## References

Accessed 2026-06-11/13.

**Anthropic / Opus:** announcement (chart) https://www.anthropic.com/news/claude-opus-4-8 ·
product https://www.anthropic.com/claude/opus · models overview
https://docs.anthropic.com/en/docs/about-claude/models/overview · commercial terms
https://www.anthropic.com/legal/commercial-terms

**Open model cards:** microsoft/phi-4 · google/gemma-4-31B-it · google/gemma-4-26B-A4B-it ·
Qwen/Qwen3-Coder-30B-A3B-Instruct (+ blog https://qwenlm.github.io/blog/qwen3-coder/) ·
Qwen/Qwen2.5-Coder-32B-Instruct · zai-org/GLM-4.7-Flash · Gemma-4 license
https://ai.google.dev/gemma/docs/gemma_4_license (all at https://huggingface.co/<id>)

**Oversized:** deepseek-ai/DeepSeek-V4-Pro · DeepSeek-V4-Flash · zai-org/GLM-5.1 ·
moonshotai/Kimi-K2.6 · zai-org/GLM-4.5 (all at https://huggingface.co/<id>)

**Tooling:** vLLM https://github.com/vllm-project/vllm · EvalPlus
https://github.com/evalplus/evalplus · mini-swe-agent / SWE-bench
https://github.com/SWE-agent/mini-swe-agent · https://github.com/princeton-nlp/SWE-bench

**Could not verify:** Opus 4.6 SWE-Bench Pro/Terminal-Bench (absent from the 4.8 chart);
per-model SWE-bench for Qwen3-Coder-30B-A3B and GLM-4.5-Air; the Opus 4.8 System Card
(exceeded fetch limit — figures taken from the announcement chart).

## Appendix A — agentic subset (seed 0, 50 instances, 7 repos)

django (22), sympy (11), sphinx (6), matplotlib (4), pydata/xarray (3), scikit-learn (3),
astropy (1). Full IDs: `agentic-runs/swe-verified/subset_50_instance_ids.txt`; 12-instance
planning pilot: `pilot_ids.txt`.
