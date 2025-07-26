#!/usr/bin/env python3
"""
Test script to verify the YouTube Metadata Generator setup.
Run this to check if everything is working correctly.
"""

import os
import sys

def test_imports():
    """Test if all required modules can be imported."""
    print("🔍 Testing imports...")
    
    try:
        import yt_dlp
        print("✅ yt-dlp imported successfully")
    except ImportError as e:
        print(f"❌ yt-dlp import failed: {e}")
        return False
    
    try:
        import groq
        print("✅ groq imported successfully")
    except ImportError as e:
        print(f"❌ groq import failed: {e}")
        return False
    
    try:
        import streamlit
        print("✅ streamlit imported successfully")
    except ImportError as e:
        print(f"❌ streamlit import failed: {e}")
        return False
    
    try:
        import requests
        print("✅ requests imported successfully")
    except ImportError as e:
        print(f"❌ requests import failed: {e}")
        return False
    
    return True

def test_api_key():
    """Test if Groq API key is set and valid."""
    print("\n🔑 Testing API key...")
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ GROQ_API_KEY environment variable not set")
        print("   Set it with: export GROQ_API_KEY='your_api_key_here'")
        return False
    
    if not api_key.startswith("gsk_"):
        print("❌ API key doesn't start with 'gsk_' - may be invalid")
        return False
    
    print(f"✅ API key found: {api_key[:10]}...")
    
    # Test API connection
    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        print("✅ Groq client initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize Groq client: {e}")
        return False

def test_core_module():
    """Test if the core module can be imported and initialized."""
    print("\n📦 Testing core module...")
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from core import YouTubeMetaGenerator
        print("✅ Core module imported successfully")
        
        # Test initialization
        generator = YouTubeMetaGenerator()
        print("✅ YouTubeMetaGenerator initialized successfully")
        return True
        
    except ValueError as e:
        print(f"❌ Initialization failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Core module test failed: {e}")
        return False

def test_youtube_extraction():
    """Test YouTube video ID extraction."""
    print("\n🎥 Testing YouTube extraction...")
    
    try:
        from core import YouTubeMetaGenerator
        generator = YouTubeMetaGenerator()
        
        # Test video ID extraction
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        video_id = generator.extract_video_id(test_url)
        
        if video_id == "dQw4w9WgXcQ":
            print("✅ Video ID extraction works correctly")
            return True
        else:
            print(f"❌ Video ID extraction failed. Expected 'dQw4w9WgXcQ', got '{video_id}'")
            return False
            
    except Exception as e:
        print(f"❌ YouTube extraction test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 YouTube Metadata Generator - Setup Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_api_key,
        test_core_module,
        test_youtube_extraction
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your setup is ready to go.")
        print("\n🚀 You can now run:")
        print("   • Web app: streamlit run app.py --server.port 5000")
        print("   • CLI: python gen_meta.py 'https://youtube.com/watch?v=...'")
        print("   • API: python server.py")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        print("\n💡 Common fixes:")
        print("   • Install dependencies: pip install -r requirements.txt")
        print("   • Set API key: export GROQ_API_KEY='your_api_key_here'")
        print("   • Get API key from: https://console.groq.com")

if __name__ == "__main__":
    main() 