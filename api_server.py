"""FastAPI REST server wrapping the Gmail/Email client for the web UI."""

import asyncio
import json
import os
import logging
import uuid
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

import anthropic as _anthropic
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
from gmail_client import EmailClient

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Email MCP Server API",
    description="REST API wrapper for the Email MCP Server",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static UI files
import pathlib
UI_DIR = pathlib.Path(__file__).parent / "ui"
if UI_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(UI_DIR)), name="static")


# ---------------------------------------------------------------------------
# Email client singleton
# ---------------------------------------------------------------------------
_client: Optional[EmailClient] = None


def get_client() -> EmailClient:
    global _client
    if _client is None:
        email_address = os.getenv("EMAIL_ADDRESS")
        password = os.getenv("EMAIL_PASSWORD")
        imap_server = os.getenv("IMAP_SERVER", "imap.gmail.com")
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")

        if not email_address or not password:
            raise HTTPException(
                status_code=503,
                detail="EMAIL_ADDRESS and EMAIL_PASSWORD environment variables are not set.",
            )
        try:
            _client = EmailClient(
                email_address=email_address,
                password=password,
                imap_server=imap_server,
                smtp_server=smtp_server,
            )
            logger.info(f"Email client connected for {email_address}")
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Could not connect to mail server: {e}")
    return _client


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------
class SendEmailRequest(BaseModel):
    recipient: str
    subject: str
    body: str
    html: bool = False


# ---------------------------------------------------------------------------
# Routes – Serve UI
# ---------------------------------------------------------------------------
@app.get("/", include_in_schema=False)
def serve_ui():
    index = UI_DIR / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return {"message": "Email MCP API is running. UI not found – place index.html in ui/"}


# ---------------------------------------------------------------------------
# Routes – Info / Status
# ---------------------------------------------------------------------------
@app.get("/api/status", tags=["status"])
def status():
    """Check API and mail server connectivity."""
    email_address = os.getenv("EMAIL_ADDRESS", "not configured")
    imap_server = os.getenv("IMAP_SERVER", "imap.gmail.com")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    connected = _client is not None
    # Try a quick connect if not already done
    try:
        get_client()
        connected = True
    except Exception:
        pass
    return {
        "status": "ok" if connected else "error",
        "email": email_address,
        "imap_server": imap_server,
        "smtp_server": smtp_server,
        "connected": connected,
    }


@app.get("/api/tools", tags=["info"])
def list_tools():
    """Return metadata about all available MCP tools."""
    return {
        "tools": [
            {
                "name": "list_emails",
                "description": "List emails from any mailbox folder",
                "params": ["folder", "max_results", "unread_only"],
                "endpoint": "GET /api/emails",
            },
            {
                "name": "get_unread_emails",
                "description": "Fetch only unread emails",
                "params": ["folder", "max_results"],
                "endpoint": "GET /api/emails/unread",
            },
            {
                "name": "get_emails_from_sender",
                "description": "Retrieve all emails from a specific sender",
                "params": ["sender", "folder", "max_results"],
                "endpoint": "GET /api/emails/from",
            },
            {
                "name": "get_emails_by_subject",
                "description": "Find emails matching a subject keyword",
                "params": ["subject", "folder", "max_results"],
                "endpoint": "GET /api/emails/by-subject",
            },
            {
                "name": "search_emails",
                "description": "Search with raw IMAP criteria (e.g. UNSEEN, FROM, SUBJECT)",
                "params": ["query", "folder", "max_results"],
                "endpoint": "GET /api/emails/search",
            },
            {
                "name": "get_email_details",
                "description": "Get the full content of a single email by ID",
                "params": ["message_id"],
                "endpoint": "GET /api/emails/{message_id}",
            },
            {
                "name": "list_folders",
                "description": "List all mailbox folders",
                "params": [],
                "endpoint": "GET /api/folders",
            },
            {
                "name": "send_email",
                "description": "Compose and send an email (plain-text or HTML)",
                "params": ["recipient", "subject", "body", "html"],
                "endpoint": "POST /api/emails/send",
            },
        ]
    }


# ---------------------------------------------------------------------------
# Routes – Folders
# ---------------------------------------------------------------------------
@app.get("/api/folders", tags=["folders"])
def list_folders():
    """List all mailbox folders."""
    try:
        folders = get_client().list_folders()
        return {"folders": folders}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Routes – Emails (read)
# ---------------------------------------------------------------------------
@app.get("/api/emails", tags=["emails"])
def list_emails(
    folder: str = Query("INBOX", description="Mailbox folder"),
    max_results: int = Query(10, ge=1, le=100),
    unread_only: bool = Query(False),
):
    """List emails from a folder."""
    try:
        emails = get_client().list_emails(folder=folder, max_results=max_results, unread_only=unread_only)
        return {"emails": emails, "count": len(emails), "folder": folder}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/emails/unread", tags=["emails"])
def get_unread_emails(
    folder: str = Query("INBOX"),
    max_results: int = Query(10, ge=1, le=100),
):
    """Get unread emails."""
    try:
        emails = get_client().get_unread_emails(folder=folder, max_results=max_results)
        return {"emails": emails, "count": len(emails), "folder": folder}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/emails/search", tags=["emails"])
