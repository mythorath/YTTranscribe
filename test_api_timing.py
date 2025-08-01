#!/usr/bin/env python3
"""
Test script to verify API timing data extraction.
"""

import os
import sys
sys.path.insert(0, '.')

from dotenv import load_dotenv
load_dotenv()

from src.transcriber import Transcriber
from src.audio_extractor import AudioExtractor

def test_api_timing():
    """Test if API returns timing data."""
    print("🧪 Testing OpenAI API timing data extraction")
    print("=" * 50)
    
    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ No OpenAI API key found. Please set OPENAI_API_KEY")
        return
    
    print(f"✅ API key found: {api_key[-4:]}")
    
    # Initialize components
    extractor = AudioExtractor()
    transcriber = Transcriber(api_key=api_key, audio_extractor=extractor)
    
    # Test URL - a short video for quick testing
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    try:
        print(f"\n📥 Downloading audio from: {test_url}")
        
        # Extract audio - returns (audio_path, video_title, safe_title)
        audio_path, video_title, safe_title = extractor.download_audio(test_url)
        
        if audio_path:
            print(f"✅ Audio downloaded: {audio_path}")
            print(f"📹 Video title: {video_title}")
            
            # Test API transcription
            print("\n🎤 Testing API transcription with timing...")
            result = transcriber.transcribe_with_api(audio_path)
            
            print(f"\n📊 Results:")
            print(f"Text length: {len(result['text'])} characters")
            print(f"Segments: {len(result['segments'])}")
            
            if result['segments']:
                print("\n🎯 Sample segments with timing:")
                for i, segment in enumerate(result['segments'][:3]):  # Show first 3
                    start = segment['start']
                    end = segment['end']
                    text = segment['text'][:50] + "..." if len(segment['text']) > 50 else segment['text']
                    print(f"  {i+1}. {start:.1f}s - {end:.1f}s: {text}")
                
                print(f"\n✅ SUCCESS: API returned {len(result['segments'])} timestamped segments!")
            else:
                print("\n❌ No timing data returned from API")
                print(f"Raw text preview: {result['text'][:100]}...")
            
            # Cleanup
            try:
                os.remove(audio_path)
                print(f"\n🧹 Cleaned up: {audio_path}")
            except Exception as e:
                print(f"⚠️ Cleanup warning: {e}")
                
        else:
            print(f"❌ Audio extraction failed")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api_timing()
