# Graph-based memory

Design for the team's shared, agent-anchored memory graph. This document is the
specification; it contains the exact schema and an interface contract an
implementer can code to without guessing.

## Goal

Give every agent a persistent, structured memory (lessons, decisions, patterns,
gotchas) that is:

- **Committed and merge-friendly** — plain text, git-diffable, no binary DB.
- **Queryable** — keyword + graph-proximity retrieval, not whole-file dumps.
- **Concurrency-safe** — multiple parallel teammates append to it at once.
- **Self-maintaining** — old facts are superseded, not deleted, and drop out of
  retrieval by default.

## Why text source + in-memory SQLite

- **Source of truth:** one append-only text file, `memory/graph.jsonl`, one JSON
  record per line. JSONL is line-oriented, so git diffs/merges operate on whole
  records; concurrent appends almost never touch the same line region.
- **Query engine:** stdlib SQLite (`sqlite3`, built-in `json1`) loaded
  **in-memory** from the JSONL on every invocation. Nothing is persisted as a
  binary DB, so the JSONL is never out of sync with the engine — the file *is*
  the database. Load cost is trivial at team scale (thousands of records).

## Model

Agent-anchored mind-map. Every memory node belongs to exactly one agent hub.

- **Hub nodes:** `type:"agent"` — one per team member, seeded.
- **Memory nodes:** `type` ∈ {`lesson`, `decision`, `pattern`, `gotcha`},
  attached to their owner hub with a `knows` edge.
- **Edges** relate memories to each other and to hubs.

### Seeded agent hubs (6)

`orch`, `gerald`, `lange`, `patek`, `philipe`, `sohne` — each seeded as:

```json
{"kind":"node","id":"agent:orch","type":"agent","agent":"orch","text":"orch hub","props":{},"ts":"..."}
```

(…and likewise for the other five; hub id is always `agent:<name>`.)

### Relation vocabulary (edge `rel` values)

| rel            | src → dst        | meaning                                                        |
| -------------- | ---------------- | -------------------------------------------------------------- |
| `knows`        | hub → memory     | this memory belongs to this agent (created automatically by `add`) |
| `applies_to`   | memory → memory  | this memory is relevant in the context of the target           |
| `related_to`   | memory ↔ memory  | loose association (traversed both directions)                  |
| `contradicts`  | memory → memory  | the two memories conflict; retrieval surfaces both             |
| `supersedes`   | new node → old node | new node replaces old node (see supersede, below)           |

### Supersede (self-pruning)

Never delete or edit a record. To replace a memory, append the new node plus a
marker record: an edge with `rel:"supersedes"`, `src` = new node id, `dst` =
old node id. The old node stays in the file (full history, auditable in git)
but is **excluded from all default retrieval**. `--all` includes it.

## Record schema (exact)

Two record shapes, distinguished by `kind`. One record per line, UTF-8, compact
JSON (no embedded newlines).

**Node:**

```json
{"kind":"node","id":"lange:a3f9","type":"lesson","agent":"lange","text":"...","props":{"tags":["git"]},"ts":"2026-08-31T12:00:00Z"}
```

| field   | type   | required | notes                                                                 |
| ------- | ------ | -------- | --------------------------------------------------------------------- |
| `kind`  | string | yes      | always `"node"`                                                        |
| `id`    | string | yes      | unique; format `<agent>:<slug>` (hub ids are `agent:<name>`)           |
| `type`  | string | yes      | one of `agent`, `lesson`, `decision`, `pattern`, `gotcha`              |
| `agent` | string | yes      | owning agent name; equals hub name even for hubs                       |
| `text`  | string | yes      | the memory content; for hubs a short label (e.g. `"lange hub"`)        |
| `props` | object | yes      | free-form metadata, `{}` if none; conventional key: `tags` (string[])  |
| `ts`    | string | yes      | ISO-8601 UTC, e.g. `2026-08-31T12:00:00Z`                              |

**Edge** (also used for supersede markers):

```json
{"kind":"edge","src":"agent:lange","dst":"lange:a3f9","rel":"knows","props":{},"ts":"2026-08-31T12:00:00Z"}
```

| field   | type   | required | notes                                                        |
| ------- | ------ | -------- | ------------------------------------------------------------ |
| `kind`  | string | yes      | always `"edge"`                                              |
| `src`   | string | yes      | id of source node (must exist as a node record)              |
| `dst`   | string | yes      | id of destination node                                       |
| `rel`   | string | yes      | one of `knows`, `applies_to`, `related_to`, `contradicts`, `supersedes` |
| `props` | object | yes      | free-form metadata, `{}` if none                             |
| `ts`    | string | yes      | ISO-8601 UTC                                                 |

A **supersede marker** is exactly an edge record with `rel:"supersedes"`.

## Interface contract

