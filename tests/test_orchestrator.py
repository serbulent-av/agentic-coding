"""Tests for the thin agentic orchestrator launcher (no GPU / no real opencode).

`orchestrator.dispatch._run_orch` is monkeypatched so no real agent is spawned;
these tests only verify the launcher fans out one orch team per task.
"""

from __future__ import annotations

import importlib
import tempfile
import unittest
from unittest import mock

mod = importlib.import_module("orchestrator.dispatch")  # module, not the function
DispatchResult = mod.DispatchResult


class TestDispatch(unittest.TestCase):
    def test_spawns_one_orch_team_per_task(self):
        tasks = [f"task {i}" for i in range(10)]
        with tempfile.TemporaryDirectory() as repo:
            with mock.patch.object(mod, "_is_git_repo", return_value=False), \
                 mock.patch.object(mod, "_run_orch") as run:
                run.side_effect = lambda task, workdir, model, timeout_s: DispatchResult(
                    task=task, ok=True, worktree=workdir)
                results = mod.dispatch(repo, tasks, max_parallel=4)
        self.assertEqual(len(results), 10)
        self.assertEqual(run.call_count, 10)          # one orch team per task
        self.assertTrue(all(r.ok for r in results))
        for c in run.call_args_list:
            self.assertIn("Task:", mod.ORCH_PROMPT.format(task=c.args[0]))

    def test_report_marks_failures(self):
        results = [DispatchResult(task="a", ok=True),
                   DispatchResult(task="b", ok=False, error="boom")]
        out = mod.report(results)
        self.assertIn("[ok] a", out)
        self.assertIn("[FAILED] b", out)
        self.assertIn("boom", out)


if __name__ == "__main__":
    unittest.main()
