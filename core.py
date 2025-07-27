"""
Core functionality for YouTube caption extraction and metadata generation.
Shared between CLI and API interfaces.
"""

import os
import re
import time
import json
import logging
from typing import Optional, Dict, Any
from urllib.parse import urlparse, parse_qs

try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None

import yt_dlp
from groq import Groq

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YouTubeMetaGenerator:
    """Main class for extracting captions and generating metadata."""
    
    def __init__(self, groq_api_key: Optional[str] = None):
        """Initialize with Groq API key."""
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY", "")
        self.groq_client = Groq(api_key=self.groq_api_key)
        
    def log(self, message: str, style: str = "info"):
        """Log message with optional rich formatting."""
        if RICH_AVAILABLE and console:
            if style == "error":
                console.print(f"❌ {message}", style="red")
            elif style == "success":  
                console.print(f"✅ {message}", style="green")
            elif style == "warning":
                console.print(f"⚠️ {message}", style="yellow")
            else:
                console.print(f"ℹ️ {message}", style="blue")
        else:
            print(f"[{style.upper()}] {message}")
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract YouTube video ID from URL."""
        try:
            # Handle various YouTube URL formats
            patterns = [
                r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
                r'(?:embed\/)([0-9A-Za-z_-]{11})',
                r'(?:v\/)([0-9A-Za-z_-]{11})'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    return match.group(1)
            
            # Try parsing as query parameter
            parsed = urlparse(url)
            if parsed.query:
                params = parse_qs(parsed.query)
                if 'v' in params:
                    return params['v'][0]
                    
            return None
        except Exception as e:
            self.log(f"Error extracting video ID: {e}", "error")
            return None
    
    def extract_captions(self, url: str) -> Optional[str]:
        """Extract English auto-captions from YouTube video using yt-dlp."""
        try:
            self.log("Extracting captions from YouTube...")
            
            # Configure yt-dlp options
            ydl_opts = {
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': ['en'],
                'skip_download': True,
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Get video info including subtitles
                info = ydl.extract_info(url, download=False)
                
                # Check for automatic subtitles
                auto_subs = info.get('automatic_captions') if info else {}
                if not auto_subs or 'en' not in auto_subs:
                    self.log("No English auto-captions available", "error")
                    return None
                
                # Get the subtitle URL (prefer VTT format)
                en_subs = auto_subs['en']
                vtt_url = None
                
                for sub in en_subs:
                    if sub.get('ext') == 'vtt':
                        vtt_url = sub.get('url')
                        break
                
                if not vtt_url and en_subs:
                    # Fallback to first available format
                    vtt_url = en_subs[0].get('url')
                
                if not vtt_url:
                    self.log("No subtitle URL found", "error")
                    return None
                
                # Download and parse subtitles
                import requests
                response = requests.get(vtt_url)
                response.raise_for_status()
                
                # Parse VTT content and extract text
                vtt_content = response.text
                transcript = self.parse_vtt_content(vtt_content)
                
                if not transcript:
                    self.log("Failed to parse transcript", "error")
                    return None
                
                self.log("Captions extracted successfully", "success")
                return transcript
                
        except Exception as e:
            self.log(f"Error extracting captions: {e}", "error")
            return None
    
    def parse_vtt_content(self, vtt_content: str) -> str:
        """Parse VTT subtitle content and extract clean text."""
        try:
            lines = vtt_content.split('\n')
            transcript_parts = []
            
            for line in lines:
                line = line.strip()
                # Skip empty lines, timestamps, and VTT headers
                if (not line or 
                    line.startswith('WEBVTT') or 
                    '-->' in line or 
                    line.startswith('NOTE') or
                    re.match(r'^\d+$', line)):
                    continue
                
                # Remove HTML tags and timing info
                clean_line = re.sub(r'<[^>]+>', '', line)
                clean_line = re.sub(r'&[a-zA-Z]+;', '', clean_line)
                
                if clean_line and clean_line not in transcript_parts:
                    transcript_parts.append(clean_line)
            
            return ' '.join(transcript_parts)
            
        except Exception as e:
            self.log(f"Error parsing VTT content: {e}", "error")
            return ""
    
    def generate_metadata_with_backoff(self, transcript: str, max_retries: int = 3) -> Optional[Dict[str, str]]:
        """Generate metadata using Groq with exponential backoff for rate limiting."""
        
        prompt = f"""You are an expert YouTube SEO copywriter. Create compelling metadata that maximizes click-through rates and engagement.

