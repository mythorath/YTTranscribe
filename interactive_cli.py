#!/usr/bin/env python3
"""
Interactive CLI interface for YT2TranscriptBot.
Provides user-friendly prompts for URL input, mode selection, and model choices.
"""

import os
import sys
import subprocess

def print_banner():
    """Print the application banner."""
    print("=" * 60)
    print("🎬 YT2TranscriptBot - Interactive CLI")
    print("=" * 60)
    print("Extract and transcribe YouTube videos with ease!")
    print()

def get_youtube_url():
    """Prompt user for YouTube URL with validation."""
    while True:
        print("📥 Enter YouTube URL:")
        url = input("URL: ").strip()
        
        if not url:
            print("❌ Please enter a URL\n")
            continue
            
        # Basic URL validation
        youtube_patterns = [
            'youtube.com/watch?v=',
            'youtu.be/',
            'youtube.com/embed/',
            'youtube.com/v/'
        ]
        
        if any(pattern in url for pattern in youtube_patterns):
            return url
        else:
            print("❌ Please enter a valid YouTube URL\n")

def select_transcription_mode():
    """Let user select transcription mode."""
    print("\n🎤 Select transcription mode:")
    print("1. 🔄 Auto (API first, fallback to local)")
    print("2. 🌐 API only (OpenAI Whisper)")
    print("3. 🏠 Local only (faster-whisper)")
    
    while True:
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == "1":
            return "auto"
        elif choice == "2":
            return "api"
        elif choice == "3":
            return "local"
        else:
            print("❌ Please enter 1, 2, or 3")

def select_gpt_model():
    """Let user select GPT model for summarization."""
    print("\n� Available GPT models for summarization:")
    print("1. 💡 gpt-3.5-turbo (Faster, cheaper)")
    print("2. 🚀 gpt-4 (Better quality, more expensive)")
    print("3. 🎯 gpt-4-turbo (Latest, balanced performance)")
    
    models = {
        "1": "gpt-3.5-turbo",
        "2": "gpt-4", 
        "3": "gpt-4-turbo"
    }
    
    while True:
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice in models:
            return models[choice]
        else:
            print("❌ Please enter 1, 2, or 3")

def select_local_model():
    """Let user select local model size."""
    print("\n🏠 Select local model size:")
    print("1. 🚀 tiny (39 MB, fastest, least accurate)")
    print("2. ⚡ base (74 MB, balanced speed/accuracy)")
    print("3. 📊 small (244 MB, good accuracy)")
    print("4. 🎯 medium (769 MB, better accuracy)")
    print("5. 🏆 large (1550 MB, best accuracy)")
    
    models = {
        "1": "tiny",
        "2": "base", 
        "3": "small",
        "4": "medium",
        "5": "large"
    }
    
    while True:
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice in models:
            return models[choice]
        else:
            print("❌ Please enter 1, 2, 3, 4, or 5")

def select_output_options():
    """Let user select output options."""
    print("\n📁 Output options:")
    
    # Output directory
    print("Enter output directory (or press Enter for './outputs'):")
    output_dir = input("Directory: ").strip()
    if not output_dir:
        output_dir = "./outputs"
    
    # Summary option
    print("\n🧠 Generate AI summary?")
    print("1. Yes - Generate summary with GPT")
    print("2. No - Transcript only")
    
    while True:
        choice = input("Enter choice (1-2): ").strip()
        if choice == "1":
            summarize = True
            gpt_model = select_gpt_model()
            break
        elif choice == "2":
            summarize = False
            gpt_model = None  # No GPT model needed when not summarizing
            break
        else:
            print("❌ Please enter 1 or 2")
    
    return output_dir, summarize, gpt_model

def check_api_key():
    """Check if OpenAI API key is available."""
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print(f"✅ OpenAI API key found (ends with: ...{api_key[-4:]})")
        return True
    else:
        print("⚠️ No OpenAI API key found in environment")
        print("   API modes will not work without an API key")
        return False

def build_command(url, mode, model_size, output_dir, summarize, gpt_model):
    """Build the command to execute."""
    cmd = ["python", "yt2transcript.py", url]
    
    # Add backend
    cmd.extend(["--backend", mode])
    
    # Add model size for local
    if mode in ["local", "auto"]:
        cmd.extend(["--model-size", model_size])
    
    # Add output directory
    if output_dir != "./outputs":
        cmd.extend(["--output-dir", output_dir])
    
    # Add summary option
    if summarize:
        cmd.append("--summarize")
        if gpt_model:  # Only add GPT model if one was selected
            cmd.extend(["--gpt-model", gpt_model])
    
    return cmd

def main():
    """Main interactive CLI function."""
    try:
        print_banner()
        
        # Check if we're in the right directory
        if not os.path.exists("yt2transcript.py"):
            print("❌ Error: yt2transcript.py not found in current directory")
            print("   Please run this from the yt2transcriptbot directory")
            sys.exit(1)
        
        # Get YouTube URL
        url = get_youtube_url()
        
        # Check API key availability
        print("\n🔑 Checking API key...")
        has_api_key = check_api_key()
        
        # Select mode
        mode = select_transcription_mode()
        
        # Model selection
        model_size = "base"  # default
        
        if mode == "api":
            if not has_api_key:
                print("\n❌ Cannot use API mode without OpenAI API key")
                print("   Please set OPENAI_API_KEY environment variable")
                sys.exit(1)
            print("\n🤖 API mode: Using whisper-1 model (OpenAI's standard Whisper model)")
        elif mode == "local":
            model_size = select_local_model()
        else:  # auto mode
            if has_api_key:
                print("\n🔄 Auto mode: Will try API (whisper-1) first, then fallback to local if needed")
            model_size = select_local_model()
        
        # Output options (includes GPT model selection if summary requested)
        output_dir, summarize, gpt_model = select_output_options()
        
        # Build and display command
        cmd = build_command(url, mode, model_size, output_dir, summarize, gpt_model)
        
        print("\n" + "=" * 60)
        print("🚀 Ready to process!")
        print("=" * 60)
        print(f"📹 URL: {url}")
        print(f"🎤 Mode: {mode}")
        if mode in ["local", "auto"]:
            print(f"🏠 Local model: {model_size}")
        if mode in ["api", "auto"] and has_api_key:
            print("🌐 API model: whisper-1")
        print(f"📁 Output: {output_dir}")
        print(f"🧠 Summary: {'Yes' if summarize else 'No'}")
        if summarize:
            print(f"🤖 GPT model: {gpt_model}")
        print()
        print(f"Command: {' '.join(cmd)}")
        print()
        
        # Confirm execution
        while True:
            confirm = input("Execute? (y/n): ").strip().lower()
            if confirm in ['y', 'yes']:
                break
            elif confirm in ['n', 'no']:
                print("❌ Cancelled by user")
                sys.exit(0)
            else:
                print("Please enter 'y' or 'n'")
        
        # Execute the command
        print("\n🎬 Starting transcription...")
        print("=" * 60)
        
        try:
            subprocess.run(cmd, check=True)
            print("\n" + "=" * 60)
            print("✅ Transcription completed successfully!")
            print("=" * 60)
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Error during transcription: {e}")
            sys.exit(1)
        except KeyboardInterrupt:
            print("\n\n❌ Interrupted by user")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n❌ Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
