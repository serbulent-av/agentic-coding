---
name: shell-scripting
description: Use when writing or reviewing bash or shell scripts.
---

# Shell Scripting

## Purpose
Write shell scripts that fail loudly, handle paths safely, and clean up after themselves — predictable instead of silently corrupting state.

## When to use
- Writing a new bash/shell script of any non-trivial length.
- Reviewing or hardening an existing script.
- Automating setup, CI, or glue tasks in shell.

When NOT to use: logic complex enough to need real data structures or error handling — reach for Python or another language instead.

## Method
1. Set strict mode. Start with `set -euo pipefail` so unset vars, failures, and broken pipes abort instead of continuing.
2. Quote every expansion. Wrap `"$var"` and `"$(cmd)"` to survive spaces, globs, and empty values.
3. Test with `[[ ]]`. Prefer `[[ ]]` over `[ ]` for safer, more capable conditionals.
4. Check before acting. Verify command existence with `command -v` and check exit codes; don't assume a step succeeded.
5. Factor into functions. Break logic into named functions with a clear `main`; avoid long top-level scripts.
6. Clean up with `trap`. Register a `trap` to remove temp files and release resources on exit or error.
7. Parse robustly. Never parse `ls`; use globs or `find`. Keep operations idempotent where possible.
8. Lint it. Run `shellcheck` and fix what it flags before shipping.

## Red flags
- No `set -euo pipefail` — errors pass silently.
- Unquoted `$var` that breaks on spaces or globs.
- Parsing `ls` output instead of globbing or `find`.
- Temp files left behind because there's no cleanup trap.
- One long unstructured script with no functions.
- Shipping without running shellcheck.

## Checklist
- [ ] `set -euo pipefail` at the top.
- [ ] All variable expansions quoted.
- [ ] `[[ ]]` used for tests.
- [ ] Command existence and exit codes checked.
- [ ] Logic factored into functions.
- [ ] `trap` cleans up temp files and resources.
- [ ] No `ls` parsing; script idempotent where possible.
- [ ] shellcheck run and clean.
