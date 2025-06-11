"""
Whisper transcription engine for the Whisper Transcription App.
Handles audio transcription using OpenAI's Whisper model.
"""

import whisper
import torch
from pathlib import Path
from typing import Dict, Any, Optional
import streamlit as st
import config


class WhisperEngine:
    """Handles audio transcription using Whisper model."""
    def __init__(self):
        """Initialize the Whisper engine."""
        self.model = None
        self.device = self._get_device()
        
    def _get_device(self) -> str:
        """Determine the best device for inference."""
        if torch.cuda.is_available():
            # For RTX 4090 and other modern GPUs, ensure optimal CUDA usage
            device_count = torch.cuda.device_count()
            current_device = torch.cuda.current_device()
            gpu_name = torch.cuda.get_device_name(current_device)
            
            # Log GPU information for transparency
            print(f"🚀 GPU detected: {gpu_name}")
            print(f"📊 CUDA version: {torch.version.cuda}")
            print(f"🔧 Using device: cuda:{current_device}")
            
            return "cuda"
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            return "mps"  # Apple Silicon
        else:
            print("⚠️  No GPU detected, using CPU (this will be slower)")
            return "cpu"
    
    def load_model(self) -> bool:
        """
        Load the Whisper model with GPU optimization.
        
        Returns:
            True if model loaded successfully, False otherwise
        """
        try:
            if self.model is None:
                with st.spinner(f"Loading Whisper {config.WHISPER_MODEL} model on {self.device}..."):
                    # Clear GPU cache before loading model for optimal memory usage
                    if self.device == "cuda":
                        torch.cuda.empty_cache()
                        
                    self.model = whisper.load_model(
                        config.WHISPER_MODEL,
                        device=self.device
                    )
                    
                    # Display GPU memory usage after model loading
                    if self.device == "cuda":
                        self._log_gpu_memory_usage("after model loading")
                        
                st.success(f"✅ Model loaded on {self.device.upper()}")
                
                # Show GPU performance info
                if self.device == "cuda":
                    gpu_name = torch.cuda.get_device_name(0)
                    st.info(f"🚀 Using GPU: {gpu_name} for fast transcription!")
                    
            return True
              except Exception as e:
            st.error(f"Failed to load Whisper model: {str(e)}")
            return False
    
    def _log_gpu_memory_usage(self, stage: str = ""):
        """Log GPU memory usage for monitoring."""
        if self.device == "cuda" and torch.cuda.is_available():
            try:
                memory_allocated = torch.cuda.memory_allocated() / 1024**3  # GB
                memory_reserved = torch.cuda.memory_reserved() / 1024**3   # GB
                total_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3  # GB
                
                print(f"🔍 GPU Memory {stage}:")
                print(f"   Allocated: {memory_allocated:.2f} GB")
                print(f"   Reserved: {memory_reserved:.2f} GB") 
                print(f"   Total: {total_memory:.2f} GB")
                print(f"   Usage: {(memory_allocated/total_memory)*100:.1f}%")
            except Exception as e:
                print(f"Could not get GPU memory info: {e}")
    
    def _optimize_gpu_settings(self):
        """Optimize GPU settings for RTX 4090 and similar high-end GPUs."""
        if self.device == "cuda":
            try:
                # Enable TensorFloat-32 (TF32) for RTX 30/40 series cards
                torch.backends.cuda.matmul.allow_tf32 = True
                torch.backends.cudnn.allow_tf32 = True
                
                # Enable CUDNN benchmarking for consistent input sizes
                torch.backends.cudnn.benchmark = True
                
                print("🔧 GPU optimizations enabled for RTX 4090")
                
            except Exception as e:
                print(f"Warning: Could not apply all GPU optimizations: {e}")
    
    def transcribe_audio(self, audio_path: Path, progress_callback=None) -> Optional[Dict[str, Any]]:
        """
        Transcribe audio file using Whisper.
        
        Args:
            audio_path: Path to the audio file
            progress_callback: Optional callback for progress updates
            
        Returns:
            Dictionary containing transcription results, or None if failed
        """
        if not self.load_model():
            return None
        
        try:
            if progress_callback:
                progress_callback(0.1, "Starting transcription...")
            
            # Transcribe with Whisper
            result = self.model.transcribe(
                str(audio_path),
                language=config.LANGUAGE,
                task=config.TASK,
                verbose=False,
                word_timestamps=True  # Enable word-level timestamps
            )
            
            if progress_callback:
                progress_callback(0.9, "Processing results...")
            
            # Process the results
            processed_result = self._process_transcription_result(result)
            
            if progress_callback:
                progress_callback(1.0, "Transcription complete!")
            
            return processed_result
            
        except Exception as e:
            st.error(f"Transcription failed: {str(e)}")
            return None
    
    def _process_transcription_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process raw Whisper results into structured format.
        
        Args:
            result: Raw Whisper transcription result
            
        Returns:
            Processed transcription data
        """
        try:
            # Extract plain text
            text = result.get("text", "").strip()
            
            # Extract segments with timestamps
            segments = []
            for segment in result.get("segments", []):
                segments.append({
                    "id": segment.get("id"),
                    "start": segment.get("start"),
                    "end": segment.get("end),
                    "text": segment.get("text", "").strip(),
                    "words": segment.get("words", [])
                })
            
            # Extract word-level timestamps
            words = []
            for segment in segments:
                for word in segment.get("words", []):
                    words.append({
                        "word": word.get("word", "").strip(),
                        "start": word.get("start"),
                        "end": word.get("end"),
                        "probability": word.get("probability", 0.0)
                    })
            
            # Calculate statistics
            total_duration = segments[-1]["end"] if segments else 0
            word_count = len([w for w in words if w["word"]])
            
            return {
                "text": text,
                "segments": segments,
                "words": words,
                "language": result.get("language", "unknown"),
                "duration": total_duration,
                "word_count": word_count,
                "segment_count": len(segments)
            }
            
        except Exception as e:
            st.error(f"Error processing transcription results: {str(e)}")
            return {
                "text": result.get("text", ""),
                "segments": [],
                "words": [],
                "language": "unknown",
                "duration": 0,
                "word_count": 0,
                "segment_count": 0
            }
    
    def get_model_info(self) -> Dict[str, str]:
        """
        Get information about the loaded model.
        
        Returns:
            Dictionary containing model information
        """
        return {
            "model": config.WHISPER_MODEL,
            "device": self.device,
            "loaded": self.model is not None,
            "language": config.LANGUAGE or "auto-detect",
            "task": config.TASK
        }
    
    def unload_model(self):
        """Unload the model to free memory."""
        if self.model is not None:
            del self.model
            self.model = None
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            st.info("Model unloaded to free memory")
    
    def estimate_processing_time(self, duration_seconds: float) -> str:
        """
        Estimate processing time based on audio duration.
        
        Args:
            duration_seconds: Audio duration in seconds
            
        Returns:
            Estimated processing time as string
        """
        # Rough estimates based on device and model
        if self.device == "cuda":
            ratio = 0.1  # GPU is ~10x faster
        elif self.device == "mps":
            ratio = 0.2  # Apple Silicon is ~5x faster
        else:
            ratio = 1.0  # CPU baseline
        
        # Whisper turbo is faster than base models
        if config.WHISPER_MODEL == "turbo":
            ratio *= 0.5
        
        estimated_seconds = duration_seconds * ratio
        
        if estimated_seconds < 60:
            return f"~{int(estimated_seconds)} seconds"
        elif estimated_seconds < 3600:
            return f"~{int(estimated_seconds / 60)} minutes"
        else:
            return f"~{estimated_seconds / 3600:.1f} hours"
    
    def _log_gpu_memory_usage(self, stage: str = ""):
        """Log GPU memory usage for monitoring."""
        if self.device == "cuda" and torch.cuda.is_available():
            try:
                memory_allocated = torch.cuda.memory_allocated() / 1024**3  # GB
                memory_reserved = torch.cuda.memory_reserved() / 1024**3   # GB
                total_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3  # GB
                
                print(f"🔍 GPU Memory {stage}:")
                print(f"   Allocated: {memory_allocated:.2f} GB")
                print(f"   Reserved: {memory_reserved:.2f} GB") 
                print(f"   Total: {total_memory:.2f} GB")
                print(f"   Usage: {(memory_allocated/total_memory)*100:.1f}%")
            except Exception as e:
                print(f"Could not get GPU memory info: {e}")
    
    def _optimize_gpu_settings(self):
        """Optimize GPU settings for RTX 4090 and similar high-end GPUs."""
        if self.device == "cuda":
            try:
                # Enable TensorFloat-32 (TF32) for RTX 30/40 series cards
                torch.backends.cuda.matmul.allow_tf32 = True
                torch.backends.cudnn.allow_tf32 = True
                
                # Enable CUDNN benchmarking for consistent input sizes
                torch.backends.cudnn.benchmark = True
                
                # Set memory fraction to avoid OOM on large models
                if hasattr(torch.cuda, 'set_memory_fraction'):
                    torch.cuda.set_memory_fraction(0.9)  # Use 90% of GPU memory
                
                print("🔧 GPU optimizations enabled for RTX 4090")
                
            except Exception as e:
                print(f"Warning: Could not apply all GPU optimizations: {e}")
