---
name: skill-creator
description: Use when scaffolding a new skill or revising an existing one for this library.
---

# Skill Creator

## Purpose
Produce a single, focused skill file that fires at the right moment and tells an agent exactly how to act.

## When to use
- Adding a new skill to this library.
- Revising an existing skill's scope, trigger, or body.
- Splitting a bloated skill that tries to do more than one job.

When NOT to use: for a one-off note that is not a reusable procedure — record it elsewhere instead of minting a skill.

## Method
1. One skill, one job. If the scope needs an "and", split it into two skills.
2. Scaffold the folder. Create `skills/<name>/` holding a single `SKILL.md`, nothing else.
3. Write minimal frontmatter. Only `name` (equal to the folder) and `description`.
4. Make the trigger fire. Description is third-person and states WHEN/triggers to use it.
5. Fill the fixed body. Use the headers Purpose, When to use, Method, Red flags, Checklist.
6. Keep it tight. Stay ≤120 lines, specific and actionable; cut filler.

## Red flags
- A skill that spans several jobs — split it.
- Frontmatter with any key beyond `name` and `description`.
- `name` not matching the folder name.
- A vague description with no trigger — it won't fire when needed.
- README files, images, or asset clutter in the skill folder.
- A body over 120 lines or padded with generic advice.

## Checklist
- [ ] Folder is `skills/<name>/` with exactly one SKILL.md.
- [ ] Frontmatter is only name + description; name == folder.
- [ ] Description is third-person and includes WHEN/triggers.
- [ ] All five body headers are present.
- [ ] ≤120 lines with no asset clutter.
- [ ] Trigger reads naturally and is distinct from sibling skills.
