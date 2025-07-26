#!/usr/bin/env python3
"""
Streamlit web application for YouTube metadata generation.
Provides a user-friendly interface for extracting captions and generating SEO metadata.
"""

import os
import sys
import time
import json
import qrcode
import base64
import socket
from io import BytesIO
from typing import Optional, Dict, Any

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from core import YouTubeMetaGenerator

# Page configuration
st.set_page_config(
    page_title="YouTube Metadata Generator",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Mobile-first responsive design */
    @media (max-width: 768px) {
        .main-header {
            padding: 1rem 0;
            font-size: 1.5rem;
        }
        .metadata-card {
            padding: 1rem;
            margin: 0.5rem 0;
        }
        .stButton > button {
            width: 100%;
            height: 3rem;
            font-size: 1.1rem;
        }
        .stTextInput > div > div > input {
            font-size: 1rem;
            padding: 0.75rem;
        }
    }
    
    .main-header {
        text-align: center;
        padding: 2rem 0;
        color: #1f1f1f;
    }
    .success-box {
        padding: 1rem;
        border-left: 5px solid #28a745;
        background-color: #d4edda;
        color: #155724;
        margin: 1rem 0;
        border-radius: 8px;
    }
    .error-box {
        padding: 1rem;
        border-left: 5px solid #dc3545;
        background-color: #f8d7da;
        color: #721c24;
        margin: 1rem 0;
        border-radius: 8px;
    }
    .info-box {
        padding: 1rem;
        border-left: 5px solid #007bff;
        background-color: #d1ecf1;
        color: #0c5460;
        margin: 1rem 0;
        border-radius: 8px;
    }
    .metadata-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Mobile app-like styling */
    .mobile-container {
        max-width: 100%;
        padding: 0.5rem;
    }
    
    /* Better touch targets */
    .stButton > button {
        border-radius: 12px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* QR code styling */
    .qr-container {
        text-align: center;
        padding: 1rem;
        background: white;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_generator():
    """Initialize the YouTube metadata generator."""
    if 'generator' not in st.session_state:
        st.session_state.generator = YouTubeMetaGenerator()
    return st.session_state.generator

def display_header():
    """Display the main header."""
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.title("🎥 YouTube Metadata Generator")
    st.markdown("**Generate SEO-optimized titles and descriptions from YouTube videos**")
    st.markdown('</div>', unsafe_allow_html=True)

def display_instructions():
    """Display usage instructions."""
    with st.expander("📖 How to use", expanded=False):
        st.markdown("""
        **Simple 3-step process:**
        
        1. **Paste YouTube URL** - Any YouTube video with English auto-captions
        2. **Click Generate** - AI will extract captions and create metadata
        3. **Download Results** - Get your SEO-optimized title and description
        
        **Features:**
        - ✅ Catchy titles (≤53 characters for SEO)
        - ✅ Engaging descriptions (≤140 words + 3 hashtags)
        - ✅ Auto-saves to markdown files
        - ✅ Works with any YouTube video that has English auto-captions
        
        **Requirements:**
        - YouTube video must have English auto-generated captions
        - Valid YouTube URL (youtube.com or youtu.be)
        """)

def validate_youtube_url(url: str) -> bool:
    """Validate if the URL is a valid YouTube URL."""
    if not url:
        return False
    return 'youtube.com' in url or 'youtu.be' in url

def display_url_input():
    """Display URL input section."""
    st.markdown("### 📎 YouTube Video URL")
    
    # URL input
    url = st.text_input(
        "Paste your YouTube video URL here:",
        placeholder="https://www.youtube.com/watch?v=...",
        help="Supports youtube.com and youtu.be links"
    )
    
    return url

def display_processing_section(url: str, generator: YouTubeMetaGenerator):
    """Display the processing section with generate button and results."""
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        generate_button = st.button(
            "🚀 Generate Metadata",
            type="primary",
            use_container_width=True,
            disabled=not validate_youtube_url(url)
        )
    
    if generate_button and url:
        if not validate_youtube_url(url):
            st.markdown('<div class="error-box">❌ Please enter a valid YouTube URL</div>', 
                       unsafe_allow_html=True)
            return
        
        # Processing
        with st.spinner("🔄 Processing video... This may take 30-60 seconds"):
            
            # Create progress steps
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Step 1: Extract video ID
            status_text.text("📹 Extracting video information...")
            progress_bar.progress(20)
            
            video_id = generator.extract_video_id(url)
            if not video_id:
                st.markdown('<div class="error-box">❌ Could not extract video ID. Please check your URL.</div>', 
                           unsafe_allow_html=True)
                return
            
            # Step 2: Extract captions
            status_text.text("📝 Extracting English auto-captions...")
            progress_bar.progress(40)
            
            transcript = generator.extract_captions(url)
            if not transcript:
                st.markdown('<div class="error-box">❌ Could not extract captions. Make sure the video has English auto-captions enabled.</div>', 
                           unsafe_allow_html=True)
                return
            
            # Step 3: Generate metadata
            status_text.text("🤖 Generating SEO metadata with AI...")
            progress_bar.progress(70)
            
            metadata = generator.generate_metadata_with_backoff(transcript)
            if not metadata:
                st.markdown('<div class="error-box">❌ Failed to generate metadata. Please try again later.</div>', 
                           unsafe_allow_html=True)
                return
            
            # Step 4: Save file
            status_text.text("💾 Saving results...")
            progress_bar.progress(90)
            
            filename = generator.save_metadata(video_id, metadata)
            
            progress_bar.progress(100)
            status_text.text("✅ Complete!")
            
            time.sleep(1)  # Brief pause to show completion
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            
            # Display results
            display_results(metadata, filename, video_id)

def display_results(metadata: Dict[str, str], filename: str, video_id: str):
    """Display the generated metadata results."""
    
    st.markdown('<div class="success-box">🎉 Metadata generated successfully!</div>', 
               unsafe_allow_html=True)
    
    # Title section
    st.markdown('<div class="metadata-card">', unsafe_allow_html=True)
    st.markdown("### 📝 Generated Title")
    st.markdown(f"**{metadata['title']}**")
    st.caption(f"Characters: {len(metadata['title'])}/53 (SEO optimized)")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Description section
    st.markdown('<div class="metadata-card">', unsafe_allow_html=True)
    st.markdown("### 📄 Generated Description")
    st.markdown(metadata['description'])
    word_count = len(metadata['description'].split())
    st.caption(f"Words: {word_count}/140")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # File download section
    st.markdown("### 💾 Download Results")
    
    # Create markdown content for download
    markdown_content = f"""# {metadata['title']}

{metadata['description']}

"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            label="📥 Download Markdown File",
            data=markdown_content,
            file_name=f"{video_id}.md",
            mime="text/markdown",
            help="Download as markdown file"
        )
    
    with col2:
        # JSON format for API compatibility
        json_data = {
            "title": metadata['title'],
            "description": metadata['description'],
            "file_path": filename,
            "video_id": video_id
        }
        
        st.download_button(
            label="📥 Download JSON Data",
            data=json.dumps(json_data, indent=2),
            file_name=f"{video_id}_metadata.json",
            mime="application/json",
            help="Download as JSON for API integration"
        )
    
    # Additional info
    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    st.markdown(f"""
    **File Information:**
    - Saved as: `{filename}`
    - Video ID: `{video_id}`
    - Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}
    """)
    st.markdown('</div>', unsafe_allow_html=True)

def display_api_info():
    """Display API information in sidebar."""
    with st.sidebar:
        st.markdown("### 📱 Mobile Access")
        
        # Get local IP address for mobile access
        try:
            # Get the actual network IP address, not localhost
            import subprocess
            result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
            if result.returncode == 0:
                local_ip = result.stdout.strip().split()[0]  # Get first IP address
            else:
                # Fallback method
                hostname = socket.gethostname()
                local_ip = socket.gethostbyname(hostname)
            
            mobile_url = f"http://{local_ip}:5000"
            
            # Generate QR code
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(mobile_url)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64 for display
            buffered = BytesIO()
            qr_img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            st.markdown(f"""
            **Scan QR code to access on your phone:**
            
            <div class="qr-container">
                <img src="data:image/png;base64,{img_str}" width="200" height="200">
                <br><small>{mobile_url}</small>
            </div>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Could not generate QR code: {e}")
        
        st.markdown("### 🔧 API Access")
        st.markdown("""
        **For mobile/programmatic access:**
        
        The same functionality is available via REST API at `/meta` endpoint.
        
        **Example curl command:**
        ```bash
        curl -X POST "http://localhost:8000/meta" \\
             -H "Content-Type: application/json" \\
             -d '{"url": "https://youtube.com/watch?v=..."}'
        ```
        
        **Response format:**
        ```json
        {
          "title": "Generated title",
          "description": "Generated description",
          "file_path": "video_id.md"
        }
        ```
        """)
        
        st.markdown("### 📊 Usage Stats")
        if 'processed_count' not in st.session_state:
            st.session_state.processed_count = 0
        
        st.metric("Videos Processed", st.session_state.processed_count)
        
        if st.button("🔄 Reset Counter"):
            st.session_state.processed_count = 0
            st.rerun()

def display_footer():
    """Display footer information."""
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p><strong>YouTube Metadata Generator</strong> | 
        Powered by <strong>Groq AI</strong> & <strong>yt-dlp</strong></p>
        <p><small>Extract captions • Generate SEO metadata • Save time</small></p>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main Streamlit application."""
    
    # Initialize generator
    generator = initialize_generator()
    
    # Display header
    display_header()
    
    # Display instructions
    display_instructions()
    
    # Main content area
    url = display_url_input()
    
    if url:
        display_processing_section(url, generator)
    
    # Sidebar info
    display_api_info()
    
    # Footer
    display_footer()

if __name__ == "__main__":
    main()