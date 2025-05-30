#!/usr/bin/env python3
"""
Test script for YouTube MCP Server
Run this to verify your setup before using with Claude Desktop
"""

import os
import sys
from pathlib import Path

def check_requirements():
    """Check if all required packages are installed"""
    required_packages = [
        "mcp",
        "httpx", 
        "google.auth",
        "googleapiclient"
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print("❌ Missing packages:", ", ".join(missing))
        print("Run: pip install -r requirements.txt")
        return False
    
    print("✅ All packages installed")
    return True

def check_credentials():
    """Check if credentials are set up"""
    if os.path.exists("credentials.json"):
        print("✅ credentials.json found")
        return True
    else:
        print("❌ credentials.json not found")
        print("Run the setup_youtube_auth tool in Claude Desktop first")
        return False

def check_python_version():
    """Check Python version"""
    if sys.version_info >= (3, 10):
        print(f"✅ Python {sys.version.split()[0]} (>= 3.10)")
        return True
    else:
        print(f"❌ Python {sys.version.split()[0]} (< 3.10)")
        return False

def main():
    print("YouTube MCP Server - Setup Verification")
    print("=" * 40)
    
    all_good = True
    all_good &= check_python_version()
    all_good &= check_requirements()
    all_good &= check_credentials()
    
    print("=" * 40)
    if all_good:
        print("✅ Setup complete! You can now use the server with Claude Desktop")
    else:
        print("❌ Please fix the issues above before proceeding")
        sys.exit(1)

if __name__ == "__main__":
    main()
