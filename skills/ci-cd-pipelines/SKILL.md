---
name: ci-cd-pipelines
description: Use when designing or fixing CI/CD pipelines such as GitHub Actions.
---

# CI/CD Pipelines

## Purpose
Give every change fast, trustworthy automated feedback and a safe, reproducible path to deploy.

## When to use
- Designing a new CI/CD pipeline or workflow.
- Fixing flaky, slow, or insecure pipeline steps.
- Adding a deploy stage gated on tests.

When NOT to use: a throwaway spike or scratch repo where automation costs more than it returns — add CI once the work is meant to last.

## Method
1. Test on every push. Run lint, tests, and build on each push and PR so feedback arrives in minutes, not at release.
2. Fail fast. Order cheap, high-signal checks first and stop on first failure; don't burn minutes after a known break.
3. Cache dependencies. Cache package downloads and build output keyed on lockfiles to keep runs quick.
4. Pin versions. Pin third-party actions to a full commit SHA (a tag like `@v4` is mutable and can be moved upstream; only a SHA is immutable) and pin tool versions, so a run is reproducible and not silently mutated.
5. Pull secrets from the store. Reference the CI secret store; never hard-code tokens or echo them into logs.
6. Aim for reproducible builds. Same commit in, same artifact out — no dependence on machine state or wall-clock.
7. Gate deploys on green. Promote or deploy only after the full pipeline passes; a red pipeline blocks release.
8. Keep pipeline-as-code in the repo. Version the workflow next to the code it builds; review changes to it like any other.

## Red flags
- Tests that run only nightly or only before release.
- Secrets pasted into workflow YAML or printed in logs.
- Unpinned `@latest` actions or floating tool versions.
- No dependency caching, so every run reinstalls from scratch.
- Deploys that proceed despite failing checks.
- Pipeline config edited only in the CI UI, not in the repo.

## Checklist
- [ ] Lint/test/build run on every push and PR.
- [ ] Cheapest checks first; run fails fast.
- [ ] Dependencies cached on lockfile keys.
- [ ] Third-party actions pinned by commit SHA; tool versions pinned.
- [ ] Secrets sourced from the CI store, never logged.
- [ ] Builds reproducible from the commit alone.
- [ ] Deploys gated on a green pipeline; config lives in the repo.
