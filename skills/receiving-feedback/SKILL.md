---
name: receiving-feedback
description: Use when receiving code-review feedback, before implementing suggestions, especially if feedback seems unclear or technically questionable.
---

# Receiving Feedback

## Purpose
Treat review feedback as suggestions to evaluate on technical merit, not orders to obey or attacks to defend against.

## When to use
- You received review comments and are about to act on them.
- A suggestion seems unclear, risky, or wrong for this codebase.
- Feedback spans multiple items and you need an order of attack.

When NOT to use: when the instruction is an unambiguous, correct fix from a trusted source — just make it. Skip the ceremony, keep the rigor.

## Method
1. Read it all first. Take in the complete feedback before reacting to any single point.
2. Restate each item. Put the requirement in your own words. If you can't, it's unclear — stop and ask before implementing anything (items may be related; partial understanding breeds wrong fixes).
3. Evaluate on merit. For each item ask: is this correct for THIS codebase? Does it break existing behavior? Is there a reason the current code is the way it is? Is the suggested feature even used (YAGNI)?
4. If right, fix it. Implement, then show the fix. No "you're absolutely right", no thanks — the corrected code is the acknowledgment.
5. If wrong, push back. Give technical reasoning and evidence (a test, a constraint, a `file:line`). Pushing back with proof is the job, not rudeness.
6. If you can't verify, say so. "I can't confirm this without X — investigate, ask, or proceed?" Don't implement on a guess.
7. One at a time. Fix, test, confirm no regression, then the next item. Close the loop on every item — none silently dropped.

## Red flags
- Performative agreement: "Great point!", "You're absolutely right!", "Thanks for catching that!"
- Implementing a questionable change without verifying it first.
- Reflexively defending your code instead of evaluating the point.
- Batch-applying all items with no test between them.
- Going quiet on items you disagree with instead of pushing back.
- Being wrong after pushback and writing a long apology — just state the correction and fix it.

## Checklist
- [ ] Whole feedback read before any action.
- [ ] Each item restated; unclear ones clarified before coding.
- [ ] Each item judged correct/incorrect for this codebase with a reason.
- [ ] Correct items fixed; incorrect items pushed back with evidence.
- [ ] No performative agreement or gratitude in the response.
- [ ] Items implemented one at a time, each tested.
- [ ] Every item resolved — fixed, rejected with reason, or flagged unverifiable.
