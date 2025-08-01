#!/usr/bin/env python3
"""
Environment variable setup helper for YT2TranscriptBot
"""

import os
import subprocess

def show_api_key_status():
    """Show current API key status and setup instructions."""
    
    print("🔑 OpenAI API Key Environment Setup")
    print("=" * 50)
    
    # Check environment variable
    env_key = os.getenv('OPENAI_API_KEY')
    if env_key:
        print(f"✅ Environment variable set: ...{env_key[-4:]}")
    else:
        print("❌ Environment variable not set")
    
    # Check .env file
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            content = f.read()
        if 'OPENAI_API_KEY=' in content:
            print("✅ .env file contains API key")
        else:
            print("❌ .env file missing API key")
    else:
        print("❌ .env file not found")
    
    print("\n📋 Setup Instructions:")
    print("=" * 50)
    
    print("\n1. 🔄 Temporary Setup (Current Session Only):")
    print("   PowerShell:")
    print('   $env:OPENAI_API_KEY = "your-api-key-here"')
    print("   ")
    print("   Command Prompt:")
    print('   set OPENAI_API_KEY=your-api-key-here')
    print("   ")
    print("   Git Bash/Linux/macOS:")
    print('   export OPENAI_API_KEY="your-api-key-here"')
    
    print("\n2. 💾 Permanent Setup (Windows):")
    print("   Method 1 - System Properties:")
    print("   • Press Win+R, type 'sysdm.cpl'")
    print("   • Advanced tab → Environment Variables")
    print("   • Add new user variable:")
    print("     Name: OPENAI_API_KEY")
    print("     Value: your-api-key-here")
    print("   ")
    print("   Method 2 - PowerShell (Admin):")
    print('   [Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "your-key", "User")')
    
    print("\n3. 🐧 Permanent Setup (Linux/macOS):")
    print("   Add to ~/.bashrc or ~/.zshrc:")
    print('   export OPENAI_API_KEY="your-api-key-here"')
    print("   Then run: source ~/.bashrc")
    
    print("\n4. 📄 .env File (Automatic Loading):")
    print("   Create/edit .env file:")
    print("   OPENAI_API_KEY=your-api-key-here")
    print("   (This is automatically loaded by the application)")
    
    print("\n🧪 Test Your Setup:")
    print("=" * 50)
    print("   python test_api_key.py")
    print("   python interactive_cli.py")
    
    print("\n💡 Tips:")
    print("   • .env file is the easiest method")
    print("   • Environment variables override .env file")
    print("   • Never commit API keys to git repositories")
    print("   • Restart terminal after permanent setup")

if __name__ == "__main__":
    show_api_key_status()
