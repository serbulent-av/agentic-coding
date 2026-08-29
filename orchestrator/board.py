"""Read-model / board. Derives the AO-style Kanban from stored durable facts.

Nothing here is persisted — status is computed at read time (AO's core rule).
"""

from __future__ import annotations

from typing import Dict, List

from .domain import Status, TaskFacts, derive_status
from .store import Store

COLUMN_ORDER = [
    Status.WORKING, Status.IN_REVIEW, Status.READY,
    Status.BLOCKED, Status.NEEDS_INPUT, Status.DONE, Status.FAILED,
]


def board(store: Store) -> Dict[Status, List[TaskFacts]]:
    cols: Dict[Status, List[TaskFacts]] = {s: [] for s in Status}
    for facts in store.list():
        cols[derive_status(facts)].append(facts)
    return cols


def render(store: Store) -> str:
    cols = board(store)
    lines = []
    for status in COLUMN_ORDER:
        tasks = cols.get(status, [])
        if not tasks:
            continue
        lines.append(f"\n## {status.value} ({len(tasks)})")
        for t in tasks:
            lines.append(
                f"  - {t.task_id} [{t.stage}] rev={t.revisions} "
                f"esc={t.escalations} tokens={t.token_spend} :: {t.prompt[:48]}"
            )
    return "\n".join(lines) if lines else "(board empty)"
