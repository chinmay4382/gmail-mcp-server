---
name: pr-review
description: Review current branch changes and create a pull request to main.
allowed-tools: Bash, Read, Grep, Glob
---

You are reviewing changes on the current branch and creating a PR to `main`.

## Steps

### 1. Understand the changes
- Run `git diff main...HEAD` to see all changes.
- Run `git log main...HEAD --oneline` to see commits.
- Identify the intent — what problem does this solve?

### 2. Review checklist

**Code quality**
- Is the logic correct and easy to follow?
- Any dead code, unnecessary complexity, or premature abstractions?

**Security**
- Any XSS, injection vulnerabilities, or exposed secrets?
- Input validated at system boundaries?

**Tests**
- Are new behaviors covered?

**Breaking changes**
- API contract changes? Dependency upgrades?

### 3. Create the PR

After reviewing, create a PR from the current branch to `main` using:

```bash
gh pr create --base main --title "<title>" --body "<body>"
```

PR body must follow this format:
```
## Summary
- <bullet points of what changed>

## Review Notes
- <any critical issues found>
- <suggestions>

🤖 Generated with Claude Code
```

- Keep the title under 70 characters.
- If there are **critical issues** (security, bugs), flag them clearly in the PR body and warn the user before creating.
- Always return the PR URL at the end.

## When invoked with arguments

`/pr-review $ARGUMENTS`

If a branch name is given, switch context to that branch before reviewing. Otherwise use the current branch.
