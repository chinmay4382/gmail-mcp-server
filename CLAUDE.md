# Claude Instructions

## Security

- **Never read `.env`** — it contains live credentials. Do not read, display, or reference its contents under any circumstances.
- If a task requires knowing env var names, refer to `.env.example` instead.
- Never commit `.env`, secrets, API keys, or passwords.
- Always validate user input at system boundaries; never trust raw external data.
- Avoid introducing command injection, SQL injection, or XSS vulnerabilities.

## Code Style

- Read existing code before making changes — match the style, naming, and patterns already in place.
- Keep changes focused and minimal; don't refactor code unrelated to the task.
- Prefer editing existing files over creating new ones.
- Only add comments for complex functions where the logic is not self-evident — do not comment simple, readable code.

## General Behavior

- Don't assume — if a requirement is unclear, ask before implementing.
- Don't over-engineer; build the simplest solution that satisfies the requirement.
- Don't add error handling, fallbacks, or validation for scenarios that can't happen.
- Prefer explicit over clever; readable code over compact code.

## Git

- Never force-push to `main`.
- Never skip pre-commit hooks (`--no-verify`).
- Always stage specific files — never `git add .` blindly.
- Write concise commit messages that explain the **why**, not just the **what**.

## Skills

Use the following project skills for relevant tasks:

- `/backend` — when working on `gmail_mcp_server.py`, `gmail_client.py`, API endpoints, IMAP/SMTP logic, or any server-side code.
- `/frontend` — when working on any UI, dashboard, or client-side code added to this project.
- `/pr-review` — before committing or pushing; review staged changes for quality, security, and correctness.

## Project-Specific

- This is a Gmail MCP server using Python and IMAP/SMTP.
- Environment variables are defined in `.env.example` — use those as reference.
- MCP server entry point is `gmail_mcp_server.py`.
