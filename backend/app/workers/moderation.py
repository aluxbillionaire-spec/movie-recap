"""
Content Moderation Worker

Handle copyright protection, watermark detection, and content compliance.
"""

import os
import cv2
import numpy as np
from typing import Dict, Any, List
from celery import current_task

from app.workers.celery_app import celery_app


@celery_app.task(bind=True)
def moderate_content(
    self, 
    job_id: str, 
    asset_id: str, 
    file_path: str
) -> Dict[str, Any]:
    """Perform content moderation for copyright compliance."""
    
    try:
        current_task.update_state(
            state="PROGRESS",
            meta={"percent": 20, "stage": "analyzing_content", "details": {}}
        )
        
        # Determine file type
        file_ext = os.path.splitext(file_path)[1].lower()
        is_video = file_ext in ['.mp4', '.avi', '.mkv', '.mov']
        
        if is_video:
            results = moderate_video(file_path)
        else:
            results = moderate_image(file_path)
        
        current_task.update_state(
            state="PROGRESS",
            meta={"percent": 80, "stage": "generating_report", "details": {}}
        )
        
        # Generate compliance report
        compliance = generate_compliance_report(results)
        
        current_task.update_state(
            state="PROGRESS",
            meta={"percent": 100, "stage": "completed", "details": {}}
        )
        
        return {
            "status": "success",
            "results": results,
            "compliance": compliance,
            "requires_review": compliance["requires_manual_review"]
        }
        
    except Exception as e:
        current_task.update_state(
            state="FAILURE",
            meta={"error": str(e), "stage": "moderation"}
        )
        raise


def moderate_video(video_path: str) -> Dict[str, Any]:
    """Moderate video content."""
    
    # Extract frames for analysis
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    frames = []
    for i in range(0, total_frames, max(1, total_frames // 10)):  # 10 sample frames
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ret, frame = cap.read()
        if ret:
            frames.append(frame)
    
    cap.release()
    
    # Analyze frames
    watermark_count = 0
    logo_count = 0
    
    for frame in frames:
        if detect_watermarks(frame):
            watermark_count += 1
        if detect_logos(frame):
            logo_count += 1
    
    return {
        "watermarks_detected": watermark_count > 0,
        "watermark_percentage": (watermark_count / len(frames)) * 100,
        "logos_detected": logo_count > 0,
        "logo_percentage": (logo_count / len(frames)) * 100,
        "frames_analyzed": len(frames)
    }


def moderate_image(image_path: str) -> Dict[str, Any]:
    """Moderate image content."""
    
    image = cv2.imread(image_path)
    
    return {
        "watermarks_detected": detect_watermarks(image),
        "logos_detected": detect_logos(image),
        "analysis_type": "single_image"
    }


def detect_watermarks(image: np.ndarray) -> bool:
    """Detect watermarks using computer vision."""
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Method 1: Edge detection for text watermarks
    edges = cv2.Canny(gray, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    h, w = gray.shape
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if 100 < area < 5000:  # Watermark size range
            x, y, width, height = cv2.boundingRect(contour)
            
            # Check if in typical watermark locations (corners/edges)
            rel_x, rel_y = x / w, y / h
            if (rel_x < 0.2 or rel_x > 0.8 or rel_y < 0.2 or rel_y > 0.8):
                aspect_ratio = width / height
                if 1.5 < aspect_ratio < 8:  # Text-like aspect ratio
                    return True
    
    # Method 2: Template matching for common patterns
    # Simplified - in production would use actual watermark templates
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
    morph = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
    
    # Check corner regions for patterns
    corner_size = min(w, h) // 4
    corners = [
        gray[0:corner_size, 0:corner_size],  # Top-left
        gray[0:corner_size, w-corner_size:w],  # Top-right
        gray[h-corner_size:h, 0:corner_size],  # Bottom-left
        gray[h-corner_size:h, w-corner_size:w]  # Bottom-right
    ]
    
    for corner in corners:
        if corner.size > 0:
            std_dev = np.std(corner)
            if 10 < std_dev < 50:  # Moderate variation typical of watermarks
                return True
    
    return False


def detect_logos(image: np.ndarray) -> bool:
    """Detect logos using simple computer vision."""
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Method 1: Circular logo detection
    circles = cv2.HoughCircles(
        gray, cv2.HOUGH_GRADIENT, dp=1, minDist=50,
        param1=50, param2=30, minRadius=15, maxRadius=100
    )
    
    if circles is not None and len(circles[0]) > 0:
        return True
    
    # Method 2: Rectangular logo detection
    edges = cv2.Canny(gray, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if 200 < area < 8000:  # Logo size range
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / h
            if 0.3 < aspect_ratio < 3.0:  # Reasonable logo proportions
                # Check complexity
                perimeter = cv2.arcLength(contour, True)
                complexity = perimeter**2 / area
                if 10 < complexity < 100:  # Moderate complexity
                    return True
    
    return False


def generate_compliance_report(results: Dict[str, Any]) -> Dict[str, Any]:
    """Generate compliance report with recommendations."""
    
    issues = []
    risk_level = "low"
    
    if results.get("watermarks_detected", False):
        issues.append({
            "type": "watermark_detected",
            "severity": "high",
            "description": "Watermarks detected in content",
            "action": "DO NOT remove watermarks - verify licensing"
        })
        risk_level = "high"
    
    if results.get("logos_detected", False):
        issues.append({
            "type": "logos_detected",
            "severity": "medium",
            "description": "Brand logos detected",
            "action": "Verify trademark usage rights"
        })
        if risk_level != "high":
            risk_level = "medium"
    
    requires_review = risk_level in ["high", "medium"]
    
    recommendations = []
    if requires_review:
        recommendations = [
            "Content contains copyrighted elements",
            "Verify proper licensing before use",
            "Consider fair use documentation",
            "Consult legal counsel if uncertain",
            "NEVER attempt to remove watermarks"
        ]
    
    return {
        "risk_level": risk_level,
        "requires_manual_review": requires_review,
        "issues": issues,
        "recommendations": recommendations,
        "legal_notice": "This analysis does not constitute legal advice"
    }


def create_copyright_pattern():
    """Create copyright symbol pattern for detection."""
    pattern = np.zeros((20, 20), dtype=np.uint8)
    cv2.circle(pattern, (10, 10), 8, 255, 2)
    cv2.putText(pattern, "C", (7, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, 255, 1)
    return pattern


def create_tv_station_pattern():
    """Create TV station watermark pattern."""
    pattern = np.zeros((30, 60), dtype=np.uint8)
    cv2.rectangle(pattern, (5, 5), (55, 25), 255, 2)
    cv2.putText(pattern, "TV", (15, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, 255, 2)
    return pattern


def create_streaming_service_pattern():
    """Create streaming service pattern."""
    pattern = np.zeros((25, 80), dtype=np.uint8)
    cv2.rectangle(pattern, (2, 2), (78, 23), 255, 1)
    cv2.putText(pattern, "STREAM", (8, 17), cv2.FONT_HERSHEY_SIMPLEX, 0.4, 255, 1)
    return pattern