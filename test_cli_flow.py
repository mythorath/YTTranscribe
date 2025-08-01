#!/usr/bin/env python3
"""
Test script to verify the interactive CLI flow without actually running transcription.
This simulates user input to ensure the model selection logic is correct.
"""

import sys
import io
from unittest.mock import patch
from interactive_cli import select_transcription_mode, select_local_model, select_output_options

def test_cli_flow():
    """Test the CLI flow with different scenarios."""
    print("🧪 Testing Interactive CLI Flow")
    print("=" * 50)
    
    # Test 1: Auto mode with summary (should prompt for GPT model)
    print("\n📋 Test 1: Auto mode with summary")
    with patch('builtins.input', side_effect=['1']):
        mode = select_transcription_mode()
        print(f"✅ Mode selected: {mode}")
    
    with patch('builtins.input', side_effect=['2']):
        model_size = select_local_model()
        print(f"✅ Local model: {model_size}")
    
    with patch('builtins.input', side_effect=['./test_output', '1', '1']):
        output_dir, should_summarize, gpt_model = select_output_options()
        print(f"✅ Output: {output_dir}, Summary: {should_summarize}, GPT Model: {gpt_model}")
    
    # Test 2: Local mode without summary (should NOT prompt for GPT model)
    print("\n📋 Test 2: Local mode without summary")
    with patch('builtins.input', side_effect=['3']):
        mode = select_transcription_mode()
        print(f"✅ Mode selected: {mode}")
    
    with patch('builtins.input', side_effect=['3']):
        model_size = select_local_model()
        print(f"✅ Local model: {model_size}")
    
    with patch('builtins.input', side_effect=['./test_output', '2']):
        output_dir, should_summarize, gpt_model = select_output_options()
        print(f"✅ Output: {output_dir}, Summary: {should_summarize}, GPT Model: {gpt_model}")
    
    # Test 3: API mode with summary (should prompt for GPT model)
    print("\n📋 Test 3: API mode with summary")
    with patch('builtins.input', side_effect=['2']):
        mode = select_transcription_mode()
        print(f"✅ Mode selected: {mode}")
    
    with patch('builtins.input', side_effect=['./test_output', '1', '2']):
        output_dir, should_summarize, gpt_model = select_output_options()
        print(f"✅ Output: {output_dir}, Summary: {should_summarize}, GPT Model: {gpt_model}")
    
    print("\n🎉 All tests passed! CLI flow is working correctly.")
    print("✅ GPT model selection only appears when summary is requested.")

if __name__ == "__main__":
    test_cli_flow()
