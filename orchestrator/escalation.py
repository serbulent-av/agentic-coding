"""Cost-capped hybrid escalation policy (local-first, Opus only when ambiguous).

Controls (per the upgrade plan, replacing a fixed N/2 cap):
- soft budget + priority queue keyed by severity
- defer-and-retry next window
- alarm when demand > budget
- global token/$ ceiling with a kill-switch
- every escalation logged with a reason
"""

from __future__ import annotations

import heapq
import itertools
import time
from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass
class EscalationEvent:
    task_id: str
    reason: str
    severity: int           # higher = more urgent
    ts: float = field(default_factory=time.time)


@dataclass
class EscalationPolicy:
    max_per_task: int = 2
    global_token_ceiling: int = 2_000_000
    soft_budget: int = 10            # preferred escalations per supervisor run
    kill_on_ceiling: bool = True

    def __post_init__(self) -> None:
        self._pq: List[Tuple[int, int, EscalationEvent]] = []  # min-heap by (-severity, seq)
        self._seq = itertools.count()
        self._used_tokens = 0
        self.events: List[EscalationEvent] = []
        self.alarm = False

    # -- demand side -------------------------------------------------------
    def request(self, task_id: str, reason: str, severity: int) -> None:
        ev = EscalationEvent(task_id=task_id, reason=reason, severity=severity)
        heapq.heappush(self._pq, (-severity, next(self._seq), ev))

    def pending(self) -> int:
        return len(self._pq)

    # -- decision ----------------------------------------------------------
    def should_escalate(self, task_escalations: int) -> Tuple[bool, str]:
        if task_escalations >= self.max_per_task:
            return False, f"per-task cap reached ({self.max_per_task})"
        if self._used_tokens >= self.global_token_ceiling:
            return False, "global token ceiling reached"
        return True, "ok"

    def pop_next(self, task_escalations: int) -> Optional[EscalationEvent]:
        """Pop the highest-severity pending escalation if budget allows."""
        if not self._pq:
            return None
        ok, _ = self.should_escalate(task_escalations)
        if not ok:
            return None
        _, _, ev = heapq.heappop(self._pq)
        self.events.append(ev)
        # soft-budget alarm: demand exceeds preferred budget
        if len(self.events) > self.soft_budget:
            self.alarm = True
        return ev

    def record_tokens(self, n: int) -> None:
        self._used_tokens += n

    def ceiling_tripped(self) -> bool:
        return self.kill_on_ceiling and self._used_tokens >= self.global_token_ceiling