Executable name: `mem`. All commands read the JSONL, load it into an in-memory
SQLite DB (tables `nodes` and `edges` with the fields above), run the query, and
exit. Writes (`add`, `link`, `supersede`) append to the file under the lock
described below. All commands print JSON to stdout; `--pretty` for humans.

### CLI command surface

```
mem add --agent <name> --type <lesson|decision|pattern|gotcha> \
        --text "<text>" [--tags t1,t2] [--props '<json>']
```
Appends a node record plus a `knows` edge from `agent:<name>`. Prints the new
node id. Id is `<agent>:<4-char-hex>` from a hash of (text, ts, pid).

```
mem link --src <id> --dst <id> --rel <applies_to|related_to|contradicts> \
         [--props '<json>']
```
Appends one edge record. Errors if either id does not exist or the rel is
`knows`/`supersedes` (those are reserved for `add`/`supersede`).

```
mem supersede --old <id> --agent <name> --type <type> --text "<text>" \
              [--tags t1,t2] [--props '<json>']
```
Appends the new node (+ its `knows` edge) and a `supersedes` edge
`src=<new id> dst=<old id>`, atomically under one lock hold. Prints the new id.

```
mem query --agent <name> --keywords "<kw1 kw2 ...>" [--k 5] [--all]
```
Top-K just-in-time retrieval. **Never dumps the whole graph.** Scoring, in
order:
1. Candidate set: nodes owned by `--agent` whose `text` LIKE-matches any
   keyword (case-insensitive, `%kw%`), **excluding superseded nodes** (any node
   that is the `dst` of a `supersedes` edge) unless `--all`.
2. Graph proximity: rank candidates by edge distance from the agent's hub
   (all hub memories are 1 hop via `knows`); ties broken by `ts` descending.
3. Also pull each hit's 1-hop neighbors along `applies_to`, `related_to`, and
   `contradicts` (both directions for `related_to`) as `context`, not scored.
4. Truncate to `k` hits (default 5, hard cap 25).

Output shape:
```json
{"hits":[{"id","type","agent","text","props","ts","distance":1,
          "context":[{"id","rel","text"}]}]}
```

```
mem path --from <id> --to <id>
```
BFS shortest path over all edges (undirected traversal, excluding `supersedes`
dst nodes from intermediate hops unless they are an endpoint). Output:
```json
{"path":[{"id","text"}, ...], "hops": 2}
```
or `{"path":[], "hops": -1}` when unreachable.

```
mem export [--agent <name>] [--dir agents]
```
Mirror (see below). Without `--agent`, exports all six agents.

### Concurrency model

- Appends open `memory/graph.jsonl` with `O_WRONLY|O_CREAT|O_APPEND` and hold an
  `fcntl.flock(LOCK_EX)` on the file descriptor for the duration of the write.
- `O_APPEND` + a single `write()` per record keeps each line atomic on POSIX —
  safe for parallel teammates sharing the working directory.
- `supersede` writes all its records (node, `knows` edge, `supersedes` edge)
  under one lock hold, so the marker can never be separated from its node.
- Readers take no lock: they read a consistent-enough snapshot (a torn trailing
  line, if ever observed, is skipped on parse with a warning to stderr).
- After appending, the process unlocks and exits; the in-memory DB is per-process.

### Mirror

`agents/<name>/memory.md` is **generated — do not edit**. `mem export`
regenerates it from that agent's subgraph: the hub plus all nodes reachable via
its `knows` edges, minus superseded nodes, grouped by `type`
(lessons / decisions / patterns / gotchas), newest first, each entry prefixed
with its id and `ts`, and each entry's non-supersede 1-hop relations listed
under it. The file begins with the header line:

```
<!-- generated by mem export — do not edit; source of truth is memory/graph.jsonl -->
```

`memory/graph.jsonl` is the only writable source. Hand edits to a mirrored
`memory.md` are destroyed by the next `export`.

## Management & optimization

- **Indexing:** the in-memory DB creates indexes on `nodes(agent)`,
  `nodes(type)`, `edges(src, rel)`, `edges(dst, rel)` at load time. LIKE
  keyword search scans only the querying agent's own rows, so cost stays flat
  as the graph grows. No FTS5 dependency — stdlib `json1` + LIKE is enough at
  this scale; revisit FTS if a single agent exceeds ~10k live nodes.
- **Top-K bounding:** retrieval is capped (`k` ≤ 25, 1-hop context only) so a
  query returns a small just-in-time slice; there is deliberately no
  "dump graph" command — use `git log`/`grep` on the JSONL for archaeology.
- **Supersede self-prune:** because superseded nodes are filtered by default,
  the live working set shrinks naturally without deletion; the file grows
  append-only but the *retrieved* context does not. The JSONL remains the
  complete audit trail.
- **Housekeeping (optional, manual):** if the file ever becomes unwieldy, a
  future `mem compact` may rewrite it dropping superseded nodes — out of scope
  for this design; appends and git history suffice for now.
