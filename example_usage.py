"""
Example usage script for the Whisper Transcription App.
Demonstrates how to use the app components programmatically.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

def example_youtube_download():
    """Example: Download audio from YouTube."""
    print("📺 Example: YouTube Audio Download")
    print("This would download audio from a YouTube URL:")
    print()
    
    from audio import YouTubeDownloader
    
    downloader = YouTubeDownloader()
    
    # Example URL validation
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Valid format
        "https://youtu.be/dQw4w9WgXcQ",                # Valid short format
        "https://www.google.com",                       # Invalid
        ""                                              # Empty
    ]
    
    for url in test_urls:
        is_valid, message = downloader.validate_youtube_url(url)
        status = "✅" if is_valid else "❌"
        print(f"{status} {url or '(empty)'}: {message}")
    
    print()

def example_transcription_formatting():
    """Example: Format transcription results."""
    print("📝 Example: Transcription Formatting")
    print("This shows how transcription results are formatted:")
    print()
    
    from transcription import TranscriptionFormatter
    
    formatter = TranscriptionFormatter()
    
    # Sample transcription data
    sample_data = {
        "text": "Hello world, this is a test transcription. How are you today?",
        "words": [
            {"word": "Hello", "start": 0.0, "end": 0.5, "probability": 0.99},
            {"word": "world,", "start": 0.6, "end": 1.0, "probability": 0.98},
            {"word": "this", "start": 1.1, "end": 1.3, "probability": 0.97},
            {"word": "is", "start": 1.4, "end": 1.5, "probability": 0.99},
            {"word": "a", "start": 1.6, "end": 1.7, "probability": 0.95},
            {"word": "test", "start": 1.8, "end": 2.2, "probability": 0.98},
            {"word": "transcription.", "start": 2.3, "end": 3.0, "probability": 0.99},
            {"word": "How", "start": 3.5, "end": 3.8, "probability": 0.97},
            {"word": "are", "start": 3.9, "end": 4.1, "probability": 0.98},
            {"word": "you", "start": 4.2, "end": 4.4, "probability": 0.99},
            {"word": "today?", "start": 4.5, "end": 5.0, "probability": 0.96}
        ],
        "segments": [
            {
                "id": 1,
                "start": 0.0,
                "end": 3.0,
                "text": "Hello world, this is a test transcription."
            },
            {
                "id": 2,
                "start": 3.5,
                "end": 5.0,
                "text": "How are you today?"
            }
        ],
        "duration": 5.0,
        "word_count": 11,
        "segment_count": 2,
        "language": "en"
    }
    
    # Show different formatting options
    print("🔤 Plain Text:")
    plain = formatter.format_plain_text(sample_data)
    print(f"   {plain}")
    print()
    
    print("⏰ Word-level Timestamps (sample):")
    word_format = formatter.format_word_timestamps(sample_data)
    lines = word_format.split('\n')
    for line in lines[:8]:  # Show first few lines
        print(f"   {line}")
    print("   ...")
    print()
    
    print("📑 Segment-level Timestamps (sample):")
    segment_format = formatter.format_segment_timestamps(sample_data)
    lines = segment_format.split('\n')
    for line in lines[:10]:  # Show first few lines
        print(f"   {line}")
    print("   ...")
    print()
    
    print("📊 Summary Statistics:")
    summary = formatter.get_transcription_summary(sample_data)
    for key, value in summary.items():
        print(f"   {key}: {value}")
    print()

def example_export_options():
    """Example: Export functionality."""
    print("💾 Example: Export Options")
    print("The app supports multiple export formats:")
    print()
    
    from export import DocumentExporter
    
    exporter = DocumentExporter()
    
    export_types = [
        ("plain_text", "txt", "Plain text transcription"),
        ("word_timestamps", "txt", "Word-level timestamps as text"),
        ("segment_timestamps", "txt", "Segment-level timestamps as text"),
        ("word_timestamps", "docx", "Word-level timestamps as Word document"),
        ("segment_timestamps", "docx", "Segment-level timestamps as Word document"),
        ("subtitles", "srt", "SubRip subtitle format"),
        ("subtitles", "vtt", "WebVTT subtitle format")
    ]
    
    print("📄 Available Export Formats:")
    for format_type, file_format, description in export_types:
        filename = exporter.get_filename("sample_audio", format_type, file_format)
        button_label = exporter.get_download_button_label(format_type, file_format)
        print(f"   • {description}")
        print(f"     Filename: {filename}")
        print(f"     Button: {button_label}")
        print()

def show_app_features():
    """Show main application features."""
    print("🎤 Whisper Transcription App - Features Overview")
    print("=" * 60)
    print()
    
    features = [
        ("📺 YouTube Integration", "Paste any YouTube URL to download and transcribe audio"),
        ("📁 File Upload", "Drag & drop or browse for MP3, WAV, M4A, FLAC files"),
        ("🎯 Multiple Outputs", "Plain text, word timestamps, segment timestamps"),
        ("💾 Export Options", "Download as TXT, DOCX, SRT, VTT formats"),
        ("⚡ Fast Processing", "Uses Whisper Turbo model for quick transcription"),
        ("🔧 Auto Processing", "Converts audio to optimal 16kHz mono format"),
        ("🧹 Memory Management", "Reset functionality to process multiple files"),
        ("📊 Statistics", "Duration, word count, processing time estimates"),
        ("🌐 Multi-language", "Auto-detects language or specify target language"),
        ("🎬 Subtitle Export", "Generate SRT/VTT files for video editing")
    ]
    
    for title, description in features:
        print(f"{title}")
        print(f"   {description}")
        print()

def main():
    """Main example runner."""
    show_app_features()
    
    print("🚀 Usage Examples")
    print("=" * 60)
    print()
    
    example_youtube_download()
    example_transcription_formatting()
    example_export_options()
    
    print("🌟 Getting Started")
    print("=" * 60)
    print()
    print("To run the application:")
    print("   streamlit run main.py")
    print()
    print("Then open your browser to:")
    print("   http://localhost:8501")
    print()
    print("For help and documentation:")
    print("   Check README.md for detailed instructions")
    print("   All functions include helpful tooltips and error messages")
    print()

if __name__ == "__main__":
    main()
