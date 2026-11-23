# Root cause: conductor agents don't fan out the team

Why patek/orch did task work themselves instead of delegating, and what was
changed to fix it.

## Symptom

Conductor agents (`patek` / `orch`) execute task work directly — running shell
commands, making ops decisions, editing-verifying loops — and never fan out the
role team (lange → philipe → sohne/gerald). The "agentic team" degenerates into
a single agent with a fancy prompt.

## Evidence

- Session `2026-11-23T16-10-03` (patek, GCP/APBS task): 23 self-executed
  `bash` toolCalls (46 messages counting call+result pairs) — gcloud/APBS
  commands run by patek itself, ops decisions made on its own. The first and
  only sub-agent spawn (a single `Agent` call to philipe, plus a
  get_subagent_result) came near the end, after the conductor had already
  done the work itself — which strengthens, not weakens, the thesis.
- Other session transcripts show nested delegation works fine when used: patek
  spawned `lange`, `philipe`, `sohne`, and `gerald` as expected. So the failure
  is behavioral (tool-enabled shortcut), not infrastructural.

## Mechanism (why the plugin is not the problem)

- `~/.pi/agent/subagents.json` grants nested Agent tools via
  `allowed_subagents` + `maxSubagentDepth: 3` — patek may spawn lange/philipe/
  sohne/gerald/breguet, orch may spawn patek.
- The pi-subagents extension (0.26.2) re-admits nested Agent tools regardless of
  the `tools:` list in an agent's frontmatter (verified in `agent-runner.js`).
  Removing `bash` from `tools:` does NOT remove the `Agent` tool.
- Conclusion: the plugin is fine; do not replace or work around it.

## Root cause

- Both conductors had `bash` in their `tools:` list. With a full shell
  available, the model takes the shortcut of doing the task itself — running
  commands is immediately gratifying, delegation feels like overhead.
- The single-patek design compounds this: one conductor holding a shell means
  the team never *visibly* fans out; the role pipeline exists only on paper.
- Supporting duties written into the personas (memory query/add, activity log
  appended via bash, patek-run verification, orch-run graphify indexing)
  presupposed shell access and reinforced the do-it-yourself pattern.

## Fix

1. **Removed `bash` from the frontmatter** of `~/.pi/agent/agents/patek.md` and
   `~/.pi/agent/agents/orch.md` (`tools: read, grep, find, ls`). Execution is
   now impossible without delegation — every command must go through Philipe
   (changes/commands) or Sohne/Gerald (read-only verification). The Agent tool
   remains available via the extension's nested-tool re-admission.
2. **Rewrote shell-dependent duties**:
   - *Memory*: fully dispatcher-owned — the dispatcher embeds graph-memory hits
     in briefs at dispatch and records lessons at close-out; patek/orch never
     query or add.
   - *Activity log (patek)*: kept only as a compact structured section in
     patek's final message; the "appended via bash" file option is gone.
   - *Verification*: patek never runs test/verification commands; Philipe runs
     them during implementation, Sohne/Gerald run read-only verification and
     report outcomes.
   - *Graphify (orch)*: graphify-first kept as a delegation duty — indexing/
     querying is done by the dispatcher or a team's Philipe; orch never runs
     it. Hard rule 2 and startup step 2 rephrased accordingly.
   - Both personas open their runtime rules with an explicit "You have NO
     shell — delegate every command" rule.
3. **AGENTS.md** now prefers the deterministic `team-pipeline` SubagentWorkflow
   (`~/.pi/agent/workflows/team-pipeline.js`, args `{task, files, verify?}`)
   when the user asks to "run as an agentic team", falling back to ad-hoc
   patek dispatch; it also states explicitly that the pi-subagents plugin is
   not the problem.