VIDEO TRANSCRIPT:
{transcript}

INSTRUCTIONS:
1. TITLE (≤53 characters):
   - Start with a powerful hook (number, question, or emotional trigger)
   - Include the main topic/keyword naturally
   - Use action words and create curiosity
   - Avoid clickbait but make it irresistible
   - Examples: "5 Secrets That Changed Everything", "Why Nobody Talks About This", "The Truth About..."
   - Never use "!" in the title
   - Do not every title needs to talk about "Learning" and "Journey"
   - Do not sound so extraordinary, just be natural and engaging


2. DESCRIPTION (≤140 words total):
   - First paragraph: Hook + brief value proposition (2-3 sentences)
   - Second paragraph: Key benefits/insights + call to action (2-3 sentences)
   - Use conversational, engaging language
   - Make it a description of the vide, what the video says the purpose of the video in a description to who is watching know about what the video is
   - Do not sound so extraordinary, just be natural and engaging

FORMAT YOUR RESPONSE EXACTLY LIKE THIS:
TITLE: [Your catchy title here]
DESCRIPTION: [Your engaging description here]

Remember: Quality over quantity. Make every word count for maximum impact."""
        
        for attempt in range(max_retries):
            try:
                self.log(f"Generating metadata (attempt {attempt + 1}/{max_retries})...")
                
                response = self.groq_client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    model="llama-3.3-70b-versatile",
                    temperature=0.7,  # Add some creativity
                    max_tokens=300,   # Limit response length
                )
                
                content = response.choices[0].message.content
                
                # Parse the response
                if content:
                    metadata = self.parse_groq_response(content)
                else:
                    metadata = None
                if metadata:
                    self.log("Metadata generated successfully", "success")
                    return metadata
                else:
                    self.log("Failed to parse Groq response", "warning")
                    
            except Exception as e:
                error_msg = str(e)
                
                # Handle rate limiting (429 errors)
                if "429" in error_msg or "rate limit" in error_msg.lower():
                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt) * 2  # Exponential backoff
                        self.log(f"Rate limited. Waiting {wait_time} seconds...", "warning")
                        time.sleep(wait_time)
                        continue
                    else:
                        self.log("Rate limit exceeded. Try again later.", "error")
                        return None
                else:
                    self.log(f"Error generating metadata: {e}", "error")
                    if attempt < max_retries - 1:
                        time.sleep(1)  # Brief pause before retry
                        continue
                    return None
        
        return None
    
    def parse_groq_response(self, content: str) -> Optional[Dict[str, str]]:
        """Parse Groq response to extract title and description."""
        try:
            lines = content.strip().split('\n')
            title = ""
            description_lines = []
            collecting_description = False
            
            # Clean up content first
            full_text = content.strip()
            
            # Pattern 1: TITLE: format
            if 'TITLE:' in full_text.upper():
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    if line.upper().startswith('TITLE:'):
                        title = line[6:].strip()
                        title = title.strip('"').strip("'")
                    elif line.upper().startswith('DESCRIPTION:'):
                        collecting_description = True
                        desc_part = line[12:].strip()
                        if desc_part:
                            description_lines.append(desc_part)
                    elif collecting_description:
                        description_lines.append(line)
                        
            # Pattern 2: **Title:** format
            elif '**Title:**' in full_text or '**TITLE:**' in full_text:
                import re
                title_match = re.search(r'\*\*Title:\*\*\s*([^\n]+)', full_text, re.IGNORECASE)
                desc_match = re.search(r'\*\*Description:\*\*\s*([^*]+)', full_text, re.IGNORECASE)
                
                if title_match:
                    title = title_match.group(1).strip()
                if desc_match:
                    description_lines = [desc_match.group(1).strip()]
                    
            # Pattern 3: First line as title (with ** formatting)
            else:
                first_line = lines[0].strip() if lines else ""
                if first_line.startswith('**') and first_line.endswith('**'):
                    title = first_line.strip('*').strip()
                    # Rest as description
                    description_lines = [line.strip() for line in lines[1:] if line.strip()]
                elif len(first_line) <= 53:
                    title = first_line
                    description_lines = [line.strip() for line in lines[1:] if line.strip()]
            
            # Join description lines
            description = ' '.join(description_lines).strip()
            
            # Clean up title and description
            title = title.strip('"').strip("'").strip('*').strip()
            
            # Ensure title is within character limit
            if len(title) > 53:
                title = title[:50] + "..."
            
            # If no clear separation, try to split the content intelligently
            if not title or not description:
                # Split by first period or newline for title
                sentences = full_text.replace('\n', ' ').split('. ')
                if sentences:
                    potential_title = sentences[0].strip()
                    if len(potential_title) <= 53 and not title:
                        title = potential_title
                        description = '. '.join(sentences[1:]).strip()
                    elif not description:
                        description = full_text.strip()
            
            # Final validation
            if title and description:
                return {
                    "title": title,
                    "description": description
                }
            
            return None
            
        except Exception as e:
            self.log(f"Error parsing Groq response: {e}", "error")
            return None
    
    def save_metadata(self, video_id: str, metadata: Dict[str, str]) -> str:
        """Save metadata to markdown file."""
        try:
            filename = f"{video_id}.md"
            
            content = f"""# {metadata['title']}

