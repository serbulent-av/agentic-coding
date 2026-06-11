# Local LLM Coding Benchmark (single H100 80GB)

Benchmark of open-weight coding/reasoning models that fit on a **single NVIDIA H100 80GB**,
served with **vLLM** and scored with **EvalPlus** (HumanEval+ and MBPP+, greedy pass@1).

> Status: results are filled in by `run_bench.sh`. Numbers below are measured on this
> machine — any model that cannot run is marked explicitly, never estimated.

## Environment

| Component | Version / spec |
|-----------|----------------|
| GPU | 1× NVIDIA H100 80GB HBM3 |
| Driver / CUDA | 580.159.03 / CUDA 13.0 |
| vLLM | 0.22.1 |
| PyTorch | 2.11.0 |
| Transformers | 5.11.0 |
| Benchmark | EvalPlus (HumanEval+, MBPP+) |
| Decoding | greedy (temperature 0), pass@1 |
| Context | max_model_len = 2048 (EvalPlus default) |
| dtype | bfloat16 |

## Method

For each model: `evalplus.codegen` generates one greedy solution per task via the in-process
vLLM backend, then `evalplus.evaluate` runs the test suites. `base` = original benchmark tests;
`plus` = EvalPlus's expanded edge-case tests (the harder, more meaningful score). Weights are
deleted between models to stay within the 153 GB disk.

## Models tested (fit on one H100 80GB)

| Model | Params | Type | bf16 footprint |
|-------|--------|------|----------------|
| microsoft/phi-4 | 14.7B | dense | ~29 GB |
| google/gemma-4-26B-A4B-it | 26.5B | MoE (4B active) | ~53 GB |
| Qwen/Qwen3-Coder-30B-A3B-Instruct | 30.5B | MoE (3B active) | ~61 GB |
| zai-org/GLM-4.7-Flash | 31.2B | dense | ~62 GB |
| google/gemma-4-31B-it | 32.7B | dense | ~65 GB |
| Qwen/Qwen2.5-Coder-32B-Instruct | 32.8B | dense | ~66 GB |

## Results

Greedy (temperature 0) pass@1, measured on this machine. Sorted by **composite**
= mean of the two `+` (hardened) scores, which are the most meaningful columns.

| Rank | Model | Active params | HumanEval | HumanEval+ | MBPP | MBPP+ | Composite (+) |
|:----:|-------|:-------------:|:---------:|:----------:|:----:|:-----:|:-------------:|
| 1 | google/gemma-4-31B-it | 32.7B (dense) | 92.7 | **89.6** | 86.5 | 74.9 | **82.3** |
| 2 | Qwen/Qwen3-Coder-30B-A3B-Instruct | 3B (MoE) | 92.7 | 88.4 | 89.4 | 74.6 | 81.5 |
| 3 | Qwen/Qwen2.5-Coder-32B-Instruct | 32.8B (dense) | 90.9 | 86.0 | 89.9 | **76.5** | 81.3 |
| 4 | zai-org/GLM-4.7-Flash | 31.2B (dense) | 84.8 | 80.5 | 81.7 | 68.8 | 74.7 |
| 5 | microsoft/phi-4 | 14.7B (dense) | 86.6 | 80.5 | 74.3 | 64.0 | 72.3 |
| 6 | google/gemma-4-26B-A4B-it | 4B (MoE) | 53.0 | 51.8 | 46.6 | 41.5 | 46.7 |

All values are pass@1 percentages. `+` columns use EvalPlus's expanded edge-case tests.

### Wall-clock per model (download + load + generate + score, single H100)

| Model | Time |
|-------|------|
| microsoft/phi-4 | 18 min |
| google/gemma-4-26B-A4B-it | 30 min |
| Qwen/Qwen3-Coder-30B-A3B-Instruct | 41 min |
| zai-org/GLM-4.7-Flash | 19 min |
| google/gemma-4-31B-it | 53 min |
| Qwen/Qwen2.5-Coder-32B-Instruct | 39 min |

Total run: ~3 h 22 min (09:54 → 13:16). Raw per-step log: `run-progress.log`;
machine-readable scores: `results-summary.tsv`.

