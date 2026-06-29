---
name: react-frontend
description: Use when building or reviewing React or similar component-based UI.
---

# React Frontend

## Purpose
Build component UIs that stay predictable and maintainable by keeping components small, pure, and driven by explicit state and props.

## When to use
- Building or changing a React (or similar) component or hook.
- Reviewing component structure, state flow, or rendering logic.
- Deciding where state should live or how data passes through the tree.

When NOT to use: non-UI logic, or framework build/routing config covered by its own tooling. Don't restructure a working component just to apply a pattern.

## Method
1. Keep components small and composable. One responsibility each; build screens by composing pieces, not one giant component.
2. Keep render pure. Same props and state produce the same output; no mutation or side effects during render.
3. Lift state only as high as needed. Put state at the lowest common owner; don't hoist to a global when a parent suffices.
4. Use effects for side effects only. Reach for effects to sync with the outside world, not to derive data you can compute in render; list every dependency.
5. Use stable keys in lists. Key by stable identity, never array index, so reconciliation stays correct.
6. Prefer composition and context over prop drilling. Pass children or share via context instead of threading props through layers.
7. Write semantic, accessible markup. Use real elements (button, label, nav), manage focus, and respect ARIA where needed.
8. Don't over-abstract early. Inline first; extract a component or hook after the pattern actually repeats.

## Red flags
- A god component owning unrelated state and most of the screen.
- State lifted to the top or a store when only one subtree needs it.
- Effects that derive state or run every render from missing dependencies.
- Array index used as a list key for dynamic lists.
- The same prop threaded through many layers that don't use it.
- div onClick instead of a button; missing labels and focus handling.

## Checklist
- [ ] Components are small, composable, single-purpose.
- [ ] Render is pure; no side effects mid-render.
- [ ] State lives at the lowest owner that needs it.
- [ ] Effects are for side effects, with complete dependency arrays.
- [ ] Lists use stable identity keys, not indexes.
- [ ] Composition/context used instead of deep prop drilling.
- [ ] Markup is semantic and accessible.
- [ ] No abstraction added before the pattern repeats.
