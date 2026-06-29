---
name: brainstorming
description: Use before any creative or feature work when the request is vague or the solution space is open; explores intent, requirements, and design before planning or code.
---

# Brainstorming

## Purpose
Turn a vague idea into a clear, agreed design. Separate *what problem we're solving* from *how we'll solve it* before any plan or code exists.

## When to use
- The request is open-ended ("add search", "make it faster") or the solution space is wide.
- Requirements, constraints, or success criteria are unstated or assumed.
- A change touches architecture or has several plausible designs.

**When NOT to use:** a fully-specified bug fix, a trivial or mechanical change, or work where the approach is already agreed — go straight to planning.

## Method
1. **Frame the problem, not a solution.** State the user goal, constraints, and what "done" looks like — in problem terms. Resist naming a solution yet.
2. **Explore context.** Read relevant files, docs, and recent commits. Follow existing patterns; note real constraints.
3. **Ask clarifying questions one at a time.** Target purpose, constraints, and success criteria. Prefer concrete options over open prompts. If no user is available, state your assumptions explicitly and proceed.
4. **Surface ≥3 options.** For each: how it works, tradeoffs, cost, risk. Lead with a recommendation and say why.
5. **Test assumptions.** Name what must be true for the favored option to work; validate the riskiest ones (probe the code, run a spike, ask).
6. **Converge on one approach with rationale.** Apply YAGNI — cut anything not serving the goal. Record why the others lost.
7. **Hand off.** Output the chosen approach, rejected alternatives (one line each), and open questions. That feeds planning.

## Red flags
- Jumping to a solution before the problem is stated.
- Presenting one option (no real alternatives considered).
- "Too simple to need a design" — that's where hidden assumptions bite.
- Asking five questions at once, or asking what the code already answers.
- Smuggling in scope the goal doesn't require (gold-plating).
- Ending with no clear decision or no recorded rationale.

## Checklist
- [ ] Problem stated independently of any solution.
- [ ] Project context explored (files/docs/commits).
- [ ] ≥3 options surfaced with explicit tradeoffs.
- [ ] Riskiest assumptions named and validated.
- [ ] One approach chosen, with rationale recorded.
- [ ] Rejected alternatives and open questions written down.
- [ ] Output ready to hand to planning (no code written yet).
