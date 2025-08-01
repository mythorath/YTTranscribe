#!/usr/bin/env python3
"""
YT2TranscriptBot - A CLI tool for extracting and transcribing YouTube videos.

This tool downloads audio from YouTube videos and transcribes them using 
OpenAI Whisper (API or local) with support for multiple output formats.
"""

import argparse
import os
import shutil
import sys
from typing import Optional

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file from current directory
except ImportError:
    # python-dotenv not installed, continue without it
    pass

from src.audio_extractor import AudioExtractor
from src.transcriber import Transcriber, TranscriptionError
from src.file_formatter import FileFormatter


def check_dependencies():
    """Check if required system dependencies are available."""
    # Check FFmpeg
    if not shutil.which("ffmpeg"):
        print("❌ Error: FFmpeg not found in PATH")
        print("Please install FFmpeg:")
        print("  Windows: choco install ffmpeg")
        print("  macOS: brew install ffmpeg")
        print("  Linux: sudo apt install ffmpeg")
        return False
    
    print("✅ FFmpeg found")
    return True


def create_output_directory(base_dir: str, safe_title: str) -> str:
    """Create output directory, handling conflicts by appending numbers."""
    output_dir = os.path.join(base_dir, safe_title)
    
    # Handle directory conflicts
    counter = 1
    original_dir = output_dir
    while os.path.exists(output_dir):
        output_dir = f"{original_dir}_{counter}"
        counter += 1
    
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="YT2TranscriptBot - Extract and transcribe YouTube videos",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python yt2transcript.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  python yt2transcript.py "https://youtu.be/dQw4w9WgXcQ" --backend api
  python yt2transcript.py "https://youtu.be/dQw4w9WgXcQ" --summarize --model-size small
        """
    )
    
    # Positional arguments
    parser.add_argument(
        "url",
        help="YouTube URL to transcribe"
    )
    
    # Optional arguments
    parser.add_argument(
        "--output-dir",
        default="./outputs",
        help="Output directory for transcriptions (default: ./outputs)"
    )
    
    parser.add_argument(
        "--backend",
        choices=["api", "local", "auto"],
        default="local",
        help="Transcription backend: 'api' (OpenAI), 'local' (faster-whisper), or 'auto' (default: local)"
    )
    
    parser.add_argument(
        "--model-size",
        choices=["tiny", "base", "small", "medium", "large"],
        default="base",
        help="Model size for local transcription (default: base)"
    )
    
    parser.add_argument(
        "--api-key",
        help="OpenAI API key (default: OPENAI_API_KEY environment variable)"
    )
    
    parser.add_argument(
        "--summarize",
        action="store_true",
        help="Create a summary using GPT (requires OpenAI API key)"
    )
    
    parser.add_argument(
        "--gpt-model",
        choices=["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
        default="gpt-3.5-turbo",
        help="GPT model for summarization (default: gpt-3.5-turbo)"
    )
    
    # Future features (commented out for now)
    # parser.add_argument(
    #     "--batch-file",
    #     help="Path to text file containing list of URLs to process"
    # )
    # 
    # parser.add_argument(
    #     "--playlist",
    #     action="store_true",
    #     help="Treat input URL as a playlist"
    # )
    
    args = parser.parse_args()
    
    # Check system dependencies
    print("🔍 Checking system dependencies...")
    if not check_dependencies():
        sys.exit(1)
    
    # Initialize components
    api_key = args.api_key or os.getenv('OPENAI_API_KEY')
    audio_extractor = AudioExtractor(args.output_dir)
    transcriber = Transcriber(api_key, audio_extractor)
    formatter = FileFormatter(api_key)
    
    try:
        print(f"\n🎬 Processing: {args.url}")
        
        # Step 1: Extract audio
        print("\n📥 Step 1: Extracting audio...")
        audio_path, video_title, safe_title = audio_extractor.download_audio(args.url)
        
        if not audio_path:
            print("❌ Failed to extract audio")
            sys.exit(1)
        
        print(f"✅ Audio extracted: {video_title}")
        
        # Step 2: Create output directory
        output_dir = create_output_directory(args.output_dir, safe_title)
        print(f"📁 Output directory: {output_dir}")
        
        # Step 3: Transcribe audio
        print(f"\n🎤 Step 2: Transcribing with {args.backend} backend...")
        
        try:
            # Check if file is extremely large and might need chunking
            file_size_mb = os.path.getsize(audio_path) / (1024 * 1024)
            
            # For very large files (>100MB), use chunking for local transcription
            if file_size_mb > 100 and args.backend in ["local", "auto"]:
                print(f"Large file detected ({file_size_mb:.1f}MB). Using chunked processing...")
                chunk_paths = audio_extractor.split_audio_for_processing(audio_path, chunk_duration_minutes=10)
                
                if len(chunk_paths) > 1:
                    transcription_result = transcriber.transcribe_chunked_audio(
                        chunk_paths, 
                        backend="local", 
                        model_size=args.model_size
                    )
                else:
                    # Fallback to normal processing if chunking failed
                    transcription_result = transcriber.transcribe(
                        audio_path, 
                        backend=args.backend, 
                        model_size=args.model_size
                    )
            else:
                # Normal processing for smaller files
                transcription_result = transcriber.transcribe(
                    audio_path, 
                    backend=args.backend, 
                    model_size=args.model_size
                )
        except TranscriptionError as e:
            if args.backend == "api":
                print(f"❌ API transcription failed: {e}")
                print("🔄 Attempting fallback to local transcription...")
                try:
                    transcription_result = transcriber.transcribe(
                        audio_path, 
                        backend="local", 
                        model_size=args.model_size
                    )
                except TranscriptionError as fallback_error:
                    print(f"❌ Local fallback also failed: {fallback_error}")
                    sys.exit(1)
            else:
                print(f"❌ Transcription failed: {e}")
                sys.exit(1)
        
        print("✅ Transcription completed!")
        
        # Step 4: Save all formats
        print("\n💾 Step 3: Saving output files...")
        
        saved_files = formatter.save_all_formats(
            transcription_result,
            output_dir,
            safe_title,
            create_summary=args.summarize
        )
        
        # Display results
        print(f"\n🎉 Success! Files saved to: {output_dir}")
        print("\n📄 Generated files:")
        for format_type, file_path in saved_files.items():
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            print(f"  • {format_type.upper()}: {os.path.basename(file_path)} ({file_size:,} bytes)")
        
        # Show transcript preview
        transcript_preview = transcription_result['text'][:200]
        if len(transcription_result['text']) > 200:
            transcript_preview += "..."
        
        print(f"\n📝 Transcript preview:")
        print(f"   \"{transcript_preview}\"")
        
        # Show additional info
        if 'duration' in transcription_result:
            duration = transcription_result['duration']
            print(f"\n📊 Audio duration: {duration:.1f} seconds")
        
        if 'language' in transcription_result:
            language = transcription_result['language']
            print(f"🌐 Detected language: {language}")
        
        segments_count = len(transcription_result.get('segments', []))
        if segments_count > 0:
            print(f"📋 Transcript segments: {segments_count}")
        
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
    finally:
        # Cleanup
        print("\n🧹 Cleaning up...")
        audio_extractor.cleanup()
        transcriber.cleanup()


if __name__ == "__main__":
    main()
