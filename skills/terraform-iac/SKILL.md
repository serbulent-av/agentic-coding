---
name: terraform-iac
description: Use when writing or reviewing infrastructure-as-code with Terraform.
---

# Terraform IaC

## Purpose
Manage infrastructure as reviewable, version-controlled code with predictable plans and a small blast radius per change.

## When to use
- Writing or editing Terraform configuration.
- Reviewing a plan or module before apply.
- Refactoring infra into reusable modules.

When NOT to use: one-off exploration in a throwaway sandbox — but anything others depend on belongs in code, not the console.

## Method
1. Plan before apply. Always run `terraform plan`, read the diff, and confirm it matches intent before `apply` touches anything.
2. Use remote state with locking. Store state in a shared backend with locking so teammates and CI don't corrupt or race it.
3. Never change managed infra by hand. Console edits cause drift; change the code and apply, so state stays the source of truth.
4. Pin versions. Constrain provider and module versions so plans are reproducible and upgrades are deliberate.
5. Factor reusable modules. Extract repeated infra into modules with clear inputs/outputs instead of copy-pasting blocks.
6. Keep secrets out of code and state. Source them from a vault/secret store; never commit them — and remember state can hold them too.
7. Make small blast-radius changes. Apply focused changes and scrutinize the plan for unexpected replace/destroy before proceeding.
8. Run fmt and validate. `terraform fmt` and `terraform validate` (plus lint) before commit, and again in CI as a gate.

## Red flags
- Running `apply` without reading the plan.
- Local state, or remote state without locking.
- Hand-editing resources in the cloud console (drift).
- Unpinned providers/modules drifting on every run.
- Secrets hard-coded in `.tf` files or committed state.
- A plan showing surprise destroy/replace, applied anyway.

## Checklist
- [ ] `plan` reviewed and matches intent before `apply`.
- [ ] Remote state backend with locking configured.
- [ ] Provider and module versions pinned.
- [ ] Repeated infra factored into modules.
- [ ] No secrets in code or committed state.
- [ ] Changes kept small; destroy/replace lines scrutinized.
- [ ] `fmt` and `validate` run before commit / in CI.
