---
name: delivering-work
description: Use when implementation is complete and verified and the work needs to be integrated or handed back.
---

# Delivering Work

## Purpose
Close out finished, verified work cleanly: report what changed, let the human choose how to integrate it, and leave the workspace tidy.

## When to use
- Implementation is done and verified (tests pass with real evidence).
- The change is ready to merge, PR, or hand back to the requester.
- Multiple iterations need consolidating into one final summary.

When NOT to use: work is unverified or tests fail (finish verification-before-done first), or the change is a trivial tweak not worth a formal handoff.

## Method
1. Re-confirm verification. Tests/build pass on the final state with fresh evidence. If anything fails, stop and fix — do not deliver broken work.
2. Summarize what changed and why. Describe the final shipped state (what it does now), not the trial-and-error journey. Self-contained: the reader shouldn't need the spec to understand it. Code is truth — describe what the code does.
3. Present completion options; never auto-commit. Offer a small structured menu — merge locally / open a PR / keep as-is — and let the human pick. Committing or pushing without being asked is off-limits.
4. Execute the chosen path only. Merge or PR exactly what was selected. For anything destructive (discarding work, force operations), get explicit confirmation first.
5. Clean up artifacts. Remove temp files, scratch branches, debug logs, and throwaway scaffolding you created. Don't remove workspaces/worktrees you didn't create.
6. Surface limitations and follow-ups. State known gaps, untested edges, and sensible next steps as a short list — honest, not buried.
7. Deliver one concise final report. Consolidate the above into a single, proportional summary (scale length to complexity; never longer than the work warranted).

## Red flags
- Auto-committing, pushing, or opening a PR without being asked.
- "What was tried" narrative instead of the final delivered state.
- Reporting completion while a test or build is red.
- Deleting work or force-operating without explicit confirmation.
- Leaving temp files, debug output, or dead scaffolding behind.
- Hiding known limitations to make the handoff look cleaner.
- A report longer than the change deserves.

## Checklist
- [ ] Final state verified with fresh evidence.
- [ ] Summary describes what shipped and why, self-contained.
- [ ] Completion options presented; nothing committed without consent.
- [ ] Chosen path executed; destructive actions confirmed first.
- [ ] Temp artifacts cleaned; foreign workspaces left intact.
- [ ] Known limitations and follow-ups stated plainly.
- [ ] One concise final report, proportional to the work.
