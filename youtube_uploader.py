#!/usr/bin/env python3
"""
YouTube MCP Server - Upload videos to YouTube via MCP
"""

import os
import sys
import json
import asyncio
import mimetypes
from typing import Any, Optional
from pathlib import Path

from mcp.server import FastMCP
import httpx
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# Initialize FastMCP server
mcp = FastMCP("youtube-uploader")

# YouTube API settings
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"

# OAuth2 token storage - use absolute paths to ensure files are found
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(SCRIPT_DIR, "token.json")
CREDENTIALS_FILE = os.path.join(SCRIPT_DIR, "credentials.json")

def get_authenticated_service():
    """Get authenticated YouTube service"""
    creds = None
    
    # Token file stores the user's access and refresh tokens
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                raise Exception(
                    f"Missing {CREDENTIALS_FILE}. Please download OAuth2 credentials from Google Cloud Console."
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    
    return build(API_SERVICE_NAME, API_VERSION, credentials=creds)

def initialize_upload(youtube, options):
    """Initialize video upload"""
    tags = None
    if options.get("keywords"):
        tags = options["keywords"].split(",")

    body = {
        "snippet": {
            "title": options["title"],
            "description": options.get("description", ""),
            "tags": tags,
            "categoryId": options.get("category", "22")  # Default to People & Blogs
        },
        "status": {
            "privacyStatus": options.get("privacy_status", "private"),
            "selfDeclaredMadeForKids": options.get("made_for_kids", False)
        }
    }

    # Check if file exists
    if not os.path.exists(options["file"]):
        raise FileNotFoundError(f"Video file not found: {options['file']}")

    # Create media upload object
    media = MediaFileUpload(
        options["file"],
        chunksize=-1,
        resumable=True,
        mimetype=mimetypes.guess_type(options["file"])[0] or "video/*"
    )

    # Call the API's videos.insert method to create and upload the video
    insert_request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=media
    )

    return resumable_upload(insert_request)

def resumable_upload(insert_request):
    """Execute upload with resumable support"""
    response = None
    error = None
    retry = 0
    
    while response is None:
        try:
            status, response = insert_request.next_chunk()
            if response is not None:
                if 'id' in response:
                    return {
                        "success": True,
                        "video_id": response['id'],
                        "url": f"https://www.youtube.com/watch?v={response['id']}"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Upload failed with unexpected response: {response}"
                    }
        except HttpError as e:
            if e.resp.status in [500, 502, 503, 504]:
                error = f"HTTP error {e.resp.status}: {e.content}"
                retry += 1
                if retry > 3:
                    return {"success": False, "error": error}
                
                import time
                time.sleep(5 * retry)
            else:
                return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    return {"success": False, "error": "Upload failed"}

@mcp.tool()
async def upload_video(
    file_path: str,
    title: str,
    description: str = "",
    keywords: str = "",
    category_id: str = "22",
    privacy_status: str = "private",
    made_for_kids: bool = False
) -> str:
    """Upload a video to YouTube.
    
    Args:
        file_path: Path to the video file to upload
        title: Title of the video
        description: Description of the video
        keywords: Comma-separated list of keywords/tags
        category_id: YouTube category ID (default: 22 - People & Blogs)
        privacy_status: Privacy status (private, unlisted, or public)
        made_for_kids: Whether the video is made for kids
    
    Returns:
        Upload status with video ID and URL if successful
    """
    try:
        # Get authenticated YouTube service
        youtube = get_authenticated_service()
        
        # Prepare upload options
        options = {
            "file": file_path,
            "title": title,
            "description": description,
            "keywords": keywords,
            "category": category_id,
            "privacy_status": privacy_status,
            "made_for_kids": made_for_kids
        }
        
        # Upload video
        result = initialize_upload(youtube, options)
        
        if result["success"]:
            return f"Video uploaded successfully!\nVideo ID: {result['video_id']}\nURL: {result['url']}"
        else:
            return f"Upload failed: {result['error']}"
            
    except Exception as e:
        return f"Error uploading video: {str(e)}"

@mcp.tool()
async def check_upload_quota() -> str:
    """Check YouTube API quota usage and limits.
    
    Returns:
        Information about API quota (note: detailed quota info requires additional API setup)
    """
    try:
        youtube = get_authenticated_service()
        
        # Get channel info to verify authentication
        request = youtube.channels().list(
            part="snippet,contentDetails,statistics",
            mine=True
        )
        response = request.execute()
        
        if response.get("items"):
            channel = response["items"][0]
            return f"""YouTube API Status:
✅ Authentication successful
Channel: {channel['snippet']['title']}
Subscribers: {channel['statistics'].get('subscriberCount', 'Hidden')}
Videos: {channel['statistics'].get('videoCount', 'Unknown')}

Note: Upload quota is 1,600,000 units per day. Each upload costs ~1,600 units.
This allows approximately 1,000 video uploads per day."""
        else:
            return "Authentication successful but no channel found."
            
    except Exception as e:
        return f"Error checking quota: {str(e)}"

@mcp.tool()
async def list_video_categories(region_code: str = "US") -> str:
    """List available YouTube video categories for a region.
    
    Args:
        region_code: ISO 3166-1 alpha-2 country code (default: US)
    
    Returns:
        List of video categories with their IDs
    """
    try:
        youtube = get_authenticated_service()
        
        request = youtube.videoCategories().list(
            part="snippet",
            regionCode=region_code
        )
        response = request.execute()
        
        categories = []
        for item in response.get("items", []):
            if item["snippet"]["assignable"]:
                categories.append(f"ID: {item['id']} - {item['snippet']['title']}")
        
        return "Available YouTube Categories:\n" + "\n".join(categories)
        
    except Exception as e:
        return f"Error listing categories: {str(e)}"

