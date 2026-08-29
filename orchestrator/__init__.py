"""Thin agentic orchestrator launcher.

The orchestrator is an AGENT (`.opencode/agent/orch.md`). This package only
launches `orch` sessions (one per task) and ensures the repo is Graphify-indexed
first. No custom state machine / gates / escalation engine — that intelligence
lives in the agents and skills.
"""

from .dispatch import dispatch, report, DispatchResult  # noqa: F401
from .index import ensure_indexed  # noqa: F401

__version__ = "0.1.0"
