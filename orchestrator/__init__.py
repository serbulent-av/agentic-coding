"""Headless agentic-team orchestrator for the agentic-coding repo.

Design template: Agent Orchestrator (Untrivial-ai/agent-orchestrator), reduced to
its minimal headless core:

- **Durable facts, derived status.** Only facts are persisted (see ``store``);
  display status (working/blocked/in-review/...) is *derived at read time*
  (see ``board``), never stored.
- **Port-based.** Core logic depends on the ``AgentRunner`` and ``Workspace``
  interfaces (see ``ports``), never on concrete opencode/git implementations.
- **Worktree isolation.** Each dispatched task gets its own git worktree +
  branch (see ``adapters/git_workspace``).
- **Graphify-first.** ``dispatch`` refuses to start a team on a repo until that
  repo is indexed (``ensure_indexed`` builds/updates ``graphify-out/graph.json``).

This is a *per-dispatch supervisor*: ``python -m orchestrator dispatch ...`` runs
one active supervisor loop to completion (state persisted to disk, resumable).
No long-running daemon.
"""

from .domain import (  # noqa: F401
    Role,
    Stage,
    Status,
    Artifact,
    TaskFacts,
    derive_status,
)
from .ports import AgentRunner, RunResult, Workspace  # noqa: F401
from .store import Store  # noqa: F401

__version__ = "0.1.0"
__all__ = [
    "Role",
    "Stage",
    "Status",
    "Artifact",
    "TaskFacts",
    "derive_status",
    "AgentRunner",
    "RunResult",
    "Workspace",
    "Store",
    "__version__",
]
