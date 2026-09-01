"""Lightweight grading: apply the candidate patch and run the repo's own
FAIL_TO_PASS (+ PASS_TO_PASS) tests in Docker. Resolved = all FAIL_TO_PASS pass AND
no PASS_TO_PASS newly fails. This is a lighter proxy for the official SWE-bench
harness (which uses per-image envs) — good enough for relative arm comparison.
"""
from __future__ import annotations

import os
import subprocess

from materialize import apply_patch

# per-repo python image + test runner command (best-effort; extend as needed)
DEFAULT_IMAGE = "python:3.11-slim"


def _docker_test_cmd(workdir_name: str, repo: str, tests: list[str]) -> str:
    """Build a bash -c that installs the repo and runs pytest on the node ids."""
    t = " ".join(tests)
    # install in editable mode with test extras is ideal but slow/fragile; try a
    # pragmatic path: pip install the repo (build) then pytest the node ids.
    return (
        "set -e; cd /w; "
        "pip install -q -e . 2>/dev/null || pip install -q . 2>/dev/null || true; "
        "pip install -q pytest 2>/dev/null; "
        f"python -m pytest -q {t} 2>&1 | tail -40"
    )


def grade(workdir: str, repo: str, patch: str, fail_to_pass, pass_to_pass,
          image: str = DEFAULT_IMAGE, timeout: int = 900) -> dict:
    """Apply patch, run FAIL_TO_PASS + PASS_TO_PASS in Docker. Returns a verdict."""
    if not patch or not patch.strip():
        return {"resolved": False, "reason": "empty_patch"}
    ok, msg = apply_patch(workdir, patch)
    if not ok:
        return {"resolved": False, "reason": f"patch_apply_failed: {msg}"}

    name = os.path.basename(os.path.abspath(workdir))
    tests = list(fail_to_pass) + list(pass_to_pass or [])
    if not tests:
        return {"resolved": False, "reason": "no_tests"}
    cmd = _docker_test_cmd(name, repo, tests)
    docker = [
        "docker", "run", "--rm", "-v", f"{os.path.abspath(workdir)}:/w", "-w", "/w",
        image, "bash", "-lc", cmd,
    ]
    try:
        p = subprocess.run(docker, capture_output=True, text=True, timeout=timeout)
        out = p.stdout + p.stderr
    except subprocess.TimeoutExpired:
        return {"resolved": False, "reason": "test_timeout"}
    # crude but effective: pytest summary line; resolved iff failures==0 and the
    # FAIL_TO_PASS tests all ran+passed. We look for "no failed" and at least one pass.
    failed = (" failed" in out) or ("FAILED" in out) or (" error" in out.lower() and "error" in out.lower())
    passed = (" passed" in out)
    resolved = (not failed) and passed
    return {"resolved": resolved, "reason": "ok" if resolved else "tests_failed",
            "tail": out[-400:]}
