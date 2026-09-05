"""Materialize a SWE-bench instance into a working checkout the agent can edit.

Clones the repo (cached under a base dir), checks out base_commit into a per-run
worktree, and returns the workdir. Uses `git worktree` so one clone serves many runs.
"""
from __future__ import annotations

import os
import subprocess

CLONES = os.environ.get("ABLATION_CLONES", "/tmp/opencode/swe-clones")
RUNS = os.environ.get("ABLATION_RUNS", "/tmp/opencode/swe-runs")


def _git(args, cwd):
    return subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True)


def ensure_clone(repo: str) -> str:
    """repo like 'astropy/astropy' -> local bare-ish clone path (cached)."""
    os.makedirs(CLONES, exist_ok=True)
    path = os.path.join(CLONES, repo.replace("/", "__"))
    if not os.path.exists(path):
        subprocess.run(
            ["git", "clone", "--filter=blob:none", "--no-checkout",
             f"https://github.com/{repo}", path],
            capture_output=True, text=True, timeout=600)
    return path


def materialize(repo: str, base_commit: str, run_id: str) -> str:
    """Create a fresh worktree at base_commit for this run; return its path."""
    clone = ensure_clone(repo)
    os.makedirs(RUNS, exist_ok=True)
    wt = os.path.join(RUNS, run_id)
    if os.path.exists(wt):
        _git(["worktree", "remove", "--force", wt], clone)
    # fetch the commit if the filter left it absent
    if _git(["cat-file", "-e", base_commit], clone).returncode != 0:
        _git(["fetch", "origin", base_commit], clone)
    r = _git(["worktree", "add", "--detach", wt, base_commit], clone)
    if r.returncode != 0:
        raise RuntimeError(f"worktree add failed: {r.stderr[:200]}")
    return wt


def apply_patch(workdir: str, patch: str) -> tuple[bool, str]:
    chk = subprocess.run(["git", "apply", "--check", "-"], cwd=workdir,
                         input=patch, capture_output=True, text=True)
    if chk.returncode != 0:
        return False, (chk.stderr or chk.stdout)[:200]
    ap = subprocess.run(["git", "apply", "-"], cwd=workdir, input=patch,
                        capture_output=True, text=True)
    return (ap.returncode == 0, (ap.stderr or ap.stdout)[:200])


def cleanup(workdir: str, repo: str) -> None:
    clone = os.path.join(CLONES, repo.replace("/", "__"))
    if os.path.isdir(clone):
        _git(["worktree", "remove", "--force", workdir], clone)
