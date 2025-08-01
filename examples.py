#!/usr/bin/env python3
"""
Example usage script for YT2TranscriptBot.
Demonstrates various ways to use the tool programmatically.
"""

import os
import sys
import subprocess

# Add the src directory to the Python path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from audio_extractor import AudioExtractor
from transcriber import Transcriber
from file_formatter import FileFormatter


def example_basic_usage():
    """Example of basic programmatic usage."""
    print("🎬 Example: Basic Usage")
    print("=" * 30)
    
    # Example YouTube URL (Rick Astley - Never Gonna Give You Up)
    # This is a well-known, stable video for testing
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    print(f"Processing: {url}")
    
    # Initialize components
    extractor = AudioExtractor("./example_outputs")
    transcriber = Transcriber()  # Will use env OPENAI_API_KEY if available
    formatter = FileFormatter()
    
    try:
        # Step 1: Extract audio
        print("\n📥 Extracting audio...")
        audio_path, title, safe_title = extractor.download_audio(url)
        print(f"✅ Audio extracted: {title}")
        
        # Step 2: Transcribe (using local by default)
        print("\n🎤 Transcribing...")
        result = transcriber.transcribe(audio_path, backend="local", model_size="tiny")
        print("✅ Transcription completed")
        
        # Step 3: Save outputs
        print("\n💾 Saving files...")
        output_dir = os.path.join("./example_outputs", safe_title)
        saved_files = formatter.save_all_formats(result, output_dir, safe_title)
        
        print(f"\n🎉 Success! Files saved to: {output_dir}")
        for format_type, file_path in saved_files.items():
            print(f"  • {format_type.upper()}: {os.path.basename(file_path)}")
        
        # Show preview
        preview = result['text'][:150] + "..." if len(result['text']) > 150 else result['text']
        print(f"\n📝 Preview: \"{preview}\"")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Cleanup
        extractor.cleanup_temp_files()
        transcriber.cleanup()


def example_cli_commands():
    """Show example CLI commands."""
    print("\n🖥️  Example CLI Commands")
    print("=" * 30)
    
    examples = [
        ("Basic transcription (local)", 
         'python yt2transcript.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"'),
        
        ("Using OpenAI API", 
         'python yt2transcript.py "https://youtu.be/dQw4w9WgXcQ" --backend api'),
        
        ("With summary", 
         'python yt2transcript.py "https://youtu.be/dQw4w9WgXcQ" --summarize'),
        
        ("Custom model and output", 
         'python yt2transcript.py "https://youtu.be/dQw4w9WgXcQ" --model-size small --output-dir ./my_transcripts'),
        
        ("High quality local transcription", 
         'python yt2transcript.py "https://youtu.be/dQw4w9WgXcQ" --model-size medium --backend local'),
    ]
    
    for description, command in examples:
        print(f"\n📝 {description}:")
        print(f"   {command}")


def check_setup():
    """Quick setup check."""
    print("🔍 Quick Setup Check")
    print("=" * 20)
    
    # Check if we can import our modules
    try:
        from audio_extractor import AudioExtractor
        from transcriber import Transcriber
        from file_formatter import FileFormatter
        print("✅ All modules importable")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Check FFmpeg
    import shutil
    if shutil.which("ffmpeg"):
        print("✅ FFmpeg available")
    else:
        print("❌ FFmpeg not found")
        return False
    
    # Check API key (optional)
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print("✅ OpenAI API key found")
    else:
        print("⚠️  No OpenAI API key (local transcription only)")
    
    return True


def main():
    """Run examples."""
    print("🎬 YT2TranscriptBot Examples")
    print("=" * 40)
    
    # Quick setup check
    if not check_setup():
        print("\n❌ Setup issues detected. Please run setup.bat or test_setup.py")
        return
    
    print("\n🎯 Choose an example:")
    print("1. Show CLI command examples")
    print("2. Run basic programmatic example")
    print("3. Both")
    
    try:
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice in ['1', '3']:
            example_cli_commands()
        
        if choice in ['2', '3']:
            print("\n" + "=" * 50)
            confirm = input("\nRun basic example? This will download and transcribe a short video (y/N): ").strip().lower()
            if confirm == 'y':
                example_basic_usage()
            else:
                print("Skipped programmatic example")
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled")


if __name__ == "__main__":
    main()
