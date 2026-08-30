---
name: api-design
description: Use when defining an interface, function signature, schema, or contract, before implementing the internals.
---

# API Design

## Purpose
Shape the contract a caller depends on — names, types, errors — before writing the internals behind it.

## When to use
- Defining a function or method signature, public class, or module boundary.
- Designing a request/response schema, config format, or data contract.
- Any interface others will call before you build what sits behind it.

When NOT to use: purely internal one-off code with a single caller and no boundary — just write it. Behavior-preserving cleanup of an existing contract is refactoring, not design.

## Method
1. Contract first. Specify inputs, outputs, and errors before any implementation.
2. Design for the caller. Optimize the call site, not what is easy to implement.
3. Match conventions. Follow existing naming, argument order, and error style in the codebase.
4. Minimize surface area. Expose only what callers need; keep the rest private.
5. Name to reveal intent. The call site should read clearly without docs.
6. Make errors explicit. Use typed, named failures — never null, -1, or magic strings.
7. Plan compatibility. Version it or design to extend without breaking callers.

## Red flags
- Shaping the interface around what's easy to implement instead of caller need.
- Boolean/flag parameters that fan out behavior — split into separate functions.
- Leaking internal types, storage shapes, or implementation details across the boundary.
- Vague names at the boundary (`data`, `info`, `handle`, `process`).
- Failure signaled by null, -1, or magic strings instead of typed errors.
- Breaking an existing public contract with no version or deprecation path.

## Checklist
- [ ] Contract defined before internals.
- [ ] Names read clearly at the call site.
- [ ] Surface area is the minimum that satisfies callers.
- [ ] Errors are explicit and typed.
- [ ] Consistent with existing codebase conventions.
- [ ] Backward compatibility / versioning considered.
