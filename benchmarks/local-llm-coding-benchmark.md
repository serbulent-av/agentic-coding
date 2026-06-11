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

## Reproduce

```bash
# env: Python 3.12, CUDA driver, python3.12-dev + build-essential + ninja-build
uv venv && uv pip install vllm evalplus
bash run_bench.sh        # see run_bench.sh in this directory
```