@mcp.tool()
async def authorize_youtube_access() -> str:
    """Initiate OAuth 2.0 authorization flow for YouTube access.
    
    This tool starts the OAuth 2.0 authorization process to allow users to
    authenticate with their Google/YouTube account. The user will be directed
    to Google's authorization server in their browser.
    
    OAuth 2.0 Flow:
    1. User initiates authorization (this tool)
    2. Browser opens to Google's authorization server
    3. User signs in to their Google/YouTube account
    4. User grants permission for the app to access their YouTube channel
    5. Access token is stored locally for future uploads
    
    Returns:
        Status of the authorization attempt
    """
    try:
        if not os.path.exists(CREDENTIALS_FILE):
            return """❌ OAuth2 client credentials not found.
            
Please set up OAuth2 credentials first using 'setup_youtube_auth' or ensure
credentials.json exists in the working directory.

To get OAuth2 credentials:
1. Go to Google Cloud Console (https://console.cloud.google.com/)
2. Enable YouTube Data API v3
3. Create OAuth2 credentials (Desktop application type)
4. Use setup_youtube_auth tool with your credentials"""

        # Check if user is already authenticated
        if os.path.exists(TOKEN_FILE):
            try:
                creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
                if creds and creds.valid:
                    # Test the credentials
                    youtube = build(API_SERVICE_NAME, API_VERSION, credentials=creds)
                    request = youtube.channels().list(part="snippet", mine=True)
                    response = request.execute()
                    
                    if response.get("items"):
                        channel = response["items"][0]
                        return f"""✅ Already authenticated!
                        
YouTube Channel: {channel['snippet']['title']}
Access token is valid and ready for uploads.

You can now upload videos using the 'upload_video' tool."""
                    
            except Exception:
                # Token exists but is invalid, will re-authenticate below
                pass

        # Start OAuth flow
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
        
        # Use run_local_server with explicit redirect URI
        print("🔐 Starting OAuth 2.0 authorization flow...", file=sys.stderr)
        print("🌐 Opening browser for Google authentication...", file=sys.stderr)
        print(f"📍 Using redirect URI: http://localhost:8080/", file=sys.stderr)
        
        creds = flow.run_local_server(
            port=8080,
            host='localhost',
            prompt='consent',
            authorization_prompt_message="Opening browser for YouTube authorization...",
            success_message="Authorization successful! You can close this tab."
        )
        
        # Save credentials for future use
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
        
        # Verify authentication worked by getting channel info
        youtube = build(API_SERVICE_NAME, API_VERSION, credentials=creds)
        request = youtube.channels().list(part="snippet,statistics", mine=True)
        response = request.execute()
        
        if response.get("items"):
            channel = response["items"][0]
            return f"""✅ Authorization successful!

YouTube Channel: {channel['snippet']['title']}
Subscribers: {channel['statistics'].get('subscriberCount', 'Hidden')}
Videos: {channel['statistics'].get('videoCount', 'Unknown')}

🎬 You can now upload videos using the 'upload_video' tool.
🔑 Your access tokens have been saved for future use."""
        else:
            return """✅ Authorization completed but no YouTube channel found.
            
Make sure you have a YouTube channel associated with your Google account."""
            
    except Exception as e:
        error_msg = str(e)
        if "redirect_uri_mismatch" in error_msg:
            return """❌ OAuth Configuration Error: redirect_uri_mismatch

This means the redirect URI in your OAuth2 credentials doesn't match what the app is using.

To fix this:
1. Go to Google Cloud Console > APIs & Services > Credentials
2. Edit your OAuth2 client
3. Add 'http://localhost:8080' to Authorized redirect URIs
4. Try authorization again"""
        
        elif "access_denied" in error_msg:
            return """❌ Authorization denied by user.

The user declined to grant permission. To upload videos, you need to:
1. Run this tool again
2. Grant permission when prompted in the browser"""
        
        else:
            return f"""❌ Authorization failed: {error_msg}

Common solutions:
1. Ensure YouTube Data API v3 is enabled in Google Cloud Console
2. Check that OAuth2 credentials are properly configured
3. Make sure redirect URI includes 'http://localhost:8080'
4. Try running the authorization again"""

@mcp.tool()
async def setup_youtube_auth(client_id: str, client_secret: str, project_id: str) -> str:
    """Set up YouTube OAuth2 credentials.
    
    Args:
        client_id: OAuth2 client ID from Google Cloud Console
        client_secret: OAuth2 client secret
        project_id: Google Cloud project ID
    
    Returns:
        Status of credential setup
    """
    try:
        credentials = {
            "installed": {
                "client_id": client_id,
                "client_secret": client_secret,
                "project_id": project_id,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "redirect_uris": ["http://localhost"]
            }
        }
        
        with open(CREDENTIALS_FILE, 'w') as f:
            json.dump(credentials, f, indent=2)
        
        return f"Credentials saved to {CREDENTIALS_FILE}. Run 'upload_video' to authenticate."
        
    except Exception as e:
        return f"Error setting up credentials: {str(e)}"

if __name__ == "__main__":
    # Run the server
    mcp.run(transport='stdio')
