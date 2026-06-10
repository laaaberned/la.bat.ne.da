"""Main orchestrator for visual analysis of video clips"""

import cv2
import numpy as np
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Any, List
from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class VisualMetadata:
    """Visual metadata for a video clip"""
    clip_id: str
    file_path: str
    duration: float
    fps: float
    resolution: tuple
    shot_scale: str  # wide, medium, close-up
    composition_score: float  # 0-1
    camera_movement: str  # static, pan, zoom, tracking
    movement_intensity: float  # 0-1
    lighting_key: str  # key lighting type
    lighting_intensity: float  # 0-1
    mood: str  # bright, dark, neutral, dynamic
    mood_score: float  # 0-1
    scene_transitions: int
    average_brightness: float
    average_contrast: float
    dominant_colors: List[tuple]
    metadata: Dict[str, Any]


class ClipAnalyzer:
    """Analyze video clips for visual metadata"""
    
    def __init__(self, sample_rate: int = 2, target_fps: int = 30):
        """
        Initialize clip analyzer
        
        Args:
            sample_rate: Frames to sample per second (for performance)
            target_fps: Target FPS for processing
        """
        self.sample_rate = sample_rate
        self.target_fps = target_fps
    
    def analyze_clip(self, clip_path: str, clip_id: str = None) -> VisualMetadata:
        """Analyze a video clip and extract visual metadata"""
        clip_path = Path(clip_path)
        
        if clip_id is None:
            clip_id = clip_path.stem
        
        logger.info(f"Analyzing clip: {clip_id} ({clip_path})")
        
        # Open video
        cap = cv2.VideoCapture(str(clip_path))
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {clip_path}")
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0
        
        logger.info(f"Video properties: {width}x{height} @ {fps}fps, {duration:.1f}s")
        
        # Sample frames for analysis
        sample_interval = max(1, int(fps / self.sample_rate))
        frames = []
        frame_indices = []
        
        frame_idx = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_idx % sample_interval == 0:
                frames.append(frame)
                frame_indices.append(frame_idx)
            
            frame_idx += 1
        
        cap.release()
        
        if not frames:
            raise ValueError(f"No frames extracted from video: {clip_path}")
        
        logger.info(f"Sampled {len(frames)} frames from {total_frames} total frames")
        
        # Analyze frames
        brightness_values = []
        contrast_values = []
        
        for frame in frames:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            brightness_values.append(np.mean(gray))
            contrast_values.append(np.std(gray))
        
        avg_brightness = np.mean(brightness_values)
        avg_contrast = np.mean(contrast_values)
        
        # Placeholder implementations for advanced analysis
        # These would use ML models in production
        shot_scale = self._estimate_shot_scale(width, height, avg_brightness)
        composition_score = self._estimate_composition(frames)
        camera_movement = self._detect_camera_movement(frames)
        movement_intensity = self._estimate_movement_intensity(frames)
        lighting_key = self._classify_lighting(avg_brightness)
        lighting_intensity = avg_brightness / 255.0
        mood = self._classify_mood(avg_brightness, avg_contrast)
        mood_score = self._estimate_mood_score(avg_brightness, avg_contrast)
        scene_transitions = self._detect_scene_transitions(frames)
        dominant_colors = self._extract_dominant_colors(frames)
        
        metadata = {
            "sample_count": len(frames),
            "sample_interval_frames": sample_interval,
            "avg_brightness": float(avg_brightness),
            "avg_contrast": float(avg_contrast)
        }
        
        return VisualMetadata(
            clip_id=clip_id,
            file_path=str(clip_path),
            duration=float(duration),
            fps=float(fps),
            resolution=(width, height),
            shot_scale=shot_scale,
            composition_score=float(composition_score),
            camera_movement=camera_movement,
            movement_intensity=float(movement_intensity),
            lighting_key=lighting_key,
            lighting_intensity=float(lighting_intensity),
            mood=mood,
            mood_score=float(mood_score),
            scene_transitions=int(scene_transitions),
            average_brightness=float(avg_brightness),
            average_contrast=float(avg_contrast),
            dominant_colors=dominant_colors,
            metadata=metadata
        )
    
    def _estimate_shot_scale(self, width: int, height: int, brightness: float) -> str:
        """Estimate shot scale (wide, medium, close-up) - placeholder"""
        # In production, use ML model trained on shot scale classification
        if brightness < 80:
            return "close-up"  # Darker often indicates close-up
        elif brightness < 150:
            return "medium"
        else:
            return "wide"
    
    def _estimate_composition(self, frames: List[np.ndarray]) -> float:
        """Estimate composition quality - placeholder"""
        # In production, use composition analysis models
        return np.random.random()
    
    def _detect_camera_movement(self, frames: List[np.ndarray]) -> str:
        """Detect camera movement type - placeholder"""
        # In production, use optical flow analysis
        movements = ["static", "pan", "zoom", "tracking"]
        return movements[int(len(frames) % len(movements))]
    
    def _estimate_movement_intensity(self, frames: List[np.ndarray]) -> float:
        """Estimate movement intensity - placeholder"""
        return np.random.random()
    
    def _classify_lighting(self, brightness: float) -> str:
        """Classify lighting type"""
        if brightness < 85:
            return "low-key"
        elif brightness < 170:
            return "mid-key"
        else:
            return "high-key"
    
    def _classify_mood(self, brightness: float, contrast: float) -> str:
        """Classify mood"""
        if brightness < 100:
            return "dark"
        elif brightness > 200:
            return "bright"
        elif contrast > 80:
            return "dynamic"
        else:
            return "neutral"
    
    def _estimate_mood_score(self, brightness: float, contrast: float) -> float:
        """Estimate mood intensity score"""
        return (brightness / 255.0 + contrast / 100.0) / 2.0
    
    def _detect_scene_transitions(self, frames: List[np.ndarray]) -> int:
        """Detect number of scene transitions - placeholder"""
        # In production, use scene detection algorithms
        return 0
    
    def _extract_dominant_colors(self, frames: List[np.ndarray]) -> List[tuple]:
        """Extract dominant colors from clip - placeholder"""
        # In production, use k-means clustering
        return [(128, 128, 128)]  # Placeholder: middle gray
