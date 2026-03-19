---
name: frontend
description: Build, debug, or review frontend code for the Gmail MCP Client — single-file vanilla JS/HTML/Tailwind UI at ui/index.html.
---

## Project Context

The frontend is split across three files — no build step, no framework, no TypeScript. Gmail-inspired design:
- **`ui/index.html`** — markup and structure
- **`ui/app.js`** — all JavaScript (state, API calls, event handlers, rendering)
- **`ui/styles.css`** — custom CSS (animations, overrides; Tailwind handles the rest)

**Key architecture facts:**
- Styling: Tailwind CSS (CDN) + custom `<style>` block for animations and overrides
- Font: Google Sans / Roboto (Gmail aesthetic)
- Layout: Fixed top nav → sidebar (264px) → main content area → optional chat panel (380px, right)
- State: Plain JS variables (`currentView`, `currentEmailId`, `chatSessionId`, `chatBusy`, `activeTool`)
- API calls: `apiFetch(path, opts)` wrapper — all endpoints are relative (`/api/...`)
- Chat: Server-Sent Events (SSE) streaming from `/api/chat/{sessionId}`

**API endpoints available:**
- `GET /api/status` — connection + email address
- `GET /api/folders` — mailbox folders
- `GET /api/emails` — list emails (folder, pagination)
- `GET /api/emails/unread` — unread only
- `GET /api/emails/{id}` — full email detail
- `GET /api/emails/from`, `/by-subject`, `/search` — filtered views
- `POST /api/emails/send` — send email
- `POST /api/chat/session` — init chat
- `POST /api/chat/{sessionId}` — stream AI response (SSE)

## Rules for this project

1. **Three files only** — changes go in `ui/index.html`, `ui/app.js`, or `ui/styles.css`. Do not create additional files.
2. **Read all three files first** before making any changes — the HTML, JS, and CSS are tightly coupled.
3. **Follow existing patterns** — new functions should match the style of `apiFetch`, `renderEmailList`, `showToast`, etc.
4. **Never use `innerHTML` with unsanitized user data** — always escape email content (subject, from, body) before injecting into DOM. Use `textContent` or a sanitize helper.
5. **Tailwind first** — use Tailwind utility classes for layout/spacing; only add custom CSS for animations or things Tailwind can't do.
6. **No external dependencies** — don't add new CDN scripts or libraries without explicit approval.
7. **Always handle loading, empty, and error states** in any new list or async UI.
8. **Accessibility** — add `aria-label` to all icon-only buttons; use semantic HTML.

## Known issues to be aware of (do not reintroduce)

- XSS via `innerHTML` with raw email data — always sanitize
- Fragile quote escaping in inline `onclick` handlers — prefer `addEventListener` for new code
- Compose form not clearing on modal close — fix when touching compose
- No debounce on search input — add if modifying search

## When invoked with arguments

`/frontend $ARGUMENTS`

Read `ui/index.html`, `ui/app.js`, and `ui/styles.css` first, identify the relevant section, then implement the change following the rules above.
