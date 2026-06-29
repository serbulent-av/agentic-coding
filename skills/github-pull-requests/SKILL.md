---
name: github-pull-requests
description: Use when creating, reviewing, or merging pull requests, especially via the gh CLI.
---

# GitHub Pull Requests

## Purpose
Move changes through review quickly and safely with small, well-described PRs and a clean, scriptable gh workflow.

## When to use
- Opening a pull request for a finished, focused change.
- Reviewing or merging someone else's PR.
- Automating PR steps with the `gh` CLI.

When NOT to use: work still in progress with no reviewable unit — keep it on a branch, or open a draft, until it stands on its own.

## Method
1. Keep it small and focused. One logical change per PR; split unrelated work so reviewers can actually reason about it.
2. Write a clear title and why-focused body. State what changed and, more importantly, why; link the issue it closes.
3. Get CI green first. Run `gh pr checks` and fix failures before requesting review — don't outsource red CI to a human.
4. Create with the CLI. `gh pr create` with title/body; setting reviewers and labels in the same command keeps it reproducible.
5. Review explicitly. Use `gh pr review` to approve or request changes; each comment names a location and a concrete ask.
6. Address every comment. Reply to or resolve each thread — fix it or say why not; never silently ignore feedback.
7. Keep history clean. Squash noise, write meaningful commit messages, and rebase tidily before merge.
8. Merge safely. `gh pr merge` only once checks pass and approvals are in; never force-push a branch others share.

## Red flags
- A giant PR mixing refactor, feature, and fixes.
- A title/description that says "what" but never "why", or no issue link.
- Requesting review while CI is red.
- Review comments left unanswered or quietly dismissed.
- Force-pushing a shared branch and rewriting others' history.
- Merging your own PR past failing checks.

## Checklist
- [ ] PR is small and scoped to one logical change.
- [ ] Title and why-focused description written; issue linked.
- [ ] CI green (`gh pr checks`) before review requested.
- [ ] Created/reviewed/merged via `gh` commands.
- [ ] Every review comment addressed explicitly.
- [ ] Commit history clean and meaningful.
- [ ] No force-push to a shared branch.
