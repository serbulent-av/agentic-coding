"""Unit tests for the headless orchestrator. No GPU / no opencode required:
AgentRunner and Workspace are faked. Covers gates, derived status, escalation,
the graphify-first precondition, resume, and a 10-team dispatch.
"""

from __future__ import annotations

import os
import tempfile
import unittest
from typing import Dict, List, Optional

from orchestrator import Store
from orchestrator.domain import Artifact, Role, Stage, Status, TaskFacts, derive_status
from orchestrator.escalation import EscalationPolicy
from orchestrator.gates import (looks_like_unified_diff, run_gates,
                                test_integrity_violations)
from orchestrator.index import graph_path, is_indexed
from orchestrator.ports import RunResult
from orchestrator.supervisor import Supervisor, summarize


# --------------------------------------------------------------------------
# Fakes
# --------------------------------------------------------------------------

GOOD_DIFF = (
    "diff --git a/src/foo.py b/src/foo.py\n"
    "--- a/src/foo.py\n"
    "+++ b/src/foo.py\n"
    "@@ -1 +1 @@\n"
    "-old\n"
    "+new\n"
)

BAD_TEST_DIFF = (
    "diff --git a/tests/test_x.py b/tests/test_x.py\n"
    "--- a/tests/test_x.py\n"
    "+++ b/tests/test_x.py\n"
    "@@ -1 +1 @@\n"
    "-old\n"
    "+new\n"
)


class FakeWorkspace:
    def __init__(self, repo: str):
        self.repo = repo
        self.created: List[str] = []
        self.diff_text = GOOD_DIFF
        self.tests_pass = True
        self.apply_ok = True

    def create(self, task_id: str, base_ref: str = "HEAD"):
        self.created.append(task_id)
        return (os.path.join(self.repo, ".wt", task_id), f"orc/{task_id}")

    def apply_patch(self, worktree, patch):
        return (self.apply_ok, "applied" if self.apply_ok else "reject")

    def diff(self, worktree):
        return self.diff_text

    def run_tests(self, worktree):
        return (self.tests_pass, "ok" if self.tests_pass else "1 failure")

    def remove(self, task_id, force=False):
        pass

    def cleanup(self, task_id, force=False):
        pass


class FakeRunner:
    """Scriptable runner. Reviewer sign-off and patch quality are controllable."""

    def __init__(self, signoff: bool = True, calls: Optional[List[str]] = None):
        self.signoff = signoff
        self.calls = calls if calls is not None else []

    def run(self, role: Role, prompt: str, worktree: str,
            model: Optional[str] = None, artifacts=None, timeout_s: int = 1800):
        self.calls.append(role.value)
        if role in (Role.SOHNE, Role.GERALD):
            txt = "LGTM: no critical issues" if self.signoff else "CRITICAL: bug found"
            return RunResult(ok=True, summary=txt,
                             artifacts={f"review-{role.value}": f"{worktree}/review-{role.value}.md"},
                             token_used=10)
        if role == Role.LANGE:
            return RunResult(ok=True, summary="plan: do X",
                             artifacts={"plan": f"{worktree}/plan.md"}, token_used=10)
        if role == Role.PHILIPE:
            return RunResult(ok=True, summary="implemented X",
                             artifacts={"patch": f"{worktree}/p.diff"}, token_used=20)
        return RunResult(ok=True, summary="ok", token_used=5)


def _store(tmp) -> Store:
    return Store(os.path.join(tmp, "state.jsonl"))


# --------------------------------------------------------------------------
# Gates
# --------------------------------------------------------------------------

class TestGates(unittest.TestCase):
    def test_diff_lint(self):
        self.assertTrue(looks_like_unified_diff(GOOD_DIFF))
        self.assertFalse(looks_like_unified_diff(""))
        self.assertFalse(looks_like_unified_diff("just some prose"))

    def test_test_integrity_guard(self):
        self.assertEqual(test_integrity_violations(GOOD_DIFF), [])
        self.assertEqual(test_integrity_violations(BAD_TEST_DIFF), ["tests/test_x.py"])

    def test_run_gates_pass(self):
        ws = FakeWorkspace("/r")
        rep = run_gates(ws, "/r/.wt/t", GOOD_DIFF)
        self.assertTrue(rep.passed, rep.failures)

    def test_run_gates_reject_test_edit(self):
        ws = FakeWorkspace("/r")
        rep = run_gates(ws, "/r/.wt/t", BAD_TEST_DIFF)
        self.assertFalse(rep.passed)
        self.assertTrue(any("test-integrity" in f for f in rep.failures))

    def test_run_gates_reject_bad_apply(self):
        ws = FakeWorkspace("/r")
        ws.apply_ok = False
        rep = run_gates(ws, "/r/.wt/t", GOOD_DIFF)
        self.assertFalse(rep.passed)


