# Configuration settings for the Whisper Transcription App

import os
from pathlib import Path

# Application settings
APP_TITLE = "Whisper Transcription App"
APP_DESCRIPTION = "Professional audio transcription using OpenAI's Whisper Turbo model"

# Directories
BASE_DIR = Path(__file__).parent
DOWNLOADS_DIR = BASE_DIR / "downloads"
TEMP_DIR = BASE_DIR / "temp"

# Audio processing settings
SAMPLE_RATE = 16000  # 16kHz for optimal transcription
CHANNELS = 1  # Mono
AUDIO_FORMAT = "mp3"
AUDIO_QUALITY = "192"

# Whisper model settings
WHISPER_MODEL = "turbo"  # Fast and accurate model
LANGUAGE = None  # Auto-detect language
TASK = "transcribe"  # or "translate"

# GPU optimization settings for RTX 4090
GPU_MEMORY_FRACTION = 0.9  # Use 90% of GPU memory
ENABLE_TF32 = True  # Enable TensorFloat-32 for RTX 30/40 series
ENABLE_CUDNN_BENCHMARK = True  # Optimize for consistent input sizes
USE_FP16 = True  # Use half precision on GPU for speed

# File upload settings
MAX_FILE_SIZE = 200  # MB
ALLOWED_EXTENSIONS = [".mp3", ".wav", ".m4a", ".flac"]

# YouTube download settings
YT_AUDIO_QUALITY = "bestaudio/best"

# Export settings
EXPORT_FORMATS = ["txt", "docx"]
DEFAULT_FILENAME_PREFIX = "transcription"

# UI settings
SIDEBAR_WIDTH = 300
MAX_DISPLAY_LENGTH = 10000  # Characters to display in UI

# Create necessary directories
def ensure_directories():
    """Create necessary directories if they don't exist"""
    DOWNLOADS_DIR.mkdir(exist_ok=True)
    TEMP_DIR.mkdir(exist_ok=True)

# Clean up temporary files
def cleanup_temp_files():
    """Remove temporary files older than 1 hour"""
    import time
    current_time = time.time()
    for file_path in TEMP_DIR.glob("*"):
        if file_path.is_file():
            file_age = current_time - file_path.stat().st_mtime
            if file_age > 3600:  # 1 hour
                try:
                    file_path.unlink()
                except OSError:
                    pass
