# Skills Library

A shared, portable library of Claude-Code-format skills — each a folder with a single `SKILL.md` — that the agents load on demand when a task matches a skill's trigger. Skills use progressive disclosure: an agent reads a skill's lightweight frontmatter trigger first and only pulls in the full method when it applies. The same `SKILL.md` format works unchanged across Claude.ai, Claude Code, and the API.

## How agents use skills

- An agent loads a skill when the current task matches that skill's `description` trigger — the third-person "Use when…" line in its YAML frontmatter.
- Each agent's `description.md` has a `## Skills` section naming the core skills for its role; see [Which agents use what](#which-agents-use-what).
- Skills are portable and self-contained: one folder plus one `SKILL.md`, with no agent-specific wiring, so the same skill works across Claude.ai, Claude Code, and the API.

## Catalog

### Planning & Design

| Skill | When to use |
|-------|-------------|
| [`brainstorming`](brainstorming/SKILL.md) | Use before any creative or feature work when the request is vague or the solution space is open; explores intent, requirements, and design before planning or code. |
| [`writing-plans`](writing-plans/SKILL.md) | Use when turning an agreed direction or spec into a reviewable, step-by-step implementation plan before touching code. |
| [`api-design`](api-design/SKILL.md) | Use when defining an interface, function signature, schema, or contract, before implementing the internals. |

### Implementation

| Skill | When to use |
|-------|-------------|
| [`test-driven-development`](test-driven-development/SKILL.md) | Use when implementing any new behavior or bugfix, before writing implementation code. |
| [`writing-clean-code`](writing-clean-code/SKILL.md) | Use when writing or modifying any code; enforces minimal, readable, intention-revealing implementations. |
| [`refactoring`](refactoring/SKILL.md) | Use when restructuring code without changing its observable behavior. |
| [`executing-plans`](executing-plans/SKILL.md) | Use when you have a written, approved implementation plan to execute step by step with review checkpoints. |
| [`using-git-worktrees`](using-git-worktrees/SKILL.md) | Use when starting feature work that needs isolation, or running parallel or risky experiments without disturbing the main workspace. |
| [`shell-scripting`](shell-scripting/SKILL.md) | Use when writing or reviewing bash or shell scripts. |

### Review & QA

| Skill | When to use |
|-------|-------------|
| [`code-review`](code-review/SKILL.md) | Use when reviewing a diff or pull request before sign-off; checks correctness, readability, tests, and scope. |
| [`systematic-debugging`](systematic-debugging/SKILL.md) | Use when encountering any bug, test failure, or unexpected behavior, before proposing a fix. |
| [`verification-before-done`](verification-before-done/SKILL.md) | Use before claiming any work complete, fixed, or passing, and before committing or handing off. |
| [`receiving-feedback`](receiving-feedback/SKILL.md) | Use when receiving code-review feedback, before implementing suggestions, especially if feedback seems unclear or technically questionable. |
| [`performance-optimization`](performance-optimization/SKILL.md) | Use when there is a stated performance concern or a measured bottleneck — not by default. |
| [`writing-documentation`](writing-documentation/SKILL.md) | Use when writing or updating a README, module docs, or docstrings. |

### Security

| Skill | When to use |
|-------|-------------|
| [`security-review`](security-review/SKILL.md) | Use when reviewing code that handles untrusted input, authentication, secrets, or external dependencies. |

### Orchestration & Workflow

| Skill | When to use |
|-------|-------------|
| [`subagent-orchestration`](subagent-orchestration/SKILL.md) | Use when work splits into independent tasks that can run in parallel without shared state or sequential dependencies. |
| [`task-tracking`](task-tracking/SKILL.md) | Use when work spans three or more steps or multiple sessions; track it as discrete tasks with explicit status. |
| [`checkpoint-and-resume`](checkpoint-and-resume/SKILL.md) | Use when work risks exceeding a single session or context window; persist state so it survives interruption. |
| [`asking-clarifying-questions`](asking-clarifying-questions/SKILL.md) | Use when you need a decision, clarification, or approval from the user, and to decide when to instead proceed autonomously. |
| [`persistent-memory`](persistent-memory/SKILL.md) | Use at the start or end of a session, or when a durable lesson emerges, to maintain memory across sessions. |
| [`delivering-work`](delivering-work/SKILL.md) | Use when implementation is complete and verified and the work needs to be integrated or handed back. |
| [`skill-creator`](skill-creator/SKILL.md) | Use when scaffolding a new skill or revising an existing one for this library. |

### Tools & Domains

| Skill | When to use |
|-------|-------------|
| [`docker-containerization`](docker-containerization/SKILL.md) | Use when writing or reviewing Dockerfiles or container image builds. |
| [`kubernetes-deployment`](kubernetes-deployment/SKILL.md) | Use when writing or reviewing Kubernetes manifests or deploying workloads to a cluster. |
| [`terraform-iac`](terraform-iac/SKILL.md) | Use when writing or reviewing infrastructure-as-code with Terraform. |
| [`ci-cd-pipelines`](ci-cd-pipelines/SKILL.md) | Use when designing or fixing CI/CD pipelines such as GitHub Actions. |
| [`github-pull-requests`](github-pull-requests/SKILL.md) | Use when creating, reviewing, or merging pull requests, especially via the gh CLI. |
| [`sql-and-databases`](sql-and-databases/SKILL.md) | Use when designing schemas, writing queries, or managing database migrations. |
| [`rest-api-development`](rest-api-development/SKILL.md) | Use when building or reviewing REST/HTTP APIs. |
| [`react-frontend`](react-frontend/SKILL.md) | Use when building or reviewing React or similar component-based UI. |
| [`observability-logging`](observability-logging/SKILL.md) | Use when adding logging, metrics, or tracing to code or services. |

_32 skills total: Planning & Design (3), Implementation (6), Review & QA (6), Security (1), Orchestration & Workflow (7), Tools & Domains (9)._

## Which agents use what

Each agent's `description.md` lists its core skills below. Any agent may load any skill when a task matches its trigger; these are the defaults for the role.

| Agent | Role | Core skills |
|-------|------|-------------|
| **Patek** | Orchestrator | subagent-orchestration, executing-plans, task-tracking, asking-clarifying-questions, checkpoint-and-resume, persistent-memory, delivering-work, verification-before-done, using-git-worktrees, skill-creator |
| **Lange** | Planning | brainstorming, writing-plans, api-design, asking-clarifying-questions, skill-creator |
| **Philipe** | Implementation | test-driven-development, writing-clean-code, systematic-debugging, refactoring, receiving-feedback, executing-plans, verification-before-done |
| **Sohne** | Oversight | code-review, verification-before-done, writing-clean-code, refactoring, writing-documentation |
| **Gerald** | Red Team | systematic-debugging, code-review, security-review, performance-optimization, verification-before-done, observability-logging |

## Adding a skill

Use the [`skill-creator`](skill-creator/SKILL.md) skill to scaffold a new one. A skill is a single folder containing one `SKILL.md`: its YAML frontmatter carries `name` (matching the folder name) and `description` (a third-person "Use when…" trigger so agents know when to load it), and its body uses the five canonical headers — Purpose, When to use, Method, Red flags, Checklist. Keep each skill self-contained and under 120 lines so it stays cheap to load.