# --------------------------------------------------------------------------
# Derived status (AO: never stored)
# --------------------------------------------------------------------------

class TestDerivedStatus(unittest.TestCase):
    def test_status_from_facts(self):
        f = TaskFacts(task_id="t", repo="/r", prompt="p")
        self.assertEqual(derive_status(f), Status.WORKING)         # plan stage
        f.stage = Stage.REVIEW.value
        self.assertEqual(derive_status(f), Status.IN_REVIEW)
        f.signoffs = ["sohne", "gerald"]
        self.assertEqual(derive_status(f), Status.READY)
        f.blocked_reason = "x"
        self.assertEqual(derive_status(f), Status.BLOCKED)
        f.blocked_reason = ""
        f.stage = Stage.DONE.value
        self.assertEqual(derive_status(f), Status.DONE)


# --------------------------------------------------------------------------
# Escalation policy
# --------------------------------------------------------------------------

class TestEscalation(unittest.TestCase):
    def test_caps_and_priority(self):
        pol = EscalationPolicy(max_per_task=1, soft_budget=2)
        # higher severity pops first
        pol.request("a", "low", severity=1)
        pol.request("b", "high", severity=9)
        ev = pol.pop_next(task_escalations=0)
        self.assertEqual(ev.task_id, "b")
        # per-task cap blocks further escalation for that task
        ok, _ = pol.should_escalate(task_escalations=1)
        self.assertFalse(ok)
        self.assertIsNone(pol.pop_next(task_escalations=1))

    def test_soft_budget_alarm(self):
        pol = EscalationPolicy(soft_budget=1)
        pol.request("a", "r", 1)
        pol.request("b", "r", 1)
        pol.pop_next(0)
        self.assertFalse(pol.alarm)
        pol.pop_next(0)
        self.assertTrue(pol.alarm)


# --------------------------------------------------------------------------
# Graphify-first precondition
# --------------------------------------------------------------------------

class TestIndex(unittest.TestCase):
    def test_paths(self):
        self.assertTrue(graph_path("/r").endswith("graphify-out/graph.json"))
        self.assertFalse(is_indexed(tempfile.mkdtemp()))


# --------------------------------------------------------------------------
# Supervisor: the 10-team dispatch on a small task
# --------------------------------------------------------------------------

class TestDispatch(unittest.TestCase):
    def _make(self, tmp, signoff=True):
        store = _store(tmp)
        runner = FakeRunner(signoff=signoff)
        ws_cache: Dict[str, FakeWorkspace] = {}

        def workspace_for(repo: str) -> FakeWorkspace:
            ws_cache.setdefault(repo, FakeWorkspace(repo))
            return ws_cache[repo]

        sup = Supervisor(store=store, runner=runner, workspace_for=workspace_for,
                         policy=EscalationPolicy(), max_parallel=4)
        return sup, store, ws_cache

    def test_dispatch_ten_teams(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = os.path.join(tmp, "repo")
            os.makedirs(repo, exist_ok=True)
            sup, store, ws_cache = self._make(tmp, signoff=True)

            prompts = [f"small task {i}" for i in range(10)]
            results = sup.dispatch(repo, prompts)

            # 10 teams ran
            self.assertEqual(len(results), 10)
            # each got an isolated worktree + branch
            self.assertEqual(len(ws_cache[repo].created), 10)
            self.assertEqual(len({r.branch for r in results}), 10)
            # all reached DONE via gates + both reviewer signoffs
            agg = summarize(results)
            self.assertEqual(agg.get("done"), 10)
            # role-batched pipeline exercised plan->implement->review for each
            for role in ("lange", "philipe", "sohne", "gerald"):
                self.assertGreaterEqual(sup.runner.calls.count(role), 10)
            # durable facts persisted; status derived at read time
            persisted = store.list()
            self.assertEqual(len(persisted), 10)
            self.assertTrue(all(derive_status(t) == Status.DONE for t in persisted))

    def test_resume_skips_terminated(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = os.path.join(tmp, "repo")
            os.makedirs(repo, exist_ok=True)
            sup, store, _ = self._make(tmp)
            sup.dispatch(repo, ["t once"])
            n_ws = 1
            # second dispatch of the same prompt -> no new worktree (resumed)
            sup.dispatch(repo, ["t once"])
            self.assertEqual(len(store.list()), 1)

    def test_blocking_when_no_signoff_and_no_budget(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = os.path.join(tmp, "repo")
            os.makedirs(repo, exist_ok=True)
            sup, store, _ = self._make(tmp, signoff=False)
            sup.policy.max_per_task = 0          # no escalation budget
            sup.max_revisions = 1
            res = sup.dispatch(repo, ["never sign off"])[0]
            self.assertEqual(derive_status(res), Status.BLOCKED)


if __name__ == "__main__":
    unittest.main()
