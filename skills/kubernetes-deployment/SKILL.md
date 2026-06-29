---
name: kubernetes-deployment
description: Use when writing or reviewing Kubernetes manifests or deploying workloads to a cluster.
---

# Kubernetes Deployment

## Purpose
Ship workloads to Kubernetes declaratively, with the resource limits, health checks, and least privilege a cluster needs to stay stable.

## When to use
- Writing or editing Deployment, Service, or related manifests.
- Reviewing manifests before they reach a cluster.
- Rolling out or updating a workload in a shared environment.

When NOT to use: building the image itself — see docker-containerization for image concerns.

## Method
1. Set requests and limits. Declare CPU/memory requests and limits on every container so the scheduler can place it and one pod can't starve the node.
2. Add probes. Define a readiness probe (gate traffic) and a liveness probe (restart when hung); without them rollouts route to dead pods.
3. Pin image tags. Reference images by explicit version or digest — never `:latest`, which makes rollouts non-deterministic.
4. Run multiple replicas with rolling updates. Set `replicas > 1` and a `RollingUpdate` strategy so deploys cause no downtime.
5. Keep manifests in version control. Treat YAML as the source of truth; apply from the repo, don't hand-edit live objects with `kubectl edit`.
6. Inject secrets properly. Mount Secret objects or pull from an external store — never hard-code credentials in manifests or env literals.
7. Organize with namespaces and labels. Separate environments by namespace; label consistently for selectors, ownership, and cost.
8. Apply least-privilege RBAC. Grant each ServiceAccount the narrowest role it needs; no cluster-admin "to make it work".

## Red flags
- Containers with no resource requests/limits.
- Missing readiness/liveness probes.
- `image: ...:latest` or otherwise unpinned tags.
- Secrets pasted as plaintext into manifests or env vars.
- A single replica for something expected to stay available.
- Wildcard or cluster-admin RBAC bindings.

## Checklist
- [ ] Resource requests and limits set on every container.
- [ ] Readiness and liveness probes defined.
- [ ] Images pinned to explicit versions/digests, not :latest.
- [ ] Multiple replicas with a rolling-update strategy.
- [ ] Manifests committed to version control as source of truth.
- [ ] Secrets sourced from Secret objects or an external store.
- [ ] RBAC scoped to least privilege.
