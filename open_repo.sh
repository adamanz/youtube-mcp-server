#!/bin/bash
# Commands to open the YouTube MCP Server repository

# Navigate to the repository
cd /tmp/youtube-mcp-server

# List contents
ls -la

# Open in VS Code (if installed)
code /tmp/youtube-mcp-server

# Open in Sublime Text (if installed)
subl /tmp/youtube-mcp-server

# Open in Finder (macOS)
open /tmp/youtube-mcp-server

# Open in File Explorer (Windows)
explorer /tmp/youtube-mcp-server

# Open in default file manager (Linux)
xdg-open /tmp/youtube-mcp-server

# View the README
cat /tmp/youtube-mcp-server/README.md

# Quick setup check
python /tmp/youtube-mcp-server/test_setup.py
