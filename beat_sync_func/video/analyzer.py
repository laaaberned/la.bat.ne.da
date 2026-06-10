"""
Video analysis and feature extraction.
"""

import cv2
import numpy as np
from pathlib import Path
from loguru import logger
from beat_sync_func.core.config import Config


class VideoAnalyzer:
    """Analyze video clips and extract features."""
    
    def __init__(self, config: Config):
        """Initialize video analyzer."""
        self.config = config
    
    def analyze(self, video_data: dict) -> dict:
        """Analyze a single video clip."""
        try:
            logger.info(f"Analyzing clip: {Path(video_data['path']).name}")
            
            cap = cv2.VideoCapture(video_data['path'])
            
            if not cap.isOpened():
                raise ValueError(f"Could not open video for analysis")
            
            frame_count = video_data['frame_count']
            sample_count = min(self.config.video.max_frame_sample, frame_count)
            
            # Sample frames for analysis
            frame_indices = np.linspace(
                0,
                frame_count - 1,
                sample_count,
                dtype=int
            )
            
            color_histograms = []
            motion_scores = []
            brightness_values = []
            prev_gray = None
            
            for frame_idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                
                if not ret or frame is None:
                    continue
                
                try:
                    # Compute color histogram
                    hist = cv2.calcHist(
                        [frame],
                        [0, 1, 2],
                        None,
                        [8, 8, 8],
                        [0, 256, 0, 256, 0, 256]
                    )
                    color_histograms.append(hist.flatten())
                    
                    # Compute brightness
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    brightness = np.mean(gray) / 255.0
                    brightness_values.append(brightness)
                    
                    # Compute motion (edge detection)
                    edges = cv2.Canny(gray, 50, 150)
                    motion_score = np.sum(edges) / (edges.size * 255.0)
                    motion_scores.append(motion_score)
                    
                    prev_gray = gray
                    
                except Exception as e:
                    logger.debug(f"Error processing frame {frame_idx}: {e}")
                    continue
            
            cap.release()
            
            if not motion_scores:
                raise ValueError("Failed to extract any frame features")
            
            # Calculate statistics
            avg_motion = np.mean(motion_scores)
            motion_variance = np.var(motion_scores)
            avg_brightness = np.mean(brightness_values)
            
            # Classify energy level
            energy_threshold = 0.3
            energy_level = 'high' if avg_motion > energy_threshold else 'low'
            
            features = {
                'path': video_data['path'],
                'duration': video_data['duration'],
                'fps': video_data['fps'],
                'resolution': video_data['resolution'],
                'color_histogram': np.mean(color_histograms, axis=0) if color_histograms else None,
                'motion_score': avg_motion,
                'motion_variance': motion_variance,
                'brightness': avg_brightness,
                'energy_level': energy_level,
                'scene_cuts': 0,  # Placeholder
            }
            
            logger.info(f"✅ Analysis complete: {energy_level} energy (motion={avg_motion:.3f})")
            return features
            
        except Exception as e:
            logger.error(f"Failed to analyze clip: {e}")
            raise
    
    def analyze_all(self, clips: list) -> list:
        """Analyze multiple clips."""
        if not clips:
            logger.warning("No clips to analyze")
            return []
        
        features_list = []
        for i, clip in enumerate(clips, 1):
            try:
                features = self.analyze(clip)
                features_list.append(features)
            except Exception as e:
                logger.warning(f"[{i}/{len(clips)}] Skipped clip: {e}")
        
        logger.info(f"✅ Analyzed {len(features_list)}/{len(clips)} clips successfully")
        return features_list