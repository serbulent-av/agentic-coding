---
name: security-review
description: Use when reviewing code that handles untrusted input, authentication, secrets, or external dependencies.
---

# Security Review

## Purpose
Find exploitable weaknesses in code that touches untrusted input, identity, secrets, or third-party code — before an attacker does.

## When to use
- The change parses, stores, or reflects user/network input.
- It touches authentication, authorization, sessions, or access control.
- It handles secrets, tokens, keys, or credentials.
- It adds or upgrades external dependencies.

When NOT to use: pure internal refactors with no trust-boundary, input, or dependency change. Don't manufacture theoretical risk where no untrusted data flows.

## Method
1. Map the trust boundaries. Trace where untrusted data enters and where it reaches a query, shell, filesystem, or rendered output.
2. Injection. At every input→sink meeting point check for SQL, command, path, and XSS injection. Demand parameterized queries, safe APIs, and output encoding — never string concatenation into a sink.
3. Authn/authz. For each protected action ask: can an unauthenticated caller reach it? Can one user read or mutate another user's data (IDOR)? Verify the check is server-side and on every path, not just the UI.
4. Secrets. Look for hard-coded keys/passwords, secrets in logs, secrets echoed in error responses or stack traces, and tokens with no expiry. Secrets belong in config/secret stores, never in source or output.
5. Dependencies. Check new/updated packages for known CVEs, unpinned or typo-squatted names, and excessive transitive trust. Pin versions; prefer maintained sources.
6. Least privilege. Confirm the code requests the narrowest scope, role, file permission, and network access it needs — nothing broader "just in case".
7. Report. For each finding give location, severity, the realistic attack, and a concrete fix. Separate practical (reachable) risk from theoretical.

## Red flags
- Raw input concatenated into SQL, shell, HTML, or a file path.
- Authorization enforced only client-side or assumed from prior steps.
- Secrets in source, logs, error messages, or committed config.
- `eval`, deserialization of untrusted data, or disabled TLS/cert checks.
- Unpinned, abandoned, or unfamiliar dependencies pulled in.
- Broad wildcard permissions, admin tokens, or world-writable files.

## Checklist
- [ ] Every untrusted input traced to its sink and checked for injection.
- [ ] Authentication and per-user authorization verified server-side on each path.
- [ ] No hard-coded, logged, or error-leaked secrets.
- [ ] New/updated dependencies checked for CVEs and pinned.
- [ ] Privileges, scopes, and permissions are the minimum required.
- [ ] Each finding has location, severity, and a concrete fix.
- [ ] Practical risk distinguished from theoretical.
