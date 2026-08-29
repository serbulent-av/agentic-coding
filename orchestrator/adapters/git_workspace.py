"""Git worktree adapter. One worktree + branch per task (AO's workspace isolation).

Uses only the git CLI (no Python deps). Defensive: never force-deletes a dirty
worktree unless ``force=True``.
"""

from __future__ import annotations

import os
import subprocess
from typing import Optional, Tuple


class GitWorkspace:
    def __init__(self, repo: str, work_root: Optional[str] = None):
        self.repo = os.path.abspath(repo)
        # worktrees live under <repo>/.orchestrator/worktrees by default
        self.work_root = work_root or os.path.join(self.repo, ".orchestrator", "worktrees")
        os.makedirs(self.work_root, exist_ok=True)

    def _git(self, *args: str, cwd: Optional[str] = None) -> Tuple[bool, str]:
        proc = subprocess.run(
            ["git", *args], cwd=cwd or self.repo, capture_output=True, text=True
        )
        out = (proc.stdout + proc.stderr).strip()
        return proc.returncode == 0, out

    def create(self, task_id: str, base_ref: str = "HEAD") -> Tuple[str, str]:
        branch = f"orc/{task_id}"
        path = os.path.join(self.work_root, task_id)
        ok, out = self._git("worktree", "add", "-b", branch, path, base_ref)
        if not ok:
            raise RuntimeError(f"git worktree add failed: {out}")
        return path, branch

    def apply_patch(self, worktree: str, patch: str) -> Tuple[bool, str]:
        # check first; then apply
        chk = subprocess.run(["git", "apply", "--check", "-"], cwd=worktree,
                             input=patch, capture_output=True, text=True)
        if chk.returncode != 0:
            return False, (chk.stderr or chk.stdout).strip()
        ap = subprocess.run(["git", "apply", "-"], cwd=worktree,
                            input=patch, capture_output=True, text=True)
        if ap.returncode != 0:
            return False, (ap.stderr or ap.stdout).strip()
        return True, "applied"

    def diff(self, worktree: str) -> str:
        ok, out = self._git("diff", "HEAD", cwd=worktree)
        return out if ok else ""

    def run_tests(self, worktree: str) -> Tuple[bool, str]:
        """Default test gate: run the repo's unittest suite if one exists.

        This is intentionally conservative; real projects can inject a custom
        gate. Returns (passed, output).
        """
        if os.path.isdir(os.path.join(worktree, "tests")):
            proc = subprocess.run(
                ["python", "-m", "unittest", "discover", "-s", "tests", "-q"],
                cwd=worktree, capture_output=True, text=True, timeout=900,
            )
            return proc.returncode == 0, (proc.stdout + proc.stderr)
        # no tests dir => nothing to regress; treat as pass with a note
        return True, "no tests/ directory; gate vacuously green"

    def remove(self, task_id: str, force: bool = False) -> None:
        path = os.path.join(self.work_root, task_id)
        args = ["worktree", "remove"]
        if force:
            args.append("--force")
        args.append(path)
        self._git(*args)
        self._git("branch", "-D", f"orc/{task_id}")

    def cleanup(self, task_id: str, force: bool = False) -> None:
        self.remove(task_id, force=force)
