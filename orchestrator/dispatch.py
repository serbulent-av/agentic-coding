"""Thin, agentic dispatcher.

The orchestrator is the **agent** (see `.opencode/agent/orch.md`), not this file.
This module only *launches* tasks: for each task it spawns an `orch` agent session
(in its own git worktree when the target is a git repo). The heavy reasoning —
planning, delegation to Lange/Philipe/Sohne/Gerald, gating, review, escalation —
lives in the agents and their skills, not in Python.

Design note (vs. the earlier over-built version): no custom state machine, no
reimplemented gates/escalation — those are the agents' job.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import List, Optional

ORCH_PROMPT = (
    "You are starting a dispatched run for this task. Follow your startup "
    "protocol: ensure the repo is Graphify-indexed first, then lead a Patek team "
    "(Lange -> Philipe -> Sohne + Gerald -> gates -> fix) to completion, and "
    "record lessons with the memory skill.\n\nTask:\n{task}"
)


@dataclass
class DispatchResult:
    task: str
    ok: bool
    worktree: str = ""
    output: str = ""
    error: str = ""


def _git(args: List[str], cwd: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)


def _is_git_repo(repo: str) -> bool:
    return _git(["rev-parse", "--is-inside-work-tree"], repo).returncode == 0


def _make_worktree(repo: str, name: str) -> str:
    root = os.path.join(repo, ".orchestrator", "worktrees")
    os.makedirs(root, exist_ok=True)
    path = os.path.join(root, name)
    _git(["worktree", "add", "-b", f"orc/{name}", path, "HEAD"], repo)
    return path


def _run_orch(task: str, workdir: str, model: Optional[str], timeout_s: int) -> DispatchResult:
    if shutil.which("opencode") is None:
        return DispatchResult(task=task, ok=False, worktree=workdir,
                              error="opencode CLI not on PATH")
    cmd = ["opencode", "run", "--agent", "orch", "--dir", workdir, "--format", "json"]
    if model:
        cmd += ["-m", model]
    cmd.append(ORCH_PROMPT.format(task=task))
    try:
        proc = subprocess.run(cmd, cwd=workdir, capture_output=True, text=True,
                              timeout=timeout_s)
    except subprocess.TimeoutExpired:
        return DispatchResult(task=task, ok=False, worktree=workdir,
                              error=f"timeout after {timeout_s}s")
    ok = proc.returncode == 0
    return DispatchResult(task=task, ok=ok, worktree=workdir,
                          output=proc.stdout[-2000:],
                          error="" if ok else (proc.stderr or "")[-400:])


def dispatch(
    repo: str,
    tasks: List[str],
    max_parallel: int = 4,
    model: Optional[str] = None,
    isolate: bool = True,
    timeout_s: int = 3600,
) -> List[DispatchResult]:
    """Spawn one `orch` agent team per task. Orchestrator agent does the rest."""
    repo = os.path.abspath(repo)
    use_worktrees = isolate and _is_git_repo(repo)

    def one(i_task):
        i, task = i_task
        workdir = _make_worktree(repo, f"t{i:03d}") if use_worktrees else repo
        return _run_orch(task, workdir, model, timeout_s)

    with ThreadPoolExecutor(max_workers=max(1, max_parallel)) as ex:
        return list(ex.map(one, enumerate(tasks, start=1)))


def report(results: List[DispatchResult]) -> str:
    lines = [f"dispatched {len(results)} team(s):"]
    for r in results:
        mark = "ok" if r.ok else "FAILED"
        lines.append(f"  [{mark}] {r.task[:60]}" + (f"  ({r.error})" if r.error else ""))
    return "\n".join(lines)
