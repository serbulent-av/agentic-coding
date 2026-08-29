"""Per-dispatch supervisor. Runs a set of teams to completion, headless.

Flow (your two requirements):
  1. Graphify-first: every repo is indexed via ``ensure_indexed`` BEFORE any
     team starts on it (on-demand per dispatched repo).
  2. Orchestrator active on dispatch: ``dispatch(...)`` IS the active
     orchestrator for the run — it creates isolated worktrees, runs each team,
     persists durable facts after every change, and derives status at read time.

Resumable: durable facts live in the store; re-running skips terminated tasks.
"""

from __future__ import annotations

import itertools
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Dict, List, Optional

from .domain import Stage, TaskFacts, derive_status, Status
from .escalation import EscalationPolicy
from .index import ensure_indexed
from .ports import AgentRunner, Workspace
from .store import Store
from .team import run_team


class Supervisor:
    def __init__(
        self,
        store: Store,
        runner: AgentRunner,
        workspace_for: Callable[[str], Workspace],
        policy: Optional[EscalationPolicy] = None,
        models: Optional[Dict[str, str]] = None,
        max_parallel: int = 4,
        max_revisions: int = 2,
        require_index: bool = False,
    ):
        self.store = store
        self.runner = runner
        self.workspace_for = workspace_for
        self.policy = policy or EscalationPolicy()
        self.models = models or {}
        self.max_parallel = max(1, max_parallel)
        self.max_revisions = max_revisions
        self.require_index = require_index
        self._counter = itertools.count(1)

    # -- public API --------------------------------------------------------
    def dispatch(self, repo: str, prompts: List[str]) -> List[TaskFacts]:
        """Graphify-index the repo, then run one team per prompt to completion."""
        # (1) graphify-first precondition, on-demand for this repo
        idx = ensure_indexed(repo, build=True)
        indexed = idx.ok
        if self.require_index and not indexed:
            raise RuntimeError(f"repo not graphify-indexed and require_index=True: {idx.message}")

        results: List[TaskFacts] = []
        prompts = list(prompts)
        with ThreadPoolExecutor(max_workers=self.max_parallel) as ex:
            futures = [
                ex.submit(self._run_one, repo, p, indexed) for p in prompts
            ]
            for fut in futures:
                results.append(fut.result())
        return results

    def status(self) -> List[TaskFacts]:
        return self.store.list()

    # -- internals ---------------------------------------------------------
    def _run_one(self, repo: str, prompt: str, indexed: bool) -> TaskFacts:
        n = next(self._counter)
        task_id = f"t{n:03d}"

        # resume: if a terminated task with this prompt already exists, skip
        for existing in self.store.list():
            if existing.repo == repo and existing.prompt == prompt and existing.is_terminated:
                return existing

        ws = self.workspace_for(repo)
        worktree, branch = ws.create(task_id)
        facts = TaskFacts(task_id=task_id, repo=repo, prompt=prompt,
                          worktree=worktree, branch=branch, graph_indexed=indexed)
        self.store.upsert(facts)

        def persist(f: TaskFacts) -> None:
            self.store.upsert(f)

        try:
            run_team(facts, self.runner, ws, policy=self.policy,
                     models=self.models, max_revisions=self.max_revisions,
                     on_progress=persist)
        finally:
            persist(facts)
        return facts


def summarize(results: List[TaskFacts]) -> Dict[str, int]:
    """Aggregate derived statuses for a completed dispatch."""
    out: Dict[str, int] = {}
    for f in results:
        s = derive_status(f).value
        out[s] = out.get(s, 0) + 1
    return out
