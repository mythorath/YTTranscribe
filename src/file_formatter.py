"""
File formatting module for creating SRT, VTT, and summary files.
"""

import os
from typing import Dict, List, Any, Optional
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


class FileFormatter:
    """Handles formatting and saving of transcription outputs."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if self.api_key and OPENAI_AVAILABLE:
            openai.api_key = self.api_key
    
    @staticmethod
    def format_timestamp(seconds: float, srt_format: bool = True) -> str:
        """
        Format timestamp for SRT or VTT files.
        
        Args:
            seconds: Time in seconds
            srt_format: If True, use SRT format (,), if False use VTT format (.)
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds % 1) * 1000)
        
        if srt_format:
            return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"
        else:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}.{milliseconds:03d}"
    
    def create_srt(self, segments: List[Dict[str, Any]], output_path: str) -> bool:
        """Create SRT subtitle file from segments."""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                if not segments:
                    # If no segments (API mode), create a single entry
                    f.write("1\n")
                    f.write("00:00:00,000 --> 00:05:00,000\n")
                    f.write("[Transcript available in .txt file - no timing data from API]\n\n")
                    return True
                
                for i, segment in enumerate(segments, 1):
                    start_time = self.format_timestamp(segment['start'], srt_format=True)
                    end_time = self.format_timestamp(segment['end'], srt_format=True)
                    text = segment['text'].strip()
                    
                    if text:  # Only write non-empty segments
                        f.write(f"{i}\n")
                        f.write(f"{start_time} --> {end_time}\n")
                        f.write(f"{text}\n\n")
            
            print(f"SRT file created: {output_path}")
            return True
            
        except Exception as e:
            print(f"Error creating SRT file: {e}")
            return False
    
    def create_vtt(self, segments: List[Dict[str, Any]], output_path: str) -> bool:
        """Create VTT subtitle file from segments."""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("WEBVTT\n\n")
                
                if not segments:
                    # If no segments (API mode), create a single entry
                    f.write("00:00:00.000 --> 00:05:00.000\n")
                    f.write("[Transcript available in .txt file - no timing data from API]\n\n")
                    return True
                
                for segment in segments:
                    start_time = self.format_timestamp(segment['start'], srt_format=False)
                    end_time = self.format_timestamp(segment['end'], srt_format=False)
                    text = segment['text'].strip()
                    
                    if text:  # Only write non-empty segments
                        f.write(f"{start_time} --> {end_time}\n")
                        f.write(f"{text}\n\n")
            
            print(f"VTT file created: {output_path}")
            return True
            
        except Exception as e:
            print(f"Error creating VTT file: {e}")
            return False
    
    def save_transcript(self, text: str, output_path: str, segments: List[Dict[str, Any]] = None) -> bool:
        """
        Save transcript in standard transcription format.
        
        Args:
            text: The full transcript text
            output_path: Path to save the transcript
            segments: Optional segment data with timestamps for formatted output
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                if segments and len(segments) > 0:
                    # Create formatted transcript with timestamps
                    f.write("TRANSCRIPT\n")
                    f.write("=" * 50 + "\n\n")
                    
                    for i, segment in enumerate(segments):
                        start_time = self.format_timestamp(segment['start'], srt_format=False)
                        end_time = self.format_timestamp(segment['end'], srt_format=False)
                        segment_text = segment['text'].strip()
                        
                        if segment_text:  # Only write non-empty segments
                            f.write(f"[{start_time} -> {end_time}]\n")
                            f.write(f"{segment_text}\n\n")
                    
                    # Add full text section at the end
                    f.write("\n" + "=" * 50 + "\n")
                    f.write("FULL TRANSCRIPT (Plain Text)\n")
                    f.write("=" * 50 + "\n\n")
                    
                    # Format the text into paragraphs
                    formatted_text = self._format_text_into_paragraphs(text)
                    f.write(formatted_text)
                else:
                    # Fallback for API mode or when no segments available
                    f.write("TRANSCRIPT\n")
                    f.write("=" * 50 + "\n\n")
                    
                    # Format the text into paragraphs
                    formatted_text = self._format_text_into_paragraphs(text)
                    f.write(formatted_text)
            
            print(f"Transcript saved: {output_path}")
            return True
            
        except Exception as e:
            print(f"Error saving transcript: {e}")
            return False
    
    def _format_text_into_paragraphs(self, text: str, max_line_length: int = 80, sentences_per_paragraph: int = 4) -> str:
        """
        Format raw transcript text into readable paragraphs.
        
        Args:
            text: Raw transcript text
            max_line_length: Maximum characters per line
            sentences_per_paragraph: Number of sentences per paragraph
        """
        import re
        
        # Split into sentences (basic sentence detection)
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        sentences = [s.strip() for s in sentences if s.strip()]
        
        formatted_text = ""
        current_paragraph = []
        
        for sentence in sentences:
            current_paragraph.append(sentence)
            
            # Create paragraph after specified number of sentences
            if len(current_paragraph) >= sentences_per_paragraph:
                paragraph_text = ' '.join(current_paragraph)
                formatted_text += self._wrap_paragraph(paragraph_text, max_line_length)
                current_paragraph = []
        
        # Handle remaining sentences
        if current_paragraph:
            paragraph_text = ' '.join(current_paragraph)
            formatted_text += self._wrap_paragraph(paragraph_text, max_line_length)
        
        return formatted_text
    
    def _wrap_paragraph(self, paragraph_text: str, max_line_length: int) -> str:
        """Wrap a paragraph to specified line length."""
        if len(paragraph_text) <= max_line_length:
            return paragraph_text + '\n\n'
        
        words = paragraph_text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 > max_line_length and current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
            else:
                current_line.append(word)
                current_length += len(word) + (1 if current_line else 0)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return '\n'.join(lines) + '\n\n'
    
    def create_summary(self, transcript_text: str, output_path: str, model: str = "gpt-3.5-turbo") -> bool:
        """
        Create a summary of the transcript using GPT.
        
        Args:
            transcript_text: The full transcript text
            output_path: Path to save the summary
            model: GPT model to use ("gpt-3.5-turbo" or "gpt-4")
        """
        if not OPENAI_AVAILABLE:
            print("Error: OpenAI library not available for summarization")
            return False
        
        if not self.api_key:
            print("Error: OpenAI API key not provided for summarization")
            return False
        
        try:
            # Limit text length to avoid token limits
            max_chars = 12000  # Conservative limit for GPT-3.5-turbo
            if len(transcript_text) > max_chars:
                transcript_text = transcript_text[:max_chars] + "... [truncated]"
            
            prompt = f"""Please provide a concise summary of this transcript, highlighting the main points and key information:

