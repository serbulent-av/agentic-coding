"""Minimal agentic bug-fix loop for the SWE ablation, driven by kimi_client.

Deliberately simple (mirrors the mini-swe-agent backticks scaffold): the model
emits one bash command per turn in a ```bash ... ``` block; we run it in the
repo's Docker container; the loop ends when the model emits a ```diff ... ```
block (its candidate patch) or hits the step limit.

Arm toggles (all default off; baseline A0 = all off):
  G (graphify)  : prepend graph context (graphify query) to the task prompt
  M (memory)    : prepend top-K memory recall for the task keywords
  T (team)      : plan -> implement -> review pipeline (Lange/Philipe) instead of
                  a single agent
  R (reviewers) : a reviewer (Sohne/Gerald) reviews the candidate patch and the
                  implementer revises, up to `review_rounds`
"""
from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass, field
from typing import List, Optional

from kimi_client import Usage, chat

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BASH_RE = re.compile(r"```bash\s*\n(.*?)```", re.DOTALL)
DIFF_RE = re.compile(r"```diff\s*\n(.*?)```", re.DOTALL)

# NOTE: kimi-k3 (via Copilot) returns empty when the system prompt contains
# heavy formatting language like "unified diff". Keep it short + plain; put the
# format rules in the user turn instead.
SYSTEM = (
    "You are an expert software engineer fixing a bug in a repository. The repo is "
    "your current working directory; use relative paths only, never search the wider "
    "filesystem. Work step by step, then produce the fix."
)

FORMAT_RULES = (
    "Rules for each reply: output EXACTLY ONE action. Either one ```bash``` code "
    "block with a single shell command (run in the repo root) to inspect or edit "
    "code, OR one ```diff``` code block with the final patch (git-style, a/ b/ "
    "headers). Do not modify test files. Keep the change minimal."
)

# commands must stay inside the repo worktree
_FORBIDDEN = re.compile(r"(^|[\s|;&])/(home|Users|etc|usr|var|opt|root|tmp|proc|sys|bin|sbin|lib|boot|dev)\b")


def _safe(cmd: str) -> bool:
    """Reject commands that reference absolute system paths outside the worktree."""
    if _FORBIDDEN.search(cmd):
        return False
    return True


@dataclass
class Arm:
    name: str
    graphify: bool = False
    memory: bool = False
    team: bool = False
    review: bool = False
    review_rounds: int = 2


@dataclass
class RunOutcome:
    instance_id: str
    arm: str
    patch: str = ""
    resolved_marker: bool = False   # set by external eval, not here
    steps: int = 0
    empty_patch: bool = True
    error: str = ""
    usage: Usage = field(default_factory=Usage)


def _run_bash(cmd: str, workdir: str, timeout: int = 30) -> str:
    try:
        p = subprocess.run(cmd, shell=True, cwd=workdir, capture_output=True,
                           text=True, timeout=timeout, executable="/bin/bash")
        out = (p.stdout + p.stderr).strip()
        return out[:4000] if out else "(no output)"
    except subprocess.TimeoutExpired:
        return "(command timed out)"


def _graphify_context(instance_text: str, workdir: str) -> str:
    """G: pull a scoped subgraph for the task's key terms (best-effort)."""
    if subprocess.run(["bash", "-c", "command -v graphify"],
                      capture_output=True).returncode != 0:
        return ""
    # naive keyword seed: first capitalized identifier-ish tokens
    terms = re.findall(r"[A-Za-z_][A-Za-z0-9_]{3,}", instance_text)[:4]
    q = " ".join(terms) or "bug"
    try:
        out = subprocess.run(
            ["graphify", "query", q, "--budget", "400",
             "--graph", os.path.join(workdir, "graphify-out", "graph.json")],
            capture_output=True, text=True, timeout=60, cwd=workdir)
        txt = out.stdout.strip()
        return ("Relevant code graph context:\n" + txt) if txt else ""
    except Exception:
        return ""


def _memory_context(instance_text: str, agent: str = "philipe") -> str:
    """M: top-K JIT recall from the team memory graph."""
    cli = os.path.join(REPO_ROOT, "memory", "graph_memory.py")
    if not os.path.exists(cli):
        return ""
    terms = " ".join(re.findall(r"[A-Za-z_][A-Za-z0-9_]{3,}", instance_text)[:3])
    try:
        out = subprocess.run(
            ["python3", cli, "query", terms or "bug", "--agent", agent, "--k", "5"],
            capture_output=True, text=True, timeout=30, cwd=REPO_ROOT)
        txt = out.stdout.strip()
        return ("Prior lessons from memory:\n" + txt) if txt else ""
    except Exception:
        return ""


def _build_prompt(problem: str, arm: Arm, workdir: str) -> str:
    parts = [f"{FORMAT_RULES}\n\nThe repository is checked out at your current "
             f"working directory. Repository issue to fix:\n{problem}"]
    if arm.graphify:
        g = _graphify_context(problem, workdir)
        if g:
            parts.append(g)
    if arm.memory:
        m = _memory_context(problem)
        if m:
            parts.append(m)
    return "\n\n".join(parts)


