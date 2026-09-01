"""Ablation runner: 6 arms x N instances x pass@K on SWE-bench Verified, Kimi-K3.

Run with the ablation venv python (has datasets+requests):
  /tmp/opencode/ablation-venv/bin/python run_ablation.py --n 25 --k 3 --budget 100
  .../python run_ablation.py --mock --n 2 --k 1 --arms A0-baseline   # smoke
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from agent import Arm, RunOutcome, run_instance  # noqa: E402
from kimi_client import Usage  # noqa: E402
import dataset as dsmod  # noqa: E402
import materialize as mz  # noqa: E402

OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

ARMS = [
    Arm(name="A0-baseline"),
    Arm(name="A1-graphify", graphify=True),
    Arm(name="A2-memory", memory=True),
    Arm(name="A3-team", team=True),
    Arm(name="A4-review", review=True),
    Arm(name="A5-all", graphify=True, memory=True, team=True, review=True),
]

MOCK_PROBLEM = ("The function `parse_config` in src/config.py crashes with a "
                "KeyError when the optional 'timeout' key is missing. Default it "
                "to 30 without breaking existing behaviour.")


def load_id_list(path, n):
    return [l.strip() for l in open(path) if l.strip()][:n]


def already_done(path):
    done = set()
    if os.path.exists(path):
        for line in open(path):
            try:
                r = json.loads(line)
                done.add((r["instance_id"], r["arm"], r["sample"]))
            except Exception:
                continue
    return done


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=25)
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--budget", type=float, default=100.0)
    ap.add_argument("--instances", default=os.path.join(
        HERE, "..", "agentic-runs", "swe-verified", "subset_50_instance_ids.txt"))
    ap.add_argument("--max-steps", type=int, default=25)
    ap.add_argument("--arms", default=",".join(a.name for a in ARMS))
    ap.add_argument("--mock", action="store_true")
    args = ap.parse_args()

    usage = Usage()
    results_path = os.path.join(OUT, "results.jsonl")
    done = already_done(results_path)
    arms = {a.name: a for a in ARMS}
    chosen = [arms[x] for x in args.arms.split(",") if x in arms]

    if args.mock:
        ids = [f"mock-{i}" for i in range(args.n)]
        records = {}
    else:
        ids = load_id_list(args.instances, args.n)
        records = dsmod.load_instances(ids)
        ids = [i for i in ids if i in records]

    print(f"[ablation] arms={[a.name for a in chosen]} n={len(ids)} k={args.k} "
          f"budget=${args.budget} mock={args.mock}", flush=True)

    with open(results_path, "a") as rf:
        for arm in chosen:
            preds = []
            for iid in ids:
                for sample in range(args.k):
                    if (iid, arm.name, sample) in done:
                        continue
                    if usage.cost_usd >= args.budget:
                        print(f"[ablation] BUDGET CAP at {usage}; stop.", flush=True)
                        _summary(results_path); return
                    if args.mock:
                        workdir = os.path.join(OUT, "_mock_repo")
                        os.makedirs(os.path.join(workdir, "src"), exist_ok=True)
                        with open(os.path.join(workdir, "src", "config.py"), "w") as fh:
                            fh.write('def parse_config(c):\n    return c["timeout"]\n')
                        problem = MOCK_PROBLEM
                    else:
                        rec = records[iid]
                        workdir = mz.materialize(rec["repo"], rec["base_commit"],
                                                 run_id=f"{arm.name}__{iid}__{sample}")
                        problem = rec["problem_statement"]
                    t0 = time.time()
                    try:
                        res = run_instance(iid, problem, workdir, arm, max_steps=args.max_steps)
                    except Exception as e:
                        res = RunOutcome(instance_id=iid, arm=arm.name, error=repr(e)[:200])
                    dt = time.time() - t0
                    usage.add({"prompt_tokens": res.usage.prompt,
                               "completion_tokens": res.usage.completion,
                               "total_tokens": res.usage.total})
                    rf.write(json.dumps({
                        "instance_id": iid, "arm": arm.name, "sample": sample,
                        "empty_patch": res.empty_patch, "error": res.error,
                        "wall_s": round(dt, 1), "run_tokens": res.usage.total,
                        "cum_tokens": usage.total,
                        "cum_cost_usd": round(usage.cost_usd, 3)}) + "\n")
                    rf.flush()
                    if res.patch and not args.mock:
                        preds.append({"instance_id": iid,
                                      "model_name_or_path": f"ablation-{arm.name}",
                                      "model_patch": res.patch})
                    print(f"[{arm.name}] {iid} s{sample} empty={res.empty_patch} "
                          f"tok={res.usage.total} {dt:.0f}s cum={usage}", flush=True)
            if not args.mock and preds:
                with open(os.path.join(OUT, f"preds-{arm.name}.jsonl"), "w") as pf:
                    for p in preds:
                        pf.write(json.dumps(p) + "\n")
    _summary(results_path)


def _summary(results_path):
    tot = defaultdict(int); empty = defaultdict(int); err = defaultdict(int)
    tok = defaultdict(int)
    if not os.path.exists(results_path):
        return
    for line in open(results_path):
        r = json.loads(line)
        tot[r["arm"]] += 1
        empty[r["arm"]] += 1 if r["empty_patch"] else 0
        err[r["arm"]] += 1 if r["error"] else 0
        tok[r["arm"]] += r.get("run_tokens", 0)
    print("\n[ablation] per-arm (runs, empty-patch, errors, tokens):")
    for arm in sorted(tot):
        print(f"  {arm}: runs={tot[arm]} empty={empty[arm]} err={err[arm]} tok={tok[arm]}")


if __name__ == "__main__":
    main()
