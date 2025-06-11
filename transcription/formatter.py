"""
Transcription formatting utilities for the Whisper Transcription App.
Handles formatting of transcription results for different output formats.
"""

from typing import Dict, Any, List
from datetime import timedelta
import config


class TranscriptionFormatter:
    """Handles formatting of transcription results."""
    
    @staticmethod
    def format_timestamp(seconds: float) -> str:
        """
        Format timestamp in seconds to HH:MM:SS.mmm format.
        
        Args:
            seconds: Timestamp in seconds
            
        Returns:
            Formatted timestamp string
        """
        td = timedelta(seconds=seconds)
        hours, remainder = divmod(td.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        milliseconds = int((seconds % 1) * 1000)
        return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}.{milliseconds:03d}"
    
    @staticmethod
    def format_plain_text(transcription_data: Dict[str, Any]) -> str:
        """
        Format transcription as plain text.
        
        Args:
            transcription_data: Processed transcription data
            
        Returns:
            Plain text transcription        """
        return transcription_data.get("text", "").strip()
    
    @staticmethod
    def format_word_timestamps(transcription_data: Dict[str, Any]) -> str:
        """
        Format transcription with true word-level timestamps.
        
        Args:
            transcription_data: Processed transcription data
            
        Returns:
            Word-level timestamped transcription (individual words)
        """
        words = transcription_data.get("words", [])
        if not words:
            return "No word-level timestamps available."
        
        formatted_lines = []
        formatted_lines.append("WORD-LEVEL TIMESTAMPS")
        formatted_lines.append("=" * 50)
        formatted_lines.append("Each word shown with individual timestamps")
        formatted_lines.append("")
        
        # Group words into lines for readability (about 8-10 words per line)
        words_per_line = 8
        for i in range(0, len(words), words_per_line):
            line_words = words[i:i + words_per_line]
            
            # Create the word line with individual timestamps
            word_entries = []
            for word_data in line_words:
                word = word_data.get("word", "").strip()
                start = word_data.get("start", 0)
                end = word_data.get("end", 0)
                
                if not word:
                    continue
                
                start_ts = TranscriptionFormatter.format_timestamp(start)
                end_ts = TranscriptionFormatter.format_timestamp(end)
                word_entries.append(f'"{word}" [{start_ts}-{end_ts}]')
            
            if word_entries:
                formatted_lines.append(" | ".join(word_entries))
                formatted_lines.append("")
        
        return "\n".join(formatted_lines)
    
    @staticmethod
    def format_segment_timestamps(transcription_data: Dict[str, Any]) -> str:
        """
        Format transcription with segment-level timestamps.
        
        Args:
            transcription_data: Processed transcription data
            
        Returns:
            Segment-level timestamped transcription
        """
        segments = transcription_data.get("segments", [])
        if not segments:
            return "No segment-level timestamps available."
        
        formatted_lines = []
        formatted_lines.append("SEGMENT-LEVEL TIMESTAMPS")
        formatted_lines.append("=" * 50)
        formatted_lines.append("")
        
        for i, segment in enumerate(segments, 1):
            start = segment.get("start", 0)
            end = segment.get("end", 0)
            text = segment.get("text", "").strip()
            
            if not text:
                continue
            
            start_ts = TranscriptionFormatter.format_timestamp(start)
            end_ts = TranscriptionFormatter.format_timestamp(end)
            
            formatted_lines.append(f"Segment {i:03d}")
            formatted_lines.append(f"Time: {start_ts} --> {end_ts}")
            formatted_lines.append(f"Text: {text}")
            formatted_lines.append("-" * 40)
        
        return "\n".join(formatted_lines)
    
    @staticmethod
    def format_srt_subtitles(transcription_data: Dict[str, Any]) -> str:
        """
        Format transcription as SRT subtitle format.
        
        Args:
            transcription_data: Processed transcription data
            
        Returns:
            SRT formatted transcription
        """
        segments = transcription_data.get("segments", [])
        if not segments:
            return "No segments available for SRT format."
        
        srt_lines = []
        
        for i, segment in enumerate(segments, 1):
            start = segment.get("start", 0)
            end = segment.get("end", 0)
            text = segment.get("text", "").strip()
            
            if not text:
                continue
            
            # SRT timestamp format: HH:MM:SS,mmm
            start_ts = TranscriptionFormatter.format_timestamp(start).replace('.', ',')
            end_ts = TranscriptionFormatter.format_timestamp(end).replace('.', ',')
            
            srt_lines.append(str(i))
            srt_lines.append(f"{start_ts} --> {end_ts}")
            srt_lines.append(text)
            srt_lines.append("")
        
        return "\n".join(srt_lines)
    
    @staticmethod
    def format_vtt_subtitles(transcription_data: Dict[str, Any]) -> str:
        """
        Format transcription as WebVTT subtitle format.
        
        Args:
            transcription_data: Processed transcription data
            
        Returns:
            WebVTT formatted transcription
        """
        segments = transcription_data.get("segments", [])
        if not segments:
            return "No segments available for VTT format."
        
        vtt_lines = ["WEBVTT", ""]
        
        for segment in segments:
            start = segment.get("start", 0)
            end = segment.get("end", 0)
            text = segment.get("text", "").strip()
            
            if not text:
                continue
            
            start_ts = TranscriptionFormatter.format_timestamp(start)
            end_ts = TranscriptionFormatter.format_timestamp(end)
            
            vtt_lines.append(f"{start_ts} --> {end_ts}")
            vtt_lines.append(text)
            vtt_lines.append("")
        
        return "\n".join(vtt_lines)
    
    @staticmethod
    def get_transcription_summary(transcription_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate a summary of transcription statistics.
        
        Args:
            transcription_data: Processed transcription data
            
        Returns:
            Dictionary containing transcription summary
        """
        duration = transcription_data.get("duration", 0)
        word_count = transcription_data.get("word_count", 0)
        segment_count = transcription_data.get("segment_count", 0)
        language = transcription_data.get("language", "unknown")
        
        # Calculate words per minute
        wpm = int(word_count / (duration / 60)) if duration > 0 else 0
        
        return {
            "Duration": TranscriptionFormatter.format_timestamp(duration),
            "Word Count": f"{word_count:,}",
            "Segments": str(segment_count),
            "Language": language.upper(),
            "Words per Minute": str(wpm),
            "Characters": f"{len(transcription_data.get('text', '')):,}"
        }
    
    @staticmethod
    def truncate_for_display(text: str, max_length: int = None) -> str:
        """
        Truncate text for display in UI if it's too long.
        
        Args:
            text: Text to potentially truncate
            max_length: Maximum length (uses config default if None)
            
        Returns:
            Truncated text with ellipsis if needed
        """
        if max_length is None:
            max_length = config.MAX_DISPLAY_LENGTH
        
        if len(text) <= max_length:
            return text
        
        return text[:max_length] + "\n\n... (truncated for display)"