{transcript_text}

Summary:"""
            
            print(f"Creating summary using {model}...")
            
            client = openai.OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates concise, informative summaries of transcripts."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            summary = response.choices[0].message.content.strip()
            
            # Save summary to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(summary)
            
            print(f"Summary created: {output_path}")
            return True
            
        except Exception as e:
            print(f"Error creating summary: {e}")
            return False
    
    def save_all_formats(self, transcription_result: Dict[str, Any], output_dir: str, 
                        safe_title: str, create_summary: bool = False) -> Dict[str, str]:
        """
        Save transcription in all formats (txt, srt, vtt, and optionally summary).
        
        Returns:
            Dictionary mapping format names to file paths
        """
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Define output file paths
        paths = {
            'txt': os.path.join(output_dir, 'transcript.txt'),
            'srt': os.path.join(output_dir, 'transcript.srt'),
            'vtt': os.path.join(output_dir, 'transcript.vtt'),
        }
        
        results = {}
        
        # Save transcript text with segments for formatting
        segments = transcription_result.get('segments', [])
        if self.save_transcript(transcription_result['text'], paths['txt'], segments):
            results['txt'] = paths['txt']
        
        # Save SRT and VTT files
        segments = transcription_result.get('segments', [])
        
        if self.create_srt(segments, paths['srt']):
            results['srt'] = paths['srt']
        
        if self.create_vtt(segments, paths['vtt']):
            results['vtt'] = paths['vtt']
        
        # Create summary if requested
        if create_summary:
            summary_path = os.path.join(output_dir, 'summary.txt')
            if self.create_summary(transcription_result['text'], summary_path):
                results['summary'] = summary_path
                paths['summary'] = summary_path
        
        return results
