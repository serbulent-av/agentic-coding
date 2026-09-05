"""Score ablation predictions with the official SWE-bench Docker harness (4.1.0).

Uses the swebench 4.1.0 interface, which builds the per-instance Docker env from the
dataset (no pre-built image field required). Predictions are read from
out/preds-<arm>.jsonl (model_patch format). Requires Docker + disk for images.

Run with the ablation venv (has swebench==4.1.0):
  /tmp/opencode/ablation-venv/bin/python eval_swebench.py --arms A0-baseline --run-id resolve
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
VENV_PY = os.environ.get("ABLATION_VENV_PY", "/tmp/opencode/ablation-venv/bin/python")
REPORT = os.path.join(OUT, "reports")
os.makedirs(REPORT, exist_ok=True)


def eval_arm(arm: str, run_id: str, max_workers: int) -> dict:
    preds = os.path.join(OUT, f"preds-{arm}.jsonl")
    if not os.path.exists(preds):
        return {"arm": arm, "error": "no preds"}
    rows = [json.loads(l) for l in open(preds)]
    if not rows:
        return {"arm": arm, "error": "empty preds"}
    ids = [r["instance_id"] for r in rows]
    cmd = [
        VENV_PY, "-m", "swebench.harness.run_evaluation",
        "--dataset_name", "princeton-nlp/SWE-bench_Verified", "--split", "test",
        "--predictions_path", preds, "--instance_ids", *ids,
        "--run_id", f"{run_id}-{arm}", "--max_workers", str(max_workers),
        "--cache_level", "env", "--clean", "false",
    ]
    p = subprocess.run(cmd, capture_output=True, text=True)
    out = p.stdout + p.stderr
    resolved = None
    rj = os.path.join(REPORT, f"{run_id}-{arm}.json")
    # 4.1.0 writes a report; look for resolved counts in stdout or report dir
    for line in out.splitlines():
        if "resolved" in line.lower() and any(c.isdigit() for c in line):
            pass  # captured below from report json if present
    # try to find the report
    import glob
    for f in glob.glob(os.path.join(REPORT, "**", "*.json"), recursive=True) + \
              glob.glob(os.path.join("logs", "run_evaluation", "**", "*.json"), recursive=True):
        try:
            d = json.load(open(f))
            if isinstance(d, dict) and "resolved" in d:
                resolved = len(d["resolved"]) if isinstance(d["resolved"], list) else d["resolved"]
        except Exception:
            continue
    return {"arm": arm, "n": len(ids), "resolved": resolved,
            "rc": p.returncode, "log_tail": out[-400:]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default="A0-baseline,A1-graphify,A2-memory,A3-team,A4-review,A5-all")
    ap.add_argument("--max-workers", type=int, default=4)
    ap.add_argument("--run-id", default="resolve")
    args = ap.parse_args()
    for arm in args.arms.split(","):
        r = eval_arm(arm, args.run_id, args.max_workers)
        print(json.dumps(r), flush=True)


if __name__ == "__main__":
    main()
