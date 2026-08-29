---
name: memory
description: Record and retrieve per-agent lessons and recurring patterns across runs. Use when an agent learns a non-obvious fact, finishes a run with a reusable takeaway, or needs to recall prior decisions/gotchas. Stores one-line entries in that agent's agents/<name>/memory.md and reads them back just-in-time (never dumps the whole file).
---

# Agent memory

Each agent keeps its own memory log at `agents/<name>/memory.md` (sections:
`## Sessions`, `## Lessons`, `## Recurring Patterns`). This restores the original
learning loop — keep entries compact so memory stays high-signal, not a context hog.

## Write (after a run / on a non-obvious learning)

Append ONE line to the relevant section of *your* `agents/<name>/memory.md`:

```
- [YYYY-MM-DD] <lesson or pattern in one line> (context: <task>; why it mattered)
```

Never paste diffs, transcripts, or code blocks into memory.

## Read (just-in-time)

Before planning/building/reviewing, pull only what's relevant from your own log:

```bash
grep -i "<keyword>" agents/<name>/memory.md
```

Do NOT load the whole file into context — retrieve selectively.
