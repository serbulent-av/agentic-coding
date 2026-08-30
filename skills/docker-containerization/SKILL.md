---
name: docker-containerization
description: Use when writing or reviewing Dockerfiles or container image builds.
---

# Docker Containerization

## Purpose
Produce small, reproducible, secure container images that build fast and run with least privilege.

## When to use
- Writing a new Dockerfile or container build for a service or tool.
- Reviewing an image build for size, caching, or security issues.
- Hardening or shrinking an existing image before it ships.

When NOT to use: runtime/orchestration concerns (replicas, probes, secret injection) — those belong to the deployment layer, not the image.

## Method
1. Pick a minimal base. Prefer slim, alpine, or distroless over a full OS image; smaller surface means faster pulls and fewer CVEs.
2. Pin everything. Reference the base by exact tag or digest and pin dependency versions so the build is reproducible — never `:latest`.
3. Use multi-stage builds. Compile and install in a build stage; copy only the runtime artifact into a clean final stage.
4. Order layers for cache. Copy dependency manifests and install deps before copying source, so code edits don't bust the dependency cache.
5. Add a .dockerignore. Exclude `.git`, build output, secrets, and local cruft so context stays small and nothing sensitive leaks in.
6. Drop root. Create and `USER` a non-root account; the runtime must not run as uid 0.
7. One concern per container. A single service/process per image — no SSH, cron, or supervisor bundling unrelated jobs.
8. Keep secrets out of layers. Use build secrets or runtime mounts/env; never `COPY` or `ENV` a credential — it persists in history.
9. Add a HEALTHCHECK so orchestrators can tell live from hung.

## Red flags
- `FROM ...:latest` or an otherwise unpinned base image.
- Shipping the build stage (toolchain and source left in the runtime image).
- `COPY . .` before dependency install, busting cache on every edit.
- Container running as root by default.
- Secrets, tokens, or `.env` files baked into a layer.
- No .dockerignore, so the whole working tree enters the build context.

## Checklist
- [ ] Base image is minimal and pinned by tag/digest.
- [ ] Multi-stage build keeps build tooling out of the final image.
- [ ] Dependencies installed before source copy for cache reuse.
- [ ] .dockerignore present and excludes secrets and cruft.
- [ ] Runs as a non-root user.
- [ ] No secrets baked into any layer.
- [ ] HEALTHCHECK defined; one concern per container.
