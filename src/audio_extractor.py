"""
Audio extraction module using yt-dlp for downloading YouTube audio.
"""

import os
import re
import subprocess
import tempfile
from typing import Optional, Tuple, List

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
        audio_filename = f"{video_id}.m4a"  # Updated to M4A
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
                'preferredcodec': 'm4a',  # Use M4A (AAC) for better compression
                'preferredquality': '128',  # Lower quality for smaller file size
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
    
    def compress_audio_for_api(self, audio_path: str) -> str:
        """Compress audio file to meet API size requirements."""
        file_size = os.path.getsize(audio_path)
        file_size_mb = file_size / (1024 * 1024)
        
        if file_size_mb <= 25:
            return audio_path  # No compression needed
        
        print(f"Audio file ({file_size_mb:.1f}MB) is too large for API. Compressing...")
        
        import subprocess
        
        # Create compressed version
        base_name = os.path.splitext(audio_path)[0]
        compressed_path = f"{base_name}_compressed.m4a"
        
        # Use FFmpeg to compress with lower quality
        cmd = [
            'ffmpeg', '-i', audio_path,
            '-acodec', 'aac',
            '-b:a', '64k',  # Very low bitrate for small file size
            '-ac', '1',     # Mono audio
            '-ar', '22050', # Lower sample rate
            '-y',           # Overwrite if exists
            compressed_path
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            
            # Check new file size
            new_size = os.path.getsize(compressed_path)
            new_size_mb = new_size / (1024 * 1024)
            print(f"Compressed to {new_size_mb:.1f}MB")
            
            if new_size_mb <= 25:
                return compressed_path
            else:
                print("Warning: Compressed file still too large, using local transcription")
                return audio_path
                
        except subprocess.CalledProcessError as e:
            print(f"Compression failed: {e}")
            return audio_path
    
    def split_audio_for_processing(self, audio_path: str, chunk_duration_minutes: int = 10) -> List[str]:
        """
        Split large audio files into smaller chunks for processing.
        
        Args:
            audio_path: Path to the audio file to split
            chunk_duration_minutes: Duration of each chunk in minutes
            
        Returns:
            List of paths to audio chunks
        """
        try:
            print(f"Splitting audio into {chunk_duration_minutes}-minute chunks...")
            
            # Get audio duration first
            cmd_duration = [
                'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
                '-of', 'csv=p=0', audio_path
            ]
            
            result = subprocess.run(cmd_duration, capture_output=True, text=True, check=True)
            total_duration = float(result.stdout.strip())
            chunk_duration_seconds = chunk_duration_minutes * 60
            
            print(f"Total duration: {total_duration:.1f}s, chunk size: {chunk_duration_seconds}s")
            
            chunk_paths = []
            chunk_count = int(total_duration / chunk_duration_seconds) + 1
            
            filename = os.path.basename(audio_path)
            name, _ = os.path.splitext(filename)
            
            for i in range(chunk_count):
                start_time = i * chunk_duration_seconds
                
                # Don't create chunk if start time exceeds total duration
                if start_time >= total_duration:
                    break
                    
                chunk_filename = f"{name}_chunk_{i+1:03d}.m4a"
                chunk_path = os.path.join(self.temp_dir, chunk_filename)
                
                cmd = [
                    'ffmpeg', '-i', audio_path,
                    '-ss', str(start_time),
                    '-t', str(chunk_duration_seconds),
                    '-c', 'copy',  # Copy without re-encoding when possible
                    '-y',  # Overwrite output
                    chunk_path
                ]
                
                print(f"Creating chunk {i+1}/{chunk_count}...")
                subprocess.run(cmd, check=True, capture_output=True)
                
                if os.path.exists(chunk_path):
                    chunk_paths.append(chunk_path)
                    chunk_size_mb = os.path.getsize(chunk_path) / (1024 * 1024)
                    print(f"  Created: {chunk_filename} ({chunk_size_mb:.1f}MB)")
            
            print(f"Audio split into {len(chunk_paths)} chunks")
            return chunk_paths
            
        except subprocess.CalledProcessError as e:
            print(f"Error splitting audio: {e}")
            return [audio_path]  # Return original file if splitting fails
        except Exception as e:
            print(f"Unexpected error splitting audio: {e}")
            return [audio_path]
    
    def cleanup(self):
        """Clean up temporary files."""
        try:
            import shutil
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                print(f"Cleaned up temporary files from {self.temp_dir}")
        except Exception as e:
            print(f"Warning: Failed to clean up temp files: {e}")
