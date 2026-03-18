"""Email client for IMAP/SMTP operations."""

import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import ssl
import threading
from typing import Optional, List
from datetime import datetime


class EmailClient:
    """Client for reading and sending emails via IMAP and SMTP."""
    
    def __init__(self, email_address: str, password: str, imap_server: str = 'imap.gmail.com', 
                 smtp_server: str = 'smtp.gmail.com', imap_port: int = 993, smtp_port: int = 587):
        """Initialize email client.
        
        Args:
            email_address: Email address for the account
            password: Password or app-specific password (for Gmail, use app password)
            imap_server: IMAP server address (default: imap.gmail.com for Gmail)
            smtp_server: SMTP server address (default: smtp.gmail.com for Gmail)
            imap_port: IMAP port (default: 993 for SSL)
            smtp_port: SMTP port (default: 587 for TLS)
        """
        self.email_address = email_address
        self.password = password
        self.imap_server = imap_server
        self.smtp_server = smtp_server
        self.imap_port = imap_port
        self.smtp_port = smtp_port
        self.imap_connection = None
        self._lock = threading.RLock()
        self._connect_imap()
    
    def _select_folder(self, folder: str):
        """Select an IMAP folder, quoting names that contain spaces."""
        if ' ' in folder:
            folder = f'"{folder}"'
        return self.imap_connection.select(folder)

    def _connect_imap(self):
        """Connect to IMAP server."""
        try:
            self.imap_connection = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            self.imap_connection.login(self.email_address, self.password)
        except Exception as e:
            raise Exception(f"Failed to connect to IMAP server: {str(e)}")
    
    def list_emails(self, folder: str = 'INBOX', max_results: int = 10, unread_only: bool = False) -> List[dict]:
        """List emails from a folder.

        Args:
            folder: Mailbox folder name (default: INBOX)
            max_results: Maximum number of emails to retrieve
            unread_only: If True, only return unread emails

        Returns:
            List of email dictionaries with subject, from, date, and preview
        """
        with self._lock:
            try:
                status, _ = self._select_folder(folder)
                if status != 'OK':
                    raise Exception(f"Cannot select folder: {folder}")

                search_criteria = 'UNSEEN' if unread_only else 'ALL'
                _, email_ids = self.imap_connection.search(None, search_criteria)

                email_list = email_ids[0].split()[-max_results:][::-1]

                emails = []
                for email_id in email_list:
                    email_data = self.get_email(email_id.decode(), folder=folder)
                    if email_data:
                        emails.append(email_data)

                return emails
            except Exception as e:
                raise Exception(f"Error listing emails: {str(e)}")
    
    def get_email(self, email_id: str, folder: str = 'INBOX') -> Optional[dict]:
        """Get full email details.

        Args:
            email_id: Email ID from IMAP
            folder: Mailbox folder the email is in

        Returns:
            Dictionary containing email details
        """
        with self._lock:
            try:
                status, _ = self._select_folder(folder)
                if status != 'OK':
                    return None
                _, msg_data = self.imap_connection.fetch(email_id, '(RFC822)')
                raw = next((part[1] for part in msg_data if isinstance(part, tuple)), None)
                if not raw:
                    return None
                msg = email.message_from_bytes(raw)

                subject = msg.get('Subject', 'No Subject')
                sender = msg.get('From', 'Unknown')
                date = msg.get('Date', 'Unknown')
                body = self._get_body(msg)

                return {
                    'id': email_id,
                    'subject': subject,
                    'from': sender,
                    'date': date,
                    'body': body[:500] + '...' if len(body) > 500 else body
                }
            except Exception as e:
                print(f"Error getting email {email_id}: {str(e)}")
                return None
    
    def _get_body(self, msg: email.message.Message) -> str:
        """Extract body from email message.
        
        Args:
            msg: Email message object
            
        Returns:
            Email body text
        """
        body = ''
        
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == 'text/plain':
                    payload = part.get_payload(decode=True)
                    if payload:
                        body = payload.decode('utf-8', errors='ignore')
                        break
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                body = payload.decode('utf-8', errors='ignore')
            else:
                body = msg.get_payload()
        
        return body.strip()
    
    def search_emails(self, query: str, folder: str = 'INBOX', max_results: int = 10) -> List[dict]:
        """Search emails by query.
        
        Args:
            query: Search query (IMAP search criteria: e.g., 'SUBJECT "invoice"', 'FROM "sender@example.com"', 'UNSEEN')
            folder: Mailbox folder to search
            max_results: Maximum results to return
            
        Returns:
            List of matching emails
        """
        with self._lock:
            try:
                status, _ = self._select_folder(folder)
                if status != 'OK':
                    raise Exception(f"Cannot select folder: {folder}")
                _, email_ids = self.imap_connection.search(None, query)

                email_list = email_ids[0].split()[-max_results:][::-1]

                emails = []
                for email_id in email_list:
                    email_data = self.get_email(email_id.decode(), folder=folder)
                    if email_data:
                        emails.append(email_data)

                return emails
            except Exception as e:
                raise Exception(f"Error searching emails: {str(e)}")
    
    def get_unread_emails(self, folder: str = 'INBOX', max_results: int = 10) -> List[dict]:
        """Get unread emails.
        
        Args:
            folder: Mailbox folder (default: INBOX)
            max_results: Maximum emails to retrieve
            
        Returns:
            List of unread emails
        """
        return self.list_emails(folder=folder, max_results=max_results, unread_only=True)
    
    def get_emails_from_sender(self, sender: str, folder: str = 'INBOX', max_results: int = 10) -> List[dict]:
        """Get emails from a specific sender.
        
        Args:
            sender: Sender email address
            folder: Mailbox folder to search
            max_results: Maximum emails to retrieve
            
        Returns:
            List of emails from sender
        """
        return self.search_emails(query=f'FROM "{sender}"', folder=folder, max_results=max_results)
    
    def get_emails_by_subject(self, subject: str, folder: str = 'INBOX', max_results: int = 10) -> List[dict]:
        """Get emails by subject.
        
        Args:
            subject: Subject text to search for
            folder: Mailbox folder to search
            max_results: Maximum emails to retrieve
            
        Returns:
            List of matching emails
        """
        return self.search_emails(query=f'SUBJECT "{subject}"', folder=folder, max_results=max_results)
    
    def list_folders(self) -> List[str]:
        """List all mailbox folders.
        
        Returns:
            List of folder names
        """
        with self._lock:
            try:
                _, folders = self.imap_connection.list()
                folder_list = []
                for folder in folders:
                    decoded = folder.decode()
                    if r'\Noselect' in decoded:
                        continue
                    parts = decoded.split(' "/" ')
                    if len(parts) > 1:
                        folder_name = parts[1].strip('"')
                        folder_list.append(folder_name)
                return folder_list
            except Exception as e:
                raise Exception(f"Error listing folders: {str(e)}")
    
    def send_email(self, recipient: str, subject: str, body: str, html: bool = False) -> bool:
        """Send an email.
        
        Args:
            recipient: Recipient email address
            subject: Email subject
            body: Email body text
            html: If True, body is treated as HTML
            
        Returns:
            True if successful
        """
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = recipient
            msg['Subject'] = subject
            
            if html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            # Connect to SMTP server
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.email_address, self.password)
                server.send_message(msg)
            
            return True
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False
    
    def close(self):
        """Close IMAP connection."""
        if self.imap_connection:
            try:
                self.imap_connection.close()
            except Exception:
                pass
            self.imap_connection.logout()
