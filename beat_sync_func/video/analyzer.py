"""
Video analysis and feature extraction.
"""

import cv2
import numpy as np
from loguru import logger
from beat_sync_func.core.config import Config


class VideoAnalyzer:
    """Analyze video clips and extract features."""
    
    def __init__(self, config: Config):
        """Initialize video analyzer."""
        self.config = config
    
    def analyze(self, video_data: dict) -> dict:
        """Analyze a single video clip."""
        logger.info(f"Analyzing clip: {video_data['path']}")
        
        cap = cv2.VideoCapture(video_data['path'])
        
        # Sample frames for analysis
        frame_indices = np.linspace(
            0,
            video_data['frame_count'] - 1,
            min(30, video_data['frame_count']),
            dtype=int
        )
        
        color_histogram = []
        motion_scores = []
        
        for i, frame_idx in enumerate(frame_indices):
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            
            if not ret:
                continue
            
            # Compute color histogram
            hist = cv2.calcHist(
                [frame],
                [0, 1, 2],
                None,
                [8, 8, 8],
                [0, 256, 0, 256, 0, 256]
            )
            color_histogram.append(hist.flatten())
            
            # Compute motion (edge detection)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            motion_scores.append(np.sum(edges) / edges.size)
        
        cap.release()
        
        features = {
            'path': video_data['path'],
            'duration': video_data['duration'],
            'fps': video_data['fps'],
            'resolution': video_data['resolution'],
            'color_histogram': np.mean(color_histogram, axis=0) if color_histogram else None,
            'motion_score': np.mean(motion_scores) if motion_scores else 0.0,
            'energy_level': 'high' if motion_scores and np.mean(motion_scores) > 0.3 else 'low',
        }
        
        logger.info(f"✅ Analysis complete: {features['energy_level']} energy")
        return features
    
    def analyze_all(self, clips: list) -> list:
        """Analyze multiple clips."""
        features_list = []
        for clip in clips:
            try:
                features = self.analyze(clip)
                features_list.append(features)
            except Exception as e:
                logger.warning(f"Could not analyze {clip['path']}: {e}")
        
        return features_list