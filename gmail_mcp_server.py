"""MCP Server for email operations via IMAP/SMTP."""

import json
import logging
import os
from mcp.server.fastmcp import FastMCP
from gmail_client import EmailClient
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Initialize MCP Server
mcp = FastMCP("email-mcp-server")

# Initialize email client at module level
_email_address = os.getenv('EMAIL_ADDRESS')
_password = os.getenv('EMAIL_PASSWORD')
_imap_server = os.getenv('IMAP_SERVER', 'imap.gmail.com')
_smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')

email_client: EmailClient = None
if _email_address and _password:
    try:
        email_client = EmailClient(
            email_address=_email_address,
            password=_password,
            imap_server=_imap_server,
            smtp_server=_smtp_server
        )
        logger.info(f"Email client initialized for {_email_address}")
    except Exception as e:
        logger.error(f"Failed to initialize email client: {e}")

@mcp.tool()
def list_emails(
    max_results: int = 10,
    unread_only: bool = False,
    folder: str = "INBOX"
) -> str:
    """List emails from a mailbox folder.
    
    Args:
        max_results: Maximum number of emails to retrieve (default: 10)
        unread_only: If True, only return unread emails (default: False)
        folder: Mailbox folder name (default: INBOX)
    
    Returns:
        JSON string with list of emails
    """
    try:
        emails = email_client.list_emails(folder=folder, max_results=max_results, unread_only=unread_only)
        return json.dumps(emails, indent=2, default=str)
    except Exception as e:
        logger.error(f"Error listing emails: {e}")
        return json.dumps({"error": str(e)})


@mcp.tool()
def get_unread_emails(max_results: int = 10, folder: str = "INBOX") -> str:
    """Get unread emails from a folder.
    
    Args:
        max_results: Maximum number of unread emails to retrieve (default: 10)
        folder: Mailbox folder name (default: INBOX)
    
    Returns:
        JSON string with list of unread emails
    """
    try:
        emails = email_client.get_unread_emails(folder=folder, max_results=max_results)
        return json.dumps(emails, indent=2, default=str)
    except Exception as e:
        logger.error(f"Error getting unread emails: {e}")
        return json.dumps({"error": str(e)})


@mcp.tool()
def get_emails_from_sender(
    sender: str,
    max_results: int = 10,
    folder: str = "INBOX"
) -> str:
    """Get emails from a specific sender.
    
    Args:
        sender: Email address of the sender
        max_results: Maximum number of emails to retrieve (default: 10)
        folder: Mailbox folder to search (default: INBOX)
    
    Returns:
        JSON string with list of emails from that sender
    """
    try:
        emails = email_client.get_emails_from_sender(sender=sender, folder=folder, max_results=max_results)
        return json.dumps(emails, indent=2, default=str)
    except Exception as e:
        logger.error(f"Error getting emails from sender: {e}")
        return json.dumps({"error": str(e)})


@mcp.tool()
def search_emails(
    query: str,
    max_results: int = 10,
    folder: str = "INBOX"
) -> str:
    """Search emails using IMAP search criteria.
    
    Args:
        query: IMAP search query (e.g., 'SUBJECT "invoice"', 'UNSEEN', 'FROM "user@example.com"')
        max_results: Maximum number of results to retrieve (default: 10)
        folder: Mailbox folder to search (default: INBOX)
    
    Returns:
        JSON string with search results
    """
    try:
        emails = email_client.search_emails(query=query, folder=folder, max_results=max_results)
        return json.dumps(emails, indent=2, default=str)
    except Exception as e:
        logger.error(f"Error searching emails: {e}")
        return json.dumps({"error": str(e)})


@mcp.tool()
def get_email_details(message_id: str) -> str:
    """Get full details of a specific email.
    
    Args:
        message_id: Email ID from IMAP
    
    Returns:
        JSON string with complete email details
    """
    try:
        email = email_client.get_email(message_id=message_id)
        if email:
            return json.dumps(email, indent=2, default=str)
        else:
            return json.dumps({"error": "Email not found"})
    except Exception as e:
        logger.error(f"Error getting email details: {e}")
        return json.dumps({"error": str(e)})


@mcp.tool()
def list_folders() -> str:
    """List all available mailbox folders.
    
    Returns:
        JSON string with list of folder names
    """
    try:
        folders = email_client.list_folders()
        return json.dumps({"folders": folders}, indent=2)
    except Exception as e:
        logger.error(f"Error listing folders: {e}")
        return json.dumps({"error": str(e)})


@mcp.tool()
def send_email(
    recipient: str,
    subject: str,
    body: str,
    html: bool = False
) -> str:
    """Send an email.
    
    Args:
        recipient: Recipient email address
        subject: Email subject
        body: Email body text
        html: If True, body is treated as HTML (default: False)
    
    Returns:
        JSON string with success status
    """
    try:
        success = email_client.send_email(recipient=recipient, subject=subject, body=body, html=html)
        if success:
            return json.dumps({"success": True, "message": "Email sent successfully"})
        else:
            return json.dumps({"success": False, "message": "Failed to send email"})
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        return json.dumps({"error": str(e)})


@mcp.tool()
def get_emails_by_subject(
    subject: str,
    max_results: int = 10,
    folder: str = "INBOX"
) -> str:
    """Get emails by subject text.
    
    Args:
        subject: Subject text to search for
        max_results: Maximum emails to retrieve (default: 10)
        folder: Mailbox folder to search (default: INBOX)
    
    Returns:
        JSON string with matching emails
    """
    try:
        emails = email_client.get_emails_by_subject(subject=subject, folder=folder, max_results=max_results)
        return json.dumps(emails, indent=2, default=str)
    except Exception as e:
        logger.error(f"Error searching by subject: {e}")
        return json.dumps({"error": str(e)})


if __name__ == "__main__":
    if not email_client:
        logger.error("EMAIL_ADDRESS and EMAIL_PASSWORD environment variables must be set")
        raise ValueError("EMAIL_ADDRESS and EMAIL_PASSWORD environment variables must be set")
    try:
        mcp.run()
    finally:
        email_client.close()
