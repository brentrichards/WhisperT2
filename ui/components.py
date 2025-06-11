"""
UI components for the Whisper Transcription App.
Contains reusable Streamlit UI components and layouts.
"""

import streamlit as st
from typing import Dict, Any, Optional, Callable
from pathlib import Path
import config
from transcription.formatter import TranscriptionFormatter
from export.document import DocumentExporter


class UIComponents:
    """Collection of reusable UI components for the Streamlit app."""
    
    def __init__(self):
        """Initialize UI components."""
        self.formatter = TranscriptionFormatter()
        self.exporter = DocumentExporter()
    
    def render_header(self):
        """Render the main application header."""
        st.set_page_config(
            page_title=config.APP_TITLE,
            page_icon="🎤",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        st.title("🎤 " + config.APP_TITLE)
        st.markdown(config.APP_DESCRIPTION)
        st.markdown("---")
    
    def render_sidebar_info(self):
        """Render sidebar with app information and settings."""
        with st.sidebar:
            st.header("ℹ️ Information")
            
            # GPU Status section
            st.subheader("🚀 GPU Status")
            try:
                from transcription import WhisperEngine
                engine = WhisperEngine()
                gpu_status = engine.get_gpu_status()
                
                if gpu_status.get("gpu_available"):
                    st.success("✅ GPU Acceleration Enabled")
                    if "gpu_name" in gpu_status:
                        st.info(f"**GPU:** {gpu_status['gpu_name']}")
                        memory_used = gpu_status.get('memory_allocated_gb', 0)
                        memory_total = gpu_status.get('memory_total_gb', 0)
                        if memory_total > 0:
                            memory_percent = (memory_used / memory_total) * 100
                            st.metric("GPU Memory", f"{memory_used:.1f}/{memory_total:.1f} GB", 
                                    f"{memory_percent:.1f}% used")
                        if gpu_status.get('tf32_enabled'):
                            st.info("🔧 TF32 Optimization: Enabled")
                else:
                    st.warning("⚠️ Using CPU (slower)")
            except Exception as e:
                st.warning(f"Could not check GPU status: {str(e)}")
            
            # Model information
            st.subheader("🤖 Model Settings")
            st.info(f"""
            **Model:** Whisper {config.WHISPER_MODEL}
            **Sample Rate:** {config.SAMPLE_RATE} Hz
            **Format:** {config.AUDIO_FORMAT.upper()}
            **Max File Size:** {config.MAX_FILE_SIZE} MB
            """)
            
            # Instructions
            st.subheader("📋 Instructions")
            st.markdown("""
            1. **YouTube**: Paste a URL to download audio
            2. **Upload**: Drag & drop or browse for audio files
            3. **Process**: Click to start transcription
            4. **Download**: Export results in multiple formats
            5. **Reset**: Clear session for next file
            """)
            
            # Supported formats
            st.subheader("📁 Supported Formats")
            formats = ", ".join([ext.upper() for ext in config.ALLOWED_EXTENSIONS])
            st.markdown(f"**Audio:** {formats}")
            st.markdown("**Export:** TXT, DOCX, SRT, VTT")
    
    def render_youtube_section(self, downloader, processor) -> Optional[Path]:
        """
        Render YouTube URL input section.
        
        Args:
            downloader: YouTube downloader instance
            processor: Audio processor instance
            
        Returns:
            Path to processed audio file if successful, None otherwise
        """
        st.header("📺 YouTube Audio Download")
        
        # URL input
        youtube_url = st.text_input(
            "Enter YouTube URL:",
            placeholder="https://www.youtube.com/watch?v=...",
            help="Paste a YouTube video URL to download and transcribe its audio"
        )
        
        if youtube_url:
            # Validate URL
            is_valid, message = downloader.validate_youtube_url(youtube_url)
            
            if is_valid:
                # Get video info
                video_info = downloader.get_video_info(youtube_url)
                
                if video_info:
                    # Display video information
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.success("✅ Valid YouTube URL")
                        st.write(f"**Title:** {video_info['title']}")
                        st.write(f"**Uploader:** {video_info['uploader']}")
                    
                    with col2:
                        duration_str = self.formatter.format_timestamp(video_info['duration'])
                        st.write(f"**Duration:** {duration_str}")
                        st.write(f"**Views:** {video_info['view_count']:,}")
                    
                    # Download button
                    if st.button("🔄 Download & Process Audio", type="primary"):
                        return self._download_youtube_audio(downloader, youtube_url)
            else:
                st.error(f"❌ {message}")
        
                return None
    
    def _download_youtube_audio(self, downloader, url: str) -> Optional[Path]:
        """Download YouTube audio with progress tracking."""
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def progress_callback(progress: float, message: str = ""):
            progress_bar.progress(progress)
            if message:
                status_text.text(message)
            else:
                status_text.text(f"Downloading: {progress:.1%}")
        
        try:
            status_text.text("Starting download...")
            audio_path = downloader.download_audio(url, progress_callback)
            
            if audio_path:
                progress_bar.progress(1.0)
                status_text.success("✅ Download complete!")
                return audio_path
            else:
                status_text.error("❌ Download failed")
                return None
                
        except Exception as e:
            status_text.error(f"❌ Error: {str(e)}")
            return None
        finally:
            # Clear progress indicators after a delay
            import time
            time.sleep(2)
            progress_bar.empty()
            status_text.empty()
    
    def render_upload_section(self, processor) -> Optional[Path]:
        """
        Render file upload section.
        
        Args:
            processor: Audio processor instance
            
        Returns:
            Path to processed audio file if successful, None otherwise
        """
        st.header("📁 Upload Audio File")
        
        uploaded_file = st.file_uploader(
            "Choose an audio file",
            type=[ext[1:] for ext in config.ALLOWED_EXTENSIONS],  # Remove dots
            help=f"Supported formats: {', '.join(config.ALLOWED_EXTENSIONS)}"
        )
        
        if uploaded_file is not None:
            # Display file information
            file_size_mb = len(uploaded_file.getbuffer()) / (1024 * 1024)
            
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"**File:** {uploaded_file.name}")
                st.info(f"**Size:** {file_size_mb:.1f} MB")
            
            # Validate file size
            if file_size_mb > config.MAX_FILE_SIZE:
                st.error(f"❌ File too large: {file_size_mb:.1f}MB (max: {config.MAX_FILE_SIZE}MB)")
                return None
            
            # Process button
            if st.button("🔄 Process Uploaded File", type="primary"):
                with st.spinner("Processing audio file..."):
                    processed_path = processor.process_uploaded_file(uploaded_file)
                    
                    if processed_path:
                        # Validate processed file
                        is_valid, message = processor.validate_audio_file(processed_path)
                        
                        if is_valid:
                            st.success("✅ File processed successfully!")
                            
                            # Show audio info
                            audio_info = processor.get_audio_info(processed_path)
                            with col2:
                                st.info(f"**Duration:** {audio_info.get('duration', 0):.1f}s")
                                st.info(f"**Sample Rate:** {audio_info.get('sample_rate', 0)} Hz")
                            
                            return processed_path
                        else:
                            st.error(f"❌ {message}")
                    else:
                        st.error("❌ Failed to process file")
        
        return None
    
    def render_transcription_section(self, engine, audio_path: Path) -> Optional[Dict[str, Any]]:
        """
        Render transcription processing section.
        
        Args:
            engine: Whisper engine instance
            audio_path: Path to audio file to transcribe
            
        Returns:
            Transcription results if successful, None otherwise
        """
        st.header("🎯 Transcription")
        
        # Show audio file info
        processor_temp = __import__('audio.processor', fromlist=['AudioProcessor']).AudioProcessor()
        audio_info = processor_temp.get_audio_info(audio_path)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Duration", f"{audio_info.get('duration', 0):.1f}s")
        with col2:
            st.metric("File Size", f"{audio_info.get('size_mb', 0):.1f} MB")
        with col3:
            estimated_time = engine.estimate_processing_time(audio_info.get('duration', 0))
            st.metric("Est. Time", estimated_time)
        
        # Transcription button
        if st.button("🚀 Start Transcription", type="primary"):
            return self._perform_transcription(engine, audio_path)
        
        return None
    
    def _perform_transcription(self, engine, audio_path: Path) -> Optional[Dict[str, Any]]:
        """Perform transcription with progress tracking."""
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def progress_callback(progress: float, message: str):
            progress_bar.progress(progress)
            status_text.text(message)
        
        try:
            result = engine.transcribe_audio(audio_path, progress_callback)
            
            if result:
                progress_bar.progress(1.0)
                status_text.success("✅ Transcription complete!")
                return result
            else:
                status_text.error("❌ Transcription failed")
                return None
                
        except Exception as e:
            status_text.error(f"❌ Error: {str(e)}")
            return None
        finally:
            # Clear progress indicators
            import time
            time.sleep(2)
            progress_bar.empty()
            status_text.empty()
    
    def render_results_section(self, transcription_data: Dict[str, Any], source_filename: str):
        """
        Render transcription results with download options.
        
        Args:
            transcription_data: Processed transcription data
            source_filename: Original filename for export naming
        """
        st.header("📊 Results")
        
        # Summary statistics
        summary = self.formatter.get_transcription_summary(transcription_data)
        
        cols = st.columns(len(summary))
        for i, (key, value) in enumerate(summary.items()):
            with cols[i]:
                st.metric(key, value)
        
        st.markdown("---")
        
        # Plain text transcription
        self._render_plain_text_section(transcription_data, source_filename)
        
        # Word timestamps section
        self._render_word_timestamps_section(transcription_data, source_filename)
        
        # Segment timestamps section
        self._render_segment_timestamps_section(transcription_data, source_filename)
          # Additional export options
        self._render_additional_exports(transcription_data, source_filename)
    
    def _render_plain_text_section(self, transcription_data: Dict[str, Any], source_filename: str):
        """Render plain text transcription section."""
        st.subheader("📝 Plain Text Transcription")
        
        text = self.formatter.format_plain_text(transcription_data)
        
        st.text_area(
            "Transcription:",
            value=text,
            height=200,
            help="Plain text transcription without timestamps"
        )
        
        # Download buttons
        col1, col2 = st.columns(2)
        
        with col1:
            txt_data = self.exporter.create_text_download(text, source_filename)
            filename_txt = self.exporter.get_filename(source_filename, "plain_text", "txt")
            st.download_button(
                label="📄 Download TXT",
                data=txt_data,
                file_name=filename_txt,
                mime="text/plain"
            )
        
        with col2:
            docx_data = self.exporter.create_docx_download(transcription_data, "plain_text", source_filename)
            if docx_data:
                filename_docx = self.exporter.get_filename(source_filename, "plain_text", "docx")
                st.download_button(
                    label="📄 Download DOCX",                data=docx_data,
                    file_name=filename_docx,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
    
    def _render_word_timestamps_section(self, transcription_data: Dict[str, Any], source_filename: str):
        """Render word timestamps section."""
        with st.expander("🕐 Word-Level Timestamps", expanded=False):
            word_text = self.formatter.format_word_timestamps(transcription_data)
            
            st.text_area(
                "Word timestamps:",
                value=word_text,
                height=300,
                key="word_timestamps"
            )
            
            # Download buttons
            col1, col2 = st.columns(2)
            
            with col1:
                txt_data = self.exporter.create_text_download(word_text, source_filename)
                filename_txt = self.exporter.get_filename(source_filename, "word_timestamps", "txt")
                st.download_button(
                    label="📄 Download TXT",
                    data=txt_data,
                    file_name=filename_txt,
                    mime="text/plain",
                    key="word_txt"
                )
            
            with col2:
                docx_data = self.exporter.create_docx_download(transcription_data, "word_timestamps", source_filename)
                if docx_data:
                    filename_docx = self.exporter.get_filename(source_filename, "word_timestamps", "docx")
                    st.download_button(
                        label="📄 Download DOCX",
                        data=docx_data,
                        file_name=filename_docx,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        key="word_docx"                )
    
    def _render_segment_timestamps_section(self, transcription_data: Dict[str, Any], source_filename: str):
        """Render segment timestamps section."""
        with st.expander("📑 Segment-Level Timestamps", expanded=False):
            segment_text = self.formatter.format_segment_timestamps(transcription_data)
            
            st.text_area(
                "Segment timestamps:",
                value=segment_text,
                height=300,
                key="segment_timestamps"
            )
            
            # Download buttons
            col1, col2 = st.columns(2)
            
            with col1:
                txt_data = self.exporter.create_text_download(segment_text, source_filename)
                filename_txt = self.exporter.get_filename(source_filename, "segment_timestamps", "txt")
                st.download_button(
                    label="📄 Download TXT",
                    data=txt_data,
                    file_name=filename_txt,
                    mime="text/plain",
                    key="segment_txt"
                )
            
            with col2:
                docx_data = self.exporter.create_docx_download(transcription_data, "segment_timestamps", source_filename)
                if docx_data:
                    filename_docx = self.exporter.get_filename(source_filename, "segment_timestamps", "docx")
                    st.download_button(
                        label="📄 Download DOCX",
                        data=docx_data,
                        file_name=filename_docx,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        key="segment_docx"
                    )
    
    def _render_additional_exports(self, transcription_data: Dict[str, Any], source_filename: str):
        """Render additional export options."""
        with st.expander("🎬 Subtitle Formats", expanded=False):
            st.info("Export as subtitle files for video editing or playback")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # SRT format
                srt_data = self.exporter.create_subtitle_download(transcription_data, "srt")
                if srt_data:
                    filename_srt = self.exporter.get_filename(source_filename, "subtitles", "srt")
                    st.download_button(
                        label="📺 Download SRT",
                        data=srt_data,
                        file_name=filename_srt,
                        mime="text/plain",
                        help="SubRip subtitle format"
                    )
            
            with col2:
                # VTT format
                vtt_data = self.exporter.create_subtitle_download(transcription_data, "vtt")
                if vtt_data:
                    filename_vtt = self.exporter.get_filename(source_filename, "subtitles", "vtt")
                    st.download_button(
                        label="🌐 Download VTT",
                        data=vtt_data,
                        file_name=filename_vtt,
                        mime="text/vtt",
                        help="WebVTT subtitle format"
                    )
    
    def render_reset_section(self):
        """Render session reset section."""
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col2:
            if st.button("🔄 Reset Session", type="secondary", use_container_width=True):
                # Clear session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                
                # Clean up temporary files
                try:
                    config.cleanup_temp_files()
                except:
                    pass
                
                st.success("✅ Session reset! You can now process another file.")
                st.rerun()
    
    def show_error(self, message: str):
        """Show error message with appropriate styling."""
        st.error(f"❌ {message}")
    
    def show_success(self, message: str):
        """Show success message with appropriate styling."""
        st.success(f"✅ {message}")
    
    def show_info(self, message: str):
        """Show info message with appropriate styling."""
        st.info(f"ℹ️ {message}")
    
    def show_warning(self, message: str):
        """Show warning message with appropriate styling."""
        st.warning(f"⚠️ {message}")
