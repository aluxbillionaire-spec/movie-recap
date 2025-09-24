"""
Alignment Worker

Handle script-to-video alignment using semantic matching and forced alignment.
"""

import os
import json
import tempfile
from typing import Dict, Any, List, Tuple, Optional
from celery import current_task
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import re

from app.workers.celery_app import celery_app
from app.core.config import settings


# Global model cache
_alignment_models = {}


def get_sentence_transformer(model_name: str = "all-MiniLM-L6-v2"):
    """Get or load sentence transformer model with caching."""
    
    if model_name not in _alignment_models:
        if len(_alignment_models) >= settings.ML_MODEL_CACHE_SIZE:
            _alignment_models.clear()
        
        _alignment_models[model_name] = SentenceTransformer(model_name)
    
    return _alignment_models[model_name]


@celery_app.task(bind=True)
def align_script_to_video(
    self, 
    job_id: str, 
    script_path: str, 
    transcript_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Align script scenes to video segments using semantic matching.
    
    Args:
        job_id: Processing job ID
        script_path: Path to script file
        transcript_data: Transcription data with timestamps
        
    Returns:
        Alignment results with matched scenes
    """
    
    try:
        current_task.update_state(
            state="PROGRESS",
            meta={"percent": 10, "stage": "parsing_script", "details": {}}
        )
        
        # Parse script into scenes
        script_scenes = parse_script_file(script_path)
        
        current_task.update_state(
            state="PROGRESS",
            meta={"percent": 30, "stage": "processing_transcript", "details": {"scenes_found": len(script_scenes)}}
        )
        
        # Process transcript into segments
        transcript_segments = process_transcript_segments(transcript_data)
        
        current_task.update_state(
            state="PROGRESS",
            meta={"percent": 50, "stage": "computing_embeddings", "details": {}}
        )
        
        # Compute semantic embeddings
        scene_embeddings = compute_scene_embeddings(script_scenes)
        segment_embeddings = compute_segment_embeddings(transcript_segments)
        
        current_task.update_state(
            state="PROGRESS",
            meta={"percent": 70, "stage": "matching_scenes", "details": {}}
        )
        
        # Perform semantic matching
        alignments = perform_semantic_matching(
            script_scenes, transcript_segments,
            scene_embeddings, segment_embeddings
        )
        
        current_task.update_state(
            state="PROGRESS",
            meta={"percent": 90, "stage": "refining_alignment", "details": {}}
        )
        
        # Refine alignment with temporal constraints
        refined_alignments = refine_alignment_temporal(alignments, transcript_data)
        
        current_task.update_state(
            state="PROGRESS",
            meta={"percent": 100, "stage": "completed", "details": {}}
        )
        
        return {
            "status": "success",
            "alignments": refined_alignments,
            "processing_info": {
                "script_scenes_count": len(script_scenes),
                "transcript_segments_count": len(transcript_segments),
                "matched_scenes": len([a for a in refined_alignments if a["confidence"] > settings.ALIGNMENT_CONFIDENCE_THRESHOLD]),
                "average_confidence": np.mean([a["confidence"] for a in refined_alignments]) if refined_alignments else 0
            }
        }
        
    except Exception as e:
        current_task.update_state(
            state="FAILURE",
            meta={"error": str(e), "stage": "alignment"}
        )
        raise


def parse_script_file(script_path: str) -> List[Dict[str, Any]]:
    """Parse script file into scenes."""
    
    try:
        # Read script file
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        # Try different encodings
        encodings = ['latin-1', 'cp1252', 'iso-8859-1']
        content = None
        
        for encoding in encodings:
            try:
                with open(script_path, 'r', encoding=encoding) as f:
                    content = f.read()
                break
            except UnicodeDecodeError:
                continue
        
        if content is None:
            raise Exception("Unable to decode script file")
    
    # Parse content into scenes
    scenes = []
    
    # Common scene markers
    scene_patterns = [
        r'SCENE\s+(\d+)',
        r'INT\.|EXT\.',
        r'FADE IN:',
        r'CUT TO:',
        r'^\d+\.',
        r'Chapter\s+\d+',
        r'ACT\s+[IVX]+',
    ]
    
    # Split content into potential scenes
    lines = content.split('\n')
    current_scene = {'scene_number': 1, 'text': '', 'markers': []}
    scene_number = 1
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        if not line:
            continue
        
        # Check for scene markers
        is_scene_marker = False
        for pattern in scene_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                is_scene_marker = True
                break
        
        if is_scene_marker and current_scene['text'].strip():
            # Save current scene and start new one
            current_scene['text'] = current_scene['text'].strip()
            current_scene['word_count'] = len(current_scene['text'].split())
            scenes.append(current_scene)
            
            current_scene = {
                'scene_number': scene_number,
                'text': '',
                'markers': [line]
            }
            scene_number += 1
        else:
            # Add to current scene
            if is_scene_marker:
                current_scene['markers'].append(line)
            else:
                current_scene['text'] += ' ' + line
    
    # Add final scene
    if current_scene['text'].strip():
        current_scene['text'] = current_scene['text'].strip()
        current_scene['word_count'] = len(current_scene['text'].split())
        scenes.append(current_scene)
    
    # If no scenes detected, treat whole content as one scene
    if not scenes:
        scenes = [{
            'scene_number': 1,
            'text': content.strip(),
            'word_count': len(content.split()),
            'markers': []
        }]
    
    return scenes


def process_transcript_segments(transcript_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Process transcript into semantic segments."""
    
    segments = transcript_data.get("segments", [])
    words = transcript_data.get("words", [])
    
    if not segments:
        # Create segments from words if segments not available
        if words:
            segments = create_segments_from_words(words)
        else:
            raise Exception("No transcript segments or words available")
    
    # Create sliding window segments for better matching
    window_segments = []
    window_size = 3  # 3 segments per window
    
    for i in range(len(segments)):
        # Single segment
        window_segments.append({
            'segment_id': f"single_{i}",
            'start_time': segments[i]['start'],
            'end_time': segments[i]['end'],
            'text': segments[i]['text'].strip(),
            'confidence': segments[i].get('confidence', 0.0),
            'window_type': 'single'
        })
        
        # Window segment (if enough segments available)
        if i + window_size <= len(segments):
            combined_text = ' '.join([seg['text'].strip() for seg in segments[i:i+window_size]])
            window_segments.append({
                'segment_id': f"window_{i}_{i+window_size-1}",
                'start_time': segments[i]['start'],
                'end_time': segments[i+window_size-1]['end'],
                'text': combined_text,
                'confidence': np.mean([seg.get('confidence', 0.0) for seg in segments[i:i+window_size]]),
                'window_type': 'window'
            })
    
    return window_segments


def create_segments_from_words(words: List[Dict[str, Any]], segment_duration: float = 10.0) -> List[Dict[str, Any]]:
    """Create segments from word-level timestamps."""
    
    segments = []
    current_segment = []
    current_start = 0
    
    for word in words:
        if not current_segment:
            current_start = word['start']
        
        current_segment.append(word)
        
        # Create segment when duration exceeded or at end
        if (word['end'] - current_start) >= segment_duration or word == words[-1]:
            segment_text = ' '.join([w['word'] for w in current_segment])
            avg_confidence = np.mean([w.get('confidence', 0.0) for w in current_segment])
            
            segments.append({
                'start': current_start,
                'end': word['end'],
                'text': segment_text,
                'confidence': avg_confidence
            })
            
            current_segment = []
    
    return segments


def compute_scene_embeddings(scenes: List[Dict[str, Any]]) -> np.ndarray:
    """Compute sentence embeddings for script scenes."""
    
    model = get_sentence_transformer()
    
    # Prepare texts for encoding
    scene_texts = []
    for scene in scenes:
        # Clean and prepare text
        text = scene['text']
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
        text = text.strip()
        
        # Use scene markers as context if available
        if scene.get('markers'):
            context = ' '.join(scene['markers'])
            text = f"{context} {text}"
        
        scene_texts.append(text)
    
    # Compute embeddings
    embeddings = model.encode(scene_texts, show_progress_bar=False)
    
    return embeddings


def compute_segment_embeddings(segments: List[Dict[str, Any]]) -> np.ndarray:
    """Compute sentence embeddings for transcript segments."""
    
    model = get_sentence_transformer()
    
    # Prepare texts
    segment_texts = [seg['text'] for seg in segments]
    
    # Compute embeddings
    embeddings = model.encode(segment_texts, show_progress_bar=False)
    
    return embeddings


def perform_semantic_matching(
    scenes: List[Dict[str, Any]], 
    segments: List[Dict[str, Any]],
    scene_embeddings: np.ndarray, 
    segment_embeddings: np.ndarray
) -> List[Dict[str, Any]]:
    """Perform semantic matching between scenes and segments."""
    
    # Compute cosine similarity matrix
    similarity_matrix = cosine_similarity(scene_embeddings, segment_embeddings)
    
    alignments = []
    
    for i, scene in enumerate(scenes):
        # Find best matching segments
        scene_similarities = similarity_matrix[i]
        
        # Get top matches
        top_indices = np.argsort(scene_similarities)[::-1][:5]  # Top 5 matches
        
        best_match_idx = top_indices[0]
        best_segment = segments[best_match_idx]
        confidence = scene_similarities[best_match_idx]
        
        # Additional confidence factors
        confidence_factors = {
            'semantic_similarity': confidence,
            'length_similarity': compute_length_similarity(scene, best_segment),
            'position_similarity': compute_position_similarity(i, best_match_idx, len(scenes), len(segments)),
            'transcript_confidence': best_segment.get('confidence', 0.0)
        }
        
        # Weighted final confidence
        final_confidence = (
            confidence_factors['semantic_similarity'] * 0.5 +
            confidence_factors['length_similarity'] * 0.2 +
            confidence_factors['position_similarity'] * 0.2 +
            confidence_factors['transcript_confidence'] * 0.1
        )
        
        alignment = {
            'scene_number': scene['scene_number'],
            'scene_text': scene['text'][:200] + '...' if len(scene['text']) > 200 else scene['text'],
            'matched_segment_id': best_segment['segment_id'],
            'video_start_time': best_segment['start_time'],
            'video_end_time': best_segment['end_time'],
            'confidence': final_confidence,
            'confidence_factors': confidence_factors,
            'alternative_matches': [
                {
                    'segment_id': segments[idx]['segment_id'],
                    'start_time': segments[idx]['start_time'],
                    'end_time': segments[idx]['end_time'],
                    'confidence': scene_similarities[idx]
                }
                for idx in top_indices[1:3]  # Include 2 alternatives
            ]
        }
        
        alignments.append(alignment)
    
    return alignments


def compute_length_similarity(scene: Dict[str, Any], segment: Dict[str, Any]) -> float:
    """Compute similarity based on text length."""
    
    scene_words = scene.get('word_count', len(scene['text'].split()))
    segment_duration = segment['end_time'] - segment['start_time']
    
    # Estimate words from duration (average speaking rate: 150 words/minute)
    estimated_words = (segment_duration / 60) * 150
    
    if estimated_words == 0:
        return 0.0
    
    # Similarity based on word count ratio
    ratio = min(scene_words, estimated_words) / max(scene_words, estimated_words)
    
    return ratio


def compute_position_similarity(scene_idx: int, segment_idx: int, total_scenes: int, total_segments: int) -> float:
    """Compute similarity based on relative positions."""
    
    scene_position = scene_idx / max(1, total_scenes - 1)
    segment_position = segment_idx / max(1, total_segments - 1)
    
    position_diff = abs(scene_position - segment_position)
    
    # Convert difference to similarity (1 - diff)
    return 1.0 - position_diff


def refine_alignment_temporal(alignments: List[Dict[str, Any]], transcript_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Refine alignment using temporal constraints."""
    
    refined_alignments = alignments.copy()
    
    # Sort by scene number
    refined_alignments.sort(key=lambda x: x['scene_number'])
    
    # Apply temporal constraints (scenes should generally be in order)
    for i in range(1, len(refined_alignments)):
        current = refined_alignments[i]
        previous = refined_alignments[i-1]
        
        # If current scene starts before previous scene ends, flag for review
        if current['video_start_time'] < previous['video_end_time']:
            # Reduce confidence for overlapping scenes
            overlap_penalty = 0.3
            current['confidence'] *= (1 - overlap_penalty)
            current['temporal_conflict'] = True
            
            # Try to find alternative match that doesn't overlap
            for alt_match in current['alternative_matches']:
                if alt_match['start_time'] >= previous['video_end_time']:
                    # Use alternative match
                    current['video_start_time'] = alt_match['start_time']
                    current['video_end_time'] = alt_match['end_time']
                    current['matched_segment_id'] = alt_match['segment_id']
                    current['confidence'] = alt_match['confidence']
                    current['temporal_conflict'] = False
                    break
    
    # Flag low-confidence alignments for manual review
    for alignment in refined_alignments:
        if alignment['confidence'] < settings.ALIGNMENT_CONFIDENCE_THRESHOLD:
            alignment['manual_review_required'] = True
            alignment['flagged_reason'] = 'low_confidence_alignment'
        else:
            alignment['manual_review_required'] = False
    
    return refined_alignments


@celery_app.task(bind=True)
def validate_alignment_quality(self, job_id: str, alignments: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Validate and score alignment quality."""
    
    try:
        total_scenes = len(alignments)
        high_confidence_scenes = len([a for a in alignments if a['confidence'] > 0.8])
        medium_confidence_scenes = len([a for a in alignments if 0.5 <= a['confidence'] <= 0.8])
        low_confidence_scenes = len([a for a in alignments if a['confidence'] < 0.5])
        
        # Calculate overall alignment score
        confidence_scores = [a['confidence'] for a in alignments]
        average_confidence = np.mean(confidence_scores) if confidence_scores else 0
        
        # Check for temporal issues
        temporal_conflicts = len([a for a in alignments if a.get('temporal_conflict', False)])
        
        # Overall quality score
        quality_factors = {
            'average_confidence': average_confidence,
            'high_confidence_ratio': high_confidence_scenes / total_scenes if total_scenes > 0 else 0,
            'temporal_consistency': 1.0 - (temporal_conflicts / total_scenes) if total_scenes > 0 else 1.0
        }
        
        overall_score = (
            quality_factors['average_confidence'] * 0.5 +
            quality_factors['high_confidence_ratio'] * 0.3 +
            quality_factors['temporal_consistency'] * 0.2
        )
        
        # Determine if manual review is needed
        needs_manual_review = (
            overall_score < 0.6 or
            low_confidence_scenes > total_scenes * 0.3 or
            temporal_conflicts > total_scenes * 0.1
        )
        
        return {
            "status": "success",
            "quality_score": overall_score,
            "quality_factors": quality_factors,
            "scene_statistics": {
                "total_scenes": total_scenes,
                "high_confidence": high_confidence_scenes,
                "medium_confidence": medium_confidence_scenes,
                "low_confidence": low_confidence_scenes,
                "temporal_conflicts": temporal_conflicts
            },
            "needs_manual_review": needs_manual_review,
            "recommendations": generate_alignment_recommendations(alignments, quality_factors)
        }
        
    except Exception as e:
        current_task.update_state(
            state="FAILURE",
            meta={"error": str(e), "stage": "validation"}
        )
        raise


def generate_alignment_recommendations(alignments: List[Dict[str, Any]], quality_factors: Dict[str, float]) -> List[str]:
    """Generate recommendations for improving alignment."""
    
    recommendations = []
    
    if quality_factors['average_confidence'] < 0.6:
        recommendations.append("Consider reviewing script content for clarity and detail")
    
    if quality_factors['high_confidence_ratio'] < 0.5:
        recommendations.append("Many scenes have low confidence matches - manual review recommended")
    
    if quality_factors['temporal_consistency'] < 0.8:
        recommendations.append("Temporal order issues detected - check scene sequence")
    
    low_conf_scenes = [a for a in alignments if a['confidence'] < 0.5]
    if low_conf_scenes:
        recommendations.append(f"{len(low_conf_scenes)} scenes need manual review")
    
    return recommendations