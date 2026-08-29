---
name: memory
description: Record and retrieve team lessons and recurring patterns across runs. Use when an agent learns a non-obvious fact, a run finishes with a reusable takeaway, or when recalling prior decisions/gotchas for this repo. Stores entries in MEMORY.md and reads them back just-in-time (never dumps the whole file into context).
---

# Team memory

A single shared, append-only log that replaces the per-agent `memory.md` stubs.

## File

`MEMORY.md` at the repo root, in three sections: `## Sessions`, `## Lessons`,
`## Recurring patterns`.

## Write (after a run / on a non-obvious learning)

Append ONE compact entry — a fact, not a transcript:

```
- [2026-08-29] <lesson or pattern in one line> (context: <task/team>; why it mattered)
```

Keep entries to a single line each. Never paste diffs, transcripts, or code blocks.

## Read (just-in-time)

Before planning or reviewing, pull only what's relevant:

```bash
grep -i "<keyword>" MEMORY.md
```

Do NOT load the whole file into context — retrieve selectively. This keeps memory
useful without becoming a context hog.
