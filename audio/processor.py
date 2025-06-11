"""
Audio processing utilities for the Whisper Transcription App.
Handles audio file conversion, normalization, and format optimization.
"""

import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Tuple
import streamlit as st
from pydub import AudioSegment
import config


class AudioProcessor:
    """Handles audio file processing and format conversion."""
    
    def __init__(self):
        """Initialize the audio processor."""
        self.temp_dir = config.TEMP_DIR
        
    def process_uploaded_file(self, uploaded_file) -> Optional[Path]:
        """
        Process an uploaded audio file and convert it to the optimal format.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            Path to the processed audio file, or None if processing failed
        """
        try:
            # Save uploaded file to temporary location
            temp_input = self.temp_dir / f"upload_{uploaded_file.name}"
            with open(temp_input, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Process the file
            processed_file = self.convert_to_optimal_format(temp_input)
            
            # Clean up original temp file
            temp_input.unlink(missing_ok=True)
            
            return processed_file
            
        except Exception as e:
            st.error(f"Error processing uploaded file: {str(e)}")
            return None
    
    def convert_to_optimal_format(self, input_path: Path) -> Path:
        """
        Convert audio file to optimal format for transcription (16kHz mono MP3).
        
        Args:
            input_path: Path to the input audio file
            
        Returns:
            Path to the converted audio file
        """
        output_path = self.temp_dir / f"processed_{input_path.stem}.mp3"
        
        try:
            # Use pydub for audio conversion
            audio = AudioSegment.from_file(str(input_path))
            
            # Convert to mono and set sample rate
            audio = audio.set_channels(config.CHANNELS)
            audio = audio.set_frame_rate(config.SAMPLE_RATE)
            
            # Export as MP3
            audio.export(
                str(output_path),
                format="mp3",
                bitrate=f"{config.AUDIO_QUALITY}k"
            )
            
            return output_path
            
        except Exception as e:
            # Fallback to FFmpeg if pydub fails
            return self._convert_with_ffmpeg(input_path, output_path)
    
    def _convert_with_ffmpeg(self, input_path: Path, output_path: Path) -> Path:
        """
        Fallback conversion using FFmpeg directly.
        
        Args:
            input_path: Path to the input audio file
            output_path: Path for the output audio file
            
        Returns:
            Path to the converted audio file
        """
        try:
            subprocess.run([
                "ffmpeg", "-y",
                "-i", str(input_path),
                "-ar", str(config.SAMPLE_RATE),
                "-ac", str(config.CHANNELS),
                "-b:a", f"{config.AUDIO_QUALITY}k",
                str(output_path)
            ], check=True, capture_output=True)
            
            return output_path
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"FFmpeg conversion failed: {e.stderr.decode()}")
    
    def get_audio_info(self, file_path: Path) -> dict:
        """
        Get information about an audio file.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Dictionary containing audio file information
        """
        try:
            audio = AudioSegment.from_file(str(file_path))
            
            return {
                "duration": len(audio) / 1000.0,  # Convert to seconds
                "channels": audio.channels,
                "sample_rate": audio.frame_rate,
                "size_mb": file_path.stat().st_size / (1024 * 1024)
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def validate_audio_file(self, file_path: Path) -> Tuple[bool, str]:
        """
        Validate if an audio file is suitable for processing.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Tuple of (is_valid, message)
        """
        try:
            info = self.get_audio_info(file_path)
            
            if "error" in info:
                return False, f"Cannot read audio file: {info['error']}"
            
            # Check file size
            if info["size_mb"] > config.MAX_FILE_SIZE:
                return False, f"File too large: {info['size_mb']:.1f}MB (max: {config.MAX_FILE_SIZE}MB)"
            
            # Check duration (max 3 hours)
            if info["duration"] > 10800:
                return False, f"Audio too long: {info['duration']/3600:.1f} hours (max: 3 hours)"
            
            return True, "Audio file is valid"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def cleanup_temp_files(self):
        """Clean up temporary audio files."""
        try:
            for temp_file in self.temp_dir.glob("processed_*.mp3"):
                temp_file.unlink(missing_ok=True)
            for temp_file in self.temp_dir.glob("upload_*"):
                temp_file.unlink(missing_ok=True)
        except Exception:
            pass  # Ignore cleanup errors
