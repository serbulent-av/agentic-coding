"""opencode adapter. Runs one role headlessly via the opencode CLI.

    opencode run --agent <role> --dir <worktree> --format json "<prompt>"

``--format json`` emits newline-delimited JSON events; we extract the final
assistant text as the result summary and any file artifact paths it wrote.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from typing import Dict, List, Optional

from ..domain import Role
from ..ports import RunResult


class OpencodeRunner:
    def __init__(self, binary: str = "opencode", default_model: Optional[str] = None):
        self.binary = binary
        self.default_model = default_model

    def available(self) -> bool:
        return shutil.which(self.binary) is not None

    def run(
        self,
        role: Role,
        prompt: str,
        worktree: str,
        model: Optional[str] = None,
        artifacts: Optional[List[str]] = None,
        timeout_s: int = 1800,
    ) -> RunResult:
        if not self.available():
            return RunResult(ok=False, error=f"{self.binary} not on PATH")

        full_prompt = prompt
        if artifacts:
            refs = "\n".join(f"- {a}" for a in artifacts)
            full_prompt += f"\n\nRelevant artifacts (read these files, don't restate them):\n{refs}"

        cmd = [self.binary, "run", "--agent", role.value, "--dir", worktree,
               "--format", "json"]
        mdl = model or self.default_model
        if mdl:
            cmd += ["-m", mdl]
        cmd.append(full_prompt)

        try:
            proc = subprocess.run(cmd, cwd=worktree, capture_output=True,
                                  text=True, timeout=timeout_s)
        except subprocess.TimeoutExpired:
            return RunResult(ok=False, error=f"timeout after {timeout_s}s")

        if proc.returncode != 0:
            return RunResult(ok=False, error=(proc.stderr or proc.stdout)[-400:])

        summary = self._extract_final_text(proc.stdout)
        return RunResult(ok=True, summary=summary)

    @staticmethod
    def _extract_final_text(ndjson: str) -> str:
        """Pull the last assistant text out of opencode's JSON event stream."""
        last_text = ""
        for line in ndjson.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            # tolerate a couple of shapes: {"type":"text","text":...} or
            # {"type":"message","content":[{"type":"text","text":...}]}
            if ev.get("type") in ("text", "assistant") and isinstance(ev.get("text"), str):
                last_text = ev["text"]
            elif ev.get("type") == "message":
                for part in ev.get("content", []) or []:
                    if isinstance(part, dict) and part.get("type") == "text":
                        last_text = part.get("text", last_text)
        return last_text.strip()
