# Terminal Commands for YouTube Upload

## Option 1: Using the Standalone CLI Script

### Setup
```bash
# Install dependencies
pip install google-auth-httplib2 google-auth-oauthlib google-api-python-client

# Make script executable
chmod +x youtube_cli.py

# Or use the wrapper
chmod +x youtube-upload
```

### Basic Usage
```bash
# Simple upload with just title
./youtube_cli.py video.mp4 -t "My Video Title"

# With description and tags
./youtube_cli.py video.mp4 -t "My Video" -d "This is my video description" -k "vlog,travel,2024"

# Set to public with gaming category
./youtube_cli.py video.mp4 -t "Epic Gaming Session" -p public -c 20

# Using the wrapper script
./youtube-upload video.mp4 -t "My Video" -d "Description"
```

### Command Options
- `-t, --title` (required): Video title
- `-d, --description`: Video description
- `-k, --keywords`: Comma-separated tags
- `-c, --category`: YouTube category ID (default: 22)
- `-p, --privacy`: private/unlisted/public (default: private)

## Option 2: Using youtube-upload (Third-party tool)

### Install
```bash
# Install via pip
pip install youtube-upload

# Or on macOS with Homebrew
brew install youtube-upload
```

### Usage
```bash
# Basic upload
youtube-upload --title="My Video" --description="Description" video.mp4

# With more options
youtube-upload \
  --title="My Video Title" \
  --description="Video description" \
  --tags="tag1,tag2,tag3" \
  --category="Music" \
  --privacy="private" \
  --client-secrets=client_secrets.json \
  video.mp4
```

## Option 3: Using curl with YouTube API

### Direct API Upload (Advanced)
```bash
# First, get an access token (requires OAuth2 setup)
ACCESS_TOKEN="your-access-token"

# Create video metadata
cat > metadata.json << EOF
{
  "snippet": {
    "title": "My Video",
    "description": "Description",
    "tags": ["tag1", "tag2"],
    "categoryId": "22"
  },
  "status": {
    "privacyStatus": "private"
  }
}
EOF

# Upload video (resumable upload)
curl -X POST \
  "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d @metadata.json
```

## Option 4: Using the MCP Server via Terminal

### Test MCP Server
```bash
# Run the MCP server directly
python youtube_uploader.py

# Or test with MCP CLI tools
mcp-cli call youtube-uploader upload_video \
  --file_path="/path/to/video.mp4" \
  --title="My Video" \
  --description="Test upload"
```

## Quick Examples

### Upload vacation video as private
```bash
./youtube_cli.py ~/Movies/vacation.mp4 -t "Summer Vacation 2024" -d "Family trip to Hawaii" -k "vacation,hawaii,family,2024" -p private
```

### Upload tutorial as unlisted
```bash
./youtube_cli.py tutorial.mp4 -t "Python Tutorial Part 1" -d "Learn Python basics" -k "python,programming,tutorial" -c 27 -p unlisted
```

### Upload gaming video as public
```bash
./youtube_cli.py gameplay.mp4 -t "Speedrun World Record!" -d "New speedrun record" -k "gaming,speedrun,record" -c 20 -p public
```

## Category IDs Reference
- 1: Film & Animation
- 2: Autos & Vehicles
- 10: Music
- 15: Pets & Animals
- 17: Sports
- 19: Travel & Events
- 20: Gaming
- 22: People & Blogs
- 23: Comedy
- 24: Entertainment
- 25: News & Politics
- 26: Howto & Style
- 27: Education
- 28: Science & Technology

## Troubleshooting

### Authentication Issues
```bash
# Remove old token and re-authenticate
rm token.json
./youtube_cli.py video.mp4 -t "Test"
```

### Check video format
```bash
# Use ffprobe to check video
ffprobe video.mp4

# Convert to YouTube-compatible format if needed
ffmpeg -i input.mov -c:v libx264 -c:a aac output.mp4
```
