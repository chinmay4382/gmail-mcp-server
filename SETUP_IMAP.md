# Email Setup Guide for MCP Server

This guide covers how to set up the Email MCP Server with various email providers using IMAP and SMTP.

## Gmail

### Enable IMAP and SMTP

1. Go to [Gmail Settings](https://myaccount.google.com/security)
2. Check that 2-Step Verification is enabled (recommended for security)
3. Go to [App Passwords](https://myaccount.google.com/apppasswords)
4. Generate an app password for "Mail" and "Windows Computer" (or your device type)
5. Copy the 16-character app password

### Configuration

Add to `.env`:
```
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=xxxx xxxx xxxx xxxx
IMAP_SERVER=imap.gmail.com
SMTP_SERVER=smtp.gmail.com
```

**Note:** Use the 16-character app password, NOT your Gmail password.

---

## Microsoft Outlook / Outlook.com

### Enable IMAP and SMTP

1. Go to [Account Security Settings](https://account.microsoft.com/security)
2. Check that your account is secure (enable 2FA if possible)
3. Go to [Manage Your App Passwords](https://account.microsoft.com/security/app-passwords) (if 2FA enabled)
4. Generate an app password for "Mail" and "Other devices"

### Configuration

Add to `.env`:
```
EMAIL_ADDRESS=your_email@outlook.com
EMAIL_PASSWORD=your_password
IMAP_SERVER=imap-mail.outlook.com
SMTP_SERVER=smtp-mail.outlook.com
```

**Note:** 
- If you have 2FA enabled, use the app password
- If you don't have 2FA, use your regular Outlook password
- You may need to enable "Less secure apps" in security settings

---

## Yahoo Mail

### Enable IMAP and SMTP

1. Go to [Yahoo Account Security](https://login.yahoo.com/account/security)
2. Enable 2-Step Verification (recommended)
3. Go to [Generate App Password](https://login.yahoo.com/account/security) → Generate app password
4. Select "Mail" as the app type
5. Select "Other device" and type your device name
6. Copy the generated 16-character password

### Configuration

Add to `.env`:
```
EMAIL_ADDRESS=your_email@yahoo.com
EMAIL_PASSWORD=xxxx xxxx xxxx xxxx
IMAP_SERVER=imap.mail.yahoo.com
SMTP_SERVER=smtp.mail.yahoo.com
```

**Note:** Always use the app-generated password with Yahoo Mail, not your regular password.

---

## ProtonMail / ProtonMail Bridge

ProtonMail requires special setup because the service uses end-to-end encryption.

### Requirements

1. Download and install [ProtonMail Bridge](https://protonmail.com/bridge/)
2. Sign in with your ProtonMail account
3. Enable both IMAP and SMTP in Bridge settings
4. Note the local IMAP/SMTP server addresses shown in Bridge (usually localhost:1143 for IMAP, localhost:1025 for SMTP)

### Configuration

Add to `.env`:
```
EMAIL_ADDRESS=your_email@protonmail.com
EMAIL_PASSWORD=your_protonmail_password
IMAP_SERVER=127.0.0.1
IMAP_PORT=1143
SMTP_SERVER=127.0.0.1
SMTP_PORT=1025
```

---

## Apple iCloud Mail

### Enable IMAP and SMTP

1. Go to [Apple ID Account](https://appleid.apple.com/)
2. Go to "Security" → "App-Specific Passwords"
3. Generate an app password for Mail
4. Copy the 16-character password

### Configuration

Add to `.env`:
```
EMAIL_ADDRESS=your_email@icloud.com
EMAIL_PASSWORD=xxxx xxxx xxxx xxxx
IMAP_SERVER=imap.mail.me.com
SMTP_SERVER=smtp.mail.me.com
```

**Note:** Use the app-specific password, not your iCloud password.

---

## Gmail (Custom Domain / Google Workspace)

### Enable IMAP and SMTP

1. Go to [Google Workspace Security](https://admin.google.com/u/0/ac/security)
2. Enable IMAP/POP for all users (or just your account)
3. Go to [Google Account](https://myaccount.google.com/)
4. Enable 2-Step Verification
5. Generate an [App Password](https://myaccount.google.com/apppasswords)

### Configuration

Add to `.env`:
```
EMAIL_ADDRESS=your_email@your_domain.com
EMAIL_PASSWORD=xxxx xxxx xxxx xxxx
IMAP_SERVER=imap.gmail.com
SMTP_SERVER=smtp.gmail.com
```

---

## Troubleshooting Connection Issues

### "Connection refused" or "Connection timed out"

- Verify the IMAP/SMTP server addresses are correct
- Check firewall settings - ports 993 (IMAP) and 587 (SMTP) must be open
- Some corporate networks block these ports - try using VPN if available

### "Authentication failed" or "Invalid credentials"

- **Gmail**: Ensure you're using an App Password, not your regular Gmail password
- **Outlook**: If 2FA is enabled, use an app password; otherwise use your email password
- **Yahoo**: Always use app-generated password
- **Other**: Verify username/password is correct

### "Certificate verification failed"

- This usually happens with corporate firewalls or VPN
- The server uses SSL certificates by default
- You can disable certificate verification in `gmail_client.py` if needed (not recommended for security):
  ```python
  context = ssl.create_default_context()
  context.check_hostname = False
  context.verify_mode = ssl.CERT_NONE
  ```

### "Invalid folder name"

- Use exact folder names from `list_folders()` tool
- Gmail folder names are usually: `INBOX`, `[Gmail]/All Mail`, `[Gmail]/Sent Mail`, `[Gmail]/Drafts`, etc.
- Different providers use different folder names

---

## Common IMAP Search Queries

These IMAP search queries work across all email providers:

```python
# Unread emails
search_emails("UNSEEN")

# Emails from specific sender
search_emails('FROM "user@example.com"')

# Emails with specific subject
search_emails('SUBJECT "invoice"')

# Flagged/starred emails
search_emails("FLAGGED")

# Unflagged emails
search_emails("UNFLAGGED")

# Emails before a date
search_emails('BEFORE "1-Jan-2024"')

# Emails since a date
search_emails('SINCE "1-Jan-2024"')

# Large emails
search_emails("LARGER 1000000")

# Recent emails
search_emails("RECENT")

# Combination (AND)
search_emails('UNSEEN FROM "boss@company.com"')
search_emails('FLAGGED SUBJECT "urgent"')
```

---

## Security Best Practices

1. **Never use your main account password** - Use app-specific passwords when available
2. **Enable 2-Factor Authentication** - Makes your account more secure
3. **Keep `.env` file secret** - Never commit it to version control
4. **Rotate credentials periodically** - Generate new app passwords every 3-6 months
5. **Use HTTPS/TLS** - The server uses SSL/TLS by default (recommended)
6. **Review connected apps** - Regularly check which apps have access to your email

---

## Tested Providers

- ✅ Gmail / Google Workspace
- ✅ Outlook / Outlook.com
- ✅ Yahoo Mail
- ✅ ProtonMail (with Bridge)
- ✅ iCloud Mail
- ✅ Postfix servers
- ✅ Custom SMTP/IMAP servers

If you're using a different provider and need help, check their official IMAP/SMTP documentation.
