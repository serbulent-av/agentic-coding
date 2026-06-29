---
name: observability-logging
description: Use when adding logging, metrics, or tracing to code or services.
---

# Observability and Logging

## Purpose
Make a running system explainable — so when something breaks, the logs, metrics, and traces already hold what you need to diagnose it.

## When to use
- Adding or changing logging, metrics, or tracing in code or a service.
- Instrumenting a new endpoint, job, or integration.
- Reviewing whether a failure would be diagnosable from telemetry alone.

When NOT to use: a throwaway script or one-off where no one will read the output. Don't drown the signal by logging every line of normal flow.

## Method
1. Emit structured logs. Log key-value or JSON fields, not interpolated prose, so logs are queryable and machine-parsable.
2. Log at boundaries and on errors. Record requests, external calls, and failures with enough context (ids, inputs, outcome) to reconstruct what happened.
3. Never log secrets or PII. Keep tokens, passwords, keys, and personal data out of logs; redact before emitting.
4. Use meaningful levels. ERROR is an actionable failure, WARN is recoverable, INFO is milestones, DEBUG is detail — don't make everything INFO.
5. Propagate correlation IDs. Carry a request/trace id across services so one operation can be followed end to end.
6. Track the golden signals. Measure latency, traffic, errors, and saturation for each service.
7. Make failures self-diagnosable. Ensure an error log alone — without reproducing — tells you what failed, where, and with what inputs.

## Red flags
- Unstructured string logs you can't filter or aggregate.
- Secrets, tokens, or PII written to logs.
- Everything logged at one level, so nothing stands out.
- An error logged with no context — no id, no cause, no inputs.
- A trace/correlation id dropped at a service hop, breaking the chain.
- Noisy per-iteration logging that buries the signal.

## Checklist
- [ ] Logs are structured and queryable.
- [ ] Boundaries and errors logged with enough context to diagnose.
- [ ] No secrets or PII in any log.
- [ ] Log levels are meaningful and used consistently.
- [ ] Correlation/trace ids propagate across services.
- [ ] Golden signals (latency, traffic, errors, saturation) tracked.
- [ ] A failure can be understood from telemetry alone.