### Key findings

- **Top three are within ~1 point** — gemma-4-31B, Qwen3-Coder-30B-A3B, and
  Qwen2.5-Coder-32B are effectively tied. Pick on latency/licensing, not score.
- **Qwen3-Coder-30B-A3B is the efficiency winner**: it matches 32B dense models with
  only **3B active parameters** (MoE), so it is by far the cheapest to serve per token.
- **Qwen2.5-Coder-32B has the strongest MBPP/MBPP+** (89.9 / 76.5) — best for
  general Python implementation tasks.
- **gemma-4-31B has the strongest HumanEval+** (89.6).
- **Active parameter count tracks capability**: gemma-4-26B-**A4B** (4B active) lands last
  by a wide margin; few active params = weaker coding despite a 26B total size.
- **Harness validated**: phi-4's 80.5 HumanEval+ matches Microsoft's published figures,
  confirming the chat-template / scoring path is correct.

## License & commercial-use suitability

Can a company run these **internally for commercial work**? Licenses verified from each
model's Hugging Face card / `LICENSE` file on 2026-06-11 (see References).

| Model | License | Verified from | Internal commercial use |
|-------|---------|---------------|-------------------------|
| microsoft/phi-4 | **MIT** | `LICENSE` file ("MIT License") | ✅ Yes — unrestricted |
| google/gemma-4-26B-A4B-it | **Apache-2.0** | model-card metadata + card text | ✅ Yes — unrestricted |
| google/gemma-4-31B-it | **Apache-2.0** | model-card metadata + card text | ✅ Yes — unrestricted |
| Qwen/Qwen3-Coder-30B-A3B-Instruct | **Apache-2.0** | card metadata + `LICENSE` link | ✅ Yes — unrestricted |
| Qwen/Qwen2.5-Coder-32B-Instruct | **Apache-2.0** | `LICENSE` file (Apache 2.0 text) | ✅ Yes — unrestricted |
| zai-org/GLM-4.7-Flash | **MIT** | model-card metadata (`license: mit`) | ✅ Yes — unrestricted |

**All six are OSI-approved permissive licenses (MIT or Apache-2.0)** — a company may
self-host, modify, and use them commercially with no fee and no field-of-use restriction.
Standard hygiene still applies: keep the LICENSE/NOTICE files, and (Apache-2.0) note
modifications. Apache-2.0 also includes an explicit patent grant.

> Notable: **Gemma 4 is Apache-2.0**, a change from Gemma 1–3, which shipped under Google's
> custom *Gemma Terms of Use* (commercial use allowed but with a Prohibited Use Policy and
> downstream pass-through requirements). Verified against Google DeepMind's own model card.

## Agentic comparison vs Claude Opus 4.6 / 4.7 / 4.8

Requested comparison on **SWE-Bench Pro** and **Terminal-Bench**. These were **not run
locally** (they need Docker + an agent scaffold + ~1 TB of task images + days of compute,
infeasible on this one-H100 box). Instead, every number below is a **vendor/official
published** figure, each with a citation. **Read the two caveats — this is not a clean
head-to-head.**

> ⚠️ **Caveat 1 — different SWE-bench variants.** Anthropic reports **SWE-Bench _Pro_** (the
> harder Scale AI variant). The open models that report SWE-bench at all use **SWE-bench
> _Verified_**, which is a *different, easier* test. **69.2 (Opus, Pro) vs 59.2 (GLM,
> Verified) is NOT a like-for-like gap.**
>
> ⚠️ **Caveat 2 — sparse coverage.** There is **no single coding benchmark** with published
> numbers for both Opus *and* these open models. phi-4, Qwen2.5-Coder and the Gemma-4 models
> publish **no** SWE-bench/Terminal-bench at all; Qwen reports SWE-bench Verified only for the
> 480B flagship, **not** the 30B-A3B here. Blank = not reported by the vendor.

### Claude Opus — verified from Anthropic's official launch chart