def search_emails(
    query: str = Query(..., description="IMAP search criteria, e.g. UNSEEN or SUBJECT \"invoice\""),
    folder: str = Query("INBOX"),
    max_results: int = Query(10, ge=1, le=100),
):
    """Search emails with raw IMAP criteria."""
    try:
        emails = get_client().search_emails(query=query, folder=folder, max_results=max_results)
        return {"emails": emails, "count": len(emails), "query": query}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/emails/from", tags=["emails"])
def get_emails_from_sender(
    sender: str = Query(..., description="Sender email address"),
    folder: str = Query("INBOX"),
    max_results: int = Query(10, ge=1, le=100),
):
    """Get emails from a specific sender."""
    try:
        emails = get_client().get_emails_from_sender(sender=sender, folder=folder, max_results=max_results)
        return {"emails": emails, "count": len(emails), "sender": sender}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/emails/by-subject", tags=["emails"])
def get_emails_by_subject(
    subject: str = Query(..., description="Subject keyword to search"),
    folder: str = Query("INBOX"),
    max_results: int = Query(10, ge=1, le=100),
):
    """Get emails matching a subject keyword."""
    try:
        emails = get_client().get_emails_by_subject(subject=subject, folder=folder, max_results=max_results)
        return {"emails": emails, "count": len(emails), "subject": subject}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/emails/{message_id}", tags=["emails"])
def get_email_details(message_id: str):
    """Get full details of a specific email by IMAP message ID."""
    try:
        email_data = get_client().get_email(message_id=message_id)
        if not email_data:
            raise HTTPException(status_code=404, detail="Email not found")
        return email_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Routes – Send
# ---------------------------------------------------------------------------
@app.post("/api/emails/send", tags=["emails"])
def send_email(payload: SendEmailRequest):
    """Send an email."""
    try:
        success = get_client().send_email(
            recipient=payload.recipient,
            subject=payload.subject,
            body=payload.body,
            html=payload.html,
        )
        if success:
            return {"success": True, "message": "Email sent successfully"}
        raise HTTPException(status_code=500, detail="Failed to send email")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Chat – Claude-powered natural language interface
# ---------------------------------------------------------------------------

_anthropic_client: Optional[_anthropic.AsyncAnthropic] = None
_executor = ThreadPoolExecutor(max_workers=4)
_sessions: dict[str, list] = {}   # session_id -> Anthropic messages list

_CHAT_SYSTEM = """You are a helpful email assistant connected to the user's mailbox via IMAP/SMTP.
You can read, search, and send emails. Be concise. When showing email lists, present each one on
its own line with sender, subject, and date. Always confirm before sending an email."""

