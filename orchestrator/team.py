"""Team loop: run one task through the role pipeline in its own worktree.

Pipeline (role-batched, fresh context per stage, compact handoffs):
    Lange (plan) -> Philipe (implement) -> [Sohne + Gerald] (review)
    -> deterministic gates -> [fix loop w/ escalation] -> done

Only durable facts are written to the store; status is derived elsewhere.
"""

from __future__ import annotations

from typing import Callable, Dict, Optional

from .domain import Artifact, REVIEWERS, Role, Stage, TaskFacts
from .escalation import EscalationPolicy
from .gates import run_gates
from .ports import AgentRunner, Workspace

ProgressFn = Callable[[TaskFacts], None]


def _note(facts: TaskFacts, msg: str) -> None:
    facts.add_artifact(Artifact(kind="log", path="", summary=msg))


def run_team(
    facts: TaskFacts,
    runner: AgentRunner,
    workspace: Workspace,
    policy: Optional[EscalationPolicy] = None,
    models: Optional[Dict[str, str]] = None,
    max_revisions: int = 2,
    on_progress: Optional[ProgressFn] = None,
) -> TaskFacts:
    """Drive one task to done/blocked/failed. Mutates + returns ``facts``.

    ``on_progress`` (if given) is called after each durable change so callers
    can persist to the store / refresh a board.
    """
    models = models or {}
    policy = policy or EscalationPolicy()

    def progress() -> None:
        if on_progress:
            on_progress(facts)

    # -- Stage: plan (Lange) ------------------------------------------------
    facts.stage = Stage.PLAN.value
    progress()
    plan = runner.run(Role.LANGE, _prompt_plan(facts), facts.worktree,
                      model=models.get(Role.LANGE.value))
    facts.token_spend += plan.token_used
    if not plan.ok:
        return _fail(facts, f"plan stage failed: {plan.error}", progress)
    facts.add_artifact(Artifact(kind="plan", path=plan.artifacts.get("plan", ""),
                                summary=plan.summary))
    progress()

    # -- Stage: implement (Philipe) ----------------------------------------
    facts.stage = Stage.IMPLEMENT.value
    progress()
    impl = runner.run(Role.PHILIPE, _prompt_implement(facts), facts.worktree,
                      model=models.get(Role.PHILIPE.value),
                      artifacts=[a.path for a in facts.artifacts if a.path])
    facts.token_spend += impl.token_used
    if not impl.ok:
        return _fail(facts, f"implement stage failed: {impl.error}", progress)
    facts.add_artifact(Artifact(kind="patch", path=impl.artifacts.get("patch", ""),
                                summary=impl.summary))
    progress()

    # -- Review + fix loop --------------------------------------------------
    while True:
        facts.stage = Stage.REVIEW.value
        progress()
        # parallel reviewers (run sequentially here; cheap since they're agents)
        for role in (Role.SOHNE, Role.GERALD):
            if role.value in facts.signoffs:
                continue
            res = runner.run(role, _prompt_review(facts, role), facts.worktree,
                             model=models.get(role.value),
                             artifacts=[a.path for a in facts.artifacts if a.path])
            facts.token_spend += res.token_used
            kind = f"review-{role.value}"
            facts.add_artifact(Artifact(kind=kind, path=res.artifacts.get(kind, ""),
                                        summary=res.summary))
            if res.ok and _is_signoff(res.summary):
                if role.value not in facts.signoffs:
                    facts.signoffs.append(role.value)
            progress()

        # deterministic gates on the current patch
        patch_text = _current_patch_text(facts, workspace)
        report = run_gates(workspace, facts.worktree, patch_text)
        _note(facts, "gates: " + ("PASS" if report.passed else "FAIL"))
        progress()

        all_signed = all(r in facts.signoffs for r in REVIEWERS)
        if all_signed and report.passed:
            facts.stage = Stage.DONE.value
            facts.is_terminated = True
            progress()
            return facts

        # something failed -> fix loop or escalate
        if facts.revisions >= max_revisions:
            # try escalation before giving up
            ev = None
            if policy is not None:
                policy.request(facts.task_id,
                               reason="gates/review unresolved after revisions",
                               severity=5)
                ev = policy.pop_next(facts.escalations)
            if ev is not None:
                facts.escalations += 1
                facts.escalated = True
                facts.revisions = 0  # allow a fresh round with the escalated model
                _note(facts, f"escalated: {ev.reason}")
                progress()
                continue
            return _blocked(facts, "unresolved after revisions and no escalation budget",
                            progress)

        facts.revisions += 1
        facts.stage = Stage.FIX.value
        fix_prompt = _prompt_fix(facts, report.failures)
        fix = runner.run(Role.PHILIPE, fix_prompt, facts.worktree,
                         model=models.get(Role.PHILIPE.value),
                         artifacts=[a.path for a in facts.artifacts if a.path])
        facts.token_spend += fix.token_used
        if not fix.ok:
            return _fail(facts, f"fix stage failed: {fix.error}", progress)
        facts.add_artifact(Artifact(kind="patch", path=fix.artifacts.get("patch", ""),
                                    summary=fix.summary))
        # a fix invalidates prior signoffs (re-review required)
        facts.signoffs = []
        progress()


# --------------------------------------------------------------------------
# prompt builders (compact; the heavy role identity lives in the opencode
# agent definitions, so these only carry the task + handoff)
# --------------------------------------------------------------------------

def _prompt_plan(f: TaskFacts) -> str:
    return (f"Task: {f.prompt}\n\n"
            "Query the graph (graphify query) before reading files. "
            "Produce a concise plan with acceptance criteria.")


def _prompt_implement(f: TaskFacts) -> str:
    plan = f.latest("plan")
    return (f"Implement this plan minimally.\n\nPlan:\n{plan.summary if plan else ''}")


def _prompt_review(f: TaskFacts, role: Role) -> str:
    patch = f.latest("patch")
    who = "quality/simplicity" if role == Role.SOHNE else "correctness/edge-cases"
    return (f"Review the current patch for {who}. Sign off with 'LGTM' only if "
            f"there are no critical issues.\n\nPatch:\n{patch.summary if patch else ''}")


def _prompt_fix(f: TaskFacts, failures) -> str:
    return ("Fix the following gate/review failures. Keep changes minimal.\n\n"
            + "\n".join(f"- {x}" for x in failures))


def _is_signoff(summary: str) -> bool:
    s = summary.lower()
    return "lgtm" in s or "sign-off" in s or "signoff" in s or "no critical" in s


def _current_patch_text(f: TaskFacts, workspace: Workspace) -> str:
    # Prefer the actual worktree diff as ground truth over the agent's summary.
    return workspace.diff(f.worktree)


def _fail(f: TaskFacts, msg: str, progress: ProgressFn) -> TaskFacts:
    f.stage = Stage.FAILED.value
    f.is_terminated = True
    _note(f, msg)
    progress()
    return f


def _blocked(f: TaskFacts, msg: str, progress: ProgressFn) -> TaskFacts:
    f.stage = Stage.BLOCKED.value
    f.blocked_reason = msg
    _note(f, msg)
    progress()
    return f
