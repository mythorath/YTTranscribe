#!/usr/bin/env python3
"""
Simple test script to validate YT2TranscriptBot setup and dependencies.
"""

import sys
import shutil
import os

def test_python_version():
    """Test if Python version is sufficient."""
    print("🐍 Testing Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Need 3.9+")
        return False

def test_ffmpeg():
    """Test if FFmpeg is available."""
    print("🎬 Testing FFmpeg availability...")
    if shutil.which("ffmpeg"):
        print("✅ FFmpeg - OK")
        return True
    else:
        print("❌ FFmpeg - NOT FOUND")
        print("   Install with: choco install ffmpeg (Windows)")
        return False

def test_imports():
    """Test if required packages can be imported."""
    print("📦 Testing package imports...")
    
    packages = [
        ("yt_dlp", "yt-dlp"),
        ("openai", "openai"),
        ("tqdm", "tqdm"),
        ("faster_whisper", "faster-whisper"),
        ("pydub", "pydub")
    ]
    
    results = []
    for package, pip_name in packages:
        try:
            __import__(package)
            print(f"✅ {pip_name} - OK")
            results.append(True)
        except ImportError:
            print(f"❌ {pip_name} - NOT FOUND")
            print(f"   Install with: pip install {pip_name}")
            results.append(False)
    
    return all(results)

def test_api_key():
    """Test if OpenAI API key is available."""
    print("🔑 Testing OpenAI API key...")
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        # Don't print the full key for security
        masked_key = f"{api_key[:8]}...{api_key[-4:]}" if len(api_key) > 12 else "***"
        print(f"✅ API key found: {masked_key}")
        return True
    else:
        print("⚠️  OpenAI API key not found in environment")
        print("   Set with: set OPENAI_API_KEY=your_key_here (Windows)")
        print("   Note: API key is optional for local transcription")
        return False

def test_project_structure():
    """Test if project files exist."""
    print("📁 Testing project structure...")
    
    required_files = [
        "yt2transcript.py",
        "requirements.txt",
        "README.md",
        "src/__init__.py",
        "src/audio_extractor.py",
        "src/transcriber.py",
        "src/file_formatter.py"
    ]
    
    results = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} - OK")
            results.append(True)
        else:
            print(f"❌ {file_path} - MISSING")
            results.append(False)
    
    return all(results)

def main():
    """Run all tests."""
    print("🔍 YT2TranscriptBot Setup Validation")
    print("=" * 40)
    
    tests = [
        ("Python Version", test_python_version),
        ("FFmpeg", test_ffmpeg),
        ("Python Packages", test_imports),
        ("API Key", test_api_key),
        ("Project Structure", test_project_structure)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        results.append(test_func())
    
    print("\n" + "=" * 40)
    print("📊 SUMMARY:")
    
    critical_tests = results[:3] + [results[4]]  # Python, FFmpeg, Packages, Structure
    if all(critical_tests):
        print("🎉 All critical tests passed! YT2TranscriptBot is ready to use.")
        if not results[3]:  # API key
            print("💡 Note: No API key found, but local transcription will work.")
        print("\n🚀 Try running:")
        print('   python yt2transcript.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"')
    else:
        print("❌ Some critical tests failed. Please fix the issues above.")
        print("\n📋 Setup checklist:")
        print("   1. Install Python 3.9+")
        print("   2. Install FFmpeg")
        print("   3. pip install -r requirements.txt")
        print("   4. (Optional) Set OPENAI_API_KEY environment variable")

if __name__ == "__main__":
    main()