def _single_agent_loop(instance_id: str, problem: str, workdir: str, arm: Arm,
                       usage: Usage, max_steps: int) -> str:
    prompt = _build_prompt(problem, arm, workdir)
    msgs = [{"role": "system", "content": SYSTEM},
            {"role": "user", "content": prompt}]
    for step in range(max_steps):
        reply = chat(msgs, usage=usage, max_tokens=4096)
        d = DIFF_RE.search(reply)
        if d:
            return d.group(1).strip()
        b = BASH_RE.search(reply)
        if b:
            cmd = b.group(1).strip()
            if not _safe(cmd):
                out = ("ERROR: command references paths outside the repo. Stay in "
                       "the current directory (relative paths only).")
            else:
                out = _run_bash(cmd, workdir)
            msgs.append({"role": "assistant", "content": reply})
            msgs.append({"role": "user", "content": f"Command output:\n{out}"})
        else:
            msgs.append({"role": "assistant", "content": reply})
            msgs.append({"role": "user", "content":
                         "Reply with exactly one ```bash``` or one ```diff``` block."})
    return ""


def _team_loop(instance_id: str, problem: str, workdir: str, arm: Arm,
               usage: Usage, max_steps: int) -> str:
    """T (real team, closer to orch->patek->workers):
    1. Lange plans (concise).
    2. Philipe implements the plan via the agentic loop.
    3. Sohne + Gerald review the patch IN PARALLEL (two independent reviews).
    4. Philipe revises on any critical findings (one consolidated round).
    Returns the final patch. Falls back to the un-reviewed patch if review errors."""
    from concurrent.futures import ThreadPoolExecutor

    # 1. plan
    plan = chat([{"role": "user", "content":
                  ("Produce a minimal, concrete fix plan (files + steps) for this "
                   "issue. No code, just the plan.\n\n" + problem)}],
                usage=usage, max_tokens=1024)
    planned = problem + "\n\nImplementation plan (follow it):\n" + plan

    # 2. implement
    patch = _single_agent_loop(instance_id, planned, workdir, arm, usage, max_steps)
    if not patch or not patch.strip():
        return patch

    # 3. parallel reviewers (Sohne: quality/simplicity, Gerald: correctness/breaks)
    def _review(persona):
        q = ("quality, simplicity, and docs" if persona == "sohne"
             else "correctness, edge cases, and bugs")
        return chat([{"role": "user", "content":
                      (f"Review this patch for {q}. Reply 'LGTM' if sound, else "
                       f"list only CRITICAL/MAJOR issues concisely.\n\nIssue:\n{problem}"
                       f"\n\nPatch:\n{patch}")}], usage=usage, max_tokens=1024)

    try:
        with ThreadPoolExecutor(max_workers=2) as ex:
            sohne_r, gerald_r = list(ex.map(_review, ["sohne", "gerald"]))
    except Exception:
        return patch  # review infra failed -> keep base patch

    findings = "\n".join(x for x in (sohne_r, gerald_r) if x and "lgtm" not in x.lower())
    if not findings.strip():
        return patch  # both signed off

    # 4. one consolidated revision round
    rev = chat([{"role": "user", "content":
                 ("Revise the patch to address these review findings. Return ONLY the "
                  f"final git-style diff.\n\nIssue:\n{problem}\n\nPatch:\n{patch}"
                  f"\n\nFindings:\n{findings}")}], usage=usage, max_tokens=4096)
    d = DIFF_RE.search(rev)
    return d.group(1).strip() if d else patch


def _review_loop(patch: str, problem: str, arm: Arm, usage: Usage) -> str:
    """R: reviewer critiques the patch; implementer revises. Returns final patch."""
    for _ in range(arm.review_rounds):
        review = chat([{"role": "user", "content":
                        ("Review this patch for correctness + edge cases. "
                         "Reply with 'LGTM' if sound, else specific issues.\n\n"
                         f"Issue:\n{problem}\n\nPatch:\n{patch}")}],
                      usage=usage, max_tokens=1024)
        if "lgtm" in review.lower():
            break
        patch_resp = chat([{"role": "user", "content":
                            ("Revise the patch to address the review. Return ONLY a "
                             f"unified diff.\n\nIssue:\n{problem}\n\nPatch:\n{patch}"
                             f"\n\nReview:\n{review}")}],
                          usage=usage, max_tokens=4096)
        d = DIFF_RE.search(patch_resp)
        if d:
            patch = d.group(1).strip()
    return patch


def run_instance(instance_id: str, problem: str, workdir: str, arm: Arm,
                 max_steps: int = 25) -> RunOutcome:
    out = RunOutcome(instance_id=instance_id, arm=arm.name)
    try:
        if arm.team:
            patch = _team_loop(instance_id, problem, workdir, arm, out.usage, max_steps)
        else:
            patch = _single_agent_loop(instance_id, problem, workdir, arm, out.usage, max_steps)
        if arm.review and patch:
            patch = _review_loop(patch, problem, arm, out.usage)
        out.patch = patch
        out.empty_patch = not bool(patch and patch.strip())
        out.steps = max_steps  # refined if we track per-turn; coarse for now
    except Exception as e:
        out.error = repr(e)[:300]
    return out
