---
name: asking-clarifying-questions
description: Use when you need a decision, clarification, or approval from the user, and to decide when to instead proceed autonomously.
---

# Asking Clarifying Questions

## Purpose
Get the few decisions that genuinely need a human, while resolving everything else yourself — so the loop advances instead of stalling on questions you could answer.

## When to use
- A decision is genuinely ambiguous and you can't justify one option over another.
- The action is irreversible or high-blast-radius (deletes data, force-push, spends money).
- You need explicit approval before an external or destructive effect.

When NOT to use: the answer is discoverable from the code, docs, or context — investigate and decide rather than interrupting.

## Method
1. Decide if it's worth asking. Ask only when the choice is ambiguous or hard to reverse; if you can answer it yourself, do.
2. Present concrete options. Offer named choices with a short trade-off each, plus your recommendation — not an open-ended "what should I do?".
3. Batch related questions. Group decisions that belong together into one ask; keep unrelated concerns separate.
4. Proceed autonomously when no user is available. Pick the best-justified option, state your choice and reasoning, record the assumption, and continue.
5. Prefer safe defaults headless. Favor non-interactive, text-only, minimal-scope paths; treat an approval-only request as granted.
6. Never auto-approve destruction. Irreversible actions (deleting branches/data, force-push) stay gated; choose the non-destructive path and move on.

## Red flags
- Ending the turn with a prose question when the work could continue.
- Open-ended questions with no options and no recommendation.
- Asking what the code, docs, or context already answer.
- Bundling unrelated decisions into one confusing question.
- Stalling indefinitely because no user replied.
- Auto-approving a destructive, irreversible action.

## Checklist
- [ ] Question is genuinely ambiguous or high-blast-radius.
- [ ] Concrete options presented with a recommendation.
- [ ] Related questions batched; unrelated ones kept separate.
- [ ] With no user, best option chosen and the assumption recorded.
- [ ] Destructive actions never auto-approved.
- [ ] Loop continued rather than stalled on an answerable question.
