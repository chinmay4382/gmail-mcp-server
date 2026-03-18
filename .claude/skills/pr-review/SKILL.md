---
name: pr-review
description: Review a pull request — check code quality, bugs, security, tests, and provide structured feedback.
allowed-tools: Bash, Read, Grep, Glob
---

Review the pull request or staged changes. Follow this structured checklist:

## Review Checklist

### 1. Understand the change
- Run `git diff main...HEAD` (or use provided PR context) to see all changes.
- Identify the intent — what problem does this solve?

### 2. Code quality
- Is the logic correct and easy to follow?
- Are there dead code, unnecessary complexity, or premature abstractions?
- Does naming clearly convey intent?

### 3. Security
- Any injection vulnerabilities (SQL, command, XSS)?
- Secrets or credentials accidentally committed?
- Input validation at system boundaries?

### 4. Tests
- Are new behaviors covered by tests?
- Do existing tests still make sense with the changes?

### 5. Performance
- Any N+1 queries, blocking operations, or unnecessary work in hot paths?

### 6. Breaking changes
- API contract changes? Schema migrations? Dependency upgrades?

## Output format

Produce a structured review with:
- **Summary** — one-line description of what the PR does
- **Critical issues** — must fix before merge (bugs, security)
- **Suggestions** — nice-to-haves (style, refactoring)
- **Verdict** — Approve / Request Changes / Needs Discussion

## When invoked with arguments

`/pr-review $ARGUMENTS`

If a PR number or branch name is given, use `gh` CLI to fetch the diff. Otherwise review current staged/unstaged changes.
