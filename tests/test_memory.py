"""Tests for the graph-memory CLI (no GPU; uses a temp dir store)."""

from __future__ import annotations

import contextlib
import io
import json
import os
import shutil
import sys
import tempfile
import threading
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "memory"))

import graph_memory as gm  # noqa: E402


def run_cli(argv):
    """Run the CLI, returning (exit_code, stdout_lines)."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = gm.main(argv)
    return code, buf.getvalue().splitlines()


class GraphMemoryTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="graphmem-")
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.store = os.path.join(self.tmp, "graph.jsonl")
        for name in ("orch", "patek", "lange", "philipe", "sohne", "gerald"):
            gm.append_record(self.store, {
                "kind": "node",
                "id": f"agent:{name}",
                "type": "agent",
                "agent": name,
                "text": f"{name.capitalize()} hub",
                "props": {},
                "ts": 1756684800,
            })

    def add(self, text, agent="philipe", ntype="lesson", extra=None):
        argv = ["--store", self.store, "add", text,
                "--agent", agent, "--type", ntype]
        for k, v in (extra or []):
            argv += [k, v]
        code, out = run_cli(argv)
        self.assertEqual(code, 0)
        self.assertEqual(len(out), 1)
        return out[0]

    def query(self, keyword, agent="philipe", k=5):
        code, out = run_cli(["--store", self.store, "query", keyword,
                             "--agent", agent, "--k", str(k)])
        self.assertEqual(code, 0)
        return out

    def test_add_then_query_roundtrip(self):
        nid = self.add("Always lock the JSONL file before appending")
        hits = self.query("lock")
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0], f"{nid} [lesson] Always lock the JSONL file "
                                  "before appending")
        self.assertTrue(nid.startswith("lesson:philipe:"))

    def test_add_creates_knows_and_topic_edges(self):
        nid = self.add("Prefer stdlib argparse", extra=[("--applies-to", "cli")])
        conn = gm.load_db(self.store)
        self.addCleanup(conn.close)
        rels = {tuple(r) for r in conn.execute(
            "SELECT src, dst, rel FROM edges WHERE src = ? OR dst = ?",
            (nid, nid))}
        self.assertIn(("agent:philipe", nid, "knows"), rels)
        self.assertIn((nid, "topic:cli", "applies_to"), rels)
        topic = conn.execute(
            "SELECT type FROM nodes WHERE id = 'topic:cli'").fetchone()
        self.assertIsNotNone(topic)
        self.assertEqual(topic["type"], "topic")

    def test_top_k_bounding(self):
        for i in range(8):
            self.add(f"bounded lesson number {i}")
        self.assertEqual(len(self.query("bounded", k=5)), 5)
        self.assertEqual(len(self.query("bounded", k=3)), 3)
        self.assertEqual(len(self.query("bounded", k=100)), 8)

    def test_superseded_node_excluded(self):
        old = self.add("use global locks for everything")
        new = self.add("use per-file locks for appends")
        code, _ = run_cli(["--store", self.store, "supersede", old, new])
        self.assertEqual(code, 0)
        hits = self.query("locks")
        ids = [h.split(" ", 1)[0] for h in hits]
        self.assertIn(new, ids)
        self.assertNotIn(old, ids)

    def test_path_bfs(self):
        nid = self.add("path test node", extra=[("--applies-to", "nav")])
        code, out = run_cli(["--store", self.store, "path",
                             "agent:philipe", "topic:nav"])
        self.assertEqual(code, 0)
        self.assertEqual(out[0], f"agent:philipe -> {nid} -> topic:nav")

    def test_export_regenerates_agent_md_with_header(self):
        self.add("exported lesson alpha", ntype="lesson")
        self.add("exported decision beta", ntype="decision")
        self.add("orch-only gotcha", agent="orch", ntype="gotcha")
        outdir = os.path.join(self.tmp, "agents")
        code, written = run_cli(["--store", self.store, "export",
                                 "--dir", outdir])
        self.assertEqual(code, 0)
        self.assertEqual(len(written), 6)

        path = os.path.join(outdir, "philipe", "memory.md")
        with open(path, encoding="utf-8") as fh:
            content = fh.read()
        first_line = content.splitlines()[0]
        self.assertEqual(first_line, gm.GENERATED_HEADER)
        self.assertIn("do not edit", first_line)
        self.assertIn("exported lesson alpha", content)
        self.assertIn("exported decision beta", content)
        self.assertIn("## Lessons", content)
        self.assertIn("## Decisions", content)
        self.assertNotIn("orch-only gotcha", content)

        with open(os.path.join(outdir, "orch", "memory.md"),
                  encoding="utf-8") as fh:
            orch = fh.read()
        self.assertTrue(orch.startswith(gm.GENERATED_HEADER))
        self.assertIn("orch-only gotcha", orch)

        # Export is regenerative: stale content is replaced.
        with open(path, "a", encoding="utf-8") as fh:
            fh.write("STALE JUNK\n")
        run_cli(["--store", self.store, "export", "--dir", outdir])
        with open(path, encoding="utf-8") as fh:
            self.assertNotIn("STALE JUNK", fh.read())

    def test_concurrent_writers_no_corruption(self):
        errors = []

        def writer(tag):
            try:
                for i in range(50):
                    gm.append_record(self.store, {
                        "kind": "node",
                        "id": f"lesson:t{tag}:{i:04d}",
                        "type": "lesson",
                        "agent": f"t{tag}",
                        "text": f"concurrent write {tag}-{i}",
                        "props": {},
                        "ts": 1756684800 + i,
                    })
            except Exception as exc:  # noqa: BLE001
                errors.append(exc)

        threads = [threading.Thread(target=writer, args=(t,)) for t in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(errors, [])

        with open(self.store, encoding="utf-8") as fh:
            lines = fh.readlines()
        self.assertEqual(len(lines), 6 + 8 * 50)
        for line in lines:
            self.assertTrue(line.endswith("\n"))
            rec = json.loads(line)  # raises if corrupted/interleaved
            self.assertEqual(rec["kind"], "node")

        # All 400 concurrent records are queryable.
        conn = gm.load_db(self.store)
        self.addCleanup(conn.close)
        n = conn.execute(
            "SELECT COUNT(*) FROM nodes WHERE text LIKE 'concurrent write%'"
        ).fetchone()[0]
        self.assertEqual(n, 8 * 50)


if __name__ == "__main__":
    unittest.main()
