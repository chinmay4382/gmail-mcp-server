---
name: pr-review
description: Review current branch changes and create a pull request to main.
allowed-tools: Bash, Read, Grep, Glob
---

You are reviewing changes on the current branch and creating a PR to `main`.

## Steps

### 1. Commit any uncommitted changes
- Run `git status --short` to check for uncommitted changes.
- If there are modified or untracked files (excluding `.env` and any secrets), stage and commit them:
  - Stage specific files: `git add <file1> <file2> ...` — never `git add .` blindly, and never stage `.env`.
  - Write a concise commit message explaining the why.
  - Use a HEREDOC to pass the commit message: `git commit -m "$(cat <<'EOF'\n<message>\nEOF\n)"`
- If there is nothing to commit, skip this step.

### 2. Understand the changes
- Run `git fetch origin` first to get the latest remote state.
- Run `git diff origin/main...HEAD` to see all changes.
- Run `git log origin/main...HEAD --oneline` to see commits.
- Identify the intent — what problem does this solve?

### 3. Review checklist

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

### 4. Create the PR

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
