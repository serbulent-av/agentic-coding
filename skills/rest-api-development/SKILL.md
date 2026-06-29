---
name: rest-api-development
description: Use when building or reviewing REST/HTTP APIs.
---

# REST API Development

## Purpose
Build HTTP APIs that follow REST conventions so clients can predict behavior from the URL, verb, and status code alone.

## When to use
- Adding or changing an HTTP endpoint, route, or resource.
- Reviewing a REST API for correctness and consistency.
- Designing how clients page, authenticate, or handle errors over HTTP.

When NOT to use: shaping the underlying data contract or function signature — that's api-design. Internal RPC or non-HTTP transports follow their own conventions.

## Method
1. Model resources, not actions. Use noun URLs (/orders/42/items) and let HTTP verbs carry the action; keep verbs out of paths.
2. Use verbs by their semantics. GET reads, POST creates, PUT/PATCH update, DELETE removes; keep GET/PUT/DELETE idempotent.
3. Return accurate status codes. 2xx success, 4xx client error, 5xx server error — never 200 wrapping an error.
4. Use one error shape. Every error returns the same JSON structure (code, message, detail) so clients parse one format.
5. Validate at the boundary. Reject malformed or unauthorized requests before any business logic; return 400/422 with specifics.
6. Protect every route. Authenticate and authorize on the server for each endpoint; deny by default.
7. Paginate collections. Never return an unbounded list; use limit/offset or cursors and include paging metadata.
8. Version the API. Put the version in the URL or header so changes don't break existing clients.
9. Document the contract. Keep request/response/error examples current next to the code (OpenAPI or equivalent).

## Red flags
- Verbs in the URL (/getUser, /createOrder) instead of resource nouns.
- 200 OK carrying an error, or a 500 for what is really bad client input.
- A different error format per endpoint.
- Endpoints returning whole tables with no pagination.
- Trusting client-supplied input or auth state without server validation.
- Breaking response changes shipped with no version bump.

## Checklist
- [ ] URLs are resource-oriented; actions live in HTTP verbs.
- [ ] Status codes accurately reflect the outcome.
- [ ] One consistent error response shape across the API.
- [ ] Input validated and routes authorized server-side.
- [ ] Collections paginated with metadata.
- [ ] API is versioned.
- [ ] Idempotent verbs behave idempotently.
- [ ] Contract documented with current examples.
