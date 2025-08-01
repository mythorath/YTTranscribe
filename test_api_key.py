#!/usr/bin/env python3
"""
Test script to verify that the OpenAI API key is being loaded correctly from .env file.
"""

import os
import sys

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ python-dotenv loaded successfully")
except ImportError:
    print("❌ python-dotenv not available")
    sys.exit(1)

def test_api_key_loading():
    """Test if OpenAI API key is properly loaded."""
    print("🔍 Testing API key loading...")
    
    # Check if the API key is loaded
    api_key = os.getenv('OPENAI_API_KEY')
    
    if api_key:
        # Mask the key for security (show first 8 and last 4 characters)
        if len(api_key) > 12:
            masked_key = f"{api_key[:8]}...{api_key[-4:]}"
        else:
            masked_key = "***"
        
        print(f"✅ OpenAI API key found: {masked_key}")
        print(f"📏 Key length: {len(api_key)} characters")
        
        # Check if it looks like a valid OpenAI key
        if api_key.startswith('sk-'):
            print("✅ Key format appears valid (starts with 'sk-')")
        else:
            print("⚠️  Key format unusual (doesn't start with 'sk-')")
            
        return True
    else:
        print("❌ OpenAI API key not found in environment")
        print("💡 Make sure .env file exists and contains OPENAI_API_KEY")
        return False

def test_imports():
    """Test if our modules can import and access the API key."""
    print("\n🔍 Testing module imports...")
    
    try:
        from src.transcriber import Transcriber
        transcriber = Transcriber()
        
        if transcriber.api_key:
            print("✅ Transcriber module loaded API key successfully")
        else:
            print("❌ Transcriber module could not load API key")
            
        from src.file_formatter import FileFormatter
        formatter = FileFormatter()
        
        if formatter.api_key:
            print("✅ FileFormatter module loaded API key successfully")
        else:
            print("❌ FileFormatter module could not load API key")
            
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def main():
    """Run all API key tests."""
    print("🔑 OpenAI API Key Loading Test")
    print("=" * 40)
    
    # Test direct loading
    key_loaded = test_api_key_loading()
    
    # Test module imports
    modules_ok = test_imports()
    
    print("\n" + "=" * 40)
    print("📊 SUMMARY:")
    
    if key_loaded and modules_ok:
        print("🎉 All tests passed! API key is properly loaded.")
        print("💡 You can now use the --summarize feature and API backend.")
    else:
        print("❌ Some tests failed. Check your .env file configuration.")
        print("\n📋 Troubleshooting:")
        print("1. Ensure .env file exists in the project root")
        print("2. Verify OPENAI_API_KEY is set correctly in .env")
        print("3. Make sure there are no extra spaces or quotes issues")

if __name__ == "__main__":
    main()