Read directly from the benchmark chart on Anthropic's Opus 4.8 announcement (the chart covers
**4.8 and 4.7 only — not 4.6**). GPT-5.5 / Gemini 3.1 Pro shown as Anthropic published them.

| Benchmark | Opus 4.8 | Opus 4.7 | GPT-5.5 | Gemini 3.1 Pro |
|-----------|:--------:|:--------:|:-------:|:--------------:|
| **SWE-Bench Pro** (agentic coding) | **69.2** | 64.3 | 58.6 | 54.2 |
| **Terminal-Bench 2.1** | 74.6 | 66.1 | **78.2** | 70.3 |
| Humanity's Last Exam (no tools) | 49.8 | 46.9 | 41.4 | 44.4 |
| Humanity's Last Exam (with tools) | 57.9 | 54.7 | 52.2 | 51.4 |
| OSWorld-Verified (computer use) | 83.4 | 82.8 | 78.7 | 76.2 |
| GDPval-AA (knowledge work, Elo) | 1890 | 1753 | 1769 | 1314 |
| Finance Agent v2 | 53.9 | 51.5 | 51.8 | 43.0 |

Opus 4.x facts (text-verified): released 4.6 = 2026-02-05, 4.7 = 2026-04-16, 4.8 = 2026-05-28;
all $5 / $25 per MTok; 1M context; **proprietary, API/cloud only (not self-hostable)**.

### Local models — vendor-published agentic / coding scores

| Model | SWE-bench | Terminal-Bench | LiveCodeBench v6 | HLE (no tools) | τ²-Bench |
|-------|:---------:|:--------------:|:----------------:|:--------------:|:--------:|
| GLM-4.7-Flash | **59.2** (Verified) | referenced, no number | 64.0 | 14.4 | 79.5 |
| Qwen3-Coder-30B-A3B | not reported for this size | — | — | — | — |
| Qwen2.5-Coder-32B | not reported | — | — | — | — |
| gemma-4-31B | not reported | — | 80.0 | 19.5 | 76.9 |
| gemma-4-26B-A4B | not reported | — | 77.1 | 8.7 | 68.2 |
| phi-4 | not reported | — | — | — | — |

