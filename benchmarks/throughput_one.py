import time, sys, os, json
from vllm import LLM, SamplingParams

hid, short = sys.argv[1], sys.argv[2]
OUT = "results/throughput.tsv"
PROMPT = "Write a Python function that computes the nth Fibonacci number iteratively, then briefly explain how it works and its time complexity."

def measure(llm, n, max_tokens):
    sp = SamplingParams(temperature=0, max_tokens=max_tokens, ignore_eos=True)
    outs = llm.generate([PROMPT]*n, sp)
    return outs

try:
    llm = LLM(model=hid, max_model_len=2048, trust_remote_code=True,
              gpu_memory_utilization=0.90, enforce_eager=False)
    # warmup (also triggers CUDA graph capture so timing is steady-state)
    measure(llm, 1, 32)

    # single-stream decode throughput
    t = time.perf_counter()
    outs = measure(llm, 1, 256)
    dt1 = time.perf_counter() - t
    tok1 = sum(len(o.outputs[0].token_ids) for o in outs)
    s1 = tok1 / dt1

    # batched aggregate throughput (concurrency 32)
    t = time.perf_counter()
    outs = measure(llm, 32, 256)
    dt32 = time.perf_counter() - t
    tok32 = sum(len(o.outputs[0].token_ids) for o in outs)
    s32 = tok32 / dt32

    line = f"{short}\t{s1:.1f}\t{s32:.1f}"
    with open(OUT, "a") as f:
        f.write(line + "\n")
    print("RESULT\t" + line, flush=True)
except Exception as e:
    with open(OUT, "a") as f:
        f.write(f"{short}\tERROR\tERROR\n")
    print(f"ERROR\t{short}\t{type(e).__name__}: {e}", flush=True)
    sys.exit(1)
