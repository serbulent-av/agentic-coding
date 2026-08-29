"""Port interfaces. Core orchestration logic depends ONLY on these, never on
concrete opencode/git implementations (AO's port-based design)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Protocol

from .domain import Role


@dataclass
class RunResult:
    """Outcome of a single agent invocation."""

    ok: bool
    summary: str = ""                 # distilled <= ~1-2k token result
    artifacts: Dict[str, str] = field(default_factory=dict)  # kind -> path
    token_used: int = 0
    error: str = ""


class AgentRunner(Protocol):
    """Runs one role's prompt in a worktree and returns a compact result.

    Production impl: ``adapters.opencode_runner.OpencodeRunner`` (shells
    ``opencode run --agent <role> --dir <worktree> --format json``).
    Test impl: a fake returning canned results.
    """

    def run(
        self,
        role: Role,
        prompt: str,
        worktree: str,
        model: Optional[str] = None,
        artifacts: Optional[List[str]] = None,
        timeout_s: int = 1800,
    ) -> RunResult:
        ...


class Workspace(Protocol):
    """Manages an isolated git worktree per task.

    Production impl: ``adapters.git_workspace.GitWorkspace``.
    """

    def create(self, task_id: str, base_ref: str = "HEAD") -> tuple[str, str]:
        """Create a worktree + branch; return (worktree_path, branch)."""
        ...

    def apply_patch(self, worktree: str, patch: str) -> tuple[bool, str]:
        """Apply a unified diff; return (applied_cleanly, message)."""
        ...

    def diff(self, worktree: str) -> str:
        """Return the current unified diff of the worktree vs its base."""
        ...

    def run_tests(self, worktree: str) -> tuple[bool, str]:
        """Run the repo's test gate; return (passed, output)."""
        ...

    def remove(self, task_id: str, force: bool = False) -> None:
        ...

    def cleanup(self, task_id: str, force: bool = False) -> None:
        """Alias-friendly teardown (defaults to remove)."""
        ...
