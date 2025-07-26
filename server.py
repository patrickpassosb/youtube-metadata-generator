"""
FastAPI server for mobile API access to YouTube metadata generation.
Provides /meta endpoint for POST requests with YouTube URLs.
"""

import os
import sys
from typing import Dict, Any
from contextlib import asynccontextmanager

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, HttpUrl
import uvicorn

from core import YouTubeMetaGenerator


class VideoRequest(BaseModel):
    """Request model for video URL."""
    url: str


class VideoResponse(BaseModel):
    """Response model for processed video metadata."""
    title: str
    description: str
    file_path: str


# Global generator instance
generator = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize global resources on startup."""
    global generator
    generator = YouTubeMetaGenerator()
    yield


# Initialize FastAPI app
app = FastAPI(
    title="YouTube Metadata Generator API",
    description="Extract captions and generate SEO metadata for YouTube videos",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware for mobile access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for mobile access
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint with basic info."""
    return {
        "message": "YouTube Metadata Generator API",
        "endpoints": {
            "POST /meta": "Generate metadata for YouTube video",
            "GET /health": "Health check",
            "GET /mobile": "Mobile app interface"
        },
        "usage": "POST /meta with JSON body: {'url': 'https://youtube.com/watch?v=...'}"
    }


@app.get("/mobile")
async def mobile_app():
    """Serve the mobile app interface."""
    return FileResponse("mobile_app.html")


@app.get("/manifest.json")
async def manifest():
    """Serve the PWA manifest."""
    return FileResponse("manifest.json")


@app.get("/sw.js")
async def service_worker():
    """Serve the service worker."""
    return FileResponse("sw.js")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "youtube-meta-generator"}


@app.post("/meta", response_model=VideoResponse)
async def generate_metadata(request: VideoRequest) -> VideoResponse:
    """
    Generate metadata for a YouTube video.
    
    Args:
        request: VideoRequest containing the YouTube URL
        
    Returns:
        VideoResponse with title, description, and file path
        
    Raises:
        HTTPException: If processing fails
    """
    try:
        if not generator:
            raise HTTPException(status_code=500, detail="Service not initialized")
        
        # Validate URL format (basic check)
        url = request.url.strip()
        if not url or 'youtube.com' not in url and 'youtu.be' not in url:
            raise HTTPException(status_code=400, detail="Invalid YouTube URL")
        
        # Process the video
        result = generator.process_video(url)
        
        if not result:
            raise HTTPException(
                status_code=422, 
                detail="Failed to process video. Check if captions are available and try again."
            )
        
        return VideoResponse(
            title=result["title"],
            description=result["description"],
            file_path=result["file_path"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/docs")
async def get_docs():
    """Redirect to automatic API documentation."""
    return {"message": "Visit /docs for interactive API documentation"}


def main():
    """Run the FastAPI server."""
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"Starting YouTube Metadata Generator API server...")
    print(f"Server will be available at: http://{host}:{port}")
    print(f"API documentation at: http://{host}:{port}/docs")
    print(f"Health check at: http://{host}:{port}/health")
    
    uvicorn.run(
        "server:app",
        host=host,
        port=port,
        reload=False,
        access_log=True
    )


if __name__ == "__main__":
    main()
