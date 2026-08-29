"""Headless entry point for the agentic orchestrator.

    python -m orchestrator dispatch <repo> <task...> [--max-parallel N] [--model M]

This is a thin launcher: it ensures the repo is Graphify-indexed, then spawns one
`orch` agent team per task. The orchestration intelligence lives in the agents
(`.opencode/agent/`) and skills (`skills/`), not here.
"""

from __future__ import annotations

import argparse
import sys
from typing import List

from .dispatch import dispatch, report
from .index import ensure_indexed


def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="orchestrator")
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("dispatch", help="index repo + spawn one orch team per task")
    d.add_argument("repo")
    d.add_argument("task", nargs="+")
    d.add_argument("--max-parallel", type=int, default=4)
    d.add_argument("--model", default="")
    d.add_argument("--no-isolate", action="store_true",
                   help="run in the repo directly instead of per-task worktrees")
    args = ap.parse_args(argv)

    if args.cmd == "dispatch":
        idx = ensure_indexed(args.repo, build=True)
        if not idx.ok:
            print(f"warning: graphify index unavailable ({idx.message})", file=sys.stderr)
        results = dispatch(args.repo, args.task, max_parallel=args.max_parallel,
                           model=args.model or None, isolate=not args.no_isolate)
        print(report(results))
        return 0 if all(r.ok for r in results) else 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
