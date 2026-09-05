# Graphify integration

Graphify turns this repo (code, docs) into a queryable knowledge graph so agents
answer architecture/relationship questions by **querying the graph** instead of
grepping or reading whole files (smaller, higher-signal context).

## What's installed

- CLI: `graphify` (installed via `uv tool install graphifyy`).
- Skill: `skills/graphify/SKILL.md` — tool-agnostic Agent Skills format, shared
  across tools (opencode loads it via `"skills": {"paths": ["skills"]}`; the same
  `skills/` folder is readable by other Agent-Skills-compatible tools).
- Index: `graphify-out/graph.json` (+ `GRAPH_REPORT.md`, `graph.html`).

## Bash-callable usage (works in any shell-driven agent)

```bash
graphify query "how does orch dispatch teams?"   # scoped subgraph
graphify god-nodes --top 10                       # architectural hubs
graphify explain "orch"                           # one node + its neighbors
graphify path "orch" "patek"                       # shortest path between two nodes
```

The index is local and deterministic (tree-sitter AST for code — no API key needed
with `--code-only`). Every edge is tagged `EXTRACTED` (read from source) or
`INFERRED` (resolved), so you can tell fact from inference.

## Keep it fresh

```bash
graphify update .            # re-extract changed code files (no LLM)
graphify cluster-only .      # regenerate GRAPH_REPORT.md + graph.html
```

The `orch` agent invokes the `graphify` skill to (re)index a repo before dispatching
a team, so agents never query a stale graph. Note: `graphify update` refuses to
shrink the graph; after deleting code, rebuild with `graphify extract . --code-only
--force` (or `graphify update . --force`) so removed symbols drop out.

## Optional: serve over MCP/HTTP

```bash
python -m graphify.serve graphify-out/graph.json --transport http --port 8080 \
    --api-key "$SECRET"
```

gives tools `query_graph`, `get_node`, `get_neighbors`, `shortest_path`, etc.
Useful if you later want a shared graph endpoint for a fleet. Not required for the
default bash path.

## Git

`graph.json` and `GRAPH_REPORT.md` are committed; volatile artifacts
(`cache/`, `cost.json`, `.graphify_python`, `memory/`, `reflections/`) are
gitignored. `benchmarks/agentic-runs/` is excluded via `.graphifyignore`.