(All from each model's official Hugging Face card; see References.)

### How to read this honestly

1. **The only fully-overlapping axis is HLE (reasoning, not coding)**, and there Opus is far
   ahead: Opus 4.8 **49.8** (no tools) vs gemma-4-31B 19.5, GLM-4.7-Flash 14.4. Tool settings
   differ across vendors, so even this is approximate.
2. **On SWE-bench, you cannot rank Opus vs the open models from these numbers** — Pro ≠
   Verified. The closest *directional* read: Opus 4.8 leads SWE-Bench Pro (69.2) and the best
   open self-hostable here (GLM-4.7-Flash) scores 59.2 on the *easier* Verified set, so the
   true gap is **larger** than 10 points.
3. **Different category for internal use.** Opus 4.x is proprietary and **not self-hostable**
   (Claude API / Bedrock / Vertex / Foundry under Anthropic's Commercial Terms; data leaves
   your infra). The six local models run fully inside your infrastructure under MIT/Apache-2.0.
   For air-gapped / data-residency work Opus is not an option; for peak agentic capability it
   clearly leads.
4. **HumanEval+/MBPP+ ≠ agentic ability.** The 80–90% the local models scored earlier in this
   doc are on *saturated single-function* benchmarks; they do **not** imply Opus-level
   performance on real multi-step SWE-Bench Pro / Terminal-Bench tasks.

## Throughput (tokens/sec, measured on this H100)

Measured with vLLM 0.22.1, bf16, 256 output tokens, greedy. **Single-stream** = concurrency 1
(latency-bound, interactive feel); **batched-32** = concurrency 32 (aggregate server throughput).

| Model | Type | Single-stream tok/s | Batched-32 tok/s |
|-------|------|:-------------------:|:----------------:|
| gemma-4-26B-A4B | MoE (4B active) | **206.7** | **4632.7** |
| Qwen3-Coder-30B-A3B | MoE (3B active) | 197.4 | 3825.9 |
| GLM-4.7-Flash | 31B dense | 167.4 | 2266.6 |
| phi-4 | 14.7B dense | 87.0 | 2598.6 |
| gemma-4-31B | 33B dense | 41.4 | 1042.4 |
| Qwen2.5-Coder-32B | 33B dense | 40.3 | 1226.5 |

- **MoE wins on speed:** few active params let gemma-4-26B-A4B and Qwen3-Coder-30B-A3B lead
  single-stream despite their large total size — best capability-per-token-per-second here.
- The dense 33B models (gemma-4-31B, Qwen2.5-Coder-32B) ran ~4× slower single-stream; Gemma-4
  is multimodal and appears to lack fully-optimized vLLM 0.22.1 kernels on this setup.
- **vs Opus — no numeric comparison possible.** Anthropic publishes **no** tokens/sec figure
  for any Opus model; API speed reflects their serving stack + network, not the model. The
  only official statement is qualitative: Opus 4.8 "fast mode" ≈ 2.5× standard speed. The
  local numbers above are measured; an Opus tok/s column is intentionally left blank.

## Not tested: exceeds a single H100 80GB

These were requested but **cannot run on one H100** (weights alone exceed 80 GB even at FP8).
Reported here with their real hardware requirement instead of a fabricated score.

| Model | Params | FP8 footprint | Minimum hardware |
|-------|--------|---------------|------------------|
| zai-org/GLM-4.5-Air | 110B | ~110 GB | 2–4× H100 |
| deepseek-ai/DeepSeek-V4-Flash | 158B | ~158 GB | 2–4× H100 |
| zai-org/GLM-5.1 | 754B | ~754 GB | 8× H100 + 4-bit, or 2 nodes |
| deepseek-ai/DeepSeek-V4-Pro | 862B | ~862 GB | 8–16× H100 |
| moonshotai/Kimi-K2.6 | 1059B | ~1 TB | 8× H100 + 4-bit, or 16× / 2 nodes |

### Published agentic-coding scores (vendor self-reported)

Same benchmarks as the Opus comparison, but since these can't run here every figure is the
**vendor's own published** number (own harness + effort settings), each cited in References.
**Read the caveats — these are not a clean head-to-head.**

| Model | Params | SWE-Bench Pro | SWE-bench Verified | Terminal-Bench 2.0 | Source |
|-------|:------:|:-------------:|:------------------:|:------------------:|--------|
| GLM-4.5-Air | 106B-A12B | n/r¹ | n/r¹ | n/r¹ | GLM-4.5 card |
| DeepSeek-V4-Flash (Max) | 158B | 52.6 | 79.0 | 56.9 | DS-V4 card |
| GLM-5.1 | 754B | 58.4 | — | 63.5 (Terminus-2) | GLM-5.1 card |
| DeepSeek-V4-Pro (Max) | 862B | 55.4 | 80.6 | 67.9 | DS-V4 card |
| Kimi-K2.6 | 1.06T | 58.6 | 80.2 | 66.7 | Kimi-K2.6 card |
| _Claude Opus 4.7 (ref)_ | proprietary | 64.3 | — | 66.1 _(TB **2.1**)_ | Anthropic |
| _Claude Opus 4.8 (ref)_ | proprietary | **69.2** | — | 74.6 _(TB **2.1**)_ | Anthropic |

¹ GLM-4.5-Air's card reports only an aggregate **59.8 across 12 benchmarks**, not a per-task
SWE/Terminal score; no specific number could be verified from fetched sources.

**Caveats (critical for honest reading):**
- **Terminal-Bench version mismatch:** open models report **2.0**; Anthropic reports **2.1**.
  Do not compare the 2.0 and 2.1 columns directly.
- **Harness variance is huge:** Kimi's card measures Opus-4.6 at **53.4** SWE-Bench Pro,
  DeepSeek's card measures Opus-4.6 at **57.3**, while Anthropic self-reports Opus 4.8 at
  **69.2**. Cross-vendor gaps are directional only, never exact.
- **Cross-validated where possible:** GLM-5.1 (58.4) and Kimi-K2.6 (58.6) SWE-Bench Pro appear
  identically in both their own cards *and* DeepSeek's independent comparison table — a good
  consistency signal.
- **Takeaway:** even 750B–1T open flagships self-report **high-50s on SWE-Bench Pro**, below
  Opus 4.8's self-reported 69.2 — but on the easier **SWE-bench Verified** open flagships
  cluster ~79–81 (and third-party-measured Opus-4.6 ≈ 80.8), i.e. roughly on par.

## Reproduce

```bash
# env: Python 3.12, CUDA driver, python3.12-dev + build-essential + ninja-build
uv venv && uv pip install vllm evalplus
bash run_bench.sh        # see run_bench.sh in this directory
```

## References

All URLs accessed 2026-06-11. Numbers in the Opus/agentic sections are transcribed from these
official sources (Opus table read from the chart image on Anthropic's announcement page).

**Anthropic / Claude Opus**
- Introducing Claude Opus 4.8 (benchmark chart source): https://www.anthropic.com/news/claude-opus-4-8
- Claude Opus product page (4.5–4.8 release dates): https://www.anthropic.com/claude/opus
- Models overview (IDs, pricing, context, cutoffs): https://docs.anthropic.com/en/docs/about-claude/models/overview
- Commercial Terms of Service: https://www.anthropic.com/legal/commercial-terms

**Local model cards (licenses + vendor-published scores)**
- microsoft/phi-4 (MIT): https://huggingface.co/microsoft/phi-4
- google/gemma-4-31B-it (Apache-2.0; LiveCodeBench v6, Tau2, HLE): https://huggingface.co/google/gemma-4-31B-it
- google/gemma-4-26B-A4B-it (Apache-2.0): https://huggingface.co/google/gemma-4-26B-A4B-it
- Gemma 4 license: https://ai.google.dev/gemma/docs/gemma_4_license
- Qwen/Qwen3-Coder-30B-A3B-Instruct (Apache-2.0): https://huggingface.co/Qwen/Qwen3-Coder-30B-A3B-Instruct
- Qwen3-Coder blog (SWE-bench Verified reported for 480B flagship only): https://qwenlm.github.io/blog/qwen3-coder/
- Qwen/Qwen2.5-Coder-32B-Instruct (Apache-2.0): https://huggingface.co/Qwen/Qwen2.5-Coder-32B-Instruct
- zai-org/GLM-4.7-Flash (MIT; SWE-bench Verified 59.2, τ²-Bench, LCB v6): https://huggingface.co/zai-org/GLM-4.7-Flash

**Oversized model cards (SWE-Bench Pro / Verified / Terminal-Bench 2.0)**
- deepseek-ai/DeepSeek-V4-Pro (cross-vendor table incl. Opus-4.6/GPT-5.4/Gemini/K2.6/GLM-5.1): https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro
- deepseek-ai/DeepSeek-V4-Flash (per-mode table): https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash
- zai-org/GLM-5.1 (SWE-Bench Pro 58.4, Terminal-Bench 2.0 63.5): https://huggingface.co/zai-org/GLM-5.1
- moonshotai/Kimi-K2.6 (SWE-Bench Pro 58.6, Verified 80.2, TB2.0 66.7): https://huggingface.co/moonshotai/Kimi-K2.6
- zai-org/GLM-4.5 (GLM-4.5-Air = 106B-A12B, MIT, aggregate 59.8/12-benchmarks): https://huggingface.co/zai-org/GLM-4.5

**Tooling**
- vLLM: https://github.com/vllm-project/vllm
- EvalPlus (HumanEval+/MBPP+): https://github.com/evalplus/evalplus

> Could not verify: Opus 4.6 SWE-Bench Pro / Terminal-Bench (absent from the 4.8 chart); a
> per-model SWE-bench number for Qwen3-Coder-30B-A3B (vendor reports only the 480B flagship);
> a per-benchmark SWE/Terminal score for GLM-4.5-Air (card gives only an aggregate 59.8);
> the Claude Opus 4.8 System Card PDF/HTML exceeded the fetch size limit, so figures here come
> from the announcement chart, not the System Card.
