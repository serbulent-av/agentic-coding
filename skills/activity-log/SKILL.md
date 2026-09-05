---
name: activity-log
description: Log orchestration events for auditability. Use when the orchestrator/team lead records delegations, deliveries, review findings, resolutions, plan changes, and sign-offs during a run. Append compact one-line events; log events, not reasoning.
---

# Activity log

The run's audit trail. Append one line per meaningful event to `ACTIVITY.md` (repo
root). Keep it about **events**, not internal reasoning.

## Entry

```
- [ISO-8601] <phase> | <agent> | <action> | in:<brief> -> out:<brief> | <status>
```

status ∈ success | needs-revision | blocked | escalated.

## Log
every delegation, delivery, review finding, resolution, plan change, sign-off,
blocker + unblock.

## Don't log
internal reasoning that led nowhere, or duplicates (reference the prior entry).

The log feeds accountability, cross-agent context, and the `memory` skill's
post-run lessons.
