"""
Transcription module supporting both OpenAI Whisper API and local faster-whisper.
"""

import os
import tempfile
from typing import Dict, List, Optional, Any
import logging

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: OpenAI library not available. API transcription will not work.")

try:
    from faster_whisper import WhisperModel
    FASTER_WHISPER_AVAILABLE = True
except ImportError:
    FASTER_WHISPER_AVAILABLE = False
    print("Warning: faster-whisper library not available. Local transcription will not work.")


class TranscriptionError(Exception):
    """Custom exception for transcription errors."""
    pass


class Transcriber:
    """Handles audio transcription using OpenAI API or local faster-whisper."""
    
    def __init__(self, api_key: Optional[str] = None, audio_extractor=None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.local_model = None
        self.audio_extractor = audio_extractor
        
        if self.api_key and OPENAI_AVAILABLE:
            openai.api_key = self.api_key
    
    def check_audio_file(self, audio_path: str) -> bool:
        """Check if audio file exists and has reasonable duration."""
        if not os.path.exists(audio_path):
            raise TranscriptionError(f"Audio file not found: {audio_path}")
        
        file_size = os.path.getsize(audio_path)
        file_size_mb = file_size / (1024 * 1024)
        
        if file_size < 1000:  # Less than 1KB is probably too small
            raise TranscriptionError(f"Audio file too small: {file_size} bytes")
        
        print(f"Audio file size: {file_size_mb:.1f} MB")
        return True
    
    def transcribe_with_api(self, audio_path: str) -> Dict[str, Any]:
        """Transcribe audio using OpenAI Whisper API."""
        if not OPENAI_AVAILABLE:
            raise TranscriptionError("OpenAI library not available")
        
        if not self.api_key:
            raise TranscriptionError("OpenAI API key not provided")
        
        self.check_audio_file(audio_path)
        
        # Check file size limit (25MB for OpenAI API) and compress if needed
        file_size = os.path.getsize(audio_path)
        max_size = 25 * 1024 * 1024  # 25MB
        file_size_mb = file_size / (1024 * 1024)
        
        if file_size > max_size:
            if self.audio_extractor and hasattr(self.audio_extractor, 'compress_audio_for_api'):
                print(f"File too large for API ({file_size_mb:.1f}MB > 25MB). Attempting compression...")
                audio_path = self.audio_extractor.compress_audio_for_api(audio_path)
                
                # Check if compression worked
                compressed_size = os.path.getsize(audio_path)
                compressed_size_mb = compressed_size / (1024 * 1024)
                
                if compressed_size > max_size:
                    raise TranscriptionError(f"File too large for API even after compression: {compressed_size_mb:.1f}MB > 25MB. Use --backend local for large files.")
                else:
                    print(f"Successfully compressed to {compressed_size_mb:.1f}MB")
            else:
                raise TranscriptionError(f"File too large for API: {file_size_mb:.1f}MB > 25MB. Use --backend local for large files.")
        
        try:
            print("Transcribing with OpenAI Whisper API...")
            
            with open(audio_path, 'rb') as audio_file:
                # Using the new OpenAI client format
                client = openai.OpenAI(api_key=self.api_key)
                response = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="verbose_json"
                )
            
            # Convert response to our standard format
            result = {
                'text': response.text,
                'segments': [],  # API doesn't provide detailed segments
                'language': getattr(response, 'language', 'en')
            }
            
            print("API transcription completed successfully!")
            return result
            
        except Exception as e:
            raise TranscriptionError(f"OpenAI API transcription failed: {str(e)}")
    
    def transcribe_with_local(self, audio_path: str, model_size: str = "base") -> Dict[str, Any]:
        """Transcribe audio using local faster-whisper."""
        if not FASTER_WHISPER_AVAILABLE:
            raise TranscriptionError("faster-whisper library not available")
        
        self.check_audio_file(audio_path)
        
        try:
            print(f"Loading local Whisper model ({model_size})...")
            
            # Initialize model if not already done
            if self.local_model is None or getattr(self.local_model, 'model_size', None) != model_size:
                self.local_model = WhisperModel(
                    model_size, 
                    device="cpu",  # Use CPU by default for compatibility
                    compute_type="int8"  # Optimize for speed/memory
                )
                self.local_model.model_size = model_size  # Store for reference
            
            print("Transcribing with local Whisper...")
            
            # Transcribe with simpler settings first
            segments_generator, info = self.local_model.transcribe(
                audio_path,
                language="en",  # Force English as specified
                vad_filter=False,  # Disable VAD initially to see if that's the issue
                beam_size=5,
                temperature=0.0
            )
            
            print(f"Audio info - Duration: {info.duration:.1f}s, Language: {info.language}")
            
            # Convert segments generator to list and process
            result_segments = []
            full_text = []
            
            # Convert generator to list to ensure we can iterate through it
            segments_list = list(segments_generator)
            print(f"Found {len(segments_list)} segments to process")
            
            for i, segment in enumerate(segments_list):
                segment_text = segment.text.strip()
                print(f"Segment {i}: '{segment_text}' ({segment.start:.1f}s - {segment.end:.1f}s)")
                if segment_text:  # Only process non-empty segments
                    segment_data = {
                        'start': segment.start,
                        'end': segment.end,
                        'text': segment_text,
                        'words': []
                    }
                    
                    result_segments.append(segment_data)
                    full_text.append(segment_text)
            
            # Join all text segments
            final_text = ' '.join(full_text)
            
            result = {
                'text': final_text,
                'segments': result_segments,
                'language': info.language,
                'duration': info.duration
            }
            
            print(f"Local transcription completed! Duration: {info.duration:.1f}s, Language: {info.language}")
            print(f"Extracted {len(result_segments)} segments, {len(final_text)} characters of text")
            return result
            
        except Exception as e:
            raise TranscriptionError(f"Local transcription failed: {str(e)}")
    
    def transcribe(self, audio_path: str, backend: str = "local", model_size: str = "base") -> Dict[str, Any]:
        """
        Main transcription method that chooses backend automatically or uses specified backend.
        
        Args:
            audio_path: Path to audio file
            backend: "api", "local", or "auto"
            model_size: Model size for local transcription ("tiny", "base", "small", "medium", "large")
            
        Returns:
            Dictionary with 'text', 'segments', and other metadata
        """
        if backend == "auto":
            # Try API first if available, fallback to local
            if self.api_key and OPENAI_AVAILABLE:
                try:
                    return self.transcribe_with_api(audio_path)
                except TranscriptionError as e:
                    print(f"API transcription failed, falling back to local: {e}")
                    backend = "local"
            else:
                backend = "local"
        
        if backend == "api":
            return self.transcribe_with_api(audio_path)
        elif backend == "local":
            return self.transcribe_with_local(audio_path, model_size)
        else:
            raise TranscriptionError(f"Unknown backend: {backend}")
    
    def transcribe_chunked_audio(self, chunk_paths: List[str], backend: str = "local", model_size: str = "base") -> Dict[str, Any]:
        """
        Transcribe multiple audio chunks and combine results.
        
        Args:
            chunk_paths: List of paths to audio chunks
            backend: Transcription backend to use
            model_size: Model size for local transcription
            
        Returns:
            Combined transcription result
        """
        print(f"Transcribing {len(chunk_paths)} audio chunks...")
        
        combined_segments = []
        combined_text_parts = []
        total_duration = 0.0
        chunk_duration_offset = 0.0
        
        for i, chunk_path in enumerate(chunk_paths):
            print(f"\nProcessing chunk {i+1}/{len(chunk_paths)}: {os.path.basename(chunk_path)}")
            
            try:
                # Transcribe individual chunk
                chunk_result = self.transcribe(chunk_path, backend, model_size)
                
                # Adjust timestamps to account for chunk position
                if 'segments' in chunk_result and chunk_result['segments']:
                    for segment in chunk_result['segments']:
                        adjusted_segment = {
                            'start': segment['start'] + chunk_duration_offset,
                            'end': segment['end'] + chunk_duration_offset,
                            'text': segment['text'],
                            'words': segment.get('words', [])
                        }
                        combined_segments.append(adjusted_segment)
                
                # Add text part
                if chunk_result.get('text'):
                    combined_text_parts.append(chunk_result['text'])
                
                # Update duration offset for next chunk
                if 'duration' in chunk_result:
                    chunk_duration_offset += chunk_result['duration']
                    total_duration += chunk_result['duration']
                else:
                    # Estimate chunk duration (10 minutes default)
                    estimated_duration = 600.0  # 10 minutes
                    chunk_duration_offset += estimated_duration
                    total_duration += estimated_duration
                
                print(f"  Chunk {i+1} completed ({len(chunk_result.get('segments', []))} segments)")
                
            except Exception as e:
                print(f"  Warning: Failed to transcribe chunk {i+1}: {e}")
                continue
        
        # Combine all results
        combined_text = ' '.join(combined_text_parts)
        
        result = {
            'text': combined_text,
            'segments': combined_segments,
            'language': 'en',  # Default to English
            'duration': total_duration,
            'chunk_count': len(chunk_paths)
        }
        
        print(f"\nCombined transcription: {len(combined_segments)} total segments, {total_duration:.1f}s duration")
        return result
    
    def cleanup(self):
        """Clean up loaded models and resources."""
        if self.local_model is not None:
            # faster-whisper doesn't need explicit cleanup, but we can clear the reference
            self.local_model = None
            print("Local model cleaned up")
