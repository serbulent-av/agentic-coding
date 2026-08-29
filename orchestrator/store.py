"""Durable fact store. JSONL-backed, one record per task, last-write-wins.

This is the orchestrator's single source of truth (AO's SQLite analog, kept
dependency-free). Display status is NOT stored — it is derived at read time.
State persists across invocations so a per-dispatch supervisor can resume.
"""

from __future__ import annotations

import json
import os
import tempfile
import threading
from typing import Dict, List, Optional

from .domain import TaskFacts


class Store:
    def __init__(self, path: str):
        self.path = path
        self._lock = threading.Lock()
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        if not os.path.exists(self.path):
            open(self.path, "a").close()

    def upsert(self, facts: TaskFacts) -> None:
        facts.touch()
        with self._lock:
            all_tasks = self._read_all()
            all_tasks[facts.task_id] = facts
            self._write_all(all_tasks)

    def get(self, task_id: str) -> Optional[TaskFacts]:
        return self._read_all().get(task_id)

    def list(self) -> List[TaskFacts]:
        return list(self._read_all().values())

    def active(self) -> List[TaskFacts]:
        return [t for t in self.list() if not t.is_terminated]

    def _read_all(self) -> Dict[str, TaskFacts]:
        tasks: Dict[str, TaskFacts] = {}
        if not os.path.exists(self.path):
            return tasks
        with open(self.path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                    t = TaskFacts.from_dict(rec)
                    tasks[t.task_id] = t
                except Exception:
                    # skip malformed lines rather than crash the supervisor
                    continue
        return tasks

    def _write_all(self, tasks: Dict[str, TaskFacts]) -> None:
        # atomic rewrite: tmp + rename
        d = os.path.dirname(os.path.abspath(self.path))
        fd, tmp = tempfile.mkstemp(dir=d, prefix=".store-", suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                for t in tasks.values():
                    fh.write(json.dumps(t.to_dict()) + "\n")
            os.replace(tmp, self.path)
        finally:
            if os.path.exists(tmp):
                os.remove(tmp)
