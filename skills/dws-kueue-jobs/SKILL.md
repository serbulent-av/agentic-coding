---
name: dws-kueue-jobs
description: Use when submitting or reviewing batch Jobs that need on-demand GPU/TPU capacity on Kubernetes via Kueue and a dynamic provisioning scheduler (e.g. GKE Dynamic Workload Scheduler).
---

# DWS / Kueue Jobs

## Purpose
Get burst GPU/TPU work scheduled onto hardware that does not exist yet: Kueue queues the Job and the provisioner creates the node pool on demand, instead of you keeping idle GPUs around.

## When to use
- Running a batch/inference/training `Job` that needs a GPU or TPU you don't want reserved permanently.
- Reviewing a Job manifest that carries a `kueue.x-k8s.io/queue-name` label.
- Diagnosing a queued Job that stays Pending / suspended.

When NOT to use: long-lived services (Deployments) or interactive debugging — DWS is for bounded batch Jobs.

## Concepts
- **LocalQueue** (namespaced) is what a Job names via its label; **ClusterQueue** (cluster-scoped) holds the quota and admits. A Workload is admitted only when the ClusterQueue is `Active`.
- **ResourceFlavor** maps quota to a node type (e.g. an accelerator + its node labels/taints).
- **AdmissionCheck** gates admission on an external condition — e.g. a DWS ProvisioningRequest, or a MultiKueue hop that delegates the Job to a worker cluster.
- A Job targeted at a queue should be created **suspended** (the Kueue webhook usually does this for you); the queue admits it, then the provisioner spins up nodes.

## Method
1. Confirm the queue exists and is Active *before* submitting: `kubectl get clusterqueue <cq> -o jsonpath='{.status.conditions[?(@.type=="Active")].status}'` must be `True`.
2. Label the Job with the LocalQueue: `metadata.labels: {"kueue.x-k8s.io/queue-name": <localqueue>}`, and submit it to the **namespace that LocalQueue lives in**.
3. Match the pod to the flavor's node: `nodeSelector` for the accelerator, `nvidia.com/gpu` (or `tpu`) in `requests` and `limits`, and a `tolerations` entry for the provisioning taint (commonly `cloud.google.com/gke-queued` on GKE).
4. Set `backoffLimit: 0` so an OOM surfaces as a fast `Failed` instead of silent pod retries — the orchestrator can then escalate to a larger flavor.
5. Authenticate with **Workload Identity / IAM**, never long-lived keys: set a `serviceAccountName` bound to a cloud identity and do not mount credential files or set `GOOGLE_APPLICATION_CREDENTIALS`.
6. Watch admission, not just the pod: `kubectl get workloads -n <ns>` for `Admitted`, and `kubectl get provisioningrequest -n <ns>` for DWS provisioning. A Job that never becomes `Admitted` is a queue/quota problem, not a pod problem.
7. Size memory/CPU to the node the flavor provisions; on managed offerings a per-accelerator maximum may be enforced at admission (read the rejection's stated max and stay under it).

## Red flags
- Submitting before checking the ClusterQueue is `Active` — the Job sits suspended forever.
- Queue label pointing at a LocalQueue in a different namespace than the Job.
- Service-account JSON keys, access tokens, or credential files baked into the pod spec.
- `backoffLimit > 0`, which masks OOMs and stalls tier escalation.
- Requesting memory/CPU above the provisioned node's per-accelerator cap.
- Editing the queue, flavors, admission checks, or webhooks to force admission — those are platform-admin objects; fix the Job, not the queue.

## Checklist
- [ ] ClusterQueue verified `Active` before submitting.
- [ ] Job carries the correct `kueue.x-k8s.io/queue-name` label and target namespace.
- [ ] nodeSelector + accelerator request + provisioning toleration match the ResourceFlavor.
- [ ] `backoffLimit: 0` for fast OOM surfacing.
- [ ] Workload Identity / IAM auth; no tokens or key files in the pod.
- [ ] Requests/limits within the node's per-accelerator maximum.
- [ ] No server-side (queue/admission/webhook) objects modified by the submitter.
