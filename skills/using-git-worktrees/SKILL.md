---
name: using-git-worktrees
description: Use when starting feature work that needs isolation, or running parallel or risky experiments without disturbing the main workspace.
---

# Using Git Worktrees

## Purpose
Give each branch, experiment, or parallel agent its own checked-out workspace, so risky or concurrent work never disturbs the shared working tree.

## When to use
- Starting feature work that should stay isolated from the current branch.
- Running risky or destructive experiments you may want to throw away.
- Multiple agents/tasks working in parallel — one worktree each.

**When NOT to use:** a quick edit on the current branch you intend to commit normally, or when the harness already placed you in an isolated workspace (detect first — don't nest).

## Method
1. **Detect existing isolation first.** Compare `git rev-parse --git-dir` with `--git-common-dir`; if they differ (and you're not in a submodule, per `git rev-parse --show-superproject-working-tree`), you're already in a worktree — use it, don't create another.
2. **Prefer native tooling.** If your platform/harness provides a worktree command or flag, use it — it manages placement and cleanup. Fall back to raw `git worktree` only when none exists.
3. **One worktree per branch/feature/agent.** Create it on its own branch:
   `git worktree add .worktrees/<branch> -b <branch>`
4. **Keep the worktree dir ignored.** For project-local dirs (e.g. `.worktrees/`), verify with `git check-ignore`; if not ignored, add to `.gitignore` and commit before creating. Prevents committing worktree contents.
5. **Set up and baseline.** Install deps and run the test suite so the new workspace starts green. Report pre-existing failures rather than masking them.
6. **Isolate the risk.** Run experiments here, not on the shared tree. If it goes wrong, the main workspace is untouched.
7. **Clean up after merge.** Once merged or abandoned: `git worktree remove <path>` and delete the branch. Don't leave stale worktrees behind.

## Red flags
- Creating a worktree when you're already inside one (skipped detection).
- Using raw `git worktree add` when a native tool exists ("fighting the harness").
- A worktree directory that isn't git-ignored (contents get tracked).
- Running risky/destructive experiments directly on the main working tree.
- Sharing one worktree across parallel agents.
- Leaving merged worktrees and dead branches lying around.

## Checklist
- [ ] Checked for existing isolation before creating anything.
- [ ] Used native tooling where available; git fallback only otherwise.
- [ ] One worktree per branch/feature/agent, on its own branch.
- [ ] Worktree directory verified git-ignored.
- [ ] Dependencies installed and baseline tests run.
- [ ] Risky work kept off the shared working tree.
- [ ] Worktree removed and branch cleaned up after merge.
