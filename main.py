"""
Main Streamlit application for the Whisper Transcription App.
Professional-grade audio transcription using OpenAI's Whisper Turbo model.
"""

import streamlit as st
from pathlib import Path
import sys

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent))

import config
from audio import AudioProcessor, YouTubeDownloader
from transcription import WhisperEngine
from ui import UIComponents


class WhisperTranscriptionApp:
    """Main application class for the Whisper Transcription App."""
    
    def __init__(self):
        """Initialize the application."""
        # Ensure required directories exist
        config.ensure_directories()
        
        # Initialize components
        self.ui = UIComponents()
        self.audio_processor = AudioProcessor()
        self.youtube_downloader = YouTubeDownloader()
        self.whisper_engine = WhisperEngine()
        
        # Initialize session state
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Initialize Streamlit session state variables."""
        if 'audio_file' not in st.session_state:
            st.session_state.audio_file = None
        
        if 'transcription_result' not in st.session_state:
            st.session_state.transcription_result = None
        
        if 'source_filename' not in st.session_state:
            st.session_state.source_filename = None
        
        if 'processing_stage' not in st.session_state:
            st.session_state.processing_stage = 'input'  # input, processing, results
    
    def run(self):
        """Run the main application."""
        # Render header and sidebar
        self.ui.render_header()
        self.ui.render_sidebar_info()
        
        # Main application flow based on processing stage
        if st.session_state.processing_stage == 'input':
            self._handle_input_stage()
        elif st.session_state.processing_stage == 'processing':
            self._handle_processing_stage()
        elif st.session_state.processing_stage == 'results':
            self._handle_results_stage()
        
        # Always show reset option
        self.ui.render_reset_section()
    
    def _handle_input_stage(self):
        """Handle the input stage where users provide audio files."""
        st.subheader("🎵 Choose Your Audio Source")
        
        # Create tabs for different input methods
        tab1, tab2 = st.tabs(["📺 YouTube URL", "📁 Upload File"])
        
        with tab1:
            audio_file = self.ui.render_youtube_section(
                self.youtube_downloader, 
                self.audio_processor
            )
            
            if audio_file:
                st.session_state.audio_file = audio_file
                st.session_state.source_filename = audio_file.stem
                st.session_state.processing_stage = 'processing'
                st.rerun()
        
        with tab2:
            audio_file = self.ui.render_upload_section(self.audio_processor)
            
            if audio_file:
                st.session_state.audio_file = audio_file
                st.session_state.source_filename = audio_file.stem
                st.session_state.processing_stage = 'processing'
                st.rerun()
    
    def _handle_processing_stage(self):
        """Handle the processing stage where transcription occurs."""
        if st.session_state.audio_file is None:
            st.error("No audio file found. Please go back and select an audio source.")
            st.session_state.processing_stage = 'input'
            st.rerun()
            return
        
        audio_file = Path(st.session_state.audio_file)
        
        # Show current file info
        st.success(f"✅ Audio file ready: {audio_file.name}")
        
        # Render transcription section
        transcription_result = self.ui.render_transcription_section(
            self.whisper_engine, 
            audio_file
        )
        
        if transcription_result:
            st.session_state.transcription_result = transcription_result
            st.session_state.processing_stage = 'results'
            st.rerun()
        
        # Option to go back and select different file
        if st.button("⬅️ Select Different File"):
            st.session_state.processing_stage = 'input'
            st.session_state.audio_file = None
            st.rerun()
    
    def _handle_results_stage(self):
        """Handle the results stage where transcription results are displayed."""
        if st.session_state.transcription_result is None:
            st.error("No transcription results found.")
            st.session_state.processing_stage = 'input'
            st.rerun()
            return
        
        # Display results
        self.ui.render_results_section(
            st.session_state.transcription_result,
            st.session_state.source_filename or "transcription"
        )
        
        # Navigation options
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("⬅️ Process Another File"):
                # Clean up and go back to input
                self._cleanup_session()
                st.session_state.processing_stage = 'input'
                st.rerun()
        
        with col2:
            if st.button("🔄 Re-transcribe Current File"):
                # Keep file, re-do transcription
                st.session_state.transcription_result = None
                st.session_state.processing_stage = 'processing'
                st.rerun()
    
    def _cleanup_session(self):
        """Clean up session data and temporary files."""
        # Clean up temporary audio files
        self.audio_processor.cleanup_temp_files()
        
        # Clear session state
        st.session_state.audio_file = None
        st.session_state.transcription_result = None
        st.session_state.source_filename = None
    
    def _handle_errors(self):
        """Handle any application-level errors."""
        try:
            # Check if required dependencies are available
            import whisper
            import yt_dlp
            import docx
            
        except ImportError as e:
            st.error(f"""
            ❌ Missing required dependency: {str(e)}
            
            Please install all required packages:
            ```bash
            pip install -r requirements.txt
            ```
            """)
            st.stop()
        
        except Exception as e:
            st.error(f"❌ Application error: {str(e)}")
            st.info("Please try refreshing the page or contact support if the issue persists.")


def main():
    """Main entry point for the application."""
    try:
        app = WhisperTranscriptionApp()
        app.run()
        
    except Exception as e:
        st.error(f"❌ Failed to start application: {str(e)}")
        st.info("""
        **Troubleshooting:**
        1. Ensure all dependencies are installed: `pip install -r requirements.txt`
        2. Check that FFmpeg is installed and available in PATH
        3. Verify sufficient disk space for temporary files
        4. Try refreshing the page
        """)


if __name__ == "__main__":
    main()
