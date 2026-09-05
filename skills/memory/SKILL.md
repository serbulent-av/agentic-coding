---
name: memory
description: Shared team graph memory — record and recall lessons, patterns, gotchas, and decisions across runs. Use whenever you remember/forget something, learn a non-obvious lesson or pattern, hit a gotcha, make a decision worth keeping, or need to recall prior knowledge before acting. Source of truth is the append-only graph at memory/graph.jsonl, queried via memory/graph_memory.py.
---

# Agent memory (graph)

The source of truth is a single shared team graph at `memory/graph.jsonl` —
append-only text, an agent-anchored mind-map where every node hangs off the agent
who recorded it and edges link related lessons. All access goes through:

```bash
python3 memory/graph_memory.py <add|link|supersede|query|path|export> ...
```

The human-readable mirror `agents/<name>/memory.md` is **generated** (via `export`)
— never hand-edit it; write to the graph instead.

## Record (after a run / on a non-obvious learning)

```bash
python3 memory/graph_memory.py add "<lesson or pattern in one line>" --agent <name>
```

Link related lessons with `link`; when a lesson goes stale or is proven wrong,
`supersede` it (never delete — the graph is append-only). Keep entries compact —
one line, no diffs, transcripts, or code blocks.

## Recall (just-in-time, before acting)

```bash
python3 memory/graph_memory.py query "<task keywords>" --agent <name> --k 5
```

Top-K only — retrieve selectively, **never dump the whole graph**. Use `path` to
trace how two memories connect when you need the chain of reasoning.

## Mirror

Regenerate the human-readable view after recording:

```bash
python3 memory/graph_memory.py export
```
