import streamlit as st
from pathlib import Path
from youtube_helpers import get_video_title, download_best_audio

st.title("YouTube Audio Downloader")

yt_url = st.text_input("Enter YouTube URL:")
downloads_dir = Path(__file__).parent / "downloads"

if yt_url:
    try:
        video_title = get_video_title(yt_url)
        st.write(f"Video Title: {video_title}")

        if st.button("Download Audio"):
            saved_path = download_best_audio(yt_url, downloads_dir)
            st.success(f"Audio saved as: {saved_path}")
    except Exception as e:
        st.error(f"Error: {e}")