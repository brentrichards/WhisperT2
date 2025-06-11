"""
Whisper transcription engine for the Whisper Transcription App.
Handles audio transcription using OpenAI's Whisper model with GPU optimization.
"""

import whisper
import torch
from pathlib import Path
from typing import Dict, Any, Optional
import streamlit as st
import config


class WhisperEngine:
    """Handles audio transcription using Whisper model with RTX 4090 optimization."""
    
    def __init__(self):
        """Initialize the Whisper engine."""
        self.model = None
        self.device = self._get_device()
        # Apply GPU optimizations for RTX 4090
        self._optimize_gpu_settings()
        
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
    
    def _optimize_gpu_settings(self):
        """Optimize GPU settings for RTX 4090 and similar high-end GPUs."""
        if self.device == "cuda":
            try:
                # Enable TensorFloat-32 (TF32) for RTX 30/40 series cards
                torch.backends.cuda.matmul.allow_tf32 = True
                torch.backends.cudnn.allow_tf32 = True
                
                # Enable CUDNN benchmarking for consistent input sizes
                torch.backends.cudnn.benchmark = True
                
                # Set optimal memory growth
                torch.cuda.empty_cache()
                
                print("🔧 GPU optimizations enabled for RTX 4090")
                
            except Exception as e:
                print(f"Warning: Could not apply all GPU optimizations: {e}")
    
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
    
    def load_model(self) -> bool:
        """
        Load the Whisper model with GPU optimization.
        
        Returns:
            True if model loaded successfully, False otherwise
        """
        try:
            if self.model is None:
                with st.spinner(f"Loading Whisper {config.WHISPER_MODEL} model on {self.device.upper()}..."):
                    # Clear GPU cache before loading model for optimal memory usage
                    if self.device == "cuda":
                        torch.cuda.empty_cache()
                        self._log_gpu_memory_usage("before model loading")
                        
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
    
    def transcribe_audio(self, audio_path: Path, progress_callback=None) -> Optional[Dict[str, Any]]:
        """
        Transcribe audio file using Whisper with GPU acceleration.
        
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
                progress_callback(0.1, "Starting GPU transcription...")
            
            # Log GPU memory before transcription
            if self.device == "cuda":
                self._log_gpu_memory_usage("before transcription")            # Transcribe with Whisper using GPU (Triton disabled for compatibility)
            result = self.model.transcribe(
                str(audio_path),
                language=config.LANGUAGE,
                task=config.TASK,
                verbose=False,
                word_timestamps=True,  # Enable word-level timestamps
                fp16=self.device == "cuda"  # Use FP16 on GPU for speed
            )
            
            if progress_callback:
                progress_callback(0.9, "Processing results...")
            
            # Log GPU memory after transcription
            if self.device == "cuda":
                self._log_gpu_memory_usage("after transcription")
            
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
                    "end": segment.get("end"),
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
        Get information about the loaded model and GPU.
        
        Returns:
            Dictionary containing model and GPU information
        """
        info = {
            "model": config.WHISPER_MODEL,
            "device": self.device,
            "loaded": self.model is not None,
            "language": config.LANGUAGE or "auto-detect",
            "task": config.TASK
        }
        
        # Add GPU specific information
        if self.device == "cuda" and torch.cuda.is_available():
            info.update({
                "gpu_name": torch.cuda.get_device_name(0),
                "cuda_version": torch.version.cuda,
                "gpu_memory_total": f"{torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB",
                "gpu_memory_allocated": f"{torch.cuda.memory_allocated() / 1024**3:.2f} GB",            "tf32_enabled": torch.backends.cuda.matmul.allow_tf32
            })
        
        return info
    
    def unload_model(self):
        """Unload the model to free GPU memory."""
        if self.model is not None:
            del self.model
            self.model = None
            
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                self._log_gpu_memory_usage("after model unload")
            st.info("Model unloaded to free GPU memory")
    
    def estimate_processing_time(self, duration_seconds: float) -> str:
        """
        Estimate processing time based on audio duration and device.
        
        Args:
            duration_seconds: Audio duration in seconds
            
        Returns:
            Estimated processing time as string
        """        # Realistic estimates based on actual performance observations
        # Accounts for Triton kernel fallbacks and real-world performance
        if self.device == "cuda":
            # RTX 4090 with Triton fallbacks - conservative estimate based on real performance
            ratio = 0.15  # GPU is ~6-7x faster than CPU (accounting for Triton fallbacks)
        elif self.device == "mps":
            ratio = 0.25  # Apple Silicon estimate
        else:
            ratio = 1.5  # CPU baseline (slower due to word timestamps)
        
        # Whisper turbo is faster than base models but not dramatically
        if config.WHISPER_MODEL == "turbo":
            ratio *= 0.8  # More conservative speedup estimate
        
        # Add overhead for word-level timestamp processing (significant overhead)
        ratio *= 1.3  # 30% overhead for word timestamps and post-processing
        
        estimated_seconds = duration_seconds * ratio
        
        if estimated_seconds < 60:
            return f"~{int(estimated_seconds)} seconds"
        elif estimated_seconds < 3600:
            return f"~{int(estimated_seconds / 60)} minutes"
        else:
            return f"~{estimated_seconds / 3600:.1f} hours"
    
    def get_gpu_status(self) -> Dict[str, Any]:
        """Get current GPU status and utilization."""
        if self.device != "cuda" or not torch.cuda.is_available():
            return {"gpu_available": False}
        
        try:
            return {
                "gpu_available": True,
                "gpu_name": torch.cuda.get_device_name(0),
                "memory_allocated_gb": torch.cuda.memory_allocated() / 1024**3,
                "memory_reserved_gb": torch.cuda.memory_reserved() / 1024**3,
                "memory_total_gb": torch.cuda.get_device_properties(0).total_memory / 1024**3,
                "cuda_version": torch.version.cuda,
                "device_count": torch.cuda.device_count(),
                "tf32_enabled": torch.backends.cuda.matmul.allow_tf32
            }
        except Exception as e:
            return {"gpu_available": True, "error": str(e)}
