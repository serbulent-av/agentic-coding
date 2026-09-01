"""Ablation runner: 6 arms x N instances x pass@K on SWE-bench Verified, Kimi-K3.

Budget-guarded: estimates cumulative USD from token usage and stops before
exceeding the cap. Writes per-run results to results.jsonl (resumable).

Usage:
  python run_ablation.py --n 25 --k 3 --budget 100 \
      --instances ../agentic-runs/swe-verified/subset_50_instance_ids.txt

Notes
- Evaluation (official SWE-bench Docker harness) is intentionally separate: this
  runner produces candidate patches + writes them to preds-<arm>.json. Score with
  `swebench.harness.run_evaluation` where Docker images are available.
- Repo checkout: needs a real SWE-bench task checkout per instance to be a true
  run. Use --workdir-template to point at prepared checkouts, or --mock to
  smoke-test the pipeline without the dataset (synthetic problem text, no real fix).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import asdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from agent import Arm, run_instance  # noqa: E402
from kimi_client import Usage  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
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

MOCK_PROBLEM = (
    "The function `parse_config` in src/config.py crashes with a KeyError when the "
    "optional 'timeout' key is missing. Make it default to 30 without breaking "
    "existing behaviour."
)


def load_instances(path: str, n: int):
    ids = [l.strip() for l in open(path) if l.strip()][:n]
    return ids


def already_done(results_path: str):
    done = set()
    if os.path.exists(results_path):
        for line in open(results_path):
            try:
                r = json.loads(line)
                done.add((r["instance_id"], r["arm"], r["sample"]))
            except Exception:
                continue
    return done


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=25)
    ap.add_argument("--k", type=int, default=3, help="pass@K samples")
    ap.add_argument("--budget", type=float, default=100.0, help="USD cap")
    ap.add_argument("--instances", default=os.path.join(
        HERE, "..", "agentic-runs", "swe-verified", "subset_50_instance_ids.txt"))
    ap.add_argument("--max-steps", type=int, default=25)
    ap.add_argument("--arms", default=",".join(a.name for a in ARMS))
    ap.add_argument("--mock", action="store_true",
                    help="smoke-test pipeline without the SWE dataset")
    ap.add_argument("--workdir-template", default="",
                    help="e.g. /path/to/checkouts/{instance_id}; empty => mock dir")
    args = ap.parse_args()

    usage = Usage()
    results_path = os.path.join(OUT, "results.jsonl")
    done = already_done(results_path)
    arms = {a.name: a for a in ARMS}
    chosen = [arms[n] for n in args.arms.split(",") if n in arms]

    ids = [f"mock-{i}" for i in range(args.n)] if args.mock else load_instances(args.instances, args.n)

    print(f"[ablation] arms={[a.name for a in chosen]} n={len(ids)} k={args.k} "
          f"budget=${args.budget} mock={args.mock}", flush=True)

    rf = open(results_path, "a")
    for arm in chosen:
        for iid in ids:
            for sample in range(args.k):
                if (iid, arm.name, sample) in done:
                    continue
                if usage.cost_usd >= args.budget:
                    print(f"[ablation] BUDGET CAP reached at {usage}; stopping.", flush=True)
                    rf.close(); _summary(results_path); return
                workdir = (args.workdir_template.format(instance_id=iid)
                           if args.workdir_template else
                           os.path.join(OUT, "_mock_repo"))
                if args.mock or not args.workdir_template:
                    os.makedirs(workdir, exist_ok=True)
                problem = MOCK_PROBLEM if args.mock else f"(problem_statement for {iid})"
                if args.mock:
                    # materialize a trivially-fixable mock repo so the loop has something to edit
                    os.makedirs(os.path.join(workdir, "src"), exist_ok=True)
                    with open(os.path.join(workdir, "src", "config.py"), "w") as fh:
                        fh.write('def parse_config(c):\n    return c["timeout"]\n')
                t0 = time.time()
                res = run_instance(iid, problem, workdir, arm, max_steps=args.max_steps)
                dt = time.time() - t0
                # aggregate per-run usage into the budget counter
                usage.add({"prompt_tokens": res.usage.prompt,
                           "completion_tokens": res.usage.completion,
                           "total_tokens": res.usage.total})
                rec = {
                    "instance_id": iid, "arm": arm.name, "sample": sample,
                    "empty_patch": res.empty_patch, "error": res.error,
                    "steps": res.steps, "wall_s": round(dt, 1),
                    "cum_tokens": usage.total, "cum_cost_usd": round(usage.cost_usd, 3),
                }
                rf.write(json.dumps(rec) + "\n"); rf.flush()
                # persist candidate patch for later official scoring
                if res.patch:
                    pd = os.path.join(OUT, f"preds-{arm.name}")
                    os.makedirs(pd, exist_ok=True)
                    with open(os.path.join(pd, f"{iid}__{sample}.diff"), "w") as pf:
                        pf.write(res.patch)
                print(f"[{arm.name}] {iid} s{sample} empty={res.empty_patch} "
                      f"{dt:.0f}s cum={usage}", flush=True)
    rf.close()
    _summary(results_path)


def _summary(results_path: str):
    from collections import defaultdict
    empty = defaultdict(int); tot = defaultdict(int); err = defaultdict(int)
    for line in open(results_path):
        r = json.loads(line)
        tot[r["arm"]] += 1
        empty[r["arm"]] += 1 if r["empty_patch"] else 0
        err[r["arm"]] += 1 if r["error"] else 0
    print("\n[ablation] per-arm (runs, empty-patch, errors):")
    for arm in sorted(tot):
        print(f"  {arm}: runs={tot[arm]} empty={empty[arm]} err={err[arm]}")


if __name__ == "__main__":
    main()
