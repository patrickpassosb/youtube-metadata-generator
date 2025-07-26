# YouTube Metadata Generator

A Python tool that extracts YouTube captions and generates SEO-optimized titles and descriptions using Groq AI. Provides three interfaces: a user-friendly Streamlit web app, CLI, and mobile-friendly API.

**Created by:** [Patrick Passos](https://github.com/patrickpassosb)  
**Contact:** patrickpassosb@gmail.com

## Features

- 🎥 Extract English auto-captions from YouTube videos using `yt-dlp`
- 🤖 Generate catchy titles (≤53 chars) and SEO descriptions using Groq AI
- 🌐 **Streamlit Web Interface** - User-friendly web application
- 💾 Save metadata to markdown files
- 📱 Mobile-friendly HTTP API endpoint
- 🔄 Rate limiting with exponential backoff
- 🌐 Cross-platform compatibility (Windows, macOS, Linux, Termux)
- 📊 Batch processing support for CSV files

## Quick Start

### Web Interface (Recommended)
```bash
pip install yt-dlp groq fastapi uvicorn pydantic requests rich streamlit
streamlit run app.py --server.port 5000
```
Open http://localhost:5000 in your browser

### CLI Usage
```bash
pip install yt-dlp groq fastapi uvicorn pydantic requests rich
python gen_meta.py <youtube_url>
```

### API Server
```bash
python server.py
```

## Setup

1. **Get Groq API Key**: Sign up at [console.groq.com](https://console.groq.com) and get your API key

2. **Set API Key**: Add your Groq API key to `core.py` or set as environment variable:
```bash
export GROQ_API_KEY="your_api_key_here"
```

3. **Install Dependencies**:
```bash
pip install yt-dlp groq fastapi uvicorn pydantic requests rich streamlit
```

## Usage Examples

### Web Interface
1. Start the web app: `streamlit run app.py --server.port 5000`
2. Open http://localhost:5000
3. Paste YouTube URL and click "Generate Metadata"
4. Download results as Markdown or JSON

### Command Line
```bash
python gen_meta.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

### API Endpoint
```bash
curl -X POST "http://localhost:8000/meta" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://youtube.com/watch?v=dQw4w9WgXcQ"}'
```

Response:
```json
{
  "title": "Generated catchy title",
  "description": "SEO-optimized description with exactly 3 hashtags",
  "file_path": "dQw4w9WgXcQ.md"
}
```

### Batch Processing
Create a CSV file with YouTube URLs:
```csv
url
https://www.youtube.com/watch?v=dQw4w9WgXcQ
https://www.youtube.com/watch?v=jNQXAC9IVRw
```

```python
from core import process_csv_batch
process_csv_batch('urls.csv')
```

## File Structure

```
.
├── app.py              # Streamlit web interface
├── core.py             # Main business logic
├── gen_meta.py         # CLI interface
├── server.py           # FastAPI server
├── test_demo.py        # Unit tests and demos
├── README.md           # This file
└── .streamlit/
    └── config.toml     # Streamlit configuration
```

## Requirements

- Python 3.11+
- English auto-captions enabled on YouTube videos
- Valid Groq API key

## Dependencies

### Core Dependencies
- `yt-dlp`: YouTube video/audio downloader and metadata extractor
- `groq`: Official Groq API client for AI text generation
- `rich`: Enhanced terminal formatting and progress display

### Web Application
- `streamlit`: Modern framework for creating interactive web applications

### API Dependencies
- `fastapi`: Modern async web framework for the HTTP API
- `uvicorn`: ASGI server for running FastAPI applications
- `pydantic`: Data validation and serialization for API models

### Standard Library
- `urllib.parse`: URL parsing and video ID extraction
- `requests`: HTTP client for downloading subtitles
- `json`, `os`, `sys`, `logging`, `re`: Built-in Python modules

## Architecture

This tool follows a modular architecture:

1. **Core Module** (`core.py`): Main business logic for caption extraction and metadata generation
2. **Streamlit Web App** (`app.py`): User-friendly web interface with real-time feedback
3. **CLI Interface** (`gen_meta.py`): Simple command-line tool for quick processing
4. **API Server** (`server.py`): RESTful API for mobile and programmatic access

## Mobile Integration

The HTTP API is designed for mobile integration:

### iOS (Shortcuts App)
1. Create a new shortcut
2. Add "Get Text from Input" action
3. Add "Get Contents of URL" action with POST method
4. Use the JSON response to display or save results

### Android (Termux)
```bash
termux-setup-storage
pkg install python
pip install requests
# Use curl or python requests to call the API
```

### Testing Mobile Integration
```bash
# Test from mobile browser
curl -X POST "http://your-server-ip:8000/meta" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://youtube.com/watch?v=..."}'
```

## Hosting Options

### Local Network (LAN Access)
```bash
# For API server
python server.py  # Runs on 0.0.0.0:8000

# For Streamlit
streamlit run app.py --server.port 5000 --server.address 0.0.0.0
```

### Cloud Deployment
- **Replit**: Ready for deployment (includes replit.md configuration)
- **Heroku**: Add `Procfile` with `web: streamlit run app.py --server.port $PORT`
- **Railway**: Direct deployment from GitHub
- **Render**: Web service deployment

## Rate Limiting

- Groq API: < 20 calls per day recommended
- Exponential backoff on 429 errors
- 2-second delay between batch processing requests

## Troubleshooting

### Common Issues

1. **No captions available**: Ensure the YouTube video has English auto-generated captions
2. **API key errors**: Verify your Groq API key is valid and has sufficient quota
3. **Rate limiting**: Wait before retrying, the tool handles this automatically
4. **Network errors**: Check internet connection and YouTube accessibility

### Debug Mode
Add debug logging to see detailed processing information:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with various YouTube videos
5. Submit a pull request

## License

MIT License - feel free to use for personal and commercial projects.

## Changelog

- **v1.0.0**: Initial release with CLI and API
- **v1.1.0**: Added Streamlit web interface
- **v1.2.0**: Updated to Groq llama-3.3-70b-versatile model
- **v1.2.1**: Improved response parsing for various AI output formats
- **v1.3.0**: Enhanced mobile support with PWA, QR codes, and improved AI prompts

## Author

**Patrick Passos**  
- GitHub: [@patrickpassosb](https://github.com/patrickpassosb)
- Email: patrickpassosb@gmail.com

## Support

If you find this project helpful, please consider:
- ⭐ **Starring** the repository
- 🍴 **Forking** for your own projects
- 🐛 **Reporting** bugs or suggesting features
- 💬 **Sharing** with other content creators
