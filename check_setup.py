#!/usr/bin/env python3
"""Setup script for Email MCP Server."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
# load environment variables from .env if available

def check_env_variables():
    """Check if email credentials are configured in the environment."""
    load_dotenv() #is already called at import time
    email = os.getenv('EMAIL_ADDRESS')
    password = os.getenv('EMAIL_PASSWORD')
    print(f"Checking EMAIL_ADDRESS: {email}")
    print(f"Checking EMAIL_PASSWORD: {'*' * len(password) if password else None}")
    if email and password:
        print(f"✓ Email credentials configured ({email})")
        return True
    else:
        print("✗ Email credentials not configured")
        print("\nSetup instructions:")
        print("1. Copy .env.example to .env")
        print("2. Edit .env with your EMAIL_ADDRESS and EMAIL_PASSWORD")
        print("3. For Gmail, generate an App Password: https://myaccount.google.com/apppasswords")
        print("4. Re-run this script or export the variables manually (source .env)")
        return False


def check_env_file():
    """Check if .env file exists."""
    if os.path.exists('.env'):
        print("✓ .env file found")
        return True
    else:
        print("✗ .env file not found")
        print("Run: cp .env.example .env")
        return False


def check_python_version():
    """Check Python version."""
    if sys.version_info >= (3, 10):
        print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} (required: 3.10+)")
        return True
    else:
        print(f"✗ Python {sys.version_info.major}.{sys.version_info.minor} (required: 3.10+)")
        return False


def install_dependencies():
    """Check if dependencies are installed."""
    try:
        import mcp
        print("✓ MCP library installed")
    except ImportError:
        print("✗ MCP library not found")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True


def main():
    """Run setup checks."""
    print("Email MCP Server Setup Check\n")
    print("=" * 40)
    
    checks = [
        ("Python version", check_python_version),
        ("Dependencies", install_dependencies),
        (".env file", check_env_file),
        ("Email credentials", check_env_variables),
    ]
    
    all_passed = True
    for name, check_fn in checks:
        print(f"\nChecking {name}...")
        if not check_fn():
            all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("\n✓ All checks passed! Ready to start the server.")
        print("Run: python gmail_mcp_server.py")
    else:
        print("\n✗ Some checks failed. Please complete the setup steps above.")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
