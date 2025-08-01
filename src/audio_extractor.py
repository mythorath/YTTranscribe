"""
Audio extraction module using yt-dlp for downloading YouTube audio.
"""

import os
import re
import subprocess
import tempfile
from typing import Optional, Tuple

import yt_dlp
from tqdm import tqdm


class AudioExtractor:
    """Handles audio extraction from YouTube URLs using yt-dlp."""
    
    def __init__(self, output_dir: str = "./outputs"):
        self.output_dir = output_dir
        self.temp_dir = tempfile.mkdtemp()
    
    def validate_url(self, url: str) -> bool:
        """Validate if the URL is a valid YouTube URL."""
        youtube_patterns = [
            r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=[\w-]+',
            r'(?:https?://)?(?:www\.)?youtu\.be/[\w-]+',
            r'(?:https?://)?(?:www\.)?youtube\.com/embed/[\w-]+',
            r'(?:https?://)?(?:www\.)?youtube\.com/v/[\w-]+'
        ]
        
        for pattern in youtube_patterns:
            if re.match(pattern, url):
                return True
        return False
    
    def get_video_info(self, url: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract video title and ID from URL."""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'unknown_video')
                video_id = info.get('id', 'unknown_id')
                return title, video_id
                
        except Exception as e:
            print(f"Error extracting video info: {e}")
            return None, None
    
    def create_safe_filename(self, title: str) -> str:
        """Create a safe filename from video title."""
        # Remove or replace invalid characters
        safe_title = re.sub(r'[<>:"/\\|?*]', '', title)
        safe_title = re.sub(r'\s+', '_', safe_title.strip())
        # Limit length
        safe_title = safe_title[:100]
        return safe_title or "unknown_video"
    
    def download_audio(self, url: str, progress_callback=None) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Download audio from YouTube URL.
        
        Returns:
            Tuple of (audio_file_path, video_title, safe_title) or (None, None, None) on failure
        """
        if not self.validate_url(url):
            raise ValueError("Invalid YouTube URL format")
        
        print("Extracting video information...")
        title, video_id = self.get_video_info(url)
        if not title or not video_id:
            raise Exception("Failed to extract video information")
        
        safe_title = self.create_safe_filename(title)
        audio_filename = f"{video_id}.wav"  # Updated to WAV
        audio_path = os.path.join(self.temp_dir, audio_filename)
        
        # Progress hook for yt-dlp
        def progress_hook(d):
            if d['status'] == 'downloading':
                if progress_callback:
                    progress_callback(d)
                else:
                    if 'total_bytes' in d:
                        progress = (d['downloaded_bytes'] / d['total_bytes']) * 100
                        print(f"\rDownloading: {progress:.1f}%", end='', flush=True)
            elif d['status'] == 'finished':
                print("\nDownload completed, processing...")
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(self.temp_dir, f'{video_id}.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',  # Use WAV first, then convert if needed
                'preferredquality': '192',
            }],
            'progress_hooks': [progress_hook],
            'quiet': False,
            'no_warnings': False,
        }
        
        try:
            print(f"Downloading audio from: {title}")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            if os.path.exists(audio_path):
                print(f"Audio extracted successfully: {audio_path}")
                return audio_path, title, safe_title
            else:
                raise Exception("Audio file not found after download")
                
        except yt_dlp.utils.DownloadError as e:
            raise Exception(f"Download failed: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error during download: {str(e)}")
    
    def cleanup_temp_files(self):
        """Clean up temporary files."""
        try:
            import shutil
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                print(f"Cleaned up temporary files from {self.temp_dir}")
        except Exception as e:
            print(f"Warning: Failed to clean up temp files: {e}")
