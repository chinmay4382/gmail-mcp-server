---
name: backend
description: Build, debug, or review backend code — APIs, databases, server logic, auth, MCP servers.
---

You are helping with backend development on a Gmail MCP server. The key files are:
- `gmail_client.py` — IMAP/SMTP logic, email fetching, sending
- `api_server.py` — FastAPI REST endpoints (entry point for the web UI)
- `gmail_mcp_server.py` — MCP server entry point

## Steps

1. **Read before changing** — always read the relevant file(s) first to understand existing patterns before modifying.
2. **Follow existing conventions** — match the code style, error handling, and naming already in place.
3. **API design** — keep endpoints RESTful; use consistent request/response shapes.
4. **IMAP/SMTP** — be mindful of connection state and authentication; avoid leaking connections.
5. **Auth & security** — validate at system boundaries; never read or expose `.env`; avoid injection vulnerabilities.
6. **Error handling** — return structured errors with clear messages and appropriate HTTP status codes.
7. **Logging** — add structured logs at key decision points, not for routine flow.

## When invoked with arguments

`/backend $ARGUMENTS`

Treat the arguments as the specific task. Read the relevant backend files first, then implement.
