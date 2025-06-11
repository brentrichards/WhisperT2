"""
Test script for the Whisper Transcription App.
Tests core functionality without requiring actual transcription.
"""

import sys
from pathlib import Path
import tempfile
import io

# Add project root to path
sys.path.append(str(Path(__file__).parent))

def test_imports():
    """Test that all modules can be imported."""
    print("🧪 Testing imports...")
    
    try:
        import config
        print("✅ Config module imported")
        
        from audio import AudioProcessor, YouTubeDownloader
        print("✅ Audio modules imported")
        
        from transcription import WhisperEngine, TranscriptionFormatter
        print("✅ Transcription modules imported")
        
        from export import DocumentExporter
        print("✅ Export modules imported")
        
        from ui import UIComponents
        print("✅ UI modules imported")
        
        print("✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_config():
    """Test configuration settings."""
    print("\n🧪 Testing configuration...")
    
    try:
        import config
        
        # Test directory creation
        config.ensure_directories()
        
        assert config.DOWNLOADS_DIR.exists(), "Downloads directory not created"
        assert config.TEMP_DIR.exists(), "Temp directory not created"
        
        print(f"✅ Directories created: {config.DOWNLOADS_DIR}, {config.TEMP_DIR}")
        
        # Test cleanup function
        config.cleanup_temp_files()
        print("✅ Cleanup function works")
        
        return True
        
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False

def test_audio_processor():
    """Test audio processor initialization."""
    print("\n🧪 Testing audio processor...")
    
    try:
        from audio import AudioProcessor
        
        processor = AudioProcessor()
        print("✅ AudioProcessor initialized")
        
        # Test validation for non-existent file
        is_valid, message = processor.validate_audio_file(Path("nonexistent.mp3"))
        assert not is_valid, "Should fail for non-existent file"
        print("✅ File validation works")
        
        return True
        
    except Exception as e:
        print(f"❌ Audio processor error: {e}")
        return False

def test_youtube_downloader():
    """Test YouTube downloader initialization."""
    print("\n🧪 Testing YouTube downloader...")
    
    try:
        from audio import YouTubeDownloader
        
        downloader = YouTubeDownloader()
        print("✅ YouTubeDownloader initialized")
        
        # Test URL validation
        is_valid, message = downloader.validate_youtube_url("")
        assert not is_valid, "Should fail for empty URL"
        print("✅ URL validation works")
        
        is_valid, message = downloader.validate_youtube_url("https://www.google.com")
        assert not is_valid, "Should fail for non-YouTube URL"
        print("✅ Non-YouTube URL correctly rejected")
        
        return True
        
    except Exception as e:
        print(f"❌ YouTube downloader error: {e}")
        return False

def test_whisper_engine():
    """Test Whisper engine initialization."""
    print("\n🧪 Testing Whisper engine...")
    
    try:
        from transcription import WhisperEngine
        
        engine = WhisperEngine()
        print("✅ WhisperEngine initialized")
        
        # Test device detection
        device = engine._get_device()
        print(f"✅ Device detected: {device}")
        
        # Test model info
        info = engine.get_model_info()
        assert isinstance(info, dict), "Model info should be a dictionary"
        print("✅ Model info generated")
        
        # Test time estimation
        estimate = engine.estimate_processing_time(120)  # 2 minutes
        print(f"✅ Time estimation: {estimate}")
        
        return True
        
    except Exception as e:
        print(f"❌ Whisper engine error: {e}")
        return False

def test_formatter():
    """Test transcription formatter."""
    print("\n🧪 Testing transcription formatter...")
    
    try:
        from transcription import TranscriptionFormatter
        
        formatter = TranscriptionFormatter()
        
        # Test timestamp formatting
        timestamp = formatter.format_timestamp(125.5)
        expected = "00:02:05.500"
        assert timestamp == expected, f"Expected {expected}, got {timestamp}"
        print("✅ Timestamp formatting works")
        
        # Test with sample data
        sample_data = {
            "text": "Hello world test",
            "words": [
                {"word": "Hello", "start": 0.0, "end": 0.5},
                {"word": "world", "start": 0.6, "end": 1.0},
                {"word": "test", "start": 1.1, "end": 1.5}
            ],
            "segments": [
                {"id": 1, "start": 0.0, "end": 1.5, "text": "Hello world test"}
            ],
            "duration": 1.5,
            "word_count": 3,
            "segment_count": 1,
            "language": "en"
        }
        
        plain_text = formatter.format_plain_text(sample_data)
        assert plain_text == "Hello world test", "Plain text formatting failed"
        print("✅ Plain text formatting works")
        
        word_timestamps = formatter.format_word_timestamps(sample_data)
        assert "WORD-LEVEL TIMESTAMPS" in word_timestamps, "Word timestamps formatting failed"
        print("✅ Word timestamps formatting works")
        
        segment_timestamps = formatter.format_segment_timestamps(sample_data)
        assert "SEGMENT-LEVEL TIMESTAMPS" in segment_timestamps, "Segment timestamps formatting failed"
        print("✅ Segment timestamps formatting works")
        
        summary = formatter.get_transcription_summary(sample_data)
        assert isinstance(summary, dict), "Summary should be a dictionary"
        print("✅ Summary generation works")
        
        return True
        
    except Exception as e:
        print(f"❌ Formatter error: {e}")
        return False

def test_document_exporter():
    """Test document exporter."""
    print("\n🧪 Testing document exporter...")
    
    try:
        from export import DocumentExporter
        
        exporter = DocumentExporter()
        print("✅ DocumentExporter initialized")
        
        # Test text export
        content = "Test transcription content"
        txt_data = exporter.create_text_download(content, "test")
        assert isinstance(txt_data, bytes), "Text export should return bytes"
        print("✅ Text export works")
        
        # Test filename generation
        filename = exporter.get_filename("test file", "plain_text", "txt")
        assert filename == "test_file_plain_text.txt", f"Unexpected filename: {filename}"
        print("✅ Filename generation works")
        
        return True
        
    except Exception as e:
        print(f"❌ Document exporter error: {e}")
        return False

def run_all_tests():
    """Run all tests."""
    print("🚀 Starting Whisper Transcription App Tests\n")
    
    tests = [
        test_imports,
        test_config,
        test_audio_processor,
        test_youtube_downloader,
        test_whisper_engine,
        test_formatter,
        test_document_exporter
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"❌ {test.__name__} failed")
        except Exception as e:
            print(f"❌ {test.__name__} crashed: {e}")
    
    print(f"\n🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application is ready to use.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
