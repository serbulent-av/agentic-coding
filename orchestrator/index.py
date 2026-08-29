"""Graphify-first precondition.

``ensure_indexed(repo)`` builds or refreshes ``<repo>/graphify-out/graph.json``
so a team's agents query a knowledge graph instead of grepping raw files. The
dispatcher refuses to start a team until this succeeds.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass


@dataclass
class IndexResult:
    ok: bool
    graph_path: str
    built: bool = False        # True if we (re)built it this call
    message: str = ""


def graph_path(repo: str) -> str:
    return os.path.join(repo, "graphify-out", "graph.json")


def is_indexed(repo: str) -> bool:
    return os.path.exists(graph_path(repo))


def graphify_available() -> bool:
    return shutil.which("graphify") is not None


def ensure_indexed(repo: str, build: bool = True, timeout_s: int = 900) -> IndexResult:
    """Ensure ``repo`` has a graphify index. Builds it if missing (code-only,
    local AST — no API key). If it already exists, does a cheap ``update``.

    Returns an IndexResult; the dispatcher checks ``.ok`` before proceeding.
    """
    repo = os.path.abspath(repo)
    gp = graph_path(repo)

    if not graphify_available():
        # Graceful degradation: index absent but we can still run (agents fall
        # back to grep). Report not-ok only if caller requires the index.
        return IndexResult(ok=False, graph_path=gp, built=False,
                           message="graphify CLI not on PATH; running without index")

    try:
        if not is_indexed(repo):
            if not build:
                return IndexResult(ok=False, graph_path=gp, built=False,
                                   message="no index and build disabled")
            proc = subprocess.run(
                ["graphify", "extract", repo, "--code-only", "--no-cluster"],
                capture_output=True, text=True, timeout=timeout_s,
            )
            ok = proc.returncode == 0 and is_indexed(repo)
            return IndexResult(ok=ok, graph_path=gp, built=ok,
                               message=(proc.stdout + proc.stderr)[-400:])
        # already indexed -> cheap refresh of code nodes (no LLM)
        proc = subprocess.run(
            ["graphify", "update", repo],
            capture_output=True, text=True, timeout=timeout_s,
        )
        ok = proc.returncode == 0 and is_indexed(repo)
        return IndexResult(ok=ok, graph_path=gp, built=False,
                           message=(proc.stdout + proc.stderr)[-400:])
    except subprocess.TimeoutExpired:
        return IndexResult(ok=is_indexed(repo), graph_path=gp, built=False,
                           message="graphify timed out")
    except Exception as exc:  # pragma: no cover - defensive
        return IndexResult(ok=is_indexed(repo), graph_path=gp, built=False,
                           message=f"graphify error: {exc}")
