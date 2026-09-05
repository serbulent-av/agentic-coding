"""Score ablation predictions with the official SWE-bench Docker harness.

Wraps `swebench.harness.run_evaluation` for each arm's preds-<arm>.jsonl. Pulls/
builds the required instance images (large; ensure disk). Prints resolved counts.

Usage (inside the ablation venv):
  python eval_swebench.py --arms A0-baseline,A5-all --max-workers 4 --run-id pilot
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
VENV_PY = os.environ.get("ABLATION_VENV_PY", "/tmp/opencode/ablation-venv/bin/python")


def eval_arm(arm: str, run_id: str, max_workers: int) -> dict:
    preds = os.path.join(OUT, f"preds-{arm}.jsonl")
    if not os.path.exists(preds):
        return {"arm": arm, "error": "no preds"}
    ids = [json.loads(l)["instance_id"] for l in open(preds)]
    if not ids:
        return {"arm": arm, "error": "empty preds"}
    report_dir = os.path.join(OUT, f"eval-{arm}")
    os.makedirs(report_dir, exist_ok=True)
    cmd = [VENV_PY, "-m", "swebench.harness.run_evaluation",
           "--dataset_name", "princeton-nlp/SWE-bench_Verified", "--split", "test",
           "--predictions_path", preds, "--instance_ids", *ids,
           "--run_id", f"{run_id}-{arm}", "--max_workers", str(max_workers),
           "--report_dir", report_dir]
    p = subprocess.run(cmd, capture_output=True, text=True)
    resolved = 0
    # the harness writes a results json per run; try to read it
    for f in glob.glob(os.path.join(report_dir, "*.json")) + glob.glob(os.path.join(OUT, "**", "*.json"), recursive=True):
        try:
            d = json.load(open(f))
            if isinstance(d, dict) and "resolved" in d:
                resolved = max(resolved, len(d.get("resolved", [])))
        except Exception:
            continue
    return {"arm": arm, "resolved": resolved, "n": len(ids),
            "log_tail": (p.stdout + p.stderr)[-300:]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default="A0-baseline,A5-all")
    ap.add_argument("--max-workers", type=int, default=4)
    ap.add_argument("--run-id", default="pilot")
    args = ap.parse_args()
    for arm in args.arms.split(","):
        print(json.dumps(eval_arm(arm, args.run_id, args.max_workers)), flush=True)


if __name__ == "__main__":
    main()
