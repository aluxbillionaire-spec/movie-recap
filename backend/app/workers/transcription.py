"""
Transcription Worker

Handle speech-to-text processing using Whisper.
"""

import os
import tempfile
import json
from typing import Dict, Any, List, Optional
from celery import current_task
import whisper
import torch

from app.workers.celery_app import celery_app
from app.core.config import settings


# Global model cache to avoid reloading
_whisper_models = {}


def get_whisper_model(model_size: str = "base"):
    """Get or load Whisper model with caching."""
    
    if model_size not in _whisper_models:
        # Clear cache if we have too many models loaded
        if len(_whisper_models) >= settings.ML_MODEL_CACHE_SIZE:
            _whisper_models.clear()
            
        _whisper_models[model_size] = whisper.load_model(model_size)
        
    return _whisper_models[model_size]


@celery_app.task(bind=True)
def transcribe_audio(
    self, 
    job_id: str, 
    asset_id: str, 
    file_path: str,
    model_size: str = "base",
    language: Optional[str] = None
) -> Dict[str, Any]:
    """
    Transcribe audio from video file using Whisper.
    
    Args:
        job_id: Processing job ID
        asset_id: Asset ID in database
        file_path: Path to video file
        model_size: Whisper model size (tiny, base, small, medium, large)
        language: Optional language hint
        
    Returns:
        Transcription results with word-level timestamps
    """
    
    try:
        current_task.update_state(
            state="PROGRESS",
            meta={"percent": 10, "stage": "extracting_audio", "details": {}}
        )
        
        # Extract audio from video
        audio_path = extract_audio_from_video(file_path, job_id)
        
        current_task.update_state(
            state="PROGRESS",
            meta={"percent": 30, "stage": "loading_model", "details": {"model_size": model_size}}
        )
        
        # Load Whisper model
        model = get_whisper_model(model_size)
        
        current_task.update_state(
            state="PROGRESS",
            meta={"percent": 50, "stage": "transcribing", "details": {}}
        )
        
        # Transcribe audio
        transcribe_options = {
            "verbose": False,
            "word_timestamps": True,
            "temperature": 0.0,  # More deterministic results
        }
        
        if language:
            transcribe_options["language"] = language
            
        result = model.transcribe(audio_path, **transcribe_options)
        
        current_task.update_state(
            state="PROGRESS",
            meta={"percent": 80, "stage": "processing_results", "details": {}}
        )
        
        # Process transcription results
        transcript_data = process_transcription_result(result)
        
        current_task.update_state(
            state="PROGRESS",
            meta={"percent": 100, "stage": "completed", "details": {}}
        )
        
        # Clean up temporary audio file
        if os.path.exists(audio_path):
            os.remove(audio_path)
            
        return {
            "status": "success",
            "transcript": transcript_data,
            "processing_info": {
                "model_size": model_size,
                "language": result.get("language"),
                "duration": transcript_data.get("duration"),
                "word_count": len(transcript_data.get("words", [])),
                "confidence": calculate_average_confidence(transcript_data.get("words", []))
            }
        }
        
    except Exception as e:
        current_task.update_state(
            state="FAILURE",
            meta={"error": str(e), "stage": "transcription"}
        )
        
        # Clean up on error
        if 'audio_path' in locals() and os.path.exists(audio_path):
            os.remove(audio_path)
            
        raise


