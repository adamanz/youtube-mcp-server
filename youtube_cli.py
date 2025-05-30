#!/usr/bin/env python3
"""
YouTube CLI Uploader - Standalone command-line tool to upload videos to YouTube
"""

import os
import sys
import json
import argparse
import mimetypes
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# YouTube API settings
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"

# OAuth2 token storage
TOKEN_FILE = "token.json"
CREDENTIALS_FILE = "credentials.json"

def get_authenticated_service():
    """Get authenticated YouTube service"""
    creds = None
    
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                print(f"Error: Missing {CREDENTIALS_FILE}")
                print("Please download OAuth2 credentials from Google Cloud Console")
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    
    return build(API_SERVICE_NAME, API_VERSION, credentials=creds)

def upload_video(youtube, options):
    """Upload video to YouTube"""
    tags = None
    if options['keywords']:
        tags = options['keywords'].split(',')

    body = {
        'snippet': {
            'title': options['title'],
            'description': options['description'],
            'tags': tags,
            'categoryId': options['category']
        },
        'status': {
            'privacyStatus': options['privacy']
        }
    }

    # Call the API's videos.insert method
    insert_request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=MediaFileUpload(
            options['file'],
            chunksize=-1,
            resumable=True
        )
    )

    # Execute upload
    print(f"Uploading: {options['file']}")
    response = None
    
    while response is None:
        try:
            status, response = insert_request.next_chunk()
            if status:
                print(f"Upload progress: {int(status.progress() * 100)}%")
        except HttpError as e:
            print(f"HTTP error: {e}")
            sys.exit(1)
    
    print(f"Upload successful!")
    print(f"Video ID: {response['id']}")
    print(f"URL: https://www.youtube.com/watch?v={response['id']}")

def main():
    parser = argparse.ArgumentParser(
        description='Upload videos to YouTube from command line',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic upload
  %(prog)s video.mp4 -t "My Video Title"
  
  # With description and tags
  %(prog)s video.mp4 -t "My Video" -d "Description here" -k "tag1,tag2,tag3"
  
  # Set privacy and category
  %(prog)s video.mp4 -t "My Video" -p public -c 22
        """
    )
    
    parser.add_argument('file', help='Path to video file')
    parser.add_argument('-t', '--title', required=True, help='Video title')
    parser.add_argument('-d', '--description', default='', help='Video description')
    parser.add_argument('-k', '--keywords', default='', help='Comma-separated tags')
    parser.add_argument('-c', '--category', default='22', help='Category ID (default: 22)')
    parser.add_argument('-p', '--privacy', default='private', 
                       choices=['private', 'unlisted', 'public'],
                       help='Privacy status (default: private)')
    
    args = parser.parse_args()
    
    # Verify file exists
    if not os.path.exists(args.file):
        print(f"Error: File not found: {args.file}")
        sys.exit(1)
    
    # Get authenticated service
    try:
        youtube = get_authenticated_service()
    except Exception as e:
        print(f"Authentication error: {e}")
        sys.exit(1)
    
    # Upload video
    options = {
        'file': args.file,
        'title': args.title,
        'description': args.description,
        'keywords': args.keywords,
        'category': args.category,
        'privacy': args.privacy
    }
    
    try:
        upload_video(youtube, options)
    except Exception as e:
        print(f"Upload error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
