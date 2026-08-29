"""Headless CLI for the orchestrator.

Usage:
  python -m orchestrator dispatch <repo> <task...> [--max-parallel N] [--require-index]
  python -m orchestrator status  [--store PATH]
  python -m orchestrator board   [--store PATH]

`dispatch` is the active orchestrator: it indexes the repo (graphify-first),
spins one team per task in isolated worktrees, supervises gates/escalation, and
persists durable facts to the store for later `status`/`board`.
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import List

from .adapters.git_workspace import GitWorkspace
from .adapters.opencode_runner import OpencodeRunner
from .board import render
from .domain import derive_status
from .escalation import EscalationPolicy
from .store import Store
from .supervisor import Supervisor, summarize

DEFAULT_STORE = os.path.join(".orchestrator", "state.jsonl")


def _build_supervisor(args) -> Supervisor:
    store = Store(args.store)
    runner = OpencodeRunner(default_model=args.model or None)
    policy = EscalationPolicy(
        max_per_task=args.max_escalations_per_task,
        global_token_ceiling=args.token_ceiling,
        soft_budget=args.soft_budget,
    )
    models = {}
    if args.models:
        for kv in args.models:
            role, _, mdl = kv.partition("=")
            if mdl:
                models[role.strip()] = mdl.strip()
    return Supervisor(
        store=store,
        runner=runner,
        workspace_for=lambda repo: GitWorkspace(repo),
        policy=policy,
        models=models,
        max_parallel=args.max_parallel,
        max_revisions=args.max_revisions,
        require_index=args.require_index,
    )


def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="orchestrator")
    ap.add_argument("--store", default=DEFAULT_STORE, help="durable fact store path")
    sub = ap.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("dispatch", help="index repo + run one team per task")
    d.add_argument("repo")
    d.add_argument("task", nargs="+", help="task prompt(s)")
    d.add_argument("--max-parallel", type=int, default=4)
    d.add_argument("--max-revisions", type=int, default=2)
    d.add_argument("--require-index", action="store_true",
                   help="fail if the repo cannot be graphify-indexed")
    d.add_argument("--model", default="", help="default model (provider/model)")
    d.add_argument("--models", nargs="*", default=[],
                   help="per-role model overrides, e.g. philipe=local/gemma-4-31B")
    d.add_argument("--token-ceiling", type=int, default=2_000_000)
    d.add_argument("--soft-budget", type=int, default=10)
    d.add_argument("--max-escalations-per-task", type=int, default=2)

    s = sub.add_parser("status", help="list durable task facts + derived status")
    b = sub.add_parser("board", help="render the derived Kanban board")

    # allow `--store` (and other global opts) after the subcommand too
    for sp in (d, s, b):
        sp.add_argument("--store", default=argparse.SUPPRESS,
                        help="durable fact store path")

    args = ap.parse_args(argv)

    if args.cmd == "status":
        store = Store(args.store)
        for t in store.list():
            print(f"{t.task_id}\t{derive_status(t).value}\t[{t.stage}]\t{t.prompt[:60]}")
        return 0

    if args.cmd == "board":
        store = Store(args.store)
        print(render(store))
        return 0

    if args.cmd == "dispatch":
        sup = _build_supervisor(args)
        if isinstance(sup.runner, OpencodeRunner) and not sup.runner.available():
            print("error: opencode CLI not found on PATH", file=sys.stderr)
            return 2
        results = sup.dispatch(args.repo, args.task)
        print("dispatch complete:")
        for status, count in sorted(summarize(results).items()):
            print(f"  {status}: {count}")
        if sup.policy.alarm:
            print("WARNING: escalation demand exceeded soft budget", file=sys.stderr)
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