{metadata['description']}

"""
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.log(f"Saved to {filename}", "success")
            return filename
            
        except Exception as e:
            self.log(f"Error saving metadata: {e}", "error")
            return ""
    
    def process_video(self, url: str) -> Optional[Dict[str, Any]]:
        """Main processing function for a single video."""
        try:
            # Extract video ID
            video_id = self.extract_video_id(url)
            if not video_id:
                self.log("Could not extract video ID from URL", "error")
                return None
            
            self.log(f"Processing video ID: {video_id}")
            
            # Extract captions
            transcript = self.extract_captions(url)
            if not transcript:
                return None
            
            # Truncate transcript if too long (to avoid token limits)
            if len(transcript) > 8000:
                transcript = transcript[:8000] + "..."
                self.log("Transcript truncated to fit token limits", "warning")
            
            # Generate metadata
            metadata = self.generate_metadata_with_backoff(transcript)
            if not metadata:
                return None
            
            # Save to file
            filename = self.save_metadata(video_id, metadata)
            
            return {
                "video_id": video_id,
                "title": metadata["title"],
                "description": metadata["description"],
                "file_path": filename
            }
            
        except Exception as e:
            self.log(f"Error processing video: {e}", "error")
            return None


def process_csv_batch(csv_file: str, groq_api_key: Optional[str] = None) -> None:
    """Process a batch of URLs from CSV file."""
    import csv
    
    generator = YouTubeMetaGenerator(groq_api_key)
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Expect CSV with 'url' column
            for row in reader:
                url = row.get('url', '').strip()
                if not url:
                    continue
                
                generator.log(f"Processing: {url}")
                result = generator.process_video(url)
                
                if result:
                    generator.log(f"✅ Generated: {result['title']}")
                else:
                    generator.log(f"❌ Failed to process: {url}")
                
                # Brief pause between requests to be respectful
                time.sleep(2)
                
    except FileNotFoundError:
        generator.log(f"CSV file not found: {csv_file}", "error")
    except Exception as e:
        generator.log(f"Error processing CSV: {e}", "error")
