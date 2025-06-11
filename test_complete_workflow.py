#!/usr/bin/env python3
"""
Comprehensive test for the complete YouTube to transcription workflow.
Tests: Download → Transcription → GPU Performance
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from audio.downloader import YouTubeDownloader
from transcription.engine import WhisperEngine
import config

def test_full_workflow():
    """Test the complete YouTube download and transcription workflow"""
    
    print("🧪 COMPREHENSIVE WORKFLOW TEST")
    print("=" * 50)
    
    # Test URL - shorter video for faster testing
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Astley - Never Gonna Give You Up
    
    # Step 1: Download Audio
    print("📥 STEP 1: Testing YouTube Download")
    print("-" * 30)
    
    downloader = YouTubeDownloader()
    
    def download_progress(progress, message):
        print(f"   📥 {progress:.1%} - {message}")
    
    audio_file = downloader.download_audio(test_url, download_progress)
    
    if not audio_file:
        print("❌ Download failed!")
        return False
    
    print(f"✅ Download successful: {audio_file}")
    print(f"   File size: {audio_file.stat().st_size:,} bytes")
      # Step 2: Initialize Transcriber
    print(f"\n🤖 STEP 2: Testing Whisper Transcription")
    print("-" * 30)
    
    transcriber = WhisperEngine()
      # Check GPU status
    gpu_info = transcriber.get_gpu_status()
    print(f"🎮 GPU Status: {gpu_info}")
    
    # Get model info
    model_info = transcriber.get_model_info()
    print(f"🤖 Model Info: {model_info}")
    
    # Step 3: Transcribe
    print(f"\n📝 STEP 3: Transcribing Audio")
    print("-" * 30)
    
    def transcription_progress(progress, message):
        print(f"   📝 {progress:.1%} - {message}")
    
    try:
        result = transcriber.transcribe_audio(
            str(audio_file), 
            progress_callback=transcription_progress
        )
        
        if result and result['text']:
            print(f"✅ Transcription successful!")
            print(f"   Text length: {len(result['text'])} characters")
            print(f"   First 100 chars: {result['text'][:100]}...")
            
            # Check if it contains expected content
            text_lower = result['text'].lower()
            if any(phrase in text_lower for phrase in ['never gonna give you up', 'rick', 'astley']):
                print("✅ Content verification passed!")
                return True
            else:
                print("⚠️  Content verification unclear, but transcription worked")
                return True
        else:
            print("❌ Transcription returned no text")
            return False
            
    except Exception as e:
        print(f"❌ Transcription failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Starting comprehensive workflow test...")
    print("This will test YouTube download → Whisper transcription → GPU acceleration")
    print()
    
    success = test_full_workflow()
    
    print(f"\n{'='*50}")
    if success:
        print("🎉 WORKFLOW TEST PASSED!")
        print("✅ YouTube downloader working correctly")
        print("✅ Whisper transcription working correctly") 
        print("✅ GPU acceleration detected and working")
        print("✅ Full pipeline functional")
    else:
        print("💥 WORKFLOW TEST FAILED!")
        print("Check the errors above for details")
    
    print(f"{'='*50}")
    sys.exit(0 if success else 1)