_EMAIL_TOOLS = [
    {
        "name": "list_emails",
        "description": "List emails from a mailbox folder.",
        "input_schema": {
            "type": "object",
            "properties": {
                "folder":      {"type": "string",  "description": "Folder name (default: INBOX)"},
                "max_results": {"type": "integer", "description": "Max emails (default: 10)"},
                "unread_only": {"type": "boolean", "description": "Only unread emails"},
            },
        },
    },
    {
        "name": "get_unread_emails",
        "description": "Get unread emails from a folder.",
        "input_schema": {
            "type": "object",
            "properties": {
                "folder":      {"type": "string",  "description": "Folder (default: INBOX)"},
                "max_results": {"type": "integer", "description": "Max emails (default: 10)"},
            },
        },
    },
    {
        "name": "get_emails_from_sender",
        "description": "Get emails from a specific sender's address.",
        "input_schema": {
            "type": "object",
            "properties": {
                "sender":      {"type": "string",  "description": "Sender email address"},
                "folder":      {"type": "string",  "description": "Folder (default: INBOX)"},
                "max_results": {"type": "integer", "description": "Max emails (default: 10)"},
            },
            "required": ["sender"],
        },
    },
    {
        "name": "get_emails_by_subject",
        "description": "Find emails whose subject contains a keyword.",
        "input_schema": {
            "type": "object",
            "properties": {
                "subject":     {"type": "string",  "description": "Subject keyword"},
                "folder":      {"type": "string",  "description": "Folder (default: INBOX)"},
                "max_results": {"type": "integer", "description": "Max emails (default: 10)"},
            },
            "required": ["subject"],
        },
    },
    {
        "name": "search_emails",
        "description": "Search emails using raw IMAP criteria, e.g. UNSEEN, FROM \"x@y\", SUBJECT \"z\".",
        "input_schema": {
            "type": "object",
            "properties": {
                "query":       {"type": "string",  "description": "IMAP search query"},
                "folder":      {"type": "string",  "description": "Folder (default: INBOX)"},
                "max_results": {"type": "integer", "description": "Max results (default: 10)"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_email_details",
        "description": "Get the full body and headers of a single email by its IMAP ID.",
        "input_schema": {
            "type": "object",
            "properties": {
                "message_id": {"type": "string", "description": "IMAP message ID (e.g. '42')"},
            },
            "required": ["message_id"],
        },
    },
    {
        "name": "list_folders",
        "description": "List all available mailbox folders.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "send_email",
        "description": "Send an email to a recipient.",
        "input_schema": {
            "type": "object",
            "properties": {
                "recipient": {"type": "string", "description": "Recipient email address"},
                "subject":   {"type": "string", "description": "Email subject"},
                "body":      {"type": "string", "description": "Email body"},
                "html":      {"type": "boolean", "description": "True if body is HTML"},
            },
            "required": ["recipient", "subject", "body"],
        },
    },
]


def _get_anthropic() -> _anthropic.AsyncAnthropic:
    global _anthropic_client
    if _anthropic_client is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=503,
                detail="ANTHROPIC_API_KEY environment variable is not set.",
            )
        _anthropic_client = _anthropic.AsyncAnthropic(api_key=api_key)
    return _anthropic_client


def _run_email_tool(name: str, inp: dict) -> str:
    """Execute an email client method synchronously (runs in thread pool)."""
    c = get_client()
    try:
        if name == "list_emails":
            r = c.list_emails(
                folder=inp.get("folder", "INBOX"),
                max_results=inp.get("max_results", 10),
                unread_only=inp.get("unread_only", False),
            )
        elif name == "get_unread_emails":
            r = c.get_unread_emails(folder=inp.get("folder", "INBOX"), max_results=inp.get("max_results", 10))
        elif name == "get_emails_from_sender":
            r = c.get_emails_from_sender(sender=inp["sender"], folder=inp.get("folder", "INBOX"), max_results=inp.get("max_results", 10))
        elif name == "get_emails_by_subject":
            r = c.get_emails_by_subject(subject=inp["subject"], folder=inp.get("folder", "INBOX"), max_results=inp.get("max_results", 10))
        elif name == "search_emails":
            r = c.search_emails(query=inp["query"], folder=inp.get("folder", "INBOX"), max_results=inp.get("max_results", 10))
        elif name == "get_email_details":
            r = c.get_email(message_id=inp["message_id"])
        elif name == "list_folders":
            r = {"folders": c.list_folders()}
        elif name == "send_email":
            ok = c.send_email(recipient=inp["recipient"], subject=inp["subject"], body=inp["body"], html=inp.get("html", False))
            r = {"success": ok, "message": "Email sent successfully" if ok else "Failed to send email"}
        else:
            r = {"error": f"Unknown tool: {name}"}
        return json.dumps(r, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})


def _content_to_dict(block) -> dict:
    if block.type == "text":
        return {"type": "text", "text": block.text}
    if block.type == "tool_use":
        return {"type": "tool_use", "id": block.id, "name": block.name, "input": block.input}
    return block.model_dump()


class ChatMessageRequest(BaseModel):
    message: str


def _sse(obj: dict) -> str:
    return f"data: {json.dumps(obj)}\n\n"


@app.post("/api/chat/session", tags=["chat"])
def create_session():
    """Create a new chat session and return its ID."""
    sid = str(uuid.uuid4())
    _sessions[sid] = []
    return {"session_id": sid}


@app.post("/api/chat/{session_id}", tags=["chat"])
async def chat(session_id: str, payload: ChatMessageRequest):
    """Send a message; returns a Server-Sent Events stream with the AI reply."""
    if session_id not in _sessions:
        raise HTTPException(status_code=404, detail="Session not found. Create one via POST /api/chat/session")

    loop = asyncio.get_running_loop()

    async def generate():
        messages = _sessions[session_id] + [{"role": "user", "content": payload.message}]

        try:
            claude = _get_anthropic()
        except HTTPException as exc:
            yield _sse({"type": "error", "text": exc.detail})
            return

        while True:
            try:
                async with claude.messages.stream(
                    model="claude-opus-4-6",
                    max_tokens=4096,
                    system=_CHAT_SYSTEM,
                    tools=_EMAIL_TOOLS,
                    messages=messages,
                ) as stream:
                    async for event in stream:
                        if (
                            event.type == "content_block_delta"
                            and hasattr(event.delta, "text")
                        ):
                            yield _sse({"type": "text", "text": event.delta.text})

                    final = await stream.get_final_message()
            except Exception as exc:
                yield _sse({"type": "error", "text": str(exc)})
                return

            if final.stop_reason == "end_turn":
                messages.append({
                    "role": "assistant",
                    "content": "".join(b.text for b in final.content if b.type == "text"),
                })
                _sessions[session_id] = messages
                yield _sse({"type": "done"})
                break

            if final.stop_reason == "tool_use":
                tool_uses = [b for b in final.content if b.type == "tool_use"]
                messages.append({"role": "assistant", "content": [_content_to_dict(b) for b in final.content]})

                tool_results = []
                for tu in tool_uses:
                    yield _sse({"type": "tool_call", "name": tu.name, "input": tu.input})
                    result = await loop.run_in_executor(_executor, _run_email_tool, tu.name, tu.input)
                    yield _sse({"type": "tool_result", "name": tu.name})
                    tool_results.append({"type": "tool_result", "tool_use_id": tu.id, "content": result})

                messages.append({"role": "user", "content": tool_results})
            else:
                yield _sse({"type": "done"})
                break

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
