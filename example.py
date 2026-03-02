#!/usr/bin/env python3
"""
Example usage of the Email MCP Server.

This script demonstrates how to set up and use the email MCP server.
"""

import os
from dotenv import load_dotenv
from gmail_client import EmailClient


def main():
    """Demonstrate email client usage."""
    
    # Load environment variables from .env file
    load_dotenv()
    
    email_address = os.getenv('EMAIL_ADDRESS')
    password = os.getenv('EMAIL_PASSWORD')
    
    if not email_address or not password:
        print("Please set EMAIL_ADDRESS and EMAIL_PASSWORD in your .env file")
        return
    
    print(f"Connecting to {email_address}...")
    
    try:
        # Initialize the email client
        client = EmailClient(email_address=email_address, password=password)
        
        # List available folders
        print("\n--- Available Folders ---")
        folders = client.list_folders()
        for folder in folders[:10]:  # Show first 10 folders
            print(f"  {folder}")
        
        # Get unread emails
        print("\n--- Unread Emails ---")
        unread = client.get_unread_emails(max_results=5)
        for email in unread:
            print(f"From: {email['from']}")
            print(f"Subject: {email['subject']}")
            print(f"Date: {email['date']}")
            print(f"Preview: {email['body'][:100]}...")
            print()
        
        # Search for emails from a sender
        print("\n--- Emails from a Sender ---")
        sender_emails = client.get_emails_from_sender("support@example.com", max_results=3)
        for email in sender_emails:
            print(f"Subject: {email['subject']}")
            print()
        
        # Search by subject
        print("\n--- Search by Subject ---")
        subject_emails = client.get_emails_by_subject("invoice", max_results=3)
        print(f"Found {len(subject_emails)} emails with 'invoice' in subject")
        for email in subject_emails:
            print(f"  {email['subject']}")
        
        # Send a test email
        print("\n--- Sending Email ---")
        success = client.send_email(
            recipient="your_email@example.com",
            subject="Test Email from MCP Server",
            body="This is a test email sent via IMAP/SMTP MCP server."
        )
        if success:
            print("Email sent successfully!")
        else:
            print("Failed to send email")
        
        # Close connection
        client.close()
        print("\nConnection closed.")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
