# YouTube MCP Server

An MCP (Model Context Protocol) server that enables uploading videos to YouTube through Claude Desktop or any MCP-compatible client.

## Features

- 📹 **Upload Videos**: Upload video files to YouTube with customizable metadata
- 🔐 **OAuth2 Authentication**: Secure authentication with YouTube API
- 📊 **Quota Checking**: Monitor your YouTube API usage
- 📝 **Category Listing**: Browse available video categories
- 🔧 **Easy Setup**: Built-in credential configuration tool

## Prerequisites

- Python 3.10 or higher
- A Google Cloud Project with YouTube Data API v3 enabled
- OAuth2 credentials from Google Cloud Console
- Claude Desktop (or another MCP client)

## Setup Instructions

### 1. Install Dependencies

```bash
# Clone or download this repository
cd youtube-mcp-server

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

### 2. Set Up Google Cloud Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable YouTube Data API v3:
   - Go to "APIs & Services" > "Library"
   - Search for "YouTube Data API v3"
   - Click Enable
4. Create OAuth2 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop app" as application type
   - Download the credentials JSON file

### 3. Configure Claude Desktop

Add the server to your Claude Desktop configuration:

**macOS/Linux:**
```bash
# Open config file
code ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Windows:**
```powershell
code $env:AppData\Claude\claude_desktop_config.json
```

Add this configuration:

```json
{
    "mcpServers": {
        "youtube-uploader": {
            "command": "python",
            "args": [
                "/ABSOLUTE/PATH/TO/youtube-mcp-server/youtube_uploader.py"
            ]
        }
    }
}
```

### 4. First-Time Authentication

1. Restart Claude Desktop
2. Use the `setup_youtube_auth` tool with your OAuth2 credentials:
   - Provide client_id, client_secret, and project_id from downloaded JSON
3. Try uploading a video - a browser window will open for authentication
4. Grant permissions to your YouTube account

## Available Tools

### 1. `upload_video`
Upload a video file to YouTube.

**Parameters:**
- `file_path` (required): Path to video file
- `title` (required): Video title
- `description`: Video description
- `keywords`: Comma-separated tags
- `category_id`: YouTube category ID (default: 22)
- `privacy_status`: "private", "unlisted", or "public" (default: private)
- `made_for_kids`: Boolean for COPPA compliance

**Example:**
```
Upload the video at /Users/me/video.mp4 with title "My Amazing Video" and description "This is a test upload"
```

### 2. `check_upload_quota`
Check your YouTube API quota usage and channel information.

### 3. `list_video_categories`
List available YouTube video categories for a specific region.

**Parameters:**
- `region_code`: ISO country code (default: US)

### 4. `setup_youtube_auth`
Configure OAuth2 credentials for YouTube API access.

## Important Notes

- **Quota Limits**: YouTube API has daily quotas. Each upload costs ~1,600 units out of 1,600,000 daily units.
- **File Size**: Large files may take time to upload. The server uses resumable uploads.
- **Privacy**: Videos upload as "private" by default for safety.
- **Authentication**: OAuth2 tokens are stored locally in `token.json`.

## Troubleshooting

1. **"Missing credentials.json"**: Run `setup_youtube_auth` first
2. **Authentication errors**: Delete `token.json` and re-authenticate
3. **Upload failures**: Check file path, size, and format
4. **Quota exceeded**: Wait 24 hours for quota reset

## Security

- Keep your `credentials.json` and `token.json` files secure
- Don't commit these files to version control
- OAuth2 tokens expire; the server will refresh them automatically

## License

MIT License
