"""Load SWE-bench Verified instance metadata (problem, repo, base_commit,
FAIL_TO_PASS, PASS_TO_PASS) for a fixed list of instance_ids. Uses streaming so we
don't download the whole dataset."""
from __future__ import annotations

import json
import os

# isolated HF cache to avoid clobbering anything and respect disk
os.environ.setdefault("HF_HOME", "/tmp/opencode/hf")


def load_instances(instance_ids, want_full=False):
    """Return {instance_id: record}. Streams the dataset and filters.

    want_full=True keeps environment_setup/commit metadata for Docker grading.
    """
    from datasets import load_dataset
    want = set(instance_ids)
    out = {}
    ds = load_dataset("princeton-nlp/SWE-bench_Verified", split="test", streaming=True)
    for r in ds:
        if r["instance_id"] in want:
            rec = {
                "instance_id": r["instance_id"],
                "repo": r["repo"],
                "base_commit": r["base_commit"],
                "problem_statement": r["problem_statement"],
                "FAIL_TO_PASS": json.loads(r["FAIL_TO_PASS"]) if isinstance(r.get("FAIL_TO_PASS"), str) else r.get("FAIL_TO_PASS", []),
                "PASS_TO_PASS": json.loads(r["PASS_TO_PASS"]) if isinstance(r.get("PASS_TO_PASS"), str) else r.get("PASS_TO_PASS", []),
            }
            # carry any extra fields the harness needs (e.g. image, version, env_setup)
            for extra in ("image", "version", "environment_setup_commit", "created_at"):
                if extra in r:
                    rec[extra] = r[extra]
            out[r["instance_id"]] = rec
            if len(out) == len(want):
                break
    return out


if __name__ == "__main__":
    import sys
    ids = [l.strip() for l in open(sys.argv[1]) if l.strip()][:3]
    got = load_instances(ids)
    for iid, r in got.items():
        print(iid, r["repo"], r["base_commit"][:8], "ftp:", len(r["FAIL_TO_PASS"]))
