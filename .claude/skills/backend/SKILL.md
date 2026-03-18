---
name: backend
description: Build, debug, or review backend code — APIs, databases, server logic, auth, MCP servers.
allowed-tools: Bash, Read, Write, Edit, Grep, Glob
---

You are helping with backend development. Apply the following approach:

## Steps

1. **Read before changing** — always read existing files to understand patterns before modifying.
2. **Follow existing conventions** — match the code style, error handling, and naming already in place.
3. **API design** — keep endpoints RESTful; use consistent request/response shapes.
4. **Database** — document any schema changes; consider migrations and rollbacks.
5. **Auth & security** — validate at system boundaries; never expose secrets; avoid injection vulnerabilities.
6. **Error handling** — return structured errors with clear messages and appropriate HTTP status codes.
7. **Logging** — add structured logs at key decision points (not noise).
8. **Tests** — write unit tests for business logic and integration tests for external boundaries.

## When invoked with arguments

`/backend $ARGUMENTS`

Treat the arguments as the specific task. Explore the relevant backend files first, then implement.
