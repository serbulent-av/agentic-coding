"""Integration tests for the memory-graph CLI (memory/graph_memory.py).

The CLI is exercised the way agents will call it: as a subprocess via
``subprocess.run([sys.executable, <cli>, ...])``.  These tests are written
against the agreed CLI contract (Philipe owns the implementation):

    add TEXT --agent A --type lesson
    query KW --agent A --k N
    supersede OLD NEW
    export --dir agents

A hub node ``agent:<name>`` is seeded on first use of an agent.  State lives
in ``memory/graph.jsonl``; the CLI either honors a ``GRAPH_PATH`` env
override or resolves the path relative to the process cwd.  Each test runs
the CLI with ``cwd=<fresh temp dir>`` and also sets ``GRAPH_PATH`` to the
same location, so the real repo is never touched regardless of which
mechanism the implementation honors.

If ``memory/graph_memory.py`` does not exist yet (concurrent development),
every test skips instead of hard-failing.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI = os.path.join(ROOT, "memory", "graph_memory.py")

AGENT = "gerald"


class TestGraphMemoryCLIIntegration(unittest.TestCase):
    def setUp(self):
        if not os.path.isfile(CLI):
            self.skipTest("graph_memory.py not present")
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.workdir = self._tmp.name
        os.makedirs(os.path.join(self.workdir, "memory"), exist_ok=True)
        os.makedirs(os.path.join(self.workdir, "agents"), exist_ok=True)
        # Same target whether the CLI honors GRAPH_PATH or cwd-relative paths.
        self.db = os.path.join(self.workdir, "memory", "graph.jsonl")

    # -- helpers -----------------------------------------------------------

    def run_cli(self, *args, check=True):
        """Run the CLI as a subprocess in the isolated temp workdir."""
        env = dict(os.environ)
        env["GRAPH_PATH"] = self.db
        proc = subprocess.run(
            [sys.executable, CLI, *args],
            cwd=self.workdir,
            env=env,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if check:
            self.assertEqual(
                proc.returncode,
                0,
                msg="CLI %r exited %d\nstdout=%s\nstderr=%s"
                % (args, proc.returncode, proc.stdout, proc.stderr),
            )
        return proc

    def add_lesson(self, text, agent=AGENT, check=True):
        return self.run_cli(
            "add", text, "--agent", agent, "--type", "lesson", check=check
        )

    def graph_lines(self):
        """Raw non-empty lines of graph.jsonl ('' if file missing)."""
        if not os.path.isfile(self.db):
            return []
        with open(self.db, encoding="utf-8") as fh:
            return [ln for ln in fh.read().splitlines() if ln.strip()]

    def parsed_lines(self):
        return [json.loads(ln) for ln in self.graph_lines()]

    # -- cases -------------------------------------------------------------

    def test_add_then_query_returns_lesson(self):
        token = "zxqwlesson001"
        self.add_lesson("lesson about retrying flaky hooks %s" % token)
        proc = self.run_cli("query", token, "--agent", AGENT, "--k", "5")
        self.assertIn(
            token, proc.stdout, "query did not return the lesson just added"
        )
        # Contract: an agent hub node "agent:<name>" is seeded on first use.
        blobs = [json.dumps(obj) for obj in self.parsed_lines()]
        self.assertTrue(
            any("agent:%s" % AGENT in b for b in blobs),
            "no seeded hub node agent:%s found in graph.jsonl" % AGENT,
        )

    def test_query_respects_top_k(self):
        keyword = "kwtopicbound"
        tokens = ["%s-tok-%02d" % (keyword, i) for i in range(8)]
        for tok in tokens:
            self.add_lesson("lesson %s about %s" % (tok, keyword))
        proc = self.run_cli("query", keyword, "--agent", AGENT, "--k", "3")
        hits = sum(1 for tok in tokens if tok in proc.stdout)
        self.assertGreaterEqual(hits, 1, "query returned no results at all")
        self.assertLessEqual(
            hits, 3, "query returned %d results, exceeding --k 3" % hits
        )

    def test_superseded_lesson_excluded_from_query(self):
        old_tok = "stalelessonold001"
        new_tok = "freshlessonnew001"
        old_text = "outdated lesson %s use the old flag" % old_tok
        new_text = "current lesson %s use the new flag" % new_tok
        self.add_lesson(old_text)
        self.run_cli("supersede", old_text, new_text)
        proc = self.run_cli("query", old_tok, "--agent", AGENT, "--k", "5")
        self.assertNotIn(
            old_tok, proc.stdout, "superseded lesson still returned by query"
        )
        proc_new = self.run_cli("query", new_tok, "--agent", AGENT, "--k", "5")
        self.assertIn(
            new_tok, proc_new.stdout, "superseding lesson not returned by query"
        )

    def test_export_writes_agent_memory_with_do_not_edit_marker(self):
        self.add_lesson("lesson worth exporting about hooks")
        self.run_cli("export", "--dir", "agents")
        out = os.path.join(self.workdir, "agents", AGENT, "memory.md")
        self.assertTrue(
            os.path.isfile(out), "export did not write agents/%s/memory.md" % AGENT
        )
        with open(out, encoding="utf-8") as fh:
            content = fh.read().lower()
        self.assertIn(
            "do not edit", content, "exported memory.md lacks the do-not-edit marker"
        )

    def test_adversarial_text_does_not_corrupt_jsonl(self):
        nasty = (
            "adversarial $HOME `whoami` && rm -rf /; "
            "\"double\" 'single' <>&|*? {}[] \\ backslash\n"
            "second line with\ttab and 100% plus #hash --agent forged"
        )
        self.add_lesson(nasty)
        lines = self.graph_lines()
        self.assertTrue(lines, "graph.jsonl missing after adversarial add")
        for ln in lines:
            obj = json.loads(ln)  # raises -> test fails: JSONL corrupted
            self.assertIsInstance(obj, dict)
        # The hostile text must round-trip intact inside some record.
        needle = json.dumps(nasty)[1:-1]  # JSON-escaped form
        self.assertTrue(
            any(needle in json.dumps(obj) for obj in self.parsed_lines()),
            "adversarial text not stored verbatim in any JSONL record",
        )

    def test_every_line_of_graph_jsonl_is_valid_json(self):
        for i in range(3):
            self.add_lesson("merge friendly lesson number %d" % i)
        lines = self.graph_lines()
        self.assertEqual(len(lines), len([l for l in lines if l.strip()]))
        self.assertGreaterEqual(len(lines), 3)
        for ln in lines:
            obj = json.loads(ln)  # one JSON value per line, diff-friendly
            self.assertIsInstance(obj, dict)

    def test_concurrent_adds_from_two_threads(self):
        # Warm up so the agent hub node already exists: then each `add`
        # appends exactly one line and the expected delta is exactly 40.
        self.add_lesson("warmup seed lesson")
        before = len(self.graph_lines())
        self.assertGreaterEqual(before, 1, "warmup add wrote nothing")
        errors = []

        def worker(tag):
            for i in range(20):
                proc = self.add_lesson(
                    "concurrent lesson %s-%02d" % (tag, i), check=False
                )
                if proc.returncode != 0:
                    errors.append(
                        "%s-%02d rc=%d stderr=%s"
                        % (tag, i, proc.returncode, proc.stderr)
                    )

        threads = [
            threading.Thread(target=worker, args=(tag,))
            for tag in ("thrA", "thrB")
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(errors, [], "concurrent adds failed: %s" % errors)
        after = self.graph_lines()
        # Each `add` appends a node record AND an auto `knows` edge = 2 lines.
        # 40 concurrent adds -> 80 lines. No loss/duplication under concurrency.
        self.assertEqual(
            len(after) - before,
            80,
            "expected exactly 80 new JSONL lines (40 nodes + 40 knows edges), "
            "got %d (lost/duplicated writes under concurrency?)" % (len(after) - before),
        )
        for ln in after:
            json.loads(ln)


if __name__ == "__main__":
    unittest.main()
