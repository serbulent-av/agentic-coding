# Agentic Coding

A multi-agent system for software development. Each agent has a specialized role, and together they form a complete workflow from planning through implementation to quality assurance.

## Agents

| Agent | Role | Description |
|-------|------|-------------|
| **Patek** | Main / Orchestrator | Coordinates all agents, delegates tasks, and logs every action into an activity log. The central hub of the system. |
| **Philipe** | Implementation | Analyzes requirements, plans the implementation, and writes the code. Iterates based on review feedback. |
| **Lange** | Planning | Creates and maintains the project plan. Monitors progress and expands the plan when new information emerges. |
| **Sohne** | Oversight | Ensures best practices are followed without over-engineering. Reviews documentation quality (README, module docs, inline comments). |
| **Gerald** | Red Team | Adversarial reviewer. Hunts for bugs, edge cases, plan deviations, and potential problems. Does not sign off until all critical issues are resolved. |

## Workflow

```
User Prompt
    |
    v
 [Patek] -- delegates to --> [Lange] (creates plan)
    |
    v
 [Patek] -- delegates to --> [Philipe] (implements step by step)
    |
    v  (after each step)
 [Patek] -- triggers --> [Sohne] (oversight review)
 [Patek] -- triggers --> [Gerald] (red team review)
    |
    v  (if issues found)
 [Patek] -- routes feedback to --> [Philipe] (fixes)
    |
    v  (repeat until sign-off)
 [Patek] -- compiles final log and delivers result
```

## Repository Structure

```
agents/
  patek/
    description.md   # Role, responsibilities, workflow, rules
    memory.md         # Experience log across projects
  philipe/
    description.md
    memory.md
  lange/
    description.md
    memory.md
  sohne/
    description.md
    memory.md
  gerald/
    description.md
    memory.md
```

## How to Use

1. **Start with Patek**: Give your project prompt to Patek. It will orchestrate the entire process.
2. **Lange plans**: Lange produces a structured plan with milestones, tasks, and acceptance criteria.
3. **Philipe builds**: Philipe implements the plan step by step, following coding standards.
4. **Sohne and Gerald review**: After each step, Sohne checks for best practices and documentation, while Gerald hunts for bugs and issues.
5. **Iterate**: Feedback loops back to Philipe until both reviewers sign off.
6. **Patek logs everything**: The full activity log is available for audit and learning.

## Agent Files

Each agent has two files:

- **`description.md`**: Defines the agent's role, responsibilities, workflow, and rules. This is the agent's "instruction manual".
- **`memory.md`**: A running log of experiences, lessons learned, and recurring patterns. Updated after each project to improve future performance.