def extract_audio_from_video(video_path: str, job_id: str) -> str:
    """Extract audio track from video file."""
    
    try:
        import ffmpeg
        
        audio_filename = f"audio_{job_id}.wav"
        audio_path = os.path.join(tempfile.gettempdir(), audio_filename)
        
        # Extract audio using ffmpeg
        (
            ffmpeg
            .input(video_path)
            .output(
                audio_path,
                acodec="pcm_s16le",  # Uncompressed WAV
                ac=1,  # Mono channel
                ar=16000  # 16kHz sample rate (Whisper's preferred)
            )
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        
        return audio_path
        
    except Exception as e:
        raise Exception(f"Failed to extract audio: {str(e)}")


def process_transcription_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """Process Whisper transcription result into structured format."""
    
    # Extract full text
    full_text = result["text"].strip()
    
    # Extract segments with timestamps
    segments = []
    for segment in result["segments"]:
        segments.append({
            "id": segment["id"],
            "start": segment["start"],
            "end": segment["end"],
            "text": segment["text"].strip(),
            "confidence": segment.get("avg_logprob", 0.0)
        })
    
    # Extract word-level timestamps if available
    words = []
    for segment in result["segments"]:
        if "words" in segment:
            for word_info in segment["words"]:
                words.append({
                    "word": word_info["word"].strip(),
                    "start": word_info["start"],
                    "end": word_info["end"],
                    "confidence": word_info.get("probability", 0.0)
                })
    
    return {
        "full_text": full_text,
        "language": result.get("language"),
        "duration": segments[-1]["end"] if segments else 0,
        "segments": segments,
        "words": words
    }


def calculate_average_confidence(words: List[Dict[str, Any]]) -> float:
    """Calculate average confidence score from word-level results."""
    
    if not words:
        return 0.0
        
    confidences = [word.get("confidence", 0.0) for word in words]
    return sum(confidences) / len(confidences)


@celery_app.task(bind=True)
def enhance_transcript_alignment(
    self,
    job_id: str,
    transcript_data: Dict[str, Any],
    video_path: str
) -> Dict[str, Any]:
    """
    Enhance transcript alignment using forced alignment techniques.
    
    Args:
        job_id: Processing job ID
        transcript_data: Original transcript data
        video_path: Path to video file
        
    Returns:
        Enhanced transcript with improved alignment
    """
    
    try:
        current_task.update_state(
            state="PROGRESS",
            meta={"percent": 20, "stage": "preparing_alignment", "details": {}}
        )
        
        # For now, we'll implement a basic alignment enhancement
        # In production, you could use tools like Montreal Forced Aligner
        # or other forced alignment systems
        
        enhanced_words = enhance_word_alignment(transcript_data.get("words", []))
        
        current_task.update_state(
            state="PROGRESS",
            meta={"percent": 80, "stage": "validating_alignment", "details": {}}
        )
        
        # Validate alignment quality
        alignment_quality = validate_alignment_quality(enhanced_words)
        
        current_task.update_state(
            state="PROGRESS",
            meta={"percent": 100, "stage": "completed", "details": {}}
        )
        
        return {
            "status": "success",
            "enhanced_transcript": {
                **transcript_data,
                "words": enhanced_words,
                "alignment_quality": alignment_quality
            },
            "processing_info": {
                "original_word_count": len(transcript_data.get("words", [])),
                "enhanced_word_count": len(enhanced_words),
                "alignment_score": alignment_quality.get("score", 0.0)
            }
        }
        
    except Exception as e:
        current_task.update_state(
            state="FAILURE",
            meta={"error": str(e), "stage": "alignment"}
        )
        raise


def enhance_word_alignment(words: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Enhance word-level alignment using heuristics.
    
    This is a simplified implementation. In production, you would use
    more sophisticated forced alignment techniques.
    """
    
    enhanced_words = []
    
    for i, word in enumerate(words):
        enhanced_word = word.copy()
        
        # Apply smoothing to remove unrealistic gaps or overlaps
        if i > 0:
            prev_end = enhanced_words[-1]["end"]
            if word["start"] > prev_end + 0.5:  # Gap > 0.5 seconds
                enhanced_word["start"] = prev_end + 0.1  # Reduce gap
                
        # Ensure minimum word duration
        duration = word["end"] - enhanced_word["start"]
        if duration < 0.1:  # Minimum 100ms per word
            enhanced_word["end"] = enhanced_word["start"] + 0.1
            
        enhanced_words.append(enhanced_word)
    
    return enhanced_words


def validate_alignment_quality(words: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Validate quality of word-level alignment."""
    
    if not words:
        return {"score": 0.0, "issues": ["No words found"]}
    
    issues = []
    
    # Check for overlapping words
    overlaps = 0
    for i in range(1, len(words)):
        if words[i]["start"] < words[i-1]["end"]:
            overlaps += 1
            
    if overlaps > 0:
        issues.append(f"{overlaps} overlapping words")
    
    # Check for large gaps
    large_gaps = 0
    for i in range(1, len(words)):
        gap = words[i]["start"] - words[i-1]["end"]
        if gap > 2.0:  # Gap > 2 seconds
            large_gaps += 1
            
    if large_gaps > 0:
        issues.append(f"{large_gaps} large gaps between words")
    
    # Calculate overall alignment score
    total_words = len(words)
    problems = overlaps + large_gaps
    score = max(0.0, 1.0 - (problems / total_words))
    
    return {
        "score": score,
        "issues": issues,
        "overlapping_words": overlaps,
        "large_gaps": large_gaps,
        "total_words": total_words
    }