# YouTube Metadata Generator

## Overview

This is a Python-based YouTube metadata generation tool that automates the process of extracting captions from YouTube videos and generating SEO-optimized titles and descriptions using Groq AI. The system provides three interfaces: a user-friendly Streamlit web application, a command-line interface for desktop use, and a mobile-friendly HTTP API for on-the-go processing.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a modular architecture with four main components:

### Core Module (`core.py`)
- **Purpose**: Contains the main business logic for YouTube caption extraction and AI-powered metadata generation
- **Technology**: Uses `yt-dlp` for YouTube data extraction and Groq API for AI text generation
- **Design Pattern**: Single responsibility class (`YouTubeMetaGenerator`) that handles the entire workflow

### Streamlit Web Application (`app.py`)
- **Purpose**: Provides a user-friendly web interface for non-technical users
- **Framework**: Streamlit for rapid web application development
- **Features**: Real-time processing feedback, progress indicators, file downloads, responsive design
- **Port**: Runs on port 5000 for easy access and deployment

### CLI Interface (`gen_meta.py`)
- **Purpose**: Provides a simple command-line interface for desktop users
- **Usage**: `python gen_meta.py <youtube_url>`
- **Integration**: Imports and uses the core module for processing

### HTTP API Server (`server.py`)
- **Purpose**: Offers a mobile-friendly REST API endpoint
- **Framework**: FastAPI for high-performance async HTTP handling
- **Endpoint**: `/meta` accepts POST requests with YouTube URLs
- **Response**: Returns JSON with generated title, description, and file path

## Key Components

### YouTube Data Extraction
- **Library**: `yt-dlp` (successor to youtube-dl)
- **Target**: English auto-generated captions only
- **Rationale**: Avoids browser automation complexity while providing reliable caption extraction

### AI Text Generation
- **Service**: Groq API with `llama-3.3-70b-versatile` model (updated January 2025)
- **API Key**: Set as environment variable `GROQ_API_KEY` in Replit secrets
- **Constraints**: 
  - Titles limited to 53 characters for SEO optimization
  - Descriptions limited to 140 words with exactly 3 hashtags

### File Output System
- **Format**: Markdown files named `<video_id>.md`
- **Structure**: Title as H1 header followed by description content
- **Storage**: Local filesystem in the application directory

### Rich Console Interface
- **Library**: Rich library for enhanced terminal output
- **Features**: Colored console output, progress indicators, spinner animations
- **Fallback**: Graceful degradation when Rich is not available

## Data Flow

1. **Input Processing**: YouTube URL validation and video ID extraction
2. **Caption Extraction**: `yt-dlp` downloads English auto-captions
3. **AI Processing**: Transcript sent to Groq API with specific prompt template
4. **Content Generation**: AI returns formatted title and description
5. **File Creation**: Metadata saved to markdown file with video ID as filename
6. **Response**: Success confirmation with file path returned

## External Dependencies

### Core Dependencies
- **yt-dlp**: YouTube video/audio downloader and metadata extractor
- **groq**: Official Groq API client for AI text generation
- **rich**: Enhanced terminal formatting and progress display

### Web Application Dependencies
- **streamlit**: Modern framework for creating interactive web applications with Python
- **fastapi**: Modern async web framework for the HTTP API
- **uvicorn**: ASGI server for running FastAPI applications
- **pydantic**: Data validation and serialization for API models

### Standard Library Usage
- **urllib.parse**: URL parsing and video ID extraction
- **os/sys**: Environment variable handling and path management
- **logging**: Application logging and error tracking
- **re**: Regular expression pattern matching for URL validation

## Deployment Strategy

### Development Environment
- **Python Version**: 3.11+ required
- **Installation**: pip-based dependency management
- **Cross-Platform**: Compatible with Windows, macOS, Linux, and Termux (Android)

### API Deployment
- **Server**: FastAPI with Uvicorn ASGI server
- **Endpoint**: Single `/meta` POST endpoint for mobile integration
- **Format**: JSON request/response for easy mobile app integration
- **Authentication**: None (relies on Groq API key for service access)

### Mobile Integration
- **Target Platforms**: Pythonista (iOS), Termux (Android), Shortcuts app
- **Protocol**: Simple HTTP POST with JSON payload
- **Testing**: Includes curl examples for mobile testing scenarios

### Error Handling
- **API Errors**: HTTP status codes with descriptive error messages
- **CLI Errors**: Exit codes and console error messages
- **Logging**: Comprehensive logging for debugging and monitoring
- **Graceful Degradation**: Rich console features optional, basic functionality maintained