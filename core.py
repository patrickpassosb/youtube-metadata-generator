"""
Core functionality for YouTube caption extraction and metadata generation.
Shared between CLI and API interfaces.
"""

import os
import re
import time
import logging
from typing import Optional, Dict, Any
from urllib.parse import urlparse, parse_qs



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
        """Log message with simple formatting."""
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

INSTRUCTIONS

### **OBJECTIVE**

Generate **YouTube video titles** and **descriptions** for **Patrick Passos**, a bilingual Brazilian creator documenting his personal journey learning English, Generative AI, Prompt Engineering, and Python. The content is part of his mission to learn, grow a personal brand, and eventually earn income through his skills.

---

### **BACKGROUND CONTEXT (FOR INTERNAL USE ONLY — NOT TO BE INCLUDED IN OUTPUT)**

- Patrick Passos is a young content creator from São Paulo, Brazil.
- He began his YouTube journey on **Jan 25, 2025**, primarily to **learn English** and has been posting **almost daily** since.
- He's immersing himself in English: media, devices, conversations — everything.
- He is now learning **Generative AI**, **Prompt Engineering**, and **Python** to build useful AI agents and automate tasks.
- His goals:
    1. Learn English
    2. Build a personal brand
    3. Document his journey

**⚠️ IMPORTANT:** Titles and descriptions **must not include personal details**. This background is to help generate better, more authentic content.

### 2. TITLE (≤53 characters):

- Start with a **hook** (number, question, insight, etc.)
- Include the **main topic or keyword** naturally
- Use **action verbs** and **create curiosity**
- Sound **natural, not exaggerated**
- Do not talk about "grow","learning" and "journey" everytime
- Avoid **clickbait** and **exclamation marks (!)**

**✅ Good examples:**

- `How I Learned AI Without a Degree`
- `3 Tools I Use to Learn Python Fast`
- `Why English Changed My Life`
- `What I Wish I Knew Before Starting AI`

3. DESCRIPTION (≤140 words total):

**Paragraph 1 (Hook + Purpose):**

Start with a short, engaging hook. Briefly describe the **purpose of the video** and why it's relevant to viewers.

**Paragraph 2 (Value + CTA):**

Mention **what viewers will learn or gain**. Add a simple **call to action** like subscribing, watching until the end, or leaving a comment.

**Tone:**

- Friendly, casual, and conversational
- Honest and relatable
- Avoid hype and exaggeration
- **Never use exclamation marks**
- Do not talk about "grow","learning" and "journey" everytime

**✅ Example:**

In this video, I share how I started learning Python to build simple AI agents from scratch — no experience needed. If you're also new to coding, this is for you.

You'll see how I'm using free tools, practicing daily, and staying consistent. Subscribe to follow along.

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
            
            return {
                "video_id": video_id,
                "title": metadata["title"],
                "description": metadata["description"]
            }
            
        except Exception as e:
            self.log(f"Error processing video: {e}", "error")
            return None



