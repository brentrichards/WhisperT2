# youtube_helpers.py

import os
import pathlib
import yt_dlp
import subprocess
from pathlib import Path

def convert_to_mono(wav_path: Path) -> Path:
    """
    Convert a WAV file to mono using ffmpeg.
    """
    mono_path = wav_path.with_name(wav_path.stem + "_mono.wav")
    subprocess.run([
        "ffmpeg", "-y", "-i", str(wav_path), "-ac", "1", str(mono_path)
    ], check=True)
    wav_path.unlink()  # remove original stereo file
    return mono_path

def fetch_audio(url: str, out_dir: str = "downloads") -> str:
    """
    Download the audio track of a YouTube URL and save it as a WAV file.
    Returns the path to the downloaded .wav file.

    Args:
        url (str): The YouTube video URL.
        out_dir (str): Directory where the WAV file will be saved.
        
    Returns:
        str: Absolute path to the downloaded WAV file.
    """
    os.makedirs(out_dir, exist_ok=True)

    # Directly get mono audio from YouTube using FFmpeg options
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": f"{out_dir}/%(id)s.%(ext)s",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "wav",
            "preferredquality": "192",
            # Force mono output in the FFmpeg args
            "additional_ffmpeg_params": ["-ac", "1"],
        }],
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        video_id = info.get("id")
        wav_path = pathlib.Path(out_dir) / f"{video_id}.wav"
        return wav_path.as_posix()

def sanitize_title(raw_title: str, max_len: int = 50) -> str:
    title = raw_title.strip().replace(" ", "_")
    safe = "".join(c for c in title if c.isalnum() or c in ("_", "-"))
    return safe[:max_len]

def get_video_title(url: str) -> str:
    ydl_opts = {'quiet': True, 'skip_download': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    return info.get('title', '')

def download_best_audio(url: str, downloads_dir: Path) -> tuple[Path, Path]:
    downloads_dir.mkdir(parents=True, exist_ok=True)
    title = get_video_title(url)
    safe_title = sanitize_title(title)
    out_template = str(downloads_dir / f"{safe_title}.%(ext)s")

    # Extract MP3 (mono)
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': out_template,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
            'additional_ffmpeg_params': ["-ac", "1"],  # Force mono
        }],
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)
        mp3_path = downloads_dir / f"{safe_title}.mp3"
        wav_path = downloads_dir / f"{safe_title}.wav"
        
        # Convert mono MP3 to mono WAV
        subprocess.run([
            "ffmpeg", "-y", "-i", str(mp3_path), "-ac", "1", str(wav_path)
        ], check=True)
        return mp3_path, wav_path
    except Exception as e:
        # Fallback: download raw audio then convert to both formats
        fallback_opts = {
            'format': 'bestaudio/best',
            'outtmpl': out_template,
        }
        with yt_dlp.YoutubeDL(fallback_opts) as ydl:
            info = ydl.extract_info(url, download=True)
        ext = info.get('ext', 'webm')
        raw_path = downloads_dir / f"{safe_title}.{ext}"
        mp3_path = downloads_dir / f"{safe_title}.mp3"
        wav_path = downloads_dir / f"{safe_title}.wav"
        try:
            # Convert to mono MP3
            subprocess.run([
                "ffmpeg", "-y", "-i", str(raw_path), "-ac", "1", str(mp3_path)
            ], check=True)
            # Convert to mono WAV
            subprocess.run([
                "ffmpeg", "-y", "-i", str(raw_path), "-ac", "1", str(wav_path)
            ], check=True)
        except Exception:
            pass
        return mp3_path, wav_path
