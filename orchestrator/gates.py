"""Deterministic gates. Cheap, objective checks run BEFORE any LLM judgment.

Legitimate gates only (per the upgrade plan):
- patch applies cleanly (``git apply --check``)
- pre-existing test suite does not regress
- test-integrity guard: a candidate patch must not modify test/oracle files
- patch-format lint: non-empty, looks like a unified diff

Gates are treated as noisy evidence, not ground truth (the SWE-bench verifier
itself is ~8.5% FP / 24% FN); they filter, they don't certify.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List

from .ports import Workspace

# Paths that indicate test/oracle files a solution patch must not touch.
_TEST_PATH_RE = re.compile(
    r"(^|/)(tests?/|testing/|test_|.*_test\.|conftest\.py|.*\.spec\.)", re.IGNORECASE
)


@dataclass
class GateReport:
    passed: bool
    checks: List[str] = field(default_factory=list)
    failures: List[str] = field(default_factory=list)

    def add(self, name: str, ok: bool, detail: str = "") -> None:
        self.checks.append(f"{name}: {'ok' if ok else 'FAIL'}" + (f" — {detail}" if detail else ""))
        if not ok:
            self.failures.append(f"{name}: {detail}")
            self.passed = False


def looks_like_unified_diff(patch: str) -> bool:
    if not patch or not patch.strip():
        return False
    return ("--- " in patch and "+++ " in patch and "@@" in patch) or patch.lstrip().startswith("diff --git")


def touched_files(patch: str) -> List[str]:
    files = []
    for line in patch.splitlines():
        if line.startswith("+++ b/"):
            files.append(line[len("+++ b/"):].strip())
        elif line.startswith("+++ "):
            files.append(line[len("+++ "):].strip())
    return files


def test_integrity_violations(patch: str) -> List[str]:
    return [f for f in touched_files(patch) if _TEST_PATH_RE.search(f)]


def run_gates(workspace: Workspace, worktree: str, patch: str) -> GateReport:
    """Run all deterministic gates on a candidate patch. Returns a report."""
    report = GateReport(passed=True)

    # 1. patch-format lint
    report.add("patch-format", looks_like_unified_diff(patch),
               "empty or not a unified diff")

    # 2. test-integrity guard
    violations = test_integrity_violations(patch)
    report.add("test-integrity", not violations,
               f"touches test/oracle files: {', '.join(violations)}" if violations else "")

    # 3. patch applies cleanly
    applied, msg = workspace.apply_patch(worktree, patch)
    report.add("patch-applies", applied, msg if not applied else "")

    # 4. tests non-regress (only meaningful if the patch applied)
    if applied:
        passed, out = workspace.run_tests(worktree)
        report.add("tests-nonregress", passed, "" if passed else out[-400:])
    else:
        report.add("tests-nonregress", False, "skipped (patch did not apply)")

    return report
