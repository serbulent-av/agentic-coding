---
name: verification-before-done
description: Use before claiming any work complete, fixed, or passing, and before committing or handing off.
---

# Verification Before Done

## Purpose
Replace confidence with evidence. A claim of "done", "fixed", or "passing" is only honest if a command you just ran proves it.

## When to use
- Before any statement of completion, success, or satisfaction.
- Before committing, pushing, opening a PR, or handing off.
- Before marking a task done or moving to the next one.
- After a subagent or teammate reports success — verify independently.

When NOT to use: never skip it. There is no "just this once". Mid-exploration with no claim being made is the only time it doesn't apply.

## Method
1. Identify the proof. For each claim, name the exact command/test that would confirm or refute it.
2. Run it fresh and in full. Not a partial run, not a remembered result from earlier — execute it now.
3. Read the real output. Check the exit code, count failures, scan for warnings. Paste the actual output, don't paraphrase it.
4. Check criteria one by one. Walk the acceptance list line by line; tests passing is not the same as requirements met.
5. State the result with evidence. "34/34 pass" with the output beats "should pass". If it failed, report the actual state.
6. Declare the gaps. Explicitly say what you did NOT verify (untested paths, skipped platforms, manual steps not run). Silence implies coverage you don't have.

## Red flags
- The words "should work", "probably", "seems to", "looks correct".
- Celebrating ("Done!", "Perfect!") before the command has run.
- Committing or handing off without a fresh run in this session.
- Trusting an agent's "success" report without checking the diff/output.
- Extrapolating from a partial check to the whole.
- "I'm confident" or "I'm tired" standing in for actual evidence.

## Checklist
- [ ] Every completion claim maps to a command that was just run.
- [ ] Full command executed fresh; exit code and failure count read.
- [ ] Real output shown, not summarized from memory.
- [ ] Each acceptance criterion checked explicitly, line by line.
- [ ] What was NOT verified is stated plainly.
- [ ] No "should"/"probably" language anywhere in the claim.
