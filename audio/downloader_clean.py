"""
YouTube audio downloader for the Whisper Transcription App.
Uses a reliable two-step approach: download raw audio then convert to WAV.
WAV format works better than MP3 with our FFmpeg installation and Whisper supports it natively.
"""

import os
import pathlib
import subprocess
from pathlib import Path
from typing import Optional, Tuple
import yt_dlp
import streamlit as st
import config


class YouTubeDownloader:
    """Handles downloading audio from YouTube videos using proven methods."""
    
    def __init__(self):
        """Initialize the YouTube downloader."""
        self.downloads_dir = config.DOWNLOADS_DIR
        self.temp_dir = config.TEMP_DIR
        
        # Ensure directories exist
        self.downloads_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def get_video_info(self, url: str) -> Optional[dict]:
        """
        Get information about a YouTube video without downloading.
        
        Args:
            url: YouTube video URL
            
        Returns:
            Dictionary containing video information, or None if failed
        """
        try:
            ydl_opts = {'quiet': True, 'skip_download': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
            return {
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration', 0),
                'uploader': info.get('uploader', 'Unknown'),
                'view_count': info.get('view_count', 0),
                'upload_date': info.get('upload_date', ''),
                'id': info.get('id', '')
            }
            
        except Exception as e:
            st.error(f"Error getting video info: {str(e)}")
            return None
    
    def sanitize_title(self, title: str) -> str:
        """
        Sanitize video title for use as filename.
        
        Args:
            title: Raw video title
            
        Returns:
            Sanitized filename-safe title
        """
        # Remove or replace problematic characters
        import re
        # Keep only alphanumeric, spaces, hyphens, and underscores
        safe_title = re.sub(r'[^\w\s\-_]', '', title)
        # Replace multiple spaces with single space
        safe_title = re.sub(r'\s+', ' ', safe_title)
        # Replace spaces with underscores and limit length
        safe_title = safe_title.replace(' ', '_')[:100]
        return safe_title
    
    def download_audio(self, url: str, progress_callback=None) -> Optional[Path]:
        """
        Download audio from YouTube video.
        
        Args:
            url: YouTube video URL
            progress_callback: Optional callback function for progress updates
            
        Returns:
            Path to the downloaded audio file, or None if failed
        """
        try:
            if progress_callback:
                progress_callback(0.1, "Getting video information...")
            
            # Get video info
            info = self.get_video_info(url)
            if not info:
                st.error("Could not get video information")
                return None
            
            title = info['title']
            safe_title = self.sanitize_title(title)
            
            if progress_callback:
                progress_callback(0.2, f"Downloading: {title[:50]}...")
            
            # Use the proven download method
            wav_path = self._download_best_audio(url, safe_title, progress_callback)
            
            if wav_path and wav_path.exists():
                if progress_callback:
                    progress_callback(1.0, "Download complete!")
                return wav_path
            else:
                st.error("Download failed - file not created")
                return None
                
        except Exception as e:
            st.error(f"Error downloading audio: {str(e)}")
            return None
    
    def _download_best_audio(self, url: str, safe_title: str, progress_callback=None) -> Optional[Path]:
        """
        Download using a reliable two-step approach: download raw audio then convert to WAV
        (WAV works better than MP3 with our FFmpeg installation and Whisper supports it natively)
        """
        out_template = str(self.downloads_dir / f"{safe_title}.%(ext)s")
        wav_path = self.downloads_dir / f"{safe_title}.wav"
        
        # Progress hook for yt-dlp
        def progress_hook(d):
            if progress_callback and d['status'] == 'downloading':
                try:
                    percent_str = d.get('_percent_str', '0%').replace('%', '')
                    percent = float(percent_str) / 100.0
                    progress_callback(0.2 + (percent * 0.5), f"Downloading... {percent_str}%")
                except:
                    pass
            elif progress_callback and d['status'] == 'finished':
                progress_callback(0.7, "Download complete, converting...")
        
        # Primary method: Download raw audio first (more reliable)
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': out_template,
            'progress_hooks': [progress_hook],
            'quiet': True,
            'no_warnings': True
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
            
            # Get the downloaded file extension
            ext = info.get('ext', 'webm')
            raw_path = self.downloads_dir / f"{safe_title}.{ext}"
            
            if progress_callback:
                progress_callback(0.8, "Converting to WAV...")
            
            # Convert to WAV (more reliable than MP3 with our FFmpeg setup)
            cmd = [
                "ffmpeg", "-y", "-i", str(raw_path), 
                "-ac", "1",           # Mono
                "-ar", "16000",       # 16kHz for Whisper
                str(wav_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0 and wav_path.exists() and wav_path.stat().st_size > 10000:
                # Clean up raw file
                if raw_path.exists():
                    raw_path.unlink()
                return wav_path
            else:
                # If conversion failed, try fallback method
                raise Exception(f"WAV conversion failed: {result.stderr}")
                
        except Exception as e:
            st.warning(f"Primary download failed: {str(e)}, trying fallback method...")
            return self._fallback_download(url, safe_title, progress_callback)
    
    def _fallback_download(self, url: str, safe_title: str, progress_callback=None) -> Optional[Path]:
        """
        Fallback method: download raw audio then convert to WAV using simplest FFmpeg settings
        """
        try:
            if progress_callback:
                progress_callback(0.3, "Using fallback download method...")
            
            out_template = str(self.downloads_dir / f"{safe_title}.%(ext)s")
            wav_path = self.downloads_dir / f"{safe_title}.wav"
            
            # Download raw audio without postprocessing
            fallback_opts = {
                'format': 'bestaudio/best',
                'outtmpl': out_template,
                'quiet': True
            }
            
            with yt_dlp.YoutubeDL(fallback_opts) as ydl:
                info = ydl.extract_info(url, download=True)
            
            ext = info.get('ext', 'webm')
            raw_path = self.downloads_dir / f"{safe_title}.{ext}"
            
            if progress_callback:
                progress_callback(0.7, "Converting to WAV format...")
            
            # Simple WAV conversion (most reliable)
            cmd = [
                "ffmpeg", "-y", "-i", str(raw_path), 
                "-ac", "1",           # Mono
                "-ar", "16000",       # 16kHz for Whisper
                str(wav_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0 and wav_path.exists() and wav_path.stat().st_size > 10000:
                # Clean up raw file
                if raw_path.exists():
                    raw_path.unlink()
                return wav_path
            else:
                st.error(f"WAV conversion failed: {result.stderr}")
                return None
                
        except Exception as e:
            st.error(f"Fallback download failed: {str(e)}")
            return None
