"""Domain vocabulary + durable facts for the headless orchestrator.

AO principle applied here: **never store display status**. ``TaskFacts`` holds
only durable facts; ``derive_status`` computes the board-facing status at read
time from those facts.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional


class Role(str, Enum):
    """The five team roles (distilled from agents/<name>/description.md)."""

    PATEK = "patek"        # orchestrator / lead (primary)
    LANGE = "lange"        # planner
    PHILIPE = "philipe"    # implementer
    SOHNE = "sohne"        # oversight review (quality / anti-over-engineering)
    GERALD = "gerald"      # red-team review (correctness / adversarial)


class Stage(str, Enum):
    """Execution stages of one task/team."""

    PLAN = "plan"
    IMPLEMENT = "implement"
    REVIEW = "review"
    FIX = "fix"
    DONE = "done"
    BLOCKED = "blocked"
    FAILED = "failed"


class Status(str, Enum):
    """Derived (never stored) board status — mirrors AO's Kanban columns."""

    WORKING = "working"
    NEEDS_INPUT = "needs_input"
    IN_REVIEW = "in_review"
    READY = "ready"
    BLOCKED = "blocked"
    DONE = "done"
    FAILED = "failed"


@dataclass
class Artifact:
    """A compact handoff between stages (a file reference, not inline content)."""

    kind: str            # plan | patch | review-sohne | review-gerald | log
    path: str            # repo-relative path inside the task worktree
    summary: str = ""    # <= ~1-2k token distilled summary

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Artifact":
        return Artifact(kind=d["kind"], path=d["path"], summary=d.get("summary", ""))


@dataclass
class TaskFacts:
    """Durable facts about one dispatched task. This is ALL that is persisted."""

    task_id: str
    repo: str                       # absolute path to the source repo
    prompt: str                     # the task text
    branch: str = ""
    worktree: str = ""              # absolute path to the task's git worktree
    stage: str = Stage.PLAN.value   # current stage (a fact, not display status)
    is_terminated: bool = False
    graph_indexed: bool = False     # graphify-out/graph.json exists & fresh
    revisions: int = 0              # gate-driven fix rounds so far
    escalated: bool = False         # an Opus/frontier escalation was used
    escalations: int = 0
    blocked_reason: str = ""        # non-empty => human/oversight attention needed
    signoffs: List[str] = field(default_factory=list)  # e.g. ["sohne", "gerald"]
    artifacts: List[Artifact] = field(default_factory=list)
    token_spend: int = 0
    created_ts: float = field(default_factory=time.time)
    updated_ts: float = field(default_factory=time.time)

    # -- facts are mutated through small helpers so updated_ts stays correct --
    def touch(self) -> None:
        self.updated_ts = time.time()

    def add_artifact(self, art: Artifact) -> None:
        self.artifacts.append(art)
        self.touch()

    def latest(self, kind: str) -> Optional[Artifact]:
        for a in reversed(self.artifacts):
            if a.kind == kind:
                return a
        return None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "TaskFacts":
        d = dict(d)
        d["artifacts"] = [Artifact.from_dict(a) for a in d.get("artifacts", [])]
        d["signoffs"] = list(d.get("signoffs", []))
        return TaskFacts(**d)


# Reviewer roles that must sign off before a task is "ready".
REVIEWERS = (Role.SOHNE.value, Role.GERALD.value)


def derive_status(f: TaskFacts) -> Status:
    """Compute the board-facing status from durable facts (read time only).

    Precedence mirrors AO: terminated/done > blocked/needs-input > in-review >
    ready > working.
    """
    if f.stage == Stage.FAILED.value:
        return Status.FAILED
    if f.stage == Stage.DONE.value:
        return Status.DONE
    if f.blocked_reason:
        return Status.BLOCKED
    if f.stage == Stage.REVIEW.value:
        # all reviewers signed off => ready to advance; otherwise still reviewing
        if all(r in f.signoffs for r in REVIEWERS):
            return Status.READY
        return Status.IN_REVIEW
    if f.stage in (Stage.PLAN.value, Stage.IMPLEMENT.value, Stage.FIX.value):
        return Status.WORKING
    if f.stage == Stage.BLOCKED.value:
        return Status.BLOCKED
    return Status.WORKING
