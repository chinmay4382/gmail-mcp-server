---
name: new-branch
description: Checkout main, pull latest, and create a new branch from it.
---

Create a new branch from the latest `main`.

## Steps

1. Checkout main: `git checkout main`
2. Pull latest: `git pull origin main`
3. Create and switch to the new branch: `git checkout -b <branch-name>`

## When invoked with arguments

`/new-branch $ARGUMENTS`

Use the argument as the branch name. If no argument is provided, ask the user for a branch name before proceeding.
