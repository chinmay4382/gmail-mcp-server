FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY gmail_client.py gmail_mcp_server.py api_server.py ./
COPY ui/ ./ui/

# Default env vars (overridden at runtime)
ENV EMAIL_ADDRESS=""
ENV EMAIL_PASSWORD=""
ENV IMAP_SERVER="imap.gmail.com"
ENV SMTP_SERVER="smtp.gmail.com"

CMD ["python", "gmail_mcp_server.py"]
