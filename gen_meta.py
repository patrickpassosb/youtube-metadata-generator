#!/usr/bin/env python3
"""
CLI interface for YouTube metadata generation.
Usage: python gen_meta.py <youtube_url>
"""

import sys
import os
from typing import Optional

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import YouTubeMetaGenerator


def main():
    """Main CLI entry point."""
    if len(sys.argv) != 2:
        print("Usage: python gen_meta.py <youtube_url>")
        print("Example: python gen_meta.py https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        sys.exit(1)
    
    url = sys.argv[1].strip()
    
    if not url:
        print("Error: Please provide a valid YouTube URL")
        sys.exit(1)
    
    # Initialize generator
    generator = YouTubeMetaGenerator()
    
    # Process the video
    result = generator.process_video(url)
    
    if result:
        print(f"\n✅ Saved to {result['file_path']}")
        print(f"Title: {result['title']}")
        print(f"Description preview: {result['description'][:100]}...")
        sys.exit(0)
    else:
        print("\n❌ Failed to process video")
        sys.exit(1)


if __name__ == "__main__":
    main()
