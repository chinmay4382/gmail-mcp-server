---
name: frontend
description: Build, debug, or review frontend code — UI components, styling, state management, accessibility.
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
---

You are helping with frontend development. Apply the following approach:

## Steps

1. **Read before changing** — understand existing components and design patterns first.
2. **Component design** — keep components small, single-purpose, and reusable.
3. **State management** — use the pattern already established in the project (context, zustand, redux, etc.).
4. **Styling** — follow the existing CSS/Tailwind/styling conventions; mobile-first responsive design.
5. **Performance** — avoid unnecessary re-renders; lazy-load where appropriate.
6. **Accessibility** — use semantic HTML, ARIA attributes where needed, keyboard navigation.
7. **Error states** — always handle loading, empty, and error states in UI.
8. **Types** — if TypeScript is used, keep props typed; avoid `any`.

## When invoked with arguments

`/frontend $ARGUMENTS`

Treat the arguments as the specific task. Explore relevant components/pages first, then implement.
