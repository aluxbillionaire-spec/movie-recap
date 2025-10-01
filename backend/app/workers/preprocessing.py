"""
Preprocessing Worker

Handle video analysis, scene detection, and initial processing.
"""

import os
import tempfile
import subprocess
import json
from typing import Dict, Any, List
from celery import current_task
import cv2
import ffmpeg
from scenedetect import detect, ContentDetector

from app.workers.celery_app import celery_app
from app.core.config import settings


@celery_app.task(bind=True)
def preprocess_video(self, job_id: str, asset_id: str, file_path: str) -> Dict[str, Any]:
    """
    Preprocess video file: extract metadata, detect scenes, create preview.
    
    Args:
        job_id: Processing job ID
        asset_id: Asset ID in database
        file_path: Path to video file
        
    Returns:
        Dict with processing results
    """
    
    try:
        # Update job progress
        current_task.update_state(
            state="PROGRESS",
            meta={"percent": 10, "stage": "extracting_metadata", "details": {}}
        )
        
        # Extract video metadata using ffprobe
        metadata = extract_video_metadata(file_path)
        
        current_task.update_state(
            state="PROGRESS", 
            meta={"percent": 30, "stage": "detecting_scenes", "details": metadata}
        )
        
        # Detect scenes
        scenes = detect_video_scenes(file_path)
        
        current_task.update_state(
            state="PROGRESS",
            meta={"percent": 60, "stage": "creating_preview", "details": {"scenes_count": len(scenes)}}
        )
        
        # Create low-resolution preview
        preview_path = create_video_preview(file_path, job_id)
        
        current_task.update_state(
            state="PROGRESS",
            meta={"percent": 80, "stage": "extracting_thumbnails", "details": {}}
        )
        
        # Extract thumbnails for key scenes
        thumbnails = extract_scene_thumbnails(file_path, scenes[:10])  # First 10 scenes
        
        current_task.update_state(
            state="PROGRESS",
            meta={"percent": 100, "stage": "completed", "details": {}}
        )
        
        return {
            "status": "success",
            "metadata": metadata,
            "scenes": scenes,
            "preview_path": preview_path,
            "thumbnails": thumbnails,
            "processing_info": {
                "duration_seconds": metadata.get("duration"),
                "resolution": f"{metadata.get('width')}x{metadata.get('height')}",
                "fps": metadata.get("fps"),
                "scenes_detected": len(scenes)
            }
        }
        
    except Exception as e:
        current_task.update_state(
            state="FAILURE",
            meta={"error": str(e), "stage": "preprocessing"}
        )
        raise


def extract_video_metadata(file_path: str) -> Dict[str, Any]:
    """Extract video metadata using ffprobe."""
    
    try:
        probe = ffmpeg.probe(file_path)
        video_stream = next(
            (stream for stream in probe["streams"] if stream["codec_type"] == "video"), 
            None
        )
        audio_stream = next(
            (stream for stream in probe["streams"] if stream["codec_type"] == "audio"), 
            None
        )
        
        metadata = {
            "duration": float(probe["format"]["duration"]),
            "size_bytes": int(probe["format"]["size"]),
            "bit_rate": int(probe["format"]["bit_rate"]),
            "format_name": probe["format"]["format_name"],
        }
        
        if video_stream:
            metadata.update({
                "width": int(video_stream["width"]),
                "height": int(video_stream["height"]),
                "fps": eval(video_stream["r_frame_rate"]),  # Convert fraction to float
                "video_codec": video_stream["codec_name"],
                "video_bit_rate": int(video_stream.get("bit_rate", 0)) if video_stream.get("bit_rate") else None,
            })
            
        if audio_stream:
            metadata.update({
                "audio_codec": audio_stream["codec_name"],
                "audio_channels": int(audio_stream["channels"]),
                "audio_sample_rate": int(audio_stream["sample_rate"]),
                "audio_bit_rate": int(audio_stream.get("bit_rate", 0)) if audio_stream.get("bit_rate") else None,
            })
            
        return metadata
        
    except Exception as e:
        raise Exception(f"Failed to extract video metadata: {str(e)}")


def detect_video_scenes(file_path: str, threshold: float = 0.4) -> List[Dict[str, Any]]:
    """Detect scene changes in video using PySceneDetect."""
    
    try:
        # Use content-aware scene detection
        scene_list = detect(file_path, ContentDetector(threshold=threshold))
        
        scenes = []
        for i, (start_time, end_time) in enumerate(scene_list):
            scenes.append({
                "scene_number": i + 1,
                "start_time": start_time.get_seconds(),
                "end_time": end_time.get_seconds(),
                "duration": (end_time - start_time).get_seconds()
            })
            
        return scenes
        
    except Exception as e:
        raise Exception(f"Failed to detect scenes: {str(e)}")


def create_video_preview(file_path: str, job_id: str) -> str:
    """Create low-resolution preview video."""
    
    try:
        # Create preview with reduced resolution and quality
        preview_filename = f"preview_{job_id}.mp4"
        preview_path = os.path.join(tempfile.gettempdir(), preview_filename)
        
        # Use ffmpeg to create preview (480p, lower bitrate)
        (
            ffmpeg
            .input(file_path)
            .filter("scale", 854, 480)  # Scale to 480p
            .output(
                preview_path,
                vcodec="libx264",
                crf=28,  # Higher CRF = lower quality/size
                preset="fast",
                acodec="aac",
                audio_bitrate="64k"
            )
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        
        return preview_path
        
    except Exception as e:
        raise Exception(f"Failed to create video preview: {str(e)}")


def extract_scene_thumbnails(file_path: str, scenes: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Extract thumbnail images from key scenes."""
    
    thumbnails = []
    
    try:
        for scene in scenes:
            # Extract thumbnail from middle of scene
            timestamp = scene["start_time"] + (scene["duration"] / 2)
            
            thumbnail_filename = f"thumb_{scene['scene_number']}_{timestamp:.2f}.jpg"
            thumbnail_path = os.path.join(tempfile.gettempdir(), thumbnail_filename)
            
            # Use ffmpeg to extract thumbnail
            (
                ffmpeg
                .input(file_path, ss=timestamp)
                .filter("scale", 320, 180)  # Small thumbnail size
                .output(thumbnail_path, vframes=1, format="image2")
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            
            thumbnails.append({
                "scene_number": scene["scene_number"],
                "timestamp": timestamp,
                "thumbnail_path": thumbnail_path
            })
            
        return thumbnails
        
    except Exception as e:
        raise Exception(f"Failed to extract thumbnails: {str(e)}")


@celery_app.task(bind=True)
def validate_upload(self, file_path: str, file_type: str) -> Dict[str, Any]:
    """
    Validate uploaded file meets requirements.
    
    Args:
        file_path: Path to uploaded file
        file_type: Type of file (video, script)
        
    Returns:
        Validation results
    """
    
    try:
        if file_type == "video":
            return validate_video_file(file_path)
        elif file_type == "script":
            return validate_script_file(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
            
    except Exception as e:
        current_task.update_state(
            state="FAILURE",
            meta={"error": str(e), "stage": "validation"}
        )
        raise


def validate_video_file(file_path: str) -> Dict[str, Any]:
    """Validate video file requirements."""
    
    try:
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Check file size limit (12GB)
        if file_size > settings.MAX_UPLOAD_SIZE:
            raise ValueError(f"File size {file_size} exceeds limit {settings.MAX_UPLOAD_SIZE}")
        
        # Extract metadata to check duration
        metadata = extract_video_metadata(file_path)
        duration = metadata.get("duration", 0)
        
        # Check duration limit (10 hours)
        if duration > settings.MAX_VIDEO_DURATION:
            raise ValueError(f"Video duration {duration}s exceeds limit {settings.MAX_VIDEO_DURATION}s")
        
        # Check if it's a valid video file
        if not metadata.get("width") or not metadata.get("height"):
            raise ValueError("Invalid video file: no video stream found")
        
        return {
            "status": "valid",
            "file_size": file_size,
            "duration": duration,
            "metadata": metadata
        }
        
    except Exception as e:
        return {
            "status": "invalid",
            "error": str(e)
        }


def validate_script_file(file_path: str) -> Dict[str, Any]:
    """Validate script file requirements."""
    
    try:
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Check file size limit (1GB)
        if file_size > settings.MAX_SCRIPT_SIZE:
            raise ValueError(f"Script size {file_size} exceeds limit {settings.MAX_SCRIPT_SIZE}")
        
        # Try to read and validate content
        # This is a basic validation - in production you'd want more sophisticated parsing
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if len(content.strip()) < 10:
                raise ValueError("Script content too short")
                
        except UnicodeDecodeError:
            # Try different encodings
            encodings = ['latin-1', 'cp1252', 'iso-8859-1']
            content = None
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
                    
            if content is None:
                raise ValueError("Unable to decode script file")
        
        return {
            "status": "valid", 
            "file_size": file_size,
            "character_count": len(content),
            "line_count": len(content.splitlines())
        }
        
    except Exception as e:
        return {
            "status": "invalid",
            "error": str(e)
        }